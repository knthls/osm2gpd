import numpy as np
import pytest

from osm4gpd import OSMFile
from osm4gpd.references import find_references


@pytest.mark.parametrize(
    "filename",
    ["isle_of_man", "malta"],
)
def test_get_way_references(filename: str, request: pytest.FixtureRequest) -> None:
    osm = OSMFile.from_file(request.getfixturevalue(filename))

    references = find_references(
        np.concatenate([ways.ids for ways in osm.ways]), osm.ways
    )

    members = np.unique(
        np.concatenate([np.concatenate(ways.member_ids) for ways in osm.ways])
    )
    assert np.isin(members, references["node"]).all()


@pytest.mark.parametrize(
    "filename",
    ["isle_of_man", "malta"],
)
def test_get_relation_references(filename: str, request: pytest.FixtureRequest) -> None:
    osm = OSMFile.from_file(request.getfixturevalue(filename))

    references = find_references(
        np.concatenate([relations.ids for relations in osm.relations]), osm.relations
    )

    node_ids = []
    way_ids = []
    relation_ids = []

    for relations in osm.relations:
        node_ids.append(
            np.unique(
                np.concatenate(
                    [
                        member_ids[member_types == "node"]
                        for member_ids, member_types in zip(
                            relations.member_ids, relations.member_types
                        )
                    ]
                )
            )
        )

        way_ids.append(
            np.unique(
                np.concatenate(
                    [
                        member_ids[member_types == "way"]
                        for member_ids, member_types in zip(
                            relations.member_ids, relations.member_types
                        )
                    ]
                )
            )
        )

        relation_ids.append(
            np.unique(
                np.concatenate(
                    [
                        member_ids[member_types == "relation"]
                        for member_ids, member_types in zip(
                            relations.member_ids, relations.member_types
                        )
                    ]
                )
            )
        )

    assert np.isin(np.concatenate(node_ids), references["node"]).all()
    assert np.isin(np.concatenate(way_ids), references["way"]).all()
    assert np.isin(np.concatenate(relation_ids), references["relation"]).all()
