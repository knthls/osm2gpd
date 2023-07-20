import logging
from itertools import accumulate
from typing import Iterator, Sequence

import geopandas as gpd
import pandas as pd

from .proto import PrimitiveBlock, PrimitiveGroup

logger = logging.getLogger(__name__)


def _visible(values: Sequence[bool], length: int) -> Iterator[bool]:
    if len(values) == length:
        return iter(values)
    elif len(values) == 0:
        return (True for _ in range(length))
    else:
        raise ValueError("Invalid length of 'visible' values")


def parse_dense_tags(
    keys_vals: Sequence[int], string_table: list[str]
) -> dict[int, dict[str, str]]:
    node_idx = 0
    kv_idx = 0

    tags_unpacked: dict[int, dict[str, str]] = {}

    while kv_idx < len(keys_vals):
        tags = dict()
        while keys_vals[kv_idx] != 0:
            k = keys_vals[kv_idx]
            v = keys_vals[kv_idx + 1]
            kv_idx += 2
            tags[string_table[k]] = string_table[v]

        if len(tags) > 0:
            tags_unpacked[node_idx] = tags

        kv_idx += 1
        node_idx += 1

    return tags_unpacked


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
        parse_dense_tags(group.dense.keys_vals, string_table),
        orient="index",
        dtype=pd.SparseDtype(str),
    )

    return nodes.join(tags).set_index("id")
