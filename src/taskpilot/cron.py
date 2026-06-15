"""A small, dependency-free cron expression parser and scheduler.

Supports the classic 5-field cron format::

    ┌────────────── minute        (0 - 59)
    │ ┌─────────── hour          (0 - 23)
    │ │ ┌───────── day of month  (1 - 31)
    │ │ │ ┌─────── month         (1 - 12)
    │ │ │ │ ┌───── day of week   (0 - 6, Sunday = 0)
    │ │ │ │ │
    * * * * *

Each field supports ``*``, lists (``1,2,3``), ranges (``1-5``),
steps (``*/5`` or ``0-30/10``) and a few convenience aliases
(``@hourly``, ``@daily``, ``@weekly``, ``@monthly``, ``@yearly``).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

_ALIASES = {
    "@yearly": "0 0 1 1 *",
    "@annually": "0 0 1 1 *",
    "@monthly": "0 0 1 * *",
    "@weekly": "0 0 * * 0",
    "@daily": "0 0 * * *",
    "@midnight": "0 0 * * *",
    "@hourly": "0 * * * *",
}

_FIELD_BOUNDS = (
    (0, 59),  # minute
    (0, 23),  # hour
    (1, 31),  # day of month
    (1, 12),  # month
    (0, 6),   # day of week
)

_MAX_SEARCH_MINUTES = 366 * 24 * 60  # safety bound: ~1 year


class CronError(ValueError):
    """Raised when a cron expression cannot be parsed."""


def _parse_field(field: str, low: int, high: int) -> frozenset[int]:
    """Expand a single cron field into the set of matching integers."""
    values: set[int] = set()
    for part in field.split(","):
        part = part.strip()
        if not part:
            raise CronError(f"Empty component in cron field: {field!r}")

        step = 1
        if "/" in part:
            base, _, step_str = part.partition("/")
            if not step_str.isdigit() or int(step_str) == 0:
                raise CronError(f"Invalid step in cron field: {part!r}")
            step = int(step_str)
        else:
            base = part

        if base == "*":
            start, end = low, high
        elif "-" in base:
            start_str, _, end_str = base.partition("-")
            if not (start_str.isdigit() and end_str.isdigit()):
                raise CronError(f"Invalid range in cron field: {part!r}")
            start, end = int(start_str), int(end_str)
        elif base.isdigit():
            start = end = int(base)
        else:
            raise CronError(f"Invalid token in cron field: {part!r}")

        if start > end:
            raise CronError(f"Range start greater than end: {part!r}")
        if start < low or end > high:
            raise CronError(
                f"Value out of bounds ({low}-{high}) in cron field: {part!r}"
            )

        values.update(range(start, end + 1, step))

    return frozenset(values)


@dataclass(frozen=True)
class CronSchedule:
    """An immutable, parsed cron schedule."""

    expression: str
    minutes: frozenset[int]
    hours: frozenset[int]
    days_of_month: frozenset[int]
    months: frozenset[int]
    days_of_week: frozenset[int]

    @classmethod
    def parse(cls, expression: str) -> "CronSchedule":
        raw = expression.strip()
        if not raw:
            raise CronError("Cron expression must not be empty")

        normalized = _ALIASES.get(raw.lower(), raw)
        fields = normalized.split()
        if len(fields) != 5:
            raise CronError(
                f"Expected 5 cron fields, got {len(fields)}: {expression!r}"
            )

        parsed = [
            _parse_field(field, low, high)
            for field, (low, high) in zip(fields, _FIELD_BOUNDS)
        ]
        return cls(expression, *parsed)

    def matches(self, moment: datetime) -> bool:
        """Return ``True`` if *moment* satisfies the schedule.

        Per cron convention, when both day-of-month and day-of-week are
        restricted, a match in *either* field is enough.
        """
        if moment.minute not in self.minutes:
            return False
        if moment.hour not in self.hours:
            return False
        if moment.month not in self.months:
            return False

        # cron weekday: Monday=0..Sunday=6 in Python; cron uses Sunday=0.
        cron_dow = (moment.weekday() + 1) % 7
        dom_restricted = self.days_of_month != frozenset(range(1, 32))
        dow_restricted = self.days_of_week != frozenset(range(0, 7))

        dom_match = moment.day in self.days_of_month
        dow_match = cron_dow in self.days_of_week

        if dom_restricted and dow_restricted:
            return dom_match or dow_match
        return dom_match and dow_match

    def next_after(self, moment: datetime) -> datetime:
        """Return the next datetime strictly after *moment* that matches."""
        candidate = (moment + timedelta(minutes=1)).replace(second=0, microsecond=0)
        for _ in range(_MAX_SEARCH_MINUTES):
            if self.matches(candidate):
                return candidate
            candidate += timedelta(minutes=1)
        raise CronError(
            f"No matching time found within one year for {self.expression!r}"
        )

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.expression
