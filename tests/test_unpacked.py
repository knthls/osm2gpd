from pathlib import Path
from typing import Generator

import pytest

from osm2gpd.blocks import read_blocks
from osm2gpd.proto import PrimitiveBlock, PrimitiveGroup
from osm2gpd.unpacked import NodesGroup, RelationGroup, WayGroup


def _iter_blocks(fp: Path) -> Generator[PrimitiveBlock, None, None]:
    with open(fp, "rb") as f:
        file_iterator = read_blocks(f)

        # skip header block
        next(file_iterator)

        for block in file_iterator:
            yield PrimitiveBlock.FromString(block)


@pytest.fixture
def dense_group_context(
    shared_datadir: Path,
) -> tuple[PrimitiveGroup, list[str], float, float, float]:
    for block in _iter_blocks(shared_datadir.joinpath("andorra-latest.osm.pbf")):
        for group in block.primitivegroup:
            if len(group.dense.id) > 0:
                str_tab: list[str] = [x.decode("utf-8") for x in block.stringtable.s]
                return (
                    group,
                    str_tab,
                    block.granularity,
                    block.lat_offset,
                    block.lon_offset,
                )

    raise Exception("Failed to find dense group in file")


@pytest.fixture
def way_group_context(
    shared_datadir: Path,
) -> tuple[PrimitiveGroup, list[str]]:
    for block in _iter_blocks(shared_datadir.joinpath("andorra-latest.osm.pbf")):
        for group in block.primitivegroup:
            if len(group.ways) > 0:
                str_tab: list[str] = [x.decode("utf-8") for x in block.stringtable.s]
                return group, str_tab

    raise Exception("Failed to find way group in file")


@pytest.fixture
def relation_group_context(
    shared_datadir: Path,
) -> tuple[PrimitiveGroup, list[str]]:
    for block in _iter_blocks(shared_datadir.joinpath("andorra-latest.osm.pbf")):
        for group in block.primitivegroup:
            if len(group.relations) > 0:
                str_tab: list[str] = [x.decode("utf-8") for x in block.stringtable.s]
                return group, str_tab

    raise Exception("Failed to find relation group in file")


def test_unpack_dense_group(
    dense_group_context: tuple[PrimitiveGroup, list[str], float, float, float]
) -> None:
    group, string_table, granularity, lat_offset, lon_offset = dense_group_context
    result = NodesGroup.from_dense_group(
        group,
        string_table,
        lon_offset=lon_offset,
        lat_offset=lat_offset,
        granularity=granularity,
    )

    n_items = len(result.ids)

    assert len(result.ids) > 0
    assert len(result.lon) == n_items
    assert len(result.lat) == n_items
    assert max(result.tags.keys()) < n_items
    assert len(result.version) == n_items
    assert len(result.changeset) == n_items
    assert len(result.visible) == n_items


def test_unpack_way_group(way_group_context: tuple[PrimitiveGroup, list[str]]) -> None:
    result = WayGroup.from_primitive_group(*way_group_context)

    n_items = len(result.ids)

    assert len(result.ids) > 0
    assert max(result.tags.keys()) < n_items
    assert len(result.version) == n_items
    assert len(result.changeset) == n_items
    assert len(result.visible) == n_items


def test_unpack_relations_group(
    relation_group_context: tuple[PrimitiveGroup, list[str]]
) -> None:
    result = RelationGroup.from_primitive_group(*relation_group_context)

    n_items = len(result.ids)

    assert len(result.ids) > 0
    assert max(result.tags.keys()) < n_items
    assert len(result.version) == n_items
    assert len(result.changeset) == n_items
    assert len(result.visible) == n_items
