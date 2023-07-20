from pathlib import Path

import pytest

from osm2gpd.parse import OSMFile, filter_relations


@pytest.fixture
def andorra(shared_datadir: Path) -> Path:
    return shared_datadir.joinpath("andorra-latest.osm.pbf")


@pytest.fixture
def isle_of_man(shared_datadir: Path) -> Path:
    return shared_datadir.joinpath("isle-of-man-latest.osm.pbf")


@pytest.fixture
def malta(shared_datadir: Path) -> Path:
    return shared_datadir.joinpath("malta-latest.osm.pbf")


@pytest.mark.parametrize(
    "filename",
    ["isle_of_man", "malta"],
)
def test_osm_file_object_can_be_created_with_path(
    filename: str, request: pytest.FixtureRequest
) -> None:
    osm = OSMFile.from_file(request.getfixturevalue(filename))
    assert len(osm.nodes) > 0
    assert len(osm.relations) > 0
    assert len(osm.ways) > 0


@pytest.mark.parametrize("filename", ["andorra"])
def test_osm_file_object_can_be_created_with_string(
    filename: str, request: pytest.FixtureRequest
) -> None:
    osm = OSMFile.from_file(str(request.getfixturevalue(filename)))

    assert len(osm.nodes) > 0
    assert len(osm.relations) > 0
    assert len(osm.ways) > 0


@pytest.mark.parametrize(
    "filename,tags",
    [("isle_of_man", {"type"}), ("malta", {"boundary"})],
)
def test_osm_file_object_can_be_filtered_by_tags(
    filename: str, tags: set[str], request: pytest.FixtureRequest
) -> None:
    osm = OSMFile.from_file(request.getfixturevalue(filename))
    osm.filter(tags=tags)
    assert len(osm.nodes) > 0
    assert len(osm.relations) > 0
    assert len(osm.ways) > 0


@pytest.mark.parametrize(
    "filename,tags",
    [("isle_of_man", {"type"}), ("malta", {"boundary"})],
)
def test_filter_relations(
    filename: str, tags: set[str], request: pytest.FixtureRequest
) -> None:
    """Make sure that only relations are kept, that either have a tag or are
    referenced by another relation."""
    osm = OSMFile.from_file(request.getfixturevalue(filename))

    relations, references = filter_relations(osm.relations, tags)

    for relation in relations:
        ids = relation.group.keys()
        assert len(set(ids) - references["relation"]) == 0
