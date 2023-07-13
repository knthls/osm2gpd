import geopandas as gpd
from pathlib import Path

__all__ = ["parse"]


def parse(filepath: Path | str) -> gpd.GeoDataFrame:
    raise NotImplementedError()
