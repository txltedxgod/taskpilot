"""Command-line interface for TaskPilot.

Usage examples::

    taskpilot list   -c examples/tasks.yaml
    taskpilot next   -c examples/tasks.yaml
    taskpilot run    -c examples/tasks.yaml --task heartbeat
    taskpilot serve  -c examples/tasks.yaml --poll 60
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from typing import Optional, Sequence

from taskpilot import __version__
from taskpilot.actions.base import registry
from taskpilot.config import load_tasks
from taskpilot.runner import TaskRunner
from taskpilot.scheduler import Scheduler


def _configure_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="taskpilot",
        description="Schedule and run automation tasks from a simple config.",
    )
    parser.add_argument("--version", action="version", version=f"taskpilot {__version__}")
    parser.add_argument("-v", "--verbose", action="store_true", help="verbose logging")

    sub = parser.add_subparsers(dest="command", required=True)

    for name, help_text in (
        ("list", "list configured tasks"),
        ("next", "show the next run time for each task"),
    ):
        p = sub.add_parser(name, help=help_text)
        p.add_argument("-c", "--config", required=True, help="path to config file")

    p_run = sub.add_parser("run", help="run one or all tasks immediately")
    p_run.add_argument("-c", "--config", required=True)
    p_run.add_argument("--task", help="only run the task with this name")
    p_run.add_argument("--dry-run", action="store_true", help="do not perform side effects")

    p_serve = sub.add_parser("serve", help="run the scheduling loop")
    p_serve.add_argument("-c", "--config", required=True)
    p_serve.add_argument("--poll", type=float, default=60.0, help="poll interval seconds")
    p_serve.add_argument("--max-iterations", type=int, default=None)

    sub.add_parser("actions", help="list available action types")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    _configure_logging(getattr(args, "verbose", False))

    if args.command == "actions":
        print("\n".join(registry.names()))
        return 0

    tasks = load_tasks(args.config)

    if args.command == "list":
        for task in tasks:
            state = "on" if task.enabled else "off"
            print(f"[{state}] {task.name:<24} {str(task.schedule):<16} -> {task.action}")
        return 0

    if args.command == "next":
        print(json.dumps(Scheduler(tasks).describe(), indent=2))
        return 0

    if args.command == "run":
        runner = TaskRunner(dry_run=args.dry_run)
        selected = [t for t in tasks if not args.task or t.name == args.task]
        if args.task and not selected:
            print(f"No task named {args.task!r}", file=sys.stderr)
            return 1
        exit_code = 0
        for task in selected:
            result = runner.run(task)
            print(json.dumps(result.as_dict(), indent=2))
            exit_code = exit_code or (0 if result.success else 1)
        return exit_code

    if args.command == "serve":
        Scheduler(tasks).run_forever(
            poll_seconds=args.poll,
            max_iterations=args.max_iterations,
            on_result=lambda r: print(json.dumps(r.as_dict())),
        )
        return 0

    parser.error(f"unknown command: {args.command}")  # pragma: no cover
    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
