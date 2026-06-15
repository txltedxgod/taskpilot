"""Load tasks from a YAML (or JSON) configuration file.

Example configuration::

    tasks:
      - name: heartbeat
        schedule: "*/5 * * * *"
        action: log
        params:
          message: "still alive"

      - name: nightly-backup
        schedule: "@daily"
        action: shell
        params:
          command: "tar czf /tmp/backup.tgz /data"
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Union

import yaml

from taskpilot.cron import CronSchedule
from taskpilot.models import Task

PathLike = Union[str, Path]


class ConfigError(ValueError):
    """Raised when a configuration file is structurally invalid."""


def _parse_raw(text: str, *, is_json: bool) -> Any:
    if is_json:
        return json.loads(text)
    return yaml.safe_load(text)


def load_tasks(path: PathLike) -> list[Task]:
    """Parse *path* and return a list of :class:`Task` objects."""
    file_path = Path(path)
    if not file_path.exists():
        raise ConfigError(f"Config file not found: {file_path}")

    raw = _parse_raw(
        file_path.read_text(encoding="utf-8"),
        is_json=file_path.suffix.lower() == ".json",
    )
    return parse_tasks(raw)


def parse_tasks(raw: Any) -> list[Task]:
    """Build tasks from an already-parsed config mapping/list."""
    if isinstance(raw, dict):
        entries = raw.get("tasks", [])
    elif isinstance(raw, list):
        entries = raw
    else:
        raise ConfigError("Config root must be a mapping or a list")

    if not isinstance(entries, list):
        raise ConfigError("'tasks' must be a list")

    tasks: list[Task] = []
    seen: set[str] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ConfigError(f"Task #{index} must be a mapping")
        tasks.append(_build_task(entry, index))
        if tasks[-1].name in seen:
            raise ConfigError(f"Duplicate task name: {tasks[-1].name!r}")
        seen.add(tasks[-1].name)
    return tasks


def _build_task(entry: dict[str, Any], index: int) -> Task:
    try:
        name = str(entry["name"])
        schedule = entry["schedule"]
        action = str(entry["action"])
    except KeyError as exc:
        raise ConfigError(
            f"Task #{index} is missing required field {exc.args[0]!r}"
        ) from exc

    params = entry.get("params", {}) or {}
    if not isinstance(params, dict):
        raise ConfigError(f"Task {name!r}: 'params' must be a mapping")

    return Task(
        name=name,
        schedule=CronSchedule.parse(str(schedule)),
        action=action,
        params=params,
        enabled=bool(entry.get("enabled", True)),
        description=str(entry.get("description", "")),
    )
