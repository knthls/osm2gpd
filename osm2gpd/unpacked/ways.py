from dataclasses import dataclass

from .base import BaseGroup

__all__ = ["WayGroup"]


@dataclass(repr=False)
class WayGroup(BaseGroup):
    member_ids: list[list[int]]
