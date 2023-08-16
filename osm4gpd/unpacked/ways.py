from __future__ import annotations

from dataclasses import dataclass
from itertools import accumulate

import numpy as np
from numpy.typing import NDArray

from osm4gpd.proto import PrimitiveGroup
from osm4gpd.tags import get_tags

from .base import BaseGroup

__all__ = ["WayGroup"]


@dataclass(repr=False)
class WayGroup(BaseGroup):
    member_ids: list[NDArray[np.int64]]

    @classmethod
    def from_primitive_group(
        cls, group: PrimitiveGroup, string_table: list[str]
    ) -> WayGroup:
        ids: list[int] = []
        versions: list[int] = []
        member_ids: list[NDArray[np.int64]] = []
        tags: dict[int, dict[str, str]] = {}
        visible: list[bool] = []
        changeset: list[int] = []

        for i, way in enumerate(group.ways):
            member_ids.append(np.fromiter(accumulate(way.refs), dtype=np.int64))
            _tags = get_tags(way, string_table)
            if len(_tags) > 0:
                tags[i] = _tags

            ids.append(way.id)
            # fixme: add optional here
            versions.append(way.info.version)
            visible.append(way.info.visible)
            changeset.append(way.info.changeset)

        return cls(
            ids=np.array(ids),
            tags=tags,
            member_ids=member_ids,
            version=versions,
            changeset=changeset,
            visible=visible,
        )
