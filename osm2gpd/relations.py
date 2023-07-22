import logging
from functools import partial
from itertools import accumulate
from typing import Generator

import geopandas as gpd
import pandas as pd
from shapely import (
    GeometryCollection,
    LineString,
    MultiLineString,
    MultiPolygon,
    Polygon,
    unary_union,
)
from shapely.ops import linemerge

from .proto import PrimitiveGroup, Relation
from .tags import get_tags
from .unpacked import RelationGroup

logger = logging.getLogger(__name__)


class ConsolidationError(Exception):
    pass


class UnknownInputException(Exception):
    pass


def consolidate_polygons(parts: gpd.GeoSeries) -> Generator[Polygon, None, None]:
    for gtype, geoms in parts.groupby(parts.geom_type):
        match gtype:
            case "Polygon":
                yield from iter(geoms)
            case "LinearRing":
                yield from (Polygon(g) for g in geoms)
            case "LineString":
                merged = linemerge(iter(geoms))

                if isinstance(merged, LineString):
                    yield Polygon(merged.coords)
                else:
                    yield from (Polygon(g.coords) for g in merged.geoms)
            case _:
                raise ConsolidationError(
                    f"Could not consolidate Polygon for type {gtype}"
                )


def consolidate_linestrings(parts: gpd.GeoSeries) -> Generator[LineString, None, None]:
    for gtype, geoms in parts.groupby(parts.geom_type):
        match gtype:
            case "Polygon":
                yield from (poly.boundary for poly in geoms)
            case "LinearRing" | "LineString":
                yield from iter(geoms)
            case _:
                raise ConsolidationError(
                    f"Could not consolidate LineString for type {gtype}"
                )


def parse_multipolygon_relation(
    relation: Relation, ways: gpd.GeoDataFrame, string_table: list[str]
) -> Polygon | MultiPolygon:
    ids: list[int] = list(accumulate(relation.memids))
    roles = pd.Series(dict(zip(ids, [string_table[x] for x in relation.roles_sid])))

    if all((type_ == 1 for type_ in relation.types)):
        ids_ = ways.index.intersection(ids)
        geoms = ways.loc[ids_, "geometry"]
        roles = roles.loc[ids_]

        outer = list(consolidate_polygons(geoms[roles == "outer"]))
        inner = list(consolidate_polygons(geoms[roles == "inner"]))

        return unary_union(outer).difference(unary_union(inner))
    else:
        logger.warning("Unable to parse multipolygon - invalid member geometries")
        raise NotImplementedError()


def parse_boundary_relation(
    relation: Relation, ways: gpd.GeoDataFrame, string_table: list[str]
) -> LineString | MultiLineString:
    """Boundaries are parsed as LineString, 'label', 'admin_centre' and
    'subarea' roles will be ignored.

    For more information, see
    https://wiki.openstreetmap.org/wiki/Relation:boundary#Relation_members
    """
    ids: list[int] = list(accumulate(relation.memids))
    roles = pd.Series(dict(zip(ids, [string_table[x] for x in relation.roles_sid])))

    ids_ = ways.index.intersection(ids)

    geoms = ways.loc[ids_, "geometry"]
    roles = roles.loc[ids_]

    return linemerge(consolidate_linestrings(geoms[roles.isin(("outer", "inner"))]))


def parse_generic_relation(
    relation: Relation,
    ways: gpd.GeoDataFrame,
    nodes: gpd.GeoDataFrame,
) -> GeometryCollection:
    ids: list[int] = list(accumulate(relation.memids))

    geoms = (
        ways.loc[ways.index.intersection(ids), "geometry"].to_list()
        + nodes.loc[nodes.index.intersection(ids), "geometry"].to_list()
    )

    return GeometryCollection(geoms)


def parse(
    group: PrimitiveGroup,
    string_table: list[str],
    nodes: gpd.GeoDataFrame,
    ways: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    tags = {}
    relations = {}

    for relation in group.relations:
        rel_tags: dict[str, str] = get_tags(relation, string_table)

        match rel_tags["type"]:
            case "multipolygon":
                geometry = parse_multipolygon_relation(relation, ways, string_table)
            case "boundary":
                geometry = parse_boundary_relation(relation, ways, string_table)
            case _:
                geometry = parse_generic_relation(relation, ways, nodes)

        if relation.info is not None:
            parsed = {
                "geometry": geometry,
                "version": relation.info.version,
                "changeset": relation.info.changeset,
                "visible": relation.info.visible,
            }
        else:
            parsed = {"geometry": geometry}

        relations[relation.id] = parsed
        tags[relation.id] = rel_tags

    tags = pd.DataFrame.from_dict(
        tags,
        orient="index",
        dtype=pd.SparseDtype(str),
    )

    return gpd.GeoDataFrame.from_dict(relations, orient="index", crs="EPSG:4326").join(
        tags
    )


def resolve_buffer(
    nodes: gpd.GeoDataFrame, ways: gpd.GeoDataFrame, relation_buffer: list[partial]
) -> gpd.GeoDataFrame:
    return pd.concat(
        (relations(nodes=nodes, ways=ways) for relations in relation_buffer)
    )


def unpack_relation_group(
    group: PrimitiveGroup, string_table: list[str]
) -> RelationGroup:
    ids: list[int] = []
    versions: list[int] = []
    member_ids: list[list[int]] = []
    member_types: list[list[str]] = []
    member_roles: list[list[str]] = []
    tags: dict[int, dict[str, str]] = {}
    visible: list[bool] = []
    changeset: list[int] = []

    for i, relation in enumerate(group.relations):
        ids.append(relation.id)

        member_types.append(
            [relation.MemberType.keys()[type_].lower() for type_ in relation.types]
        )
        member_ids.append(list(accumulate(relation.memids)))
        member_roles.append([string_table[sid] for sid in relation.roles_sid])

        _tags = get_tags(relation, string_table)
        if len(_tags) > 0:
            tags[i] = _tags

        # fixme: add optional here
        versions.append(relation.info.version)
        visible.append(relation.info.visible)
        changeset.append(relation.info.changeset)

    return RelationGroup(
        ids=ids,
        tags=tags,
        version=versions,
        changeset=changeset,
        visible=visible,
        member_ids=member_ids,
        member_roles=member_roles,
        member_types=member_types,
    )
