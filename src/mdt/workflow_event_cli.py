"""Headless CLI entrypoint for recording workflow events."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from mdt.core.workflow_history import record_workflow_event


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mdt-workflow-event",
        description="Record a workflow event for OpenSpec or Spec Kit integrations.",
    )
    parser.add_argument("--project-root", default=".", help="Project root to associate with the event")
    parser.add_argument("--workflow-type", required=True, choices=["openspec", "speckit"])
    parser.add_argument("--command-id", required=True)
    parser.add_argument("--raw-command", required=True)
    parser.add_argument("--success", required=True, choices=["true", "false"])
    parser.add_argument("--source", default="agent-hook")
    parser.add_argument("--change-name")
    parser.add_argument("--iteration-name")
    parser.add_argument("--timestamp")
    return parser


def run(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    payload = {
        "workflow_type": args.workflow_type,
        "command_id": args.command_id,
        "raw_command": args.raw_command,
        "success": args.success,
        "source": args.source,
        "change_name": args.change_name,
        "iteration_name": args.iteration_name,
        "timestamp": args.timestamp,
    }
    record_workflow_event(Path(args.project_root), payload)
    return 0


def main() -> int:
    return run()

