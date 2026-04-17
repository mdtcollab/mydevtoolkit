## 1. Core Implementation

- [x] 1.1 Create `src/mdt/commands/openspec_finish.py` with `run_openspec_finish` function and `OpenspecFinishCommand` class
- [x] 1.2 Implement `_get_current_branch` helper to get the current git branch name
- [x] 1.3 Implement `_extract_change_name` helper to parse the change name from a branch name by stripping known prefixes
- [x] 1.4 Implement `_is_working_tree_clean` helper to check for uncommitted changes
- [x] 1.5 Implement `_change_folder_exists` helper to check if `openspec/changes/<change-name>/` exists
- [x] 1.6 Implement the main `run_openspec_finish` workflow: validate branch → check change folder → check clean tree → checkout target → pull → merge → report result
- [x] 1.7 Handle merge conflicts by running `git merge --abort` and returning a clear error

## 2. Registration

- [x] 2.1 Register `OpenspecFinishCommand` under the `openspec` category in `src/mdt/commands/__init__.py`

## 3. Spec

- [x] 3.1 Create `openspec/specs/openspec-finish-helper/spec.md` from the change spec

## 4. Tests

- [x] 4.1 Create `tests/core/test_openspec_finish_command.py` with tests covering: branch parsing, change folder detection, dirty working tree, successful merge, merge conflict, target branch missing, pull failure

