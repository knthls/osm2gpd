import pytest

from osm4gpd.parse import OSMFile


@pytest.mark.parametrize(
    "filename,tags,expected_shape",
    [
        ("isle_of_man", {"name"}, (102488, 1109)),
        ("malta", {"amenity"}, (19247, 354)),
        ("malta", {"car_wash"}, (10, 8)),
    ],
)
def test_osm_file_can_be_consolidated(
    filename: str,
    tags: set[str],
    expected_shape: tuple[int, int],
    request: pytest.FixtureRequest,
) -> None:
    gdf = (
        OSMFile.from_file(request.getfixturevalue(filename))
        .filter(tags=tags)
        .consolidate()
    )

    assert gdf.shape == expected_shape
