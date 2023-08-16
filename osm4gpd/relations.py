import logging
from functools import partial
from typing import Generator

import geopandas as gpd
import numpy as np
import pandas as pd
from numpy.typing import NDArray
from shapely import (
    Geometry,
    GeometryCollection,
    LineString,
    MultiLineString,
    MultiPolygon,
    Polygon,
    unary_union,
)
from shapely.ops import linemerge

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
    members: NDArray[np.int64],
    roles: NDArray[np.object_],
    types: NDArray[np.object_],
    ways: gpd.GeoDataFrame,
    relations: gpd.GeoDataFrame | None = None,
) -> Polygon | MultiPolygon:
    if (types == "relation").any() and relations is None:
        raise ConsolidationError(
            "Can not consolidate multipolygon that depends on relations."
        )
    elif (types == "relation").any() and relations is not None:
        outer_ = relations.loc[
            members[(types == "relation") & (roles == "outer")], "geometry"
        ].to_list()
        inner_ = relations.loc[
            members[(types == "relation") & (roles == "inner_")], "geometry"
        ].to_list()
    else:
        outer_ = []
        inner_ = []

    loc = np.isin(members, ways.index)
    roles = roles[loc]
    geoms = ways.loc[members[loc], "geometry"]

    outer = list(consolidate_polygons(geoms[roles == "outer"]))
    inner = list(consolidate_polygons(geoms[roles == "inner"]))

    return unary_union(outer + outer_).difference(unary_union(inner + inner_))


def parse_boundary_relation(
    members: NDArray[np.int64],
    roles: NDArray[np.object_],
    types: NDArray[np.object_],
    ways: gpd.GeoDataFrame,
) -> LineString | MultiLineString:
    """Boundaries are parsed as LineString, 'label', 'admin_centre' and
    'subarea' roles will be ignored.

    For more information, see
    https://wiki.openstreetmap.org/wiki/Relation:boundary#Relation_members
    """
    idx = (
        np.isin(members, ways.index)
        & (types == "way")
        & np.isin(roles, ("outer", "inner"))
    )
    return linemerge(consolidate_linestrings(ways.loc[members[idx], "geometry"]))


def parse_generic_relation(
    members: NDArray[np.int64],
    types: NDArray[np.object_],
    *,
    ways: gpd.GeoDataFrame,
    nodes: gpd.GeoDataFrame,
    relations: gpd.GeoDataFrame | None = None,
) -> GeometryCollection:
    geoms = (
        ways.loc[ways.index.intersection(members[types == "way"]), "geometry"].to_list()
        + nodes.loc[
            nodes.index.intersection(members[types == "node"]), "geometry"
        ].to_list()
    )

    if relations is not None:
        geoms += relations.loc[
            relations.index.intersection(members[types == "relation"]), "geometry"
        ].to_list()

    return GeometryCollection(geoms)


def _consolidate_geometries(
    group: RelationGroup, ways: gpd.GeoDataFrame, nodes: gpd.GeoDataFrame
) -> Generator[tuple[int, Geometry | partial], None, None]:
    for idx, (members, roles, types) in enumerate(
        zip(group.member_ids, group.member_roles, group.member_types)
    ):
        match group.tags.get(idx, {"type": "generic"})["type"]:
            case "multipolygon":
                if (types == "relation").any():
                    yield idx, partial(
                        parse_multipolygon_relation,
                        members=members,
                        roles=roles,
                        types=types,
                        ways=ways,
                    )
                    continue

                yield idx, parse_multipolygon_relation(members, roles, types, ways)
            case "boundary":
                yield idx, parse_boundary_relation(members, roles, types, ways)
            case _:
                if (types == "relation").any():
                    yield idx, partial(
                        parse_generic_relation,
                        members=members,
                        types=types,
                        ways=ways,
                        nodes=nodes,
                    )
                    continue

                yield idx, parse_generic_relation(
                    members, types, ways=ways, nodes=nodes
                )


def consolidate_relations(
    group: RelationGroup, ways: gpd.GeoDataFrame, nodes: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    resolved_geometries: list[Geometry] = []
    resolved_idx: list[int] = []
    unresolved: list[tuple[int, Geometry]] = []

    for idx, geometry in _consolidate_geometries(group, ways, nodes):
        match geometry:
            case Geometry():  # type: ignore[misc]
                resolved_geometries.append(geometry)
                resolved_idx.append(idx)
            case partial():
                unresolved.append((idx, geometry))

    relations = gpd.GeoDataFrame(
        {
            "idx": resolved_idx,
            "id": group.ids[resolved_idx],
            "geometry": resolved_geometries,
            "version": np.array(group.version)[resolved_idx],
            "changeset": np.array(group.changeset)[resolved_idx],
            "visible": np.array(group.visible)[resolved_idx],
        },
        crs="EPSG:4326",
    )

    relations = pd.concat(
        [
            relations,
            gpd.GeoDataFrame.from_dict(
                {
                    idx: {
                        "geometry": func(relations=relations.set_index("id")),
                        "version": group.version[idx],
                        "changeset": group.version[idx],
                        "visible": group.version[idx],
                        "id": group.ids[idx],
                    }
                    for idx, func in unresolved
                },
                orient="index",
                crs="EPSG:4326",
            ),
        ]
    )

    return relations.join(
        pd.DataFrame.from_dict(
            group.tags,
            orient="index",
            dtype=str(pd.SparseDtype(str)),
        )
    ).set_index("id")
