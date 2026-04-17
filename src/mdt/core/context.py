from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class ProjectContext:
    cwd: Path
    repo_root: Path | None
    project_name: str | None

    @classmethod
    def detect(cls) -> "ProjectContext":
        cwd = Path.cwd()
        repo_root = cls._find_repo_root(cwd)
        project_name = repo_root.name if repo_root else None
        return cls(cwd=cwd, repo_root=repo_root, project_name=project_name)

    @staticmethod
    def _find_repo_root(start: Path) -> Path | None:
        for candidate in (start, *start.parents):
            if (candidate / ".git").exists():
                return candidate
        return None

