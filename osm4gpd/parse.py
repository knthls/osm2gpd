from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Generator, TypeAlias

import geopandas as gpd
import pandas as pd
from shapely import Polygon

from .blocks import read_blocks
from .filter import filter_groups
from .nodes import consolidate_nodes
from .proto import HeaderBlock, PrimitiveBlock
from .relations import consolidate_relations
from .unpacked import BaseGroup, NodesGroup, RelationGroup, WayGroup
from .ways import consolidate_ways

__all__ = ["OSMFile"]

BBox: TypeAlias = tuple[float, float, float, float] | Polygon
ReferenceDict: TypeAlias = defaultdict[str, set[int]]


def _unpack_primitive_block(
    block: PrimitiveBlock,
) -> Generator[BaseGroup, None, None]:
    string_table: list[str] = [x.decode("utf-8") for x in block.stringtable.s]

    for group in block.primitivegroup:
        # each group contains only one field at a time, where the fields can be
        # nodes, dense, ways, relations or changesets

        if len(group.nodes) > 0:
            raise NotImplementedError()

        if len(group.dense.id) > 0:
            yield NodesGroup.from_dense_group(
                group,
                string_table,
                granularity=block.granularity,
                lat_offset=block.lat_offset,
                lon_offset=block.lon_offset,
            )

        if len(group.ways) > 0:
            yield WayGroup.from_primitive_group(group, string_table)

        if len(group.relations) > 0:
            yield RelationGroup.from_primitive_group(group, string_table)


def _read_and_unpack_groups(
    file_iterator: Generator[bytes, None, None],
) -> Generator[BaseGroup, None, None]:
    """Parse all nodes from a file-iterator."""
    for block in file_iterator:
        yield from _unpack_primitive_block(PrimitiveBlock.FromString(block))


@dataclass
class OSMFile:
    nodes: list[NodesGroup] = field(default_factory=list)
    ways: list[WayGroup] = field(default_factory=list)
    relations: list[RelationGroup] = field(default_factory=list)

    # protected property that is used to store the arguments to filter
    # for later use during consolidation, since pre-consolidation filtering
    # can leave non-matching geometries that are referenced by some way or relation
    _filter: set[str] | None = None

    @classmethod
    def from_file(cls, fp: Path | str) -> OSMFile:
        if isinstance(fp, str):
            fp = Path(fp)

        nodes: list[NodesGroup] = []
        ways: list[WayGroup] = []
        relations: list[RelationGroup] = []

        with open(fp, "rb") as f:
            file_iterator = read_blocks(f)

            # fixme: do something with header block here
            _: HeaderBlock = HeaderBlock.FromString(next(file_iterator))

            for group in _read_and_unpack_groups(file_iterator):
                match group:
                    case NodesGroup():
                        nodes.append(group)
                    case WayGroup():
                        ways.append(group)
                    case RelationGroup():
                        relations.append(group)

        return cls(nodes, ways, relations)

    def filter(self, *, tags: set[str]) -> OSMFile:
        self.relations, references = filter_groups(self.relations, tags=tags)
        self.ways, references = filter_groups(
            self.ways, tags=tags, references=references
        )
        self.nodes, _ = filter_groups(self.nodes, tags=tags, references=references)

        self._filter = tags
        return self

    def _consolidate_nodes(self) -> gpd.GeoDataFrame:
        _node_parts = [
            consolidate_nodes(nodes) for nodes in self.nodes if not nodes.is_empty()
        ]
        if len(_node_parts) > 0:
            return pd.concat(_node_parts)
        else:
            raise ValueError("Nothing to consolidate.")

    def _consolidate_ways(self, *, nodes: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        _way_parts = [
            consolidate_ways(ways, nodes=nodes)
            for ways in self.ways
            if not ways.is_empty()
        ]

        if len(_way_parts) > 0:
            return pd.concat(_way_parts)
        else:
            return gpd.GeoDataFrame()

    def _consolidate_relations(
        self, *, nodes: gpd.GeoDataFrame, ways: gpd.GeoDataFrame
    ) -> gpd.GeoDataFrame:
        _relation_parts = [
            consolidate_relations(relations, ways=ways, nodes=nodes)
            for relations in self.relations
            if not relations.is_empty()
        ]

        if len(_relation_parts) > 0:
            return pd.concat(_relation_parts)
        else:
            return gpd.GeoDataFrame()

    def consolidate(self) -> gpd.GeoDataFrame:
        nodes = self._consolidate_nodes()
        ways = self._consolidate_ways(nodes=nodes)
        relations = self._consolidate_relations(nodes=nodes, ways=ways)

        gdf = pd.concat([nodes, ways, relations])

        if self._filter is not None:
            # filter for rows that match a filter category
            gdf = gdf[gdf[list(self._filter)].notna().any(axis=1)]

            # drop columns that became all NA from filtering
            gdf = gdf[gdf.columns[~gdf.isna().all()]]

        return gdf


#  header_bbox = box(
#      header_block.bbox.bottom * 1e-9,
#      header_block.bbox.left * 1e-9,
#      header_block.bbox.top * 1e-9,
#      header_block.bbox.right * 1e-9,
#  )
#
#  if bounding_box is not None and not intersects(header_bbox, bounding_box):
