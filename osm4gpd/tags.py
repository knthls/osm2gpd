from typing import Generator, Sequence

from .proto import Node, Relation, Way


def get_tags(obj: Relation | Way | Node, string_table: list[str]) -> dict[str, str]:
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
