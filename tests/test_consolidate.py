import pytest

from osm2gpd.parse import OSMFile


@pytest.mark.parametrize(
    "filename,expected_shape",
    [("isle_of_man", (102488, 1109)), ("malta", (142325, 959))],
)
def test_osm_file_can_be_consolidated(
    filename: str, expected_shape: tuple[int, int], request: pytest.FixtureRequest
) -> None:
    gdf = (
        OSMFile.from_file(request.getfixturevalue(filename))
        .filter(tags={"name"})
        .consolidate()
    )

    assert gdf.shape == expected_shape
