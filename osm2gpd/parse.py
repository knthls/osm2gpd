from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from functools import singledispatch
from itertools import accumulate
from pathlib import Path
from typing import Generator, Literal, Self, TypeAlias, TypeVar

from shapely import Polygon

from .blocks import read_blocks
from .context import (
    DenseGroupContext,
    GroupContext,
    NodeGroupContext,
    RelationGroupContext,
    WayGroupContext,
)
from .proto import HeaderBlock, PrimitiveBlock, Relation, Way
from .relations import get_tags

__all__ = ["OSMFile"]

BBox: TypeAlias = tuple[float, float, float, float] | Polygon
ReferenceDict: TypeAlias = defaultdict[str, set[int]]

ContextType = TypeVar("ContextType", RelationGroupContext, WayGroupContext)


def _init_group_context(block: PrimitiveBlock) -> Generator[GroupContext, None, None]:
    str_tab: list[str] = [x.decode("utf-8") for x in block.stringtable.s]

    for group in block.primitivegroup:
        # each group contains only one field at a time, where the fields can be
        # nodes, dense, ways, relations or changesets

        if len(group.nodes) > 0:
            yield NodeGroupContext(
                group={node.id: node for node in group.nodes}, string_table=str_tab
            )

        if len(group.dense.id) > 0:
            yield DenseGroupContext(
                block=block, group=group.dense, string_table=str_tab
            )

        if len(group.ways) > 0:
            yield WayGroupContext(
                group={way.id: way for way in group.ways}, string_table=str_tab
            )

        if len(group.relations) > 0:
            yield RelationGroupContext(
                group={relation.id: relation for relation in group.relations},
                string_table=str_tab,
            )


def _read_contexts(
    file_iterator: Generator[bytes, None, None],
) -> Generator[GroupContext, None, None]:
    """Parse all nodes from a file-iterator."""
    for block in file_iterator:
        for context in _init_group_context(PrimitiveBlock.FromString(block)):
            yield context


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
    references = defaultdict(set)
    for idx in ids:
        try:
            relation = context.group[idx]
        except KeyError:
            continue

        for k, v in get_references(relation).items():
            references[k].update(v)

    return references


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


def infer_element_type(
    element: RelationGroupContext | WayGroupContext,
) -> Literal["relation", "way"]:
    match element:
        case RelationGroupContext():
            return "relation"
        case WayGroupContext():
            return "way"
        case _:
            raise NotImplementedError()


def filter_elements(
    elements: list[ContextType], tags: set[str], references: ReferenceDict | None = None
) -> tuple[list[ContextType], ReferenceDict]:
    if references is None:
        references = defaultdict(set)

    keep: set[int] = set()

    try:
        element_type = infer_element_type(elements[0])
    except IndexError:
        return elements, references

    for element_context in elements:
        keep.update(
            {
                way.id
                for way in element_context.group.values()
                if len(tags.intersection(get_tags(way, element_context.string_table)))
                > 0
            }
        )

    match element_type:
        case "relation":
            for k, v in find_references(keep, elements, element_type).items():
                references[k].update(v)
        case "way":
            for k, v in find_references(keep, elements, element_type).items():
                references[k].update(v)
        case _:
            raise NotImplementedError()

    for element_context in elements:
        for key in set(element_context.group.keys()) - references[element_type]:
            element_context.group.pop(key, None)

    return elements, references


@dataclass
class OSMFile:
    nodes: list[DenseGroupContext] = field(default_factory=list)
    ways: list[WayGroupContext] = field(default_factory=list)
    relations: list[RelationGroupContext] = field(default_factory=list)

    @classmethod
    def from_file(cls, fp: Path | str) -> Self:
        if isinstance(fp, str):
            fp = Path(fp)

        nodes: list[DenseGroupContext] = []
        ways: list[WayGroupContext] = []
        relations: list[RelationGroupContext] = []

        with open(fp, "rb") as f:
            file_iterator = read_blocks(f)

            # fixme: do something with header block here
            _: HeaderBlock = HeaderBlock.FromString(next(file_iterator))

            for context in _read_contexts(file_iterator):
                match context:
                    case NodeGroupContext():
                        raise NotImplementedError()
                    case DenseGroupContext():
                        nodes.append(context)
                    case WayGroupContext():
                        ways.append(context)
                    case RelationGroupContext():
                        relations.append(context)

        return cls(nodes, ways, relations)

    def filter(self, *, tags: set[str]) -> None:
        self.relations, references = filter_elements(self.relations, tags)
        self.ways, references = filter_elements(self.ways, tags, references=references)
        # self.nodes, _ = filter_elements(self.nodes, tags, references=references)


#  header_bbox = box(
#      header_block.bbox.bottom * 1e-9,
#      header_block.bbox.left * 1e-9,
#      header_block.bbox.top * 1e-9,
#      header_block.bbox.right * 1e-9,
#  )
#
#  if bounding_box is not None and not intersects(header_bbox, bounding_box):
