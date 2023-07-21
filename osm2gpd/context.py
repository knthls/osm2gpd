"""These classes are used to store the context information necessary to resolve
a PrimitiveGroup into a DataFrame."""
from dataclasses import dataclass
from typing import ClassVar

from .proto import DenseNodes, Node, PrimitiveBlock, Relation, Way


@dataclass
class GroupContext:
    """Context object for resolving a PrimitiveGroup."""

    string_table: list[str]
    element_type: ClassVar[str]


@dataclass
class DenseGroupContext(GroupContext):
    element_type: ClassVar[str] = "node"
    group: DenseNodes
    block: PrimitiveBlock


@dataclass
class NodeGroupContext(GroupContext):
    element_type: ClassVar[str] = "node"
    group: dict[int, Node]


@dataclass
class WayGroupContext(GroupContext):
    element_type: ClassVar[str] = "way"
    group: dict[int, Way]


@dataclass
class RelationGroupContext(GroupContext):
    element_type: ClassVar[str] = "relation"
    group: dict[int, Relation]
