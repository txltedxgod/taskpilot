"""Execute individual tasks and capture their results."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from taskpilot.actions.base import ActionContext, ActionRegistry
from taskpilot.actions.base import registry as default_registry
from taskpilot.models import Task, TaskResult

logger = logging.getLogger("taskpilot.runner")


class TaskRunner:
    """Runs tasks against an action registry, producing :class:`TaskResult`."""

    def __init__(
        self,
        registry: Optional[ActionRegistry] = None,
        *,
        dry_run: bool = False,
        env: Optional[dict[str, str]] = None,
    ) -> None:
        self.registry = registry or default_registry
        self.dry_run = dry_run
        self.env = env or {}

    def run(self, task: Task) -> TaskResult:
        started = datetime.now()
        context = ActionContext(
            task_name=task.name, dry_run=self.dry_run, env=self.env
        )
        logger.info("Running task %r (action=%s)", task.name, task.action)
        try:
            output = self.registry.run(task.action, context, task.params)
            finished = datetime.now()
            logger.info("Task %r finished in %.3fs", task.name,
                        (finished - started).total_seconds())
            return TaskResult(
                task_name=task.name,
                started_at=started,
                finished_at=finished,
                success=True,
                output=output,
            )
        except Exception as exc:  # noqa: BLE001 - we record any failure
            finished = datetime.now()
            logger.exception("Task %r failed", task.name)
            return TaskResult(
                task_name=task.name,
                started_at=started,
                finished_at=finished,
                success=False,
                error=f"{type(exc).__name__}: {exc}",
            )
