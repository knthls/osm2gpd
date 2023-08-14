import geopandas as gpd
import pandas as pd

from .unpacked import NodesGroup


def consolidate_nodes(group: NodesGroup) -> gpd.GeoDataFrame:
    nodes = gpd.GeoDataFrame(
        {
            "geometry": gpd.points_from_xy(group.lon, group.lat, crs="EPSG:4326"),
            "id": group.ids,
            "version": group.version,
            "visible": group.visible,
            "changeset": group.changeset,
        }
    )

    tags = pd.DataFrame.from_dict(
        group.tags,
        orient="index",
        dtype=str(pd.SparseDtype(str)),
    )

    return nodes.join(tags).set_index("id")
