## 1. Extend Command Registry for Completion Support

- [x] 1.1 Add `get_completions(prefix: str) -> list[str]` method to `CommandRegistry` that returns matching command names and category prefixes
- [x] 1.2 Add `get_argument_completions(command_name: str, position: int, tokens: list[str]) -> list[str]` method to retrieve argument completions from handlers
- [x] 1.3 Write unit tests for `get_completions` covering empty prefix, partial prefix, and category sub-command scenarios
- [x] 1.4 Write unit tests for `get_argument_completions` covering handlers with and without the `get_completions` method

## 2. Add Completion Metadata to Existing Commands

- [x] 2.1 Add `get_completions(position: int, tokens: list[str]) -> list[str]` static method to `GitBranchCommand` returning known category prefixes for position 0
- [x] 2.2 Write unit tests verifying `GitBranchCommand.get_completions` returns expected values

## 3. Implement CompletionEngine

- [x] 3.1 Create `src/mdt/core/completion.py` with `CompletionEngine` class
- [x] 3.2 Implement `get_completions(input_text: str) -> list[str]` method that parses input and queries registry
- [x] 3.3 Handle command-level completion (empty input, partial command prefix)
- [x] 3.4 Handle sub-command completion (category prefix followed by space)
- [x] 3.5 Handle argument-level completion by delegating to registry's `get_argument_completions`
- [x] 3.6 Ensure case-insensitive matching and sorted output
- [x] 3.7 Write unit tests for `CompletionEngine` covering all scenarios from completion-engine spec

## 4. Create Completion Input Widget

- [x] 4.1 Create `src/mdt/ui/completion_input.py` with `CompletionInput` widget extending or wrapping Textual's `Input`
- [x] 4.2 Wire `CompletionEngine` into the widget to fetch suggestions on input change
- [x] 4.3 Implement Tab key handling: insert common prefix or cycle through candidates
- [x] 4.4 Implement Enter key handling: accept unambiguous completion before submission
- [x] 4.5 Implement Escape key handling: dismiss suggestions without changing input
- [x] 4.6 Display suggestions (inline hints or overlay) as the user types
- [x] 4.7 Write unit/integration tests for keybinding behavior and suggestion display

## 5. Integrate Completion Input into ShellScreen

- [x] 5.1 Replace plain `Input` widget with `CompletionInput` in `ShellScreen.compose()`
- [x] 5.2 Pass `CompletionEngine` (backed by the registry) to `CompletionInput`
- [x] 5.3 Verify existing shell behavior is preserved (command submission, activity log updates)
- [x] 5.4 Write integration test confirming Tab completion works in the shell context

## 6. Documentation and Cleanup

- [x] 6.1 Update README with completion feature description
- [x] 6.2 Add docstrings to new modules and classes
- [x] 6.3 Run full test suite and fix any regressions

