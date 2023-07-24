import numpy as np
import pytest

from osm2gpd import OSMFile
from osm2gpd.filter import filter_groups


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

    groups, references = filter_groups(osm.relations, tags)

    # test that relations that are kept and that don't appear in the references
    # have matching tags
    for group in groups:
        diff = np.setdiff1d(group.ids, references["relation"])
        for idx in np.where(np.isin(group.ids, diff))[0]:
            assert len(tags.intersection(group.tags[idx].keys())) > 0


@pytest.mark.parametrize(
    "filename,tags",
    [("isle_of_man", {"leisure"}), ("malta", {"amenity"})],
)
def test_filter_ways(
    filename: str, tags: set[str], request: pytest.FixtureRequest
) -> None:
    """Make sure that only ways are kept, that either have a tag or are
    referenced by another relation."""
    osm = OSMFile.from_file(request.getfixturevalue(filename))

    groups, _ = filter_groups(osm.ways, tags)

    # test that ways that are kept and that don't appear in the references
    # have matching tags
    for group in groups:
        for idx in range(len(group.ids)):
            assert len(tags.intersection(group.tags[idx].keys())) > 0


@pytest.mark.parametrize(
    "filename,tags",
    [("isle_of_man", {"leisure"}), ("malta", {"amenity"})],
)
def test_filter_nodes(
    filename: str, tags: set[str], request: pytest.FixtureRequest
) -> None:
    """Make sure that only relations are kept, that either have a tag or are
    referenced by another relation."""
    osm = OSMFile.from_file(request.getfixturevalue(filename))

    groups, _ = filter_groups(osm.nodes, tags)

    # test that ways that are kept and that don't appear in the references
    # have matching tags
    for group in groups:
        for idx in range(len(group.ids)):
            assert len(tags.intersection(group.tags[idx].keys())) > 0
