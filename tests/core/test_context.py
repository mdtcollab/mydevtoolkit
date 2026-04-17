from pathlib import Path

from mdt.core.context import ProjectContext


def test_detect_finds_repo_root(tmp_path: Path, monkeypatch) -> None:
    repo_root = tmp_path / "repo"
    nested = repo_root / "a" / "b"
    (repo_root / ".git").mkdir(parents=True)
    nested.mkdir(parents=True)
    monkeypatch.chdir(nested)

    context = ProjectContext.detect()

    assert context.cwd == nested
    assert context.repo_root == repo_root
    assert context.project_name == "repo"


def test_detect_without_repo_root(tmp_path: Path, monkeypatch) -> None:
    cwd = tmp_path / "norepo" / "sub"
    cwd.mkdir(parents=True)
    monkeypatch.chdir(cwd)

    context = ProjectContext.detect()

    assert context.cwd == cwd
    assert context.repo_root is None
    assert context.project_name is None

