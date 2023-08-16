from __future__ import annotations

from dataclasses import dataclass
from itertools import accumulate

import numpy as np
from numpy.typing import NDArray

from osm4gpd.proto import PrimitiveGroup
from osm4gpd.tags import get_tags

from .base import BaseGroup

__all__ = ["RelationGroup"]


@dataclass(repr=False)
class RelationGroup(BaseGroup):
    member_types: list[NDArray[np.object_]]
    member_roles: list[NDArray[np.object_]]
    member_ids: list[NDArray[np.int64]]

    @classmethod
    def from_primitive_group(
        cls, group: PrimitiveGroup, string_table: list[str]
    ) -> RelationGroup:
        ids: list[int] = []
        versions: list[int] = []
        member_ids: list[NDArray[np.int64]] = []
        member_types: list[NDArray[np.object_]] = []
        member_roles: list[NDArray[np.object_]] = []
        tags: dict[int, dict[str, str]] = {}
        visible: list[bool] = []
        changeset: list[int] = []

        for i, relation in enumerate(group.relations):
            ids.append(relation.id)

            member_types.append(
                np.fromiter(
                    (
                        relation.MemberType.keys()[type_].lower()
                        for type_ in relation.types
                    ),
                    dtype=np.object_,
                )
            )
            member_ids.append(np.fromiter(accumulate(relation.memids), dtype=np.int64))
            member_roles.append(
                np.fromiter(
                    (string_table[sid] for sid in relation.roles_sid), dtype=np.object_
                )
            )

            _tags = get_tags(relation, string_table)
            if len(_tags) > 0:
                tags[i] = _tags

            # fixme: add optional here
            versions.append(relation.info.version)
            visible.append(relation.info.visible)
            changeset.append(relation.info.changeset)

        return cls(
            ids=np.array(ids),
            tags=tags,
            version=versions,
            changeset=changeset,
            visible=visible,
            member_ids=member_ids,
            member_roles=member_roles,
            member_types=member_types,
        )
