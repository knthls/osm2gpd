from typing import Generator, Type

import geopandas as gpd
import numpy as np
import pandas as pd
from numpy.typing import NDArray
from shapely import Geometry, LinearRing, LineString, Polygon

from .unpacked import WayGroup


def infer_way_type(
    refs: NDArray[np.int64], tags: dict[str, str]
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


def _get_geometries(
    references: list[NDArray[np.int64]],
    tags: dict[int, dict[str, str]],
    nodes: gpd.GeoDataFrame,
) -> Generator[Geometry, None, None]:
    for i, refs in enumerate(references):
        geom_type = infer_way_type(refs, tags.get(i, {}))
        yield geom_type(nodes.loc[refs, "geometry"])


def consolidate_ways(group: WayGroup, nodes: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    tags = pd.DataFrame.from_dict(
        group.tags,
        orient="index",
        dtype=str(pd.SparseDtype(str)),
    )

    return (
        gpd.GeoDataFrame(
            {
                "geometry": _get_geometries(group.member_ids, group.tags, nodes),
                "version": group.version,
                "changeset": group.changeset,
                "visible": group.visible,
                "id": group.ids,
            },
            crs="EPSG:4326",
        )
        .join(tags)
        .set_index("id")
    )
