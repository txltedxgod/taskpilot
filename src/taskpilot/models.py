"""Core data models for TaskPilot."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from taskpilot.cron import CronSchedule


@dataclass
class Task:
    """A single scheduled unit of work.

    A task pairs a cron *schedule* with an *action* (the thing to run) and
    its keyword arguments. Tasks are created from configuration but are also
    convenient to build directly in code.
    """

    name: str
    schedule: CronSchedule
    action: str
    params: dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    description: str = ""

    def next_run(self, after: Optional[datetime] = None) -> datetime:
        """Return the next scheduled run time strictly after *after*."""
        return self.schedule.next_after(after or datetime.now())


@dataclass
class TaskResult:
    """The outcome of running a task once."""

    task_name: str
    started_at: datetime
    finished_at: datetime
    success: bool
    output: str = ""
    error: str = ""

    @property
    def duration_seconds(self) -> float:
        return (self.finished_at - self.started_at).total_seconds()

    def as_dict(self) -> dict[str, Any]:
        return {
            "task": self.task_name,
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat(),
            "duration_seconds": round(self.duration_seconds, 3),
            "success": self.success,
            "output": self.output,
            "error": self.error,
        }
