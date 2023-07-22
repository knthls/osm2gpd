from functools import partial
from itertools import accumulate
from typing import Type

import geopandas as gpd
import pandas as pd
from shapely import LinearRing, LineString, Polygon

from .proto import PrimitiveGroup
from .tags import get_tags
from .unpacked import WayGroup

__all__ = ["resolve_buffer", "parse"]


def infer_way_type(
    refs: list[int], tags: dict[str, str]
) -> Type[LinearRing] | Type[Polygon] | Type[LineString]:
    """Rules are taken from here: https://wiki.openstreetmap.org/wiki/Way#Types_of_way"""
    # if way is closed
    if refs[-1] == refs[0]:
        # exceptions where a closed way is not intended to be an area
        if "highway" not in tags and "barrier" not in tags:
            return LinearRing  # type: ignore[no-any-return]
        else:
            return Polygon  # type: ignore[no-any-return]
    else:
        return LineString  # type: ignore[no-any-return]


def parse(
    group: PrimitiveGroup, string_table: list[str], nodes: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    ways = {}
    tags = {}

    for way in group.ways:
        refs = list(accumulate(way.refs))
        way_tags = {
            string_table[k]: string_table[v] for k, v in zip(way.keys, way.vals)
        }

        geom_type = infer_way_type(refs, way_tags)

        if way.info is not None:
            parsed = {
                "geometry": geom_type(nodes.loc[refs, "geometry"]),
                "version": way.info.version,
                "changeset": way.info.changeset,
                "visible": way.info.visible,
            }
        else:
            parsed = {
                "geometry": geom_type(nodes.loc[refs, "geometry"]),
            }

        ways[way.id] = parsed
        tags[way.id] = way_tags

    tags = pd.DataFrame.from_dict(
        tags,
        orient="index",
        dtype=pd.SparseDtype(str),
    )

    return gpd.GeoDataFrame.from_dict(ways, orient="index", crs="EPSG:4326").join(tags)


def resolve_buffer(
    nodes: gpd.GeoDataFrame, way_buffer: list[partial]
) -> gpd.GeoDataFrame:
    # resolve partial calls to _parse_ways with all nodes now known
    return pd.concat((ways(nodes=nodes) for ways in way_buffer))


def unpack_way_group(group: PrimitiveGroup, string_table: list[str]) -> WayGroup:
    ids: list[int] = []
    versions: list[int] = []
    member_ids: list[list[int]] = []
    tags: dict[int, dict[str, str]] = {}
    visible: list[bool] = []
    changeset: list[int] = []

    for i, way in enumerate(group.ways):
        member_ids.append(list(accumulate(way.refs)))
        _tags = get_tags(way, string_table)
        if len(_tags) > 0:
            tags[i] = _tags

        ids.append(way.id)
        # fixme: add optional here
        versions.append(way.info.version)
        visible.append(way.info.visible)
        changeset.append(way.info.changeset)

    return WayGroup(
        ids=ids,
        tags=tags,
        member_ids=member_ids,
        version=versions,
        changeset=changeset,
        visible=visible,
    )
