## 1. Project Scaffold

- [x] 1.1 Create `pyproject.toml` with project metadata, `textual>=0.60` runtime dependency, `pytest` + `pytest-asyncio` dev dependencies, and `[project.scripts] mdt = "mdt.__main__:main"`
- [x] 1.2 Create `src/mdt/__init__.py` (empty package marker)
- [x] 1.3 Create `src/mdt/__main__.py` with a `main()` function that instantiates `MdtApp` and calls `.run()`
- [x] 1.4 Create `src/mdt/core/__init__.py` (empty package marker)
- [x] 1.5 Create `src/mdt/commands/__init__.py` (empty for now; will import built-in commands in a later task)
- [x] 1.6 Create `src/mdt/ui/__init__.py` (empty package marker)
- [x] 1.7 Create `tests/__init__.py`, `tests/core/__init__.py`, `tests/ui/__init__.py`

## 2. Headless Core — Data Models

- [x] 2.1 Create `src/mdt/core/result.py` with `CommandResult` dataclass: `success: bool`, `output: str = ""`, `error: str | None = None`, `data: dict = field(default_factory=dict)`, `exit_requested: bool = False`
- [x] 2.2 Create `src/mdt/core/context.py` with `ProjectContext` dataclass: `cwd: Path`, `repo_root: Path | None`, `project_name: str | None`; add a `detect() -> ProjectContext` factory that walks up from `Path.cwd()` looking for `.git`

## 3. Headless Core — Registry and Dispatcher

- [x] 3.1 Create `src/mdt/core/registry.py` with `CommandRegistry` class: `register(name: str, handler: type) -> None` (raises `ValueError` on duplicate), `resolve(name: str) -> type | None`, `names() -> frozenset[str]`
- [x] 3.2 Create `src/mdt/core/dispatcher.py` with `CommandDispatcher(registry: CommandRegistry, context: ProjectContext)`; implement `dispatch(raw: str) -> CommandResult`: strip input, return no-op on blank, resolve command, return failed result on unknown, call handler catching all exceptions

## 4. Built-in Commands

- [x] 4.1 Create `src/mdt/commands/help.py` with `HelpCommand`: when called, queries `registry.names()` and returns a `CommandResult` with a formatted list of available commands in `output`
- [x] 4.2 Create `src/mdt/commands/exit.py` with `ExitCommand`: returns `CommandResult(success=True, output="Goodbye.", exit_requested=True)`
- [x] 4.3 Update `src/mdt/commands/__init__.py` to import `HelpCommand` and `ExitCommand` and register both with a module-level `CommandRegistry` instance that is importable by the app

## 5. Textual UI Layer

- [x] 5.1 Create `src/mdt/ui/shell_screen.py` with `ShellScreen(Screen)`: compose a `RichLog` widget (id `output`) above an `Input` widget (id `prompt`); on `Input.Submitted` call `dispatcher.dispatch`, append result to `RichLog` (green for success, red for error), call `app.exit()` if `exit_requested`
- [x] 5.2 Create `src/mdt/ui/app.py` with `MdtApp(App)`: in `on_mount` (or `__init__`) detect project context via `ProjectContext.detect()`, build `CommandRegistry`, import commands package to trigger registration, create `CommandDispatcher`, push `ShellScreen`

## 6. Core Unit Tests

- [x] 6.1 Write `tests/core/test_result.py`: verify `CommandResult` defaults and field values
- [x] 6.2 Write `tests/core/test_context.py`: verify `ProjectContext.detect()` finds `.git` in a temp directory tree; verify `repo_root=None` when no `.git` ancestor exists
- [x] 6.3 Write `tests/core/test_registry.py`: verify `register`/`resolve`/`names`; verify `ValueError` on duplicate
- [x] 6.4 Write `tests/core/test_dispatcher.py`: verify known command returns success result; verify unknown command returns failed result; verify blank input returns no-op result; verify exception in handler returns failed result without raising

## 7. Built-in Command Tests

- [x] 7.1 Write `tests/core/test_help_command.py`: verify `HelpCommand` output lists all registered command names
- [x] 7.2 Write `tests/core/test_exit_command.py`: verify `ExitCommand` returns `exit_requested=True`

## 8. UI Smoke Test

- [x] 8.1 Write `tests/ui/test_shell_screen.py`: use Textual's `pilot` to launch `MdtApp`, type `help`, press Enter, assert the output area contains text; type `exit`, press Enter, assert app has exited

## 9. Documentation

- [x] 9.1 Create `README.md` (or update if it exists) with: prerequisites, `pip install -e .` install instructions, how to run `mdt`, project layout explanation, and a note on adding new commands

