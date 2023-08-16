import pytest

from osm4gpd.parse import OSMFile


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
