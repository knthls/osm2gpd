from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

__all__ = ["BaseGroup"]


@dataclass(repr=False)
class BaseGroup:
    ids: NDArray[np.int64]
    tags: dict[int, dict[str, str]]
    version: list[int]
    visible: list[bool]
    changeset: list[int]
