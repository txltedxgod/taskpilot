from taskpilot.actions.base import ActionContext, registry


def test_log_action_default_message():
    ctx = ActionContext(task_name="demo")
    assert "demo" in registry.run("log", ctx, {})


def test_log_action_custom_message():
    ctx = ActionContext(task_name="demo")
    assert registry.run("log", ctx, {"message": "hello"}) == "hello"


def test_shell_action_runs_command():
    ctx = ActionContext(task_name="demo")
    out = registry.run("shell", ctx, {"command": "echo taskpilot"})
    assert out == "taskpilot"


def test_shell_action_dry_run_skips_execution():
    ctx = ActionContext(task_name="demo", dry_run=True)
    out = registry.run("shell", ctx, {"command": "echo nope"})
    assert out.startswith("[dry-run]")


def test_unknown_action_raises():
    ctx = ActionContext(task_name="demo")
    try:
        registry.run("does-not-exist", ctx, {})
    except KeyError as exc:
        assert "Unknown action" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("expected KeyError")
