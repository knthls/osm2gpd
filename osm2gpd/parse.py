from pathlib import Path

import geopandas as gpd

__all__ = ["parse"]


def parse(filepath: Path | str) -> gpd.GeoDataFrame:  # type: ignore[no-any-unimported]
    raise NotImplementedError()
