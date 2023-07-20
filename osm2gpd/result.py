from dataclasses import dataclass

import geopandas as gpd

from .proto import PrimitiveGroup


@dataclass
class Result:
    result: gpd.GeoDataFrame
    deferred: list[PrimitiveGroup]
