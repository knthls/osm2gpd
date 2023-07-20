from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from itertools import accumulate
from pathlib import Path
from typing import Generator, Self, TypeAlias

from shapely import Polygon

from .blocks import read_blocks
from .context import (
    DenseGroupContext,
    GroupContext,
    NodeGroupContext,
    RelationGroupContext,
    WayGroupContext,
)
from .proto import HeaderBlock, PrimitiveBlock, Relation
from .relations import get_tags as get_relation_tags

__all__ = ["OSMFile"]

BBox: TypeAlias = tuple[float, float, float, float] | Polygon
ReferenceDict: TypeAlias = defaultdict[str, set[int]]


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


def get_references_from_relation(relation: Relation) -> ReferenceDict:
    references = defaultdict(set)

    for id_, type_ in zip(accumulate(relation.memids), relation.types):
        references[relation.MemberType.keys()[type_].lower()].add(id_)

    return references


def get_references_from_context(
    context: RelationGroupContext, ids: set[int]
) -> ReferenceDict:
    references = defaultdict(set)
    for idx in ids:
        try:
            relation = context.group[idx]
        except KeyError:
            continue

        for k, v in get_references_from_relation(relation).items():
            references[k].update(v)

    return references


def find_relation_references(
    keep: set[int], relations: list[RelationGroupContext]
) -> ReferenceDict:
    """Recursively find all relation ids, referenced by relation ids in the
    initial set `keep`."""
    relation_references: defaultdict[str, set[int]] = defaultdict(set)
    for relation_context in relations:
        for k, v in get_references_from_context(relation_context, keep).items():
            relation_references[k].update(v)

    relation_references["relation"] -= keep

    if len(relation_references["relation"]) > 0:
        for k, v in find_relation_references(
            keep.union(relation_references["relation"]), relations
        ).items():
            relation_references[k].update(v)

    relation_references["relation"] = keep
    return relation_references


def filter_relations(
    relations: list[RelationGroupContext], tags: set[str]
) -> tuple[list[RelationGroupContext], ReferenceDict]:
    relation_references = defaultdict(set)
    keep = set()
    for relation_context in relations:
        _keep = {
            relation.id
            for relation in relation_context.group.values()
            if len(
                tags.intersection(
                    get_relation_tags(relation, relation_context.string_table)
                )
            )
            > 0
        }

        keep.update(_keep)

    for k, v in find_relation_references(keep, relations).items():
        relation_references[k].update(v)

    for relation_context in relations:
        for key in set(relation_context.group.keys()) - relation_references["relation"]:
            relation_context.group.pop(key, None)

    return relations, relation_references


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
        self.relations, references = filter_relations(self.relations, tags)
        del references["relation"]


#  header_bbox = box(
#      header_block.bbox.bottom * 1e-9,
#      header_block.bbox.left * 1e-9,
#      header_block.bbox.top * 1e-9,
#      header_block.bbox.right * 1e-9,
#  )
#
#  if bounding_box is not None and not intersects(header_bbox, bounding_box):
