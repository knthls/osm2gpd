## 0.2.0a1 (2023-08-18)

### Fix

- add condition to prevent operating on emty dataframe in consolidation

## 0.2.0a0 (2023-08-16)

### Feat

- create initial release
- create initial release
- implement relation consolidation
- parse ways
- implement filtering for tags
- implement unpacked intermediate datastructures for easier filtering
- implement way filtering#
- basic parser working

### Fix

- run code quality checks only once, but type checking for different versions
- configure publish on created release
- configure releases
- fix typo
- fix status badges
- fix status badges
- make type hints compatible with python 3.10
- allow consolidation of empty groups
- allow multipolygons referencing relations
- fix filtering bug, where not all references were respected
- fix typo in filter_groups

### Refactor

- move parsing logic to unpackes submodule
- simplify element type handling
