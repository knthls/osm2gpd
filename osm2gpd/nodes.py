from itertools import accumulate
from typing import Iterator, Sequence

import geopandas as gpd
import pandas as pd

from .proto import PrimitiveBlock, PrimitiveGroup
from .tags import parse_dense_tags
from .unpacked import NodesGroup


def _visible(values: Sequence[bool], length: int) -> Iterator[bool]:
    if len(values) == length:
        return iter(values)
    elif len(values) == 0:
        return (True for _ in range(length))
    else:
        raise ValueError("Invalid length of 'visible' values")


def _parse_node_group(
    group: PrimitiveGroup, string_table: list[str]
) -> gpd.GeoDataFrame:
    raise NotImplementedError()


def _parse_dense_group(
    block: PrimitiveBlock, group: PrimitiveGroup, string_table: list[str]
) -> gpd.GeoDataFrame:
    lat = [
        (x * block.granularity + block.lat_offset) * 1e-9
        for x in accumulate(group.dense.lat)
    ]
    lon = [
        (x * block.granularity + block.lon_offset) * 1e-9
        for x in accumulate(group.dense.lon)
    ]

    nodes = gpd.GeoDataFrame(
        {
            "geometry": gpd.points_from_xy(lon, lat, crs="EPSG:4326"),
            "id": accumulate(group.dense.id),
            "version": iter(group.dense.denseinfo.version),
            "visible": _visible(group.dense.denseinfo.visible, len(group.dense.id)),
            "changeset": accumulate(group.dense.denseinfo.changeset),
        }
    )

    tags = pd.DataFrame.from_dict(
        dict(parse_dense_tags(group.dense.keys_vals, string_table)),
        orient="index",
        dtype=pd.SparseDtype(str),
    )

    return nodes.join(tags).set_index("id")


def unpack_dense_group(
    block: PrimitiveBlock, group: PrimitiveGroup, string_table: list[str]
) -> NodesGroup:
    return NodesGroup(
        ids=list(accumulate(group.dense.id)),
        lat=[
            (x * block.granularity + block.lat_offset) * 1e-9
            for x in accumulate(group.dense.lat)
        ],
        lon=[
            (x * block.granularity + block.lon_offset) * 1e-9
            for x in accumulate(group.dense.lon)
        ],
        tags=dict(parse_dense_tags(group.dense.keys_vals, string_table)),
        version=list(group.dense.denseinfo.version),
        visible=list(_visible(group.dense.denseinfo.visible, len(group.dense.id))),
        changeset=list(accumulate(group.dense.denseinfo.changeset)),
    )
