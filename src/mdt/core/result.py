from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class CommandResult:
    success: bool
    output: str = ""
    error: str | None = None
    data: dict[str, Any] = field(default_factory=dict)
    exit_requested: bool = False

