from dataclasses import dataclass


@dataclass(repr=False)
class BaseGroup:
    ids: list[int]
    tags: dict[int, dict[str, str]]
    version: list[int]
    visible: list[bool]
    changeset: list[int]
