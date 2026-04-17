## 1. Command Registry – Category Support

- [x] 1.1 Add optional `category: str | None` parameter to `CommandRegistry.register()`
- [x] 1.2 Store category alongside handler in the internal registry dict
- [x] 1.3 Add `CommandRegistry.all()` method returning list of `(name, handler_class, category)` tuples
- [x] 1.4 Update unit tests for registry to cover category registration and `all()`

## 2. Command Dispatcher – Two-Word Routing

- [x] 2.1 Update `CommandDispatcher.dispatch()` to attempt `<verb>_<subverb>` key when single-token lookup fails and input has 2+ tokens
- [x] 2.2 Pass remaining tokens after `<verb> <subverb>` as args to the handler
- [x] 2.3 Update dispatcher unit tests to cover two-word routing and unknown two-word commands

## 3. Help Command – Category-Grouped Output

- [x] 3.1 Update `HelpCommand` to call `registry.all()` and group commands by category
- [x] 3.2 Render uncategorised commands under a "Built-in" heading
- [x] 3.3 Update help command unit tests to verify grouped output

## 4. Headless Branch Helpers

- [x] 4.1 Create `src/mdt/commands/openspec_branch.py` with `OpenspecBranchCommand` that detects the latest change folder and calls `git checkout -b`
- [x] 4.2 Create `src/mdt/commands/git_branch.py` with `GitBranchCommand` that normalises free-text into `<category>/<ticket>-<slug>` and calls `git checkout -b`
- [x] 4.3 Create `src/mdt/commands/copilot.py` as a placeholder category stub (no executable commands yet)
- [x] 4.4 Register all new commands and the copilot placeholder in `src/mdt/commands/__init__.py` with appropriate categories
- [x] 4.5 Write unit tests for `OpenspecBranchCommand` (mock filesystem + subprocess)
- [x] 4.6 Write unit tests for `GitBranchCommand` (branch name normalisation + subprocess mocking)

## 5. Shell Screen Layout

- [x] 5.1 Update `ShellScreen` in `src/mdt/ui/shell_screen.py` to use a four-zone vertical layout: ASCII art header → help summary → `RichLog` activity log → command input textbox
- [x] 5.2 Add the ASCII art header as a static `Label` or `Static` widget
- [x] 5.3 Add the help summary as a static `Label` or `Static` widget showing categories
- [x] 5.4 Replace or supplement the existing output area with a `RichLog` widget for the activity log
- [x] 5.5 Ensure the command input textbox retains focus on startup and after each submission
- [x] 5.6 Wire command submission to append both the input and the result to the activity log
- [x] 5.7 Update the shell screen smoke test in `tests/ui/test_shell_screen.py` to assert the new widgets are present

## 6. Verification

- [x] 6.1 Run the full test suite (`pytest`) and confirm all tests pass
- [x] 6.2 Manually launch `mdt` and verify the four-zone layout renders correctly
- [x] 6.3 Manually run `help` and confirm category-grouped output appears in the activity log
- [x] 6.4 Manually run `openspec branch` and confirm a git branch is created
- [x] 6.5 Manually run `git branch feature abc-123 new login page` and confirm branch `feature/abc-123-new-login-page` is created

