## Context

The mdt interactive shell is built on Textual and has a working command loop, registry, dispatcher, and result model. The current shell screen is minimal: a plain output area and a command input box. There are two commands (`help`, `exit`). No command categories exist and there is no visual structure.

This change introduces a richer screen layout, an activity/timeline log widget, three command categories (`openspec`, `git`, `copilot`), and two headless branch helpers. The Textual UI must remain thin; all logic lives in the headless core.

## Goals / Non-Goals

**Goals:**
- Four-zone Textual layout: ASCII art header → help section → activity log → command input
- Activity log that accumulates entries for the session lifetime
- Category grouping on `CommandRegistry` (optional `category` field per registration)
- Updated `help` output that groups commands under their category
- Headless `openspec branch` helper: reads the latest OpenSpec change folder and creates a git branch
- Headless `git branch` helper: normalises free-text into `<category>/<ticket>-<slug>` and creates the branch
- `copilot` category placeholder registered, no commands yet
- Tests for both branch helpers

**Non-Goals:**
- Persistent activity log (session-only, lost on exit)
- GitHub API or Copilot integration
- Any copilot subcommands in this change
- Complex TUI animations or theming

## Decisions

### D1 — Activity log as a Textual `Log` widget (scrollable `RichLog`)
**Decision**: Use Textual's built-in `RichLog` widget for the activity/timeline area.  
**Rationale**: `RichLog` supports markup, auto-scrolls, and requires no custom rendering. A custom widget would duplicate work already in Textual.  
**Alternative considered**: Plain `ListView` of `ListItem` objects — more control but more code for no gain at this stage.

### D2 — Category field on `CommandRegistry`, not a separate registry
**Decision**: Add an optional `category: str` parameter to `registry.register()`. The registry stores it and `registry.names()` gains a companion `registry.all()` returning `(name, category)` pairs.  
**Rationale**: Keeps the registry as the single source of truth; avoids a parallel data structure. Help can group by category without additional infrastructure.  
**Alternative considered**: Separate `CategoryRegistry` wrapper — unnecessary complexity.

### D3 — Command routing for two-word commands (`openspec branch`, `git branch`)
**Decision**: Tokenise input into `[verb, *args]`. If `verb` resolves to `None` and the input has two+ tokens, try `verb_subverb` as the command key (e.g., `openspec_branch`).  
**Rationale**: Keeps single-word commands unchanged; multi-word routing is purely additive in the dispatcher. No grammar DSL is needed at this scale.  
**Alternative considered**: Parse a namespace tree — over-engineered for two commands.

### D4 — Git operations via `subprocess` (not `gitpython`)
**Decision**: Execute `git` CLI commands via `subprocess.run`. The helpers return a `CommandResult` with `success`, `message`, and `data`.  
**Rationale**: `subprocess` needs no extra dependency; git is already a prerequisite for mdt users. GitPython adds ~2 MB and complexity for two shell invocations.  
**Alternative considered**: `gitpython` library — not worth the dependency.

### D5 — OpenSpec branch name derived from latest change folder mtime
**Decision**: Scan `openspec/changes/` for subdirectories, pick the one with the most recent modification time, and use its name verbatim as the branch name (prepended with `feature/` if no prefix present).  
**Rationale**: Deterministic, requires no config, and mirrors the user's most recent `propose` flow automatically.  
**Alternative considered**: Read `.openspec.yaml` inside the folder — adds parsing; mtime is sufficient.

### D6 — Branch name normalisation for `git branch` helper
**Decision**: Free-text input is split on whitespace/punctuation into tokens. The first token matching `feature|bugfix|hotfix|chore|refactor` becomes the prefix; the next token matching `[a-z]+-[0-9]+` becomes the ticket; remaining tokens form the slug (lowercase, joined by `-`). Missing prefix or ticket → `CommandResult` with error message.  
**Rationale**: Explicit rules produce predictable output; clear error messages guide the user without crashing the session.

## Risks / Trade-offs

- [Branch mtime heuristic] → If the user has modified an older change folder recently, the wrong branch name is selected. Mitigation: show the detected name before creating; user can run again with explicit name in a future enhancement.
- [Two-word routing] → A registered single-word command `openspec` would shadow multi-word lookup. Mitigation: never register bare category names as commands; category names are metadata only.
- [subprocess git] → Fails silently if git is not on PATH. Mitigation: `CommandResult` captures stderr and surfaces it as an error message in the activity log.

