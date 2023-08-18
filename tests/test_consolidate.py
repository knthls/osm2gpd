import pytest

from osm4gpd.parse import OSMFile


@pytest.mark.parametrize(
    "filename,tags,expected_shape",
    [
        ("extract", {"amenity"}, (314, 155)),
        ("isle_of_man", {"name"}, (10827, 1062)),
        ("malta", {"amenity"}, (5396, 342)),
        ("malta", {"car_wash"}, (1, 8)),
    ],
)
def test_osm_file_can_be_consolidated_after_filtering(
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


@pytest.mark.parametrize(
    "filename,expected_shape",
    [
        ("extract", (1184, 157)),
    ],
)
def test_osm_file_can_be_consolidated_without_filtering(
    filename: str,
    expected_shape: tuple[int, int],
    request: pytest.FixtureRequest,
) -> None:
    gdf = OSMFile.from_file(request.getfixturevalue(filename)).consolidate()

    assert gdf.shape == expected_shape


@pytest.mark.parametrize(
    "filename,tags",
    [
        ("extract", {"amenity"}),
        ("malta", {"car_wash"}),
    ],
)
def test_consolidation_respects_filtering(
    filename: str,
    tags: set[str],
    request: pytest.FixtureRequest,
) -> None:
    gdf = (
        OSMFile.from_file(request.getfixturevalue(filename))
        .filter(tags=tags)
        .consolidate()
    )

    assert gdf[list(tags)].isna().sum().sum() == 0
