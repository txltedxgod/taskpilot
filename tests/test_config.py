import json

import pytest

from taskpilot.config import ConfigError, load_tasks, parse_tasks


def test_parse_tasks_from_mapping():
    raw = {
        "tasks": [
            {"name": "a", "schedule": "* * * * *", "action": "log",
             "params": {"message": "hi"}},
            {"name": "b", "schedule": "@daily", "action": "shell",
             "params": {"command": "echo hi"}, "enabled": False},
        ]
    }
    tasks = parse_tasks(raw)
    assert [t.name for t in tasks] == ["a", "b"]
    assert tasks[0].params["message"] == "hi"
    assert tasks[1].enabled is False


def test_duplicate_names_rejected():
    raw = {"tasks": [
        {"name": "x", "schedule": "* * * * *", "action": "log"},
        {"name": "x", "schedule": "* * * * *", "action": "log"},
    ]}
    with pytest.raises(ConfigError):
        parse_tasks(raw)


def test_missing_field_rejected():
    with pytest.raises(ConfigError):
        parse_tasks({"tasks": [{"name": "x", "action": "log"}]})


def test_load_tasks_from_json_file(tmp_path):
    path = tmp_path / "tasks.json"
    path.write_text(json.dumps({"tasks": [
        {"name": "a", "schedule": "@hourly", "action": "log"}
    ]}))
    tasks = load_tasks(path)
    assert tasks[0].name == "a"


def test_missing_file(tmp_path):
    with pytest.raises(ConfigError):
        load_tasks(tmp_path / "nope.yaml")
