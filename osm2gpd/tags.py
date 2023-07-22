from itertools import accumulate
from typing import Generator, Sequence

from .context import (
    ContextType,
    DenseGroupContext,
    RelationGroupContext,
    WayGroupContext,
)
from .proto import Node, Relation, Way


def get_tags(obj: Relation | Way | Node, string_table: list[str]) -> dict[str, str]:
    if isinstance(obj, Node):
        breakpoint()
    return {string_table[k]: string_table[v] for k, v in zip(obj.keys, obj.vals)}


def parse_dense_tags(
    keys_vals: Sequence[int], string_table: list[str]
) -> Generator[tuple[int, dict[str, str]], None, None]:
    node_idx = 0
    kv_idx = 0

    while kv_idx < len(keys_vals):
        tags = dict()
        while keys_vals[kv_idx] != 0:
            k = keys_vals[kv_idx]
            v = keys_vals[kv_idx + 1]
            kv_idx += 2
            tags[string_table[k]] = string_table[v]

        if len(tags) > 0:
            yield node_idx, tags

        kv_idx += 1
        node_idx += 1


def get_elements_matching_tags(context: ContextType, tags: set[str]) -> set[int]:
    """Return a set of osm ids that matches the given tags."""
    match context:
        case DenseGroupContext():
            # resolve delta coding
            ids = list(accumulate(context.group.id))
            return {
                ids[idx]
                for idx, element_tags in parse_dense_tags(
                    context.group.keys_vals, context.string_table
                )
                if len(tags.intersection(element_tags.keys())) > 0
            }
        case WayGroupContext() | RelationGroupContext():
            return {
                element.id
                for element in context.group.values()
                if len(tags.intersection(get_tags(element, context.string_table))) > 0
            }
        case _:
            raise NotImplementedError()
