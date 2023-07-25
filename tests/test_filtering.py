from functools import reduce
from operator import or_

import numpy as np
import pytest
from numpy.typing import NDArray

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


def _get_resolvable_relation_refs(
    osm: OSMFile, relation_references: dict[str, NDArray[np.int64]]
) -> dict[str, NDArray[np.int64]]:
    resolvable_relation_refs = {}
    resolvable_relation_refs["way"] = relation_references["way"][
        reduce(
            or_,
            [
                np.isin(relation_references["way"], osm.ways[i].ids)
                for i in range(len(osm.ways))
            ],
        )
    ]
    resolvable_relation_refs["node"] = relation_references["node"][
        reduce(
            or_,
            [
                np.isin(relation_references["node"], osm.nodes[i].ids)
                for i in range(len(osm.nodes))
            ],
        )
    ]
    return resolvable_relation_refs


@pytest.mark.parametrize(
    "filename,tags",
    [("isle_of_man", {"name"})],
)
def test_filtering_respects_resolvability_when_filtering_ways(
    filename: str, tags: set[str], request: pytest.FixtureRequest
) -> None:
    osm = OSMFile.from_file(request.getfixturevalue(filename))
    osm.relations, relation_references = filter_groups(osm.relations, tags)

    resolvable_refs = _get_resolvable_relation_refs(osm, relation_references)

    osm.ways, way_references = filter_groups(
        osm.ways, tags, references=relation_references.copy()
    )

    resolvable_refs_ = _get_resolvable_relation_refs(osm, way_references)

    assert np.isin(resolvable_refs["way"], resolvable_refs_["way"]).all()
    assert np.isin(resolvable_refs["node"], resolvable_refs_["node"]).all()


@pytest.mark.parametrize(
    "filename,tags",
    [("isle_of_man", {"name"})],
)
def test_filtering_respects_resolvability_when_filtering_nodes(
    filename: str, tags: set[str], request: pytest.FixtureRequest
) -> None:
    osm = OSMFile.from_file(request.getfixturevalue(filename))
    osm.relations, relation_references = filter_groups(osm.relations, tags)

    resolvable_refs = _get_resolvable_relation_refs(osm, relation_references)

    osm.nodes, node_references = filter_groups(
        osm.nodes, tags, references=relation_references.copy()
    )

    resolvable_refs_ = _get_resolvable_relation_refs(osm, node_references)

    assert np.isin(resolvable_refs["way"], resolvable_refs_["way"]).all()
    assert np.isin(resolvable_refs["node"], resolvable_refs_["node"]).all()


@pytest.mark.parametrize(
    "filename,tags",
    [("isle_of_man", {"name"})],
)
def test_filtering_respects_references(
    filename: str, tags: set[str], request: pytest.FixtureRequest
) -> None:
    """Check that input reference dicts are always supersets of output
    reference dicts."""
    osm = OSMFile.from_file(request.getfixturevalue(filename))
    osm.relations, relation_references = filter_groups(osm.relations, tags)

    osm.ways, way_references = filter_groups(
        osm.ways, tags, references=relation_references.copy()
    )

    assert np.isin(
        relation_references["node"], way_references["node"]
    ).all(), "node references have disappeared during way filtering"
    assert np.isin(
        relation_references["way"], way_references["way"]
    ).all(), "way references have disappeared during way filtering"

    osm.nodes, node_references = filter_groups(
        osm.nodes, tags, references=way_references.copy()
    )

    assert np.isin(
        relation_references["node"], node_references["node"]
    ).all(), "node references have disappeared have disappeared during node filtering"
    assert np.isin(
        relation_references["way"], node_references["way"]
    ).all(), "way references have disappeared during node filtering"

    assert np.isin(
        way_references["node"], node_references["node"]
    ).all(), "node references have disappeared during node filtering"
