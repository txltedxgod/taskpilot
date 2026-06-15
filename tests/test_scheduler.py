from datetime import datetime

from taskpilot.actions.base import ActionContext, ActionRegistry
from taskpilot.cron import CronSchedule
from taskpilot.models import Task
from taskpilot.runner import TaskRunner
from taskpilot.scheduler import Scheduler


def _registry_with_counter():
    reg = ActionRegistry()
    calls = {"n": 0}

    @reg.register("count")
    def _count(context: ActionContext, **_):
        calls["n"] += 1
        return f"called {calls['n']}"

    return reg, calls


def test_run_pending_runs_matching_tasks():
    reg, calls = _registry_with_counter()
    runner = TaskRunner(registry=reg)
    task = Task("tick", CronSchedule.parse("*/5 * * * *"), "count")
    scheduler = Scheduler([task], runner=runner)

    results = scheduler.run_pending(datetime(2026, 1, 1, 0, 5))
    assert len(results) == 1
    assert results[0].success
    assert calls["n"] == 1

    # Non-matching minute does nothing.
    assert scheduler.run_pending(datetime(2026, 1, 1, 0, 6)) == []
    assert calls["n"] == 1


def test_disabled_tasks_are_skipped():
    reg, calls = _registry_with_counter()
    runner = TaskRunner(registry=reg)
    task = Task("tick", CronSchedule.parse("* * * * *"), "count", enabled=False)
    scheduler = Scheduler([task], runner=runner)
    assert scheduler.run_pending(datetime(2026, 1, 1, 0, 0)) == []
    assert calls["n"] == 0


def test_failure_is_captured_as_result():
    reg = ActionRegistry()

    @reg.register("boom")
    def _boom(context, **_):
        raise ValueError("kaboom")

    runner = TaskRunner(registry=reg)
    task = Task("x", CronSchedule.parse("* * * * *"), "boom")
    result = Scheduler([task], runner=runner).run_pending(datetime(2026, 1, 1, 0, 0))[0]
    assert result.success is False
    assert "kaboom" in result.error


def test_run_forever_is_bounded_and_uses_injected_sleep():
    reg, calls = _registry_with_counter()
    runner = TaskRunner(registry=reg)
    task = Task("tick", CronSchedule.parse("* * * * *"), "count")
    scheduler = Scheduler([task], runner=runner)

    sleeps = []
    scheduler.run_forever(
        poll_seconds=1,
        max_iterations=1,
        sleep=sleeps.append,
    )
    # One iteration ran the due task once and never slept (loop ended).
    assert calls["n"] == 1
    assert sleeps == []


def test_describe_reports_next_run():
    task = Task("tick", CronSchedule.parse("0 0 * * *"), "count")
    rows = Scheduler([task]).describe(after=datetime(2026, 1, 1, 12, 0))
    assert rows[0]["name"] == "tick"
    assert rows[0]["next_run"].startswith("2026-01-02T00:00")
