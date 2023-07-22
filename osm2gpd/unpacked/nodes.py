from dataclasses import dataclass

from .base import BaseGroup

__all__ = ["NodesGroup"]


@dataclass(repr=False)
class NodesGroup(BaseGroup):
    lat: list[float]
    lon: list[float]
