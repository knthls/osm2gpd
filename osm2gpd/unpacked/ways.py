from dataclasses import dataclass
from itertools import accumulate
from typing import Self

from osm2gpd.proto import PrimitiveGroup
from osm2gpd.tags import get_tags

from .base import BaseGroup

__all__ = ["WayGroup"]


@dataclass(repr=False)
class WayGroup(BaseGroup):
    member_ids: list[list[int]]

    @classmethod
    def from_primitive_group(
        cls, group: PrimitiveGroup, string_table: list[str]
    ) -> Self:
        ids: list[int] = []
        versions: list[int] = []
        member_ids: list[list[int]] = []
        tags: dict[int, dict[str, str]] = {}
        visible: list[bool] = []
        changeset: list[int] = []

        for i, way in enumerate(group.ways):
            member_ids.append(list(accumulate(way.refs)))
            _tags = get_tags(way, string_table)
            if len(_tags) > 0:
                tags[i] = _tags

            ids.append(way.id)
            # fixme: add optional here
            versions.append(way.info.version)
            visible.append(way.info.visible)
            changeset.append(way.info.changeset)

        return cls(
            ids=ids,
            tags=tags,
            member_ids=member_ids,
            version=versions,
            changeset=changeset,
            visible=visible,
        )
