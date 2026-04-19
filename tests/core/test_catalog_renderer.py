"""Tests for CatalogRenderer."""

from pathlib import Path

from mdt.catalog.item import CatalogItem
from mdt.catalog.renderer import CatalogRenderer


def test_passthrough_render() -> None:
    renderer = CatalogRenderer()
    content = "# My Skill\nSome content"
    result = renderer.render(content, Path("SKILL.md"), target="claude")
    assert result == content


def test_custom_renderer_registration() -> None:
    renderer = CatalogRenderer()

    def opencode_render(content: str, source_path: Path, item: CatalogItem) -> str:
        return f"---\ntarget: opencode\n---\n{content}"

    renderer.register("opencode", opencode_render)
    result = renderer.render("hello", Path("SKILL.md"), target="opencode")
    assert result.startswith("---\ntarget: opencode")
    assert "hello" in result


def test_unregistered_target_passthrough() -> None:
    renderer = CatalogRenderer()
    renderer.register("opencode", lambda c, p, i: "transformed")
    result = renderer.render("original", Path("f.md"), target="claude")
    assert result == "original"


def test_renderer_receives_metadata() -> None:
    renderer = CatalogRenderer()
    received = {}

    def capture_render(content: str, source_path: Path, item: CatalogItem) -> str:
        received["content"] = content
        received["source_path"] = source_path
        received["item"] = item
        return content

    renderer.register("claude", capture_render)
    item = CatalogItem(name="test", kind="skill")
    renderer.render("hello", Path("SKILL.md"), target="claude", item=item)
    assert received["content"] == "hello"
    assert received["source_path"] == Path("SKILL.md")
    assert received["item"].name == "test"

