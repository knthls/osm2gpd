from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from functools import singledispatch
from itertools import accumulate
from pathlib import Path
from typing import Generator, Literal, Self, TypeAlias

from shapely import Polygon

from .blocks import read_blocks
from .context import ContextType, NodeGroupContext
from .nodes import unpack_dense_group
from .proto import HeaderBlock, PrimitiveBlock, Relation, Way
from .relations import unpack_relation_group
from .unpacked import BaseGroup, NodesGroup, RelationGroup, WayGroup
from .ways import unpack_way_group

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
            yield unpack_dense_group(block, group, string_table)

        if len(group.ways) > 0:
            yield unpack_way_group(group, string_table)

        if len(group.relations) > 0:
            yield unpack_relation_group(group, string_table)


def _read_and_unpacked_groups(
    file_iterator: Generator[bytes, None, None],
) -> Generator[BaseGroup, None, None]:
    """Parse all nodes from a file-iterator."""
    for block in file_iterator:
        yield from _unpack_primitive_block(PrimitiveBlock.FromString(block))


@singledispatch
def get_references(element: Relation | Way) -> ReferenceDict:
    raise NotImplementedError()


@get_references.register(Relation)
def _(element: Relation) -> ReferenceDict:
    references = defaultdict(set)

    for id_, type_ in zip(accumulate(element.memids), element.types):
        references[element.MemberType.keys()[type_].lower()].add(id_)

    return references


@get_references.register(Way)
def _(element: Way) -> ReferenceDict:
    references = defaultdict(set)
    references["node"] = set(accumulate(element.refs))
    return references


def get_references_from_context(context: ContextType, ids: set[int]) -> ReferenceDict:
    raise NotImplementedError()
    #  references = defaultdict(set)
    #  for idx in ids:
    #      try:
    #          relation = context.group[idx]
    #      except KeyError:
    #          continue
    #
    #      for k, v in get_references(relation).items():
    #          references[k].update(v)
    #
    #  return references


def find_references(
    keep: set[int],
    elements: list[ContextType],
    element_type: Literal["way", "relation"],
) -> ReferenceDict:
    """Recursively find all relation ids, referenced by relation ids in the
    initial set `keep`."""
    references: defaultdict[str, set[int]] = defaultdict(set)
    for context in elements:
        for k, v in get_references_from_context(context, keep).items():
            references[k].update(v)

    if element_type == "way":
        return references
    elif element_type == "relation":
        # Recursively find all other references
        references["relation"] -= keep

        if len(references["relation"]) > 0:
            for k, v in find_references(
                keep.union(references["relation"]), elements, element_type
            ).items():
                references[k].update(v)

        references["relation"] = keep
        return references
    else:
        raise NotImplementedError()


@dataclass
class OSMFile:
    nodes: list[NodesGroup] = field(default_factory=list)
    ways: list[WayGroup] = field(default_factory=list)
    relations: list[RelationGroup] = field(default_factory=list)

    @classmethod
    def from_file(cls, fp: Path | str) -> Self:
        if isinstance(fp, str):
            fp = Path(fp)

        nodes: list[NodesGroup] = []
        ways: list[WayGroup] = []
        relations: list[RelationGroup] = []

        with open(fp, "rb") as f:
            file_iterator = read_blocks(f)

            # fixme: do something with header block here
            _: HeaderBlock = HeaderBlock.FromString(next(file_iterator))

            for group in _read_and_unpacked_groups(file_iterator):
                match group:
                    case NodeGroupContext():
                        raise NotImplementedError()
                    case NodesGroup():
                        nodes.append(group)
                    case WayGroup():
                        ways.append(group)
                    case RelationGroup():
                        relations.append(group)

        return cls(nodes, ways, relations)

    def filter(self, *, tags: set[str]) -> None:
        raise NotImplementedError()


#  header_bbox = box(
#      header_block.bbox.bottom * 1e-9,
#      header_block.bbox.left * 1e-9,
#      header_block.bbox.top * 1e-9,
#      header_block.bbox.right * 1e-9,
#  )
#
#  if bounding_box is not None and not intersects(header_bbox, bounding_box):
