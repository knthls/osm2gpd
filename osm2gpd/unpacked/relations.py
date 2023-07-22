from dataclasses import dataclass

from .base import BaseGroup

__all__ = ["RelationGroup"]


@dataclass(repr=False)
class RelationGroup(BaseGroup):
    member_types: list[list[str]]
    member_roles: list[list[str]]
    member_ids: list[list[int]]
