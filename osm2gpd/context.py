"""These classes are used to store the context information necessary to resolve
a PrimitiveGroup into a DataFrame."""
from dataclasses import dataclass

from .proto import DenseNodes, Node, PrimitiveBlock, Relation, Way


@dataclass
class GroupContext:
    """Context object for resolving a PrimitiveGroup."""

    string_table: list[str]


@dataclass
class DenseGroupContext(GroupContext):
    group: DenseNodes
    block: PrimitiveBlock


@dataclass
class NodeGroupContext(GroupContext):
    group: dict[int, Node]


@dataclass
class WayGroupContext(GroupContext):
    group: dict[int, Way]


@dataclass
class RelationGroupContext(GroupContext):
    group: dict[int, Relation]
