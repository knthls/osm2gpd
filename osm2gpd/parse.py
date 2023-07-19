from functools import partial
from pathlib import Path
from typing import TypeAlias

import geopandas as gpd
import pandas as pd
from shapely import Polygon, box

from . import relations, ways
from .blocks import read_blocks
from .nodes import read as read_nodes
from .proto import HeaderBlock

__all__ = ["parse"]

BBox: TypeAlias = tuple[float, float, float, float] | Polygon

#  header_bbox = box(
#      header_block.bbox.bottom * 1e-9,
#      header_block.bbox.left * 1e-9,
#      header_block.bbox.top * 1e-9,
#      header_block.bbox.right * 1e-9,
#  )
#
#  if bounding_box is not None and not intersects(header_bbox, bounding_box):


def parse(fp: Path | str, *, bounding_box: BBox | None = None) -> gpd.GeoDataFrame:
    if isinstance(fp, str):
        fp = Path(fp)

    if isinstance(bounding_box, tuple):
        bounding_box = box(*bounding_box)

    with open(fp, "rb") as f:
        file_iterator = read_blocks(f)

        # ... do something with header block here
        _: HeaderBlock = HeaderBlock.FromString(next(file_iterator))

        way_buffer: list[partial] = []
        relation_buffer: list[partial] = []

        # first parse all nodes from file
        nodes: gpd.GeoDataFrame = pd.concat(
            read_nodes(
                file_iterator, way_buffer=way_buffer, relation_buffer=relation_buffer
            )
        )

        # resolve partial calls to _parse_ways with all nodes now known
        way_tab = ways.resolve_buffer(nodes, way_buffer)
        relation_tab = relations.resolve_buffer(nodes, way_tab, relation_buffer)

    return pd.concat([nodes, way_tab, relation_tab])
