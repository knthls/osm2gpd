from typing import TypeAlias, TypeVar

import numpy as np
from numpy.typing import NDArray

from .unpacked import RelationGroup, WayGroup

ReferenceDict: TypeAlias = dict[str, NDArray[np.int64]]
GroupType = TypeVar("GroupType", RelationGroup, WayGroup)


def union(ids: list[NDArray[np.int64]]) -> NDArray[np.int64]:
    try:
        return np.unique(np.concatenate(ids))
    except ValueError:
        return np.array([], dtype=np.int64)


def _get_references_from_group(
    group: GroupType, ids: NDArray[np.int64]
) -> ReferenceDict:
    references = {}

    match group:
        case WayGroup():
            references["node"] = union(
                [group.member_ids[idx] for idx in np.where(np.isin(group.ids, ids))[0]]
            )
        case RelationGroup():
            references["node"] = union(
                [
                    group.member_ids[idx][group.member_types[idx] == "node"]
                    for idx in np.where(np.isin(group.ids, ids))[0]
                ]
            )

            references["way"] = union(
                [
                    group.member_ids[idx][group.member_types[idx] == "way"]
                    for idx in np.where(np.isin(group.ids, ids))[0]
                ]
            )

            references["relation"] = union(
                [
                    group.member_ids[idx][group.member_types[idx] == "relation"]
                    for idx in np.where(np.isin(group.ids, ids))[0]
                ]
            )
        case _:
            raise NotImplementedError()

    return references


def find_references(keep: NDArray[np.int64], groups: list[GroupType]) -> ReferenceDict:
    """Recursively find all relation/way/node ids, referenced by relation/way
    ids in the initial set `keep`."""
    references: dict[str, NDArray[np.int64]] = {}

    if len(groups) == 0 or len(keep) == 0:
        return references

    for group in groups:
        for k, v in _get_references_from_group(group, keep).items():
            references[k] = np.unique(
                np.concatenate([references.get(k, np.array([], dtype=np.int64)), v])
            )

    match groups[0]:
        case RelationGroup():
            # Recursively find all other references
            for k, v in find_references(
                np.setdiff1d(np.fromiter(references["relation"], dtype=np.int64), keep),
                groups,
            ).items():
                references[k] = np.unique(
                    np.concatenate([references.get(k, np.array([], dtype=np.int64)), v])
                )
            return references
        case WayGroup():
            return references
        case _:
            raise NotImplementedError()
