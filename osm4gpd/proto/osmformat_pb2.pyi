"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""
import sys

if sys.version_info >= (3, 10):
    import typing as typing_extensions
else:
    import typing_extensions
from builtins import (
    bool,
    bytes,
    int,
    str,
    type,
)
from collections.abc import (
    Iterable,
)
from google.protobuf.descriptor import (
    Descriptor,
    EnumDescriptor,
    FileDescriptor,
)
from google.protobuf.internal.containers import (
    RepeatedCompositeFieldContainer,
    RepeatedScalarFieldContainer,
)
from google.protobuf.internal.enum_type_wrapper import (
    _EnumTypeWrapper,
)
from google.protobuf.message import (
    Message,
)
from typing import (
    NewType,
)

DESCRIPTOR: FileDescriptor

@typing_extensions.final
class HeaderBlock(Message):
    """Contains the file header."""

    DESCRIPTOR: Descriptor

    BBOX_FIELD_NUMBER: int
    REQUIRED_FEATURES_FIELD_NUMBER: int
    OPTIONAL_FEATURES_FIELD_NUMBER: int
    WRITINGPROGRAM_FIELD_NUMBER: int
    SOURCE_FIELD_NUMBER: int
    OSMOSIS_REPLICATION_TIMESTAMP_FIELD_NUMBER: int
    OSMOSIS_REPLICATION_SEQUENCE_NUMBER_FIELD_NUMBER: int
    OSMOSIS_REPLICATION_BASE_URL_FIELD_NUMBER: int
    @property
    def bbox(self) -> HeaderBBox: ...
    @property
    def required_features(self) -> RepeatedScalarFieldContainer[str]:
        """Additional tags to aid in parsing this dataset"""
    @property
    def optional_features(self) -> RepeatedScalarFieldContainer[str]: ...
    writingprogram: str
    source: str
    """From the bbox field."""
    osmosis_replication_timestamp: int
    """Tags that allow continuing an Osmosis replication

    replication timestamp, expressed in seconds since the epoch,
    otherwise the same value as in the "timestamp=..." field
    in the state.txt file used by Osmosis
    """
    osmosis_replication_sequence_number: int
    """replication sequence number (sequenceNumber in state.txt)"""
    osmosis_replication_base_url: str
    """replication base URL (from Osmosis' configuration.txt file)"""
    def __init__(
        self,
        *,
        bbox: HeaderBBox | None = ...,
        required_features: Iterable[str] | None = ...,
        optional_features: Iterable[str] | None = ...,
        writingprogram: str | None = ...,
        source: str | None = ...,
        osmosis_replication_timestamp: int | None = ...,
        osmosis_replication_sequence_number: int | None = ...,
        osmosis_replication_base_url: str | None = ...,
    ) -> None: ...
    def HasField(
        self,
        field_name: typing_extensions.Literal[
            "bbox",
            b"bbox",
            "osmosis_replication_base_url",
            b"osmosis_replication_base_url",
            "osmosis_replication_sequence_number",
            b"osmosis_replication_sequence_number",
            "osmosis_replication_timestamp",
            b"osmosis_replication_timestamp",
            "source",
            b"source",
            "writingprogram",
            b"writingprogram",
        ],
    ) -> bool: ...
    def ClearField(
        self,
        field_name: typing_extensions.Literal[
            "bbox",
            b"bbox",
            "optional_features",
            b"optional_features",
            "osmosis_replication_base_url",
            b"osmosis_replication_base_url",
            "osmosis_replication_sequence_number",
            b"osmosis_replication_sequence_number",
            "osmosis_replication_timestamp",
            b"osmosis_replication_timestamp",
            "required_features",
            b"required_features",
            "source",
            b"source",
            "writingprogram",
            b"writingprogram",
        ],
    ) -> None: ...

@typing_extensions.final
class HeaderBBox(Message):
    """* The bounding box field in the OSM header. BBOX, as used in the OSM
    header. Units are always in nanodegrees -- they do not obey
    granularity rules.
    """

    DESCRIPTOR: Descriptor

    LEFT_FIELD_NUMBER: int
    RIGHT_FIELD_NUMBER: int
    TOP_FIELD_NUMBER: int
    BOTTOM_FIELD_NUMBER: int
    left: int
    right: int
    top: int
    bottom: int
    def __init__(
        self,
        *,
        left: int | None = ...,
        right: int | None = ...,
        top: int | None = ...,
        bottom: int | None = ...,
    ) -> None: ...
    def HasField(
        self,
        field_name: typing_extensions.Literal[
            "bottom", b"bottom", "left", b"left", "right", b"right", "top", b"top"
        ],
    ) -> bool: ...
    def ClearField(
        self,
        field_name: typing_extensions.Literal[
            "bottom", b"bottom", "left", b"left", "right", b"right", "top", b"top"
        ],
    ) -> None: ...

@typing_extensions.final
class PrimitiveBlock(Message):
    """/////////////////////////////////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////
    """

    DESCRIPTOR: Descriptor

    STRINGTABLE_FIELD_NUMBER: int
    PRIMITIVEGROUP_FIELD_NUMBER: int
    GRANULARITY_FIELD_NUMBER: int
    LAT_OFFSET_FIELD_NUMBER: int
    LON_OFFSET_FIELD_NUMBER: int
    DATE_GRANULARITY_FIELD_NUMBER: int
    @property
    def stringtable(self) -> StringTable: ...
    @property
    def primitivegroup(self) -> RepeatedCompositeFieldContainer[PrimitiveGroup]: ...
    granularity: int
    """Granularity, units of nanodegrees, used to store coordinates in this block"""
    lat_offset: int
    """Offset value between the output coordinates coordinates and the granularity grid in unites of nanodegrees."""
    lon_offset: int
    date_granularity: int
    """Granularity of dates, normally represented in units of milliseconds since the 1970 epoch."""
    def __init__(
        self,
        *,
        stringtable: StringTable | None = ...,
        primitivegroup: Iterable[PrimitiveGroup] | None = ...,
        granularity: int | None = ...,
        lat_offset: int | None = ...,
        lon_offset: int | None = ...,
        date_granularity: int | None = ...,
    ) -> None: ...
    def HasField(
        self,
        field_name: typing_extensions.Literal[
            "date_granularity",
            b"date_granularity",
            "granularity",
            b"granularity",
            "lat_offset",
            b"lat_offset",
            "lon_offset",
            b"lon_offset",
            "stringtable",
            b"stringtable",
        ],
    ) -> bool: ...
    def ClearField(
        self,
        field_name: typing_extensions.Literal[
            "date_granularity",
            b"date_granularity",
            "granularity",
            b"granularity",
            "lat_offset",
            b"lat_offset",
            "lon_offset",
            b"lon_offset",
            "primitivegroup",
            b"primitivegroup",
            "stringtable",
            b"stringtable",
        ],
    ) -> None: ...

@typing_extensions.final
class PrimitiveGroup(Message):
    """Group of OSMPrimitives. All primitives in a group must be the same type."""

    DESCRIPTOR: Descriptor

    NODES_FIELD_NUMBER: int
    DENSE_FIELD_NUMBER: int
    WAYS_FIELD_NUMBER: int
    RELATIONS_FIELD_NUMBER: int
    CHANGESETS_FIELD_NUMBER: int
    @property
    def nodes(self) -> RepeatedCompositeFieldContainer[Node]: ...
    @property
    def dense(self) -> DenseNodes: ...
    @property
    def ways(self) -> RepeatedCompositeFieldContainer[Way]: ...
    @property
    def relations(self) -> RepeatedCompositeFieldContainer[Relation]: ...
    @property
    def changesets(self) -> RepeatedCompositeFieldContainer[ChangeSet]: ...
    def __init__(
        self,
        *,
        nodes: Iterable[Node] | None = ...,
        dense: DenseNodes | None = ...,
        ways: Iterable[Way] | None = ...,
        relations: Iterable[Relation] | None = ...,
        changesets: Iterable[ChangeSet] | None = ...,
    ) -> None: ...
    def HasField(
        self, field_name: typing_extensions.Literal["dense", b"dense"]
    ) -> bool: ...
    def ClearField(
        self,
        field_name: typing_extensions.Literal[
            "changesets",
            b"changesets",
            "dense",
            b"dense",
            "nodes",
            b"nodes",
            "relations",
            b"relations",
            "ways",
            b"ways",
        ],
    ) -> None: ...

@typing_extensions.final
class StringTable(Message):
    """* String table, contains the common strings in each block.

    Note that we reserve index '0' as a delimiter, so the entry at that
    index in the table is ALWAYS blank and unused.
    """

    DESCRIPTOR: Descriptor

    S_FIELD_NUMBER: int
    @property
    def s(self) -> RepeatedScalarFieldContainer[bytes]: ...
    def __init__(
        self,
        *,
        s: Iterable[bytes] | None = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["s", b"s"]) -> None: ...

@typing_extensions.final
class Info(Message):
    """Optional metadata that may be included into each primitive."""

    DESCRIPTOR: Descriptor

    VERSION_FIELD_NUMBER: int
    TIMESTAMP_FIELD_NUMBER: int
    CHANGESET_FIELD_NUMBER: int
    UID_FIELD_NUMBER: int
    USER_SID_FIELD_NUMBER: int
    VISIBLE_FIELD_NUMBER: int
    version: int
    timestamp: int
    changeset: int
    uid: int
    user_sid: int
    """String IDs"""
    visible: bool
    """The visible flag is used to store history information. It indicates that
    the current object version has been created by a delete operation on the
    OSM API.
    When a writer sets this flag, it MUST add a required_features tag with
    value "HistoricalInformation" to the HeaderBlock.
    If this flag is not available for some object it MUST be assumed to be
    true if the file has the required_features tag "HistoricalInformation"
    set.
    """
    def __init__(
        self,
        *,
        version: int | None = ...,
        timestamp: int | None = ...,
        changeset: int | None = ...,
        uid: int | None = ...,
        user_sid: int | None = ...,
        visible: bool | None = ...,
    ) -> None: ...
    def HasField(
        self,
        field_name: typing_extensions.Literal[
            "changeset",
            b"changeset",
            "timestamp",
            b"timestamp",
            "uid",
            b"uid",
            "user_sid",
            b"user_sid",
            "version",
            b"version",
            "visible",
            b"visible",
        ],
    ) -> bool: ...
    def ClearField(
        self,
        field_name: typing_extensions.Literal[
            "changeset",
            b"changeset",
            "timestamp",
            b"timestamp",
            "uid",
            b"uid",
            "user_sid",
            b"user_sid",
            "version",
            b"version",
            "visible",
            b"visible",
        ],
    ) -> None: ...

@typing_extensions.final
class DenseInfo(Message):
    """* Optional metadata that may be included into each primitive. Special dense format used in DenseNodes."""

    DESCRIPTOR: Descriptor

    VERSION_FIELD_NUMBER: int
    TIMESTAMP_FIELD_NUMBER: int
    CHANGESET_FIELD_NUMBER: int
    UID_FIELD_NUMBER: int
    USER_SID_FIELD_NUMBER: int
    VISIBLE_FIELD_NUMBER: int
    @property
    def version(self) -> RepeatedScalarFieldContainer[int]: ...
    @property
    def timestamp(self) -> RepeatedScalarFieldContainer[int]:
        """DELTA coded"""
    @property
    def changeset(self) -> RepeatedScalarFieldContainer[int]:
        """DELTA coded"""
    @property
    def uid(self) -> RepeatedScalarFieldContainer[int]:
        """DELTA coded"""
    @property
    def user_sid(self) -> RepeatedScalarFieldContainer[int]:
        """String IDs for usernames. DELTA coded"""
    @property
    def visible(self) -> RepeatedScalarFieldContainer[bool]:
        """The visible flag is used to store history information. It indicates that
        the current object version has been created by a delete operation on the
        OSM API.
        When a writer sets this flag, it MUST add a required_features tag with
        value "HistoricalInformation" to the HeaderBlock.
        If this flag is not available for some object it MUST be assumed to be
        true if the file has the required_features tag "HistoricalInformation"
        set.
        """
    def __init__(
        self,
        *,
        version: Iterable[int] | None = ...,
        timestamp: Iterable[int] | None = ...,
        changeset: Iterable[int] | None = ...,
        uid: Iterable[int] | None = ...,
        user_sid: Iterable[int] | None = ...,
        visible: Iterable[bool] | None = ...,
    ) -> None: ...
    def ClearField(
        self,
        field_name: typing_extensions.Literal[
            "changeset",
            b"changeset",
            "timestamp",
            b"timestamp",
            "uid",
            b"uid",
            "user_sid",
            b"user_sid",
            "version",
            b"version",
            "visible",
            b"visible",
        ],
    ) -> None: ...

@typing_extensions.final
class ChangeSet(Message):
    """THIS IS STUB DESIGN FOR CHANGESETS. NOT USED RIGHT NOW.
    TODO:    REMOVE THIS?
    """

    DESCRIPTOR: Descriptor

    ID_FIELD_NUMBER: int
    id: int
    """
      // Parallel arrays.
      repeated uint32 keys = 2 [packed = true]; // String IDs.
      repeated uint32 vals = 3 [packed = true]; // String IDs.

      optional Info info = 4;
    """
    def __init__(
        self,
        *,
        id: int | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["id", b"id"]) -> bool: ...
    def ClearField(
        self, field_name: typing_extensions.Literal["id", b"id"]
    ) -> None: ...

@typing_extensions.final
class Node(Message):
    DESCRIPTOR: Descriptor

    ID_FIELD_NUMBER: int
    KEYS_FIELD_NUMBER: int
    VALS_FIELD_NUMBER: int
    INFO_FIELD_NUMBER: int
    LAT_FIELD_NUMBER: int
    LON_FIELD_NUMBER: int
    id: int
    @property
    def keys(self) -> RepeatedScalarFieldContainer[int]:
        """Parallel arrays.
        String IDs.
        """
    @property
    def vals(self) -> RepeatedScalarFieldContainer[int]:
        """String IDs."""
    @property
    def info(self) -> Info:
        """May be omitted in omitmeta"""
    lat: int
    lon: int
    def __init__(
        self,
        *,
        id: int | None = ...,
        keys: Iterable[int] | None = ...,
        vals: Iterable[int] | None = ...,
        info: Info | None = ...,
        lat: int | None = ...,
        lon: int | None = ...,
    ) -> None: ...
    def HasField(
        self,
        field_name: typing_extensions.Literal[
            "id", b"id", "info", b"info", "lat", b"lat", "lon", b"lon"
        ],
    ) -> bool: ...
    def ClearField(
        self,
        field_name: typing_extensions.Literal[
            "id",
            b"id",
            "info",
            b"info",
            "keys",
            b"keys",
            "lat",
            b"lat",
            "lon",
            b"lon",
            "vals",
            b"vals",
        ],
    ) -> None: ...

@typing_extensions.final
class DenseNodes(Message):
    """Used to densly represent a sequence of nodes that do not have any tags.

    We represent these nodes columnwise as five columns: ID's, lats, and
    lons, all delta coded. When metadata is not omitted,

    We encode keys & vals for all nodes as a single array of integers
    containing key-stringid and val-stringid, using a stringid of 0 as a
    delimiter between nodes.

    ( (<keyid> <valid>)* '0' )*
    """

    DESCRIPTOR: Descriptor

    ID_FIELD_NUMBER: int
    DENSEINFO_FIELD_NUMBER: int
    LAT_FIELD_NUMBER: int
    LON_FIELD_NUMBER: int
    KEYS_VALS_FIELD_NUMBER: int
    @property
    def id(self) -> RepeatedScalarFieldContainer[int]:
        """DELTA coded"""
    @property
    def denseinfo(self) -> DenseInfo:
        """repeated Info info = 4;"""
    @property
    def lat(self) -> RepeatedScalarFieldContainer[int]:
        """DELTA coded"""
    @property
    def lon(self) -> RepeatedScalarFieldContainer[int]:
        """DELTA coded"""
    @property
    def keys_vals(self) -> RepeatedScalarFieldContainer[int]:
        """Special packing of keys and vals into one array. May be empty if all nodes in this block are tagless."""
    def __init__(
        self,
        *,
        id: Iterable[int] | None = ...,
        denseinfo: DenseInfo | None = ...,
        lat: Iterable[int] | None = ...,
        lon: Iterable[int] | None = ...,
        keys_vals: Iterable[int] | None = ...,
    ) -> None: ...
    def HasField(
        self, field_name: typing_extensions.Literal["denseinfo", b"denseinfo"]
    ) -> bool: ...
    def ClearField(
        self,
        field_name: typing_extensions.Literal[
            "denseinfo",
            b"denseinfo",
            "id",
            b"id",
            "keys_vals",
            b"keys_vals",
            "lat",
            b"lat",
            "lon",
            b"lon",
        ],
    ) -> None: ...

@typing_extensions.final
class Way(Message):
    DESCRIPTOR: Descriptor

    ID_FIELD_NUMBER: int
    KEYS_FIELD_NUMBER: int
    VALS_FIELD_NUMBER: int
    INFO_FIELD_NUMBER: int
    REFS_FIELD_NUMBER: int
    id: int
    @property
    def keys(self) -> RepeatedScalarFieldContainer[int]:
        """Parallel arrays."""
    @property
    def vals(self) -> RepeatedScalarFieldContainer[int]: ...
    @property
    def info(self) -> Info: ...
    @property
    def refs(self) -> RepeatedScalarFieldContainer[int]:
        """DELTA coded"""
    def __init__(
        self,
        *,
        id: int | None = ...,
        keys: Iterable[int] | None = ...,
        vals: Iterable[int] | None = ...,
        info: Info | None = ...,
        refs: Iterable[int] | None = ...,
    ) -> None: ...
    def HasField(
        self, field_name: typing_extensions.Literal["id", b"id", "info", b"info"]
    ) -> bool: ...
    def ClearField(
        self,
        field_name: typing_extensions.Literal[
            "id",
            b"id",
            "info",
            b"info",
            "keys",
            b"keys",
            "refs",
            b"refs",
            "vals",
            b"vals",
        ],
    ) -> None: ...

@typing_extensions.final
class Relation(Message):
    DESCRIPTOR: Descriptor

    class _MemberType:
        ValueType = NewType("ValueType", int)
        V: typing_extensions.TypeAlias = ValueType

    class _MemberTypeEnumTypeWrapper(
        _EnumTypeWrapper[Relation._MemberType.ValueType], type
    ):  # noqa: F821
        DESCRIPTOR: EnumDescriptor
        NODE: Relation._MemberType.ValueType  # 0
        WAY: Relation._MemberType.ValueType  # 1
        RELATION: Relation._MemberType.ValueType  # 2

    class MemberType(_MemberType, metaclass=_MemberTypeEnumTypeWrapper): ...
    NODE: Relation.MemberType.ValueType  # 0
    WAY: Relation.MemberType.ValueType  # 1
    RELATION: Relation.MemberType.ValueType  # 2

    ID_FIELD_NUMBER: int
    KEYS_FIELD_NUMBER: int
    VALS_FIELD_NUMBER: int
    INFO_FIELD_NUMBER: int
    ROLES_SID_FIELD_NUMBER: int
    MEMIDS_FIELD_NUMBER: int
    TYPES_FIELD_NUMBER: int
    id: int
    @property
    def keys(self) -> RepeatedScalarFieldContainer[int]:
        """Parallel arrays."""
    @property
    def vals(self) -> RepeatedScalarFieldContainer[int]: ...
    @property
    def info(self) -> Info: ...
    @property
    def roles_sid(self) -> RepeatedScalarFieldContainer[int]:
        """Parallel arrays
        This should have been defined as uint32 for consistency, but it is now too late to change it
        """
    @property
    def memids(self) -> RepeatedScalarFieldContainer[int]:
        """DELTA encoded"""
    @property
    def types(self) -> RepeatedScalarFieldContainer[Relation.MemberType.ValueType]: ...
    def __init__(
        self,
        *,
        id: int | None = ...,
        keys: Iterable[int] | None = ...,
        vals: Iterable[int] | None = ...,
        info: Info | None = ...,
        roles_sid: Iterable[int] | None = ...,
        memids: Iterable[int] | None = ...,
        types: Iterable[Relation.MemberType.ValueType] | None = ...,
    ) -> None: ...
    def HasField(
        self, field_name: typing_extensions.Literal["id", b"id", "info", b"info"]
    ) -> bool: ...
    def ClearField(
        self,
        field_name: typing_extensions.Literal[
            "id",
            b"id",
            "info",
            b"info",
            "keys",
            b"keys",
            "memids",
            b"memids",
            "roles_sid",
            b"roles_sid",
            "types",
            b"types",
            "vals",
            b"vals",
        ],
    ) -> None: ...