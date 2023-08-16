from typing import TypeAlias, TypeVar

import numpy as np
from numpy.typing import NDArray

from .references import find_references
from .unpacked import BaseGroup, NodesGroup, RelationGroup, WayGroup

ReferenceDict: TypeAlias = dict[str, NDArray[np.int64]]
GroupType = TypeVar("GroupType", bound=BaseGroup)


def get_elements_matching_tags(group: BaseGroup, tags: set[str]) -> NDArray[np.int64]:
    """Return a set of osm ids that matches the given tags."""
    return np.unique(
        np.fromiter(
            (
                group.ids[idx]
                for idx, element_tags in group.tags.items()
                if len(tags.intersection(element_tags.keys())) > 0
            ),
            dtype=np.int64,
        )
    )


def filter_groups(
    groups: list[GroupType], tags: set[str], references: ReferenceDict | None = None
) -> tuple[list[GroupType], ReferenceDict]:
    if references is None:
        references = {}

    if len(groups) == 0:
        return groups, references

    matching_ids: NDArray[np.int64] = np.concatenate(
        list(get_elements_matching_tags(group, tags) for group in groups)
    )

    match groups[0]:
        case RelationGroup():
            for k, v in find_references(
                np.concatenate([matching_ids, references.get("relation", np.array([], dtype=np.int64))]), groups  # type: ignore[type-var]
            ).items():
                references[k] = np.unique(
                    np.concatenate([references.get(k, np.array([], dtype=np.int64)), v])
                )
        case WayGroup():
            for k, v in find_references(
                np.concatenate([matching_ids, references.get("way", np.array([], dtype=np.int64))]), groups  # type: ignore[type-var]
            ).items():
                references[k] = np.unique(
                    np.concatenate([references.get(k, np.array([], dtype=np.int64)), v])
                )
        case _:
            pass

    for group in groups:
        match group:
            case RelationGroup():
                keep = np.where(
                    np.isin(group.ids, matching_ids)
                    | np.isin(group.ids, references.get("relation", []))
                )[0]

                group.ids = group.ids[keep]
                group.version = [group.version[idx] for idx in keep]
                group.member_ids = [group.member_ids[idx] for idx in keep]
                group.member_types = [group.member_types[idx] for idx in keep]
                group.member_roles = [group.member_roles[idx] for idx in keep]
                group.tags = {i: group.tags.get(idx, {}) for i, idx in enumerate(keep)}
                group.visible = [group.visible[idx] for idx in keep]
                group.changeset = [group.changeset[idx] for idx in keep]
            case WayGroup():
                keep = np.where(
                    np.isin(group.ids, matching_ids)
                    | np.isin(group.ids, references.get("way", []))
                )[0]

                group.ids = group.ids[keep]
                group.version = [group.version[idx] for idx in keep]
                group.member_ids = [group.member_ids[idx] for idx in keep]
                group.tags = {i: group.tags.get(idx, {}) for i, idx in enumerate(keep)}
                group.visible = [group.visible[idx] for idx in keep]
                group.changeset = [group.changeset[idx] for idx in keep]
            case NodesGroup():
                keep = np.where(
                    np.isin(group.ids, matching_ids)
                    | np.isin(group.ids, references.get("node", []))
                )[0]
                group.ids = group.ids[keep]
                group.version = [group.version[idx] for idx in keep]
                group.tags = {i: group.tags.get(idx, {}) for i, idx in enumerate(keep)}
                group.visible = [group.visible[idx] for idx in keep]
                group.changeset = [group.changeset[idx] for idx in keep]
                group.lat = group.lat[keep]
                group.lon = group.lon[keep]

    return groups, references
