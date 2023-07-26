import pytest

from osm2gpd.parse import OSMFile


@pytest.mark.parametrize(
    "filename",
    ["isle_of_man", "malta"],
)
def test_osm_file_can_be_consolidated(
    filename: str, request: pytest.FixtureRequest
) -> None:
    _ = (
        OSMFile.from_file(request.getfixturevalue(filename))
        .filter(tags={"name"})
        .consolidate()
    )
