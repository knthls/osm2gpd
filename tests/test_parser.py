from pathlib import Path
import pytest
from osm2gpd import parse


@pytest.fixture
def andorra(shared_datadir: Path) -> Path:
    return shared_datadir.joinpath("andorra-latest.osm.pbf")


@pytest.fixture
def isle_of_man(shared_datadir: Path) -> Path:
    return shared_datadir.joinpath("isle-of-man-latest.osm.pbf")


@pytest.fixture
def malta(shared_datadir: Path) -> Path:
    return shared_datadir.joinpath("malta-latest.osm.pbf")


@pytest.mark.parametrize("filename", ["andorra", "isle_of_man", "malta"])
def test_parse(filename: str, request: pytest.FixtureRequest):
    parse(request.getfixturevalue(filename))

