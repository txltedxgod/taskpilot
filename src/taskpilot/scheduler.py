"""The scheduling loop that ties tasks, schedules and the runner together."""

from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import Callable, Iterable, Optional

from taskpilot.models import Task, TaskResult
from taskpilot.runner import TaskRunner

logger = logging.getLogger("taskpilot.scheduler")


class Scheduler:
    """Runs enabled tasks whenever their cron schedule is due.

    The scheduler is deliberately simple and testable: :meth:`run_pending`
    is a pure function of the supplied *moment*, while :meth:`run_forever`
    wraps it in a sleep loop for real-world use.
    """

    def __init__(
        self,
        tasks: Iterable[Task],
        runner: Optional[TaskRunner] = None,
    ) -> None:
        self.tasks: list[Task] = list(tasks)
        self.runner = runner or TaskRunner()

    def run_pending(self, moment: Optional[datetime] = None) -> list[TaskResult]:
        """Run every enabled task whose schedule matches *moment*."""
        moment = (moment or datetime.now()).replace(second=0, microsecond=0)
        results: list[TaskResult] = []
        for task in self.tasks:
            if not task.enabled:
                continue
            if task.schedule.matches(moment):
                results.append(self.runner.run(task))
        return results

    def run_forever(
        self,
        *,
        poll_seconds: float = 60.0,
        max_iterations: Optional[int] = None,
        on_result: Optional[Callable[[TaskResult], None]] = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        """Continuously poll and run due tasks.

        *max_iterations* bounds the loop (useful in tests); when ``None`` the
        loop runs until interrupted. *sleep* is injectable for testing.
        """
        logger.info("Scheduler starting with %d task(s)", len(self.tasks))
        iteration = 0
        last_minute: Optional[datetime] = None
        try:
            while max_iterations is None or iteration < max_iterations:
                now = datetime.now().replace(second=0, microsecond=0)
                if now != last_minute:
                    for result in self.run_pending(now):
                        if on_result is not None:
                            on_result(result)
                    last_minute = now
                iteration += 1
                if max_iterations is None or iteration < max_iterations:
                    sleep(poll_seconds)
        except KeyboardInterrupt:  # pragma: no cover - interactive only
            logger.info("Scheduler stopped by user")

    def describe(self, after: Optional[datetime] = None) -> list[dict]:
        """Return a serialisable summary of upcoming runs."""
        after = after or datetime.now()
        rows = []
        for task in self.tasks:
            rows.append(
                {
                    "name": task.name,
                    "action": task.action,
                    "schedule": str(task.schedule),
                    "enabled": task.enabled,
                    "next_run": task.next_run(after).isoformat()
                    if task.enabled
                    else None,
                }
            )
        return rows
