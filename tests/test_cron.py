from datetime import datetime

import pytest

from taskpilot.cron import CronError, CronSchedule


def test_parses_aliases():
    assert CronSchedule.parse("@hourly").expression == "@hourly"
    sched = CronSchedule.parse("@daily")
    assert sched.minutes == frozenset({0})
    assert sched.hours == frozenset({0})


def test_wildcard_minute_matches_every_minute():
    sched = CronSchedule.parse("* * * * *")
    assert sched.matches(datetime(2026, 1, 1, 12, 34))


def test_step_values():
    sched = CronSchedule.parse("*/15 * * * *")
    assert sched.minutes == frozenset({0, 15, 30, 45})
    assert sched.matches(datetime(2026, 1, 1, 9, 30))
    assert not sched.matches(datetime(2026, 1, 1, 9, 31))


def test_ranges_and_lists():
    sched = CronSchedule.parse("0 9-11,13 * * 1-5")
    assert sched.hours == frozenset({9, 10, 11, 13})
    # Monday 2026-01-05 at 10:00 -> matches
    assert sched.matches(datetime(2026, 1, 5, 10, 0))
    # Sunday 2026-01-04 at 10:00 -> weekday excluded
    assert not sched.matches(datetime(2026, 1, 4, 10, 0))


def test_next_after_is_strictly_future():
    sched = CronSchedule.parse("*/30 * * * *")
    now = datetime(2026, 1, 1, 10, 0)
    nxt = sched.next_after(now)
    assert nxt == datetime(2026, 1, 1, 10, 30)


def test_dom_or_dow_semantics():
    # When both DOM and DOW restricted, either match suffices.
    sched = CronSchedule.parse("0 0 13 * 5")  # 13th OR any Friday
    assert sched.matches(datetime(2026, 2, 13, 0, 0))  # Friday the 13th
    assert sched.matches(datetime(2026, 1, 2, 0, 0))   # a Friday, not the 13th
    assert sched.matches(datetime(2026, 3, 13, 0, 0))  # the 13th, not a Friday
    assert not sched.matches(datetime(2026, 1, 1, 0, 0))


@pytest.mark.parametrize(
    "expr",
    ["", "* * * *", "60 * * * *", "* 24 * * *", "*/0 * * * *", "5-1 * * * *", "a * * * *"],
)
def test_invalid_expressions(expr):
    with pytest.raises(CronError):
        CronSchedule.parse(expr)
