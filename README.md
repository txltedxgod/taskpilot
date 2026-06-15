# 🛫 TaskPilot

[![CI](https://github.com/txltedxgod/taskpilot/actions/workflows/ci.yml/badge.svg)](https://github.com/txltedxgod/taskpilot/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: ruff](https://img.shields.io/badge/lint-ruff-261230.svg)](https://github.com/astral-sh/ruff)

**TaskPilot** is a lightweight automation & task-scheduling toolkit for Python.
Define *what* should run and *when* in a simple YAML file, and TaskPilot takes
care of the cron parsing, scheduling loop, execution, error handling and
structured logging — with **zero heavy dependencies** (just `PyYAML`).

Think of it as a tiny, hackable cron daemon you can read in an afternoon and
extend in minutes.

---

## 🛰️ Live demo — Flight Deck

A self-contained dashboard that visualizes the example schedule in
[`examples/tasks.yaml`](examples/tasks.yaml): live countdown dials for the
next run of every task, an arm/standby toggle, a manual "run now" trigger and
a scrolling flight log.

➡️ **[Open the Flight Deck demo](https://txltedxgod.github.io/taskpilot/dashboard.html)**
*(enable GitHub Pages on the `main` branch, `/docs` folder, to make this link live)*

Or run it locally — no build step, just open the file:

```bash
open docs/dashboard.html      # macOS
start docs\dashboard.html     # Windows
```

---

## ✨ Features

- **Real cron expressions** — `*`, ranges (`1-5`), lists (`1,3,5`), steps
  (`*/15`) and aliases (`@hourly`, `@daily`, `@weekly`, `@monthly`).
- **Pluggable actions** — ship-with `log`, `shell`, `http` and `webhook`, plus
  a one-line decorator API to register your own.
- **Config-driven** — declare tasks in YAML or JSON; no code required for
  common automations.
- **Friendly CLI** — `list`, `next`, `run`, `serve` and `actions` subcommands.
- **Testable core** — the scheduler is a pure function of the current time, so
  every behaviour is covered by fast, deterministic unit tests.
- **Type-hinted & linted** — `mypy` + `ruff` clean, CI across Python 3.9–3.12.

---

## 📦 Installation

```bash
git clone https://github.com/txltedxgod/taskpilot.git
cd taskpilot
pip install -e ".[dev]"   # drop [dev] for a runtime-only install
```

---

## 🚀 Quick start

Create a config (or use the provided [`examples/tasks.yaml`](examples/tasks.yaml)):

```yaml
tasks:
  - name: heartbeat
    schedule: "*/5 * * * *"     # every 5 minutes
    action: log
    params:
      message: "TaskPilot is alive"

  - name: nightly-backup
    schedule: "@daily"          # every day at midnight
    action: shell
    params:
      command: "tar czf /tmp/backup.tgz ./data"
```

Then drive it from the CLI:

```bash
# See what is configured
taskpilot list -c examples/tasks.yaml

# Inspect the next scheduled run for each task (JSON)
taskpilot next -c examples/tasks.yaml

# Run a single task right now (great for debugging)
taskpilot run -c examples/tasks.yaml --task heartbeat

# Start the scheduling loop
taskpilot serve -c examples/tasks.yaml --poll 60
```

> Tip: add `--dry-run` to `run` to preview side-effectful actions safely.

---

## 🧩 Writing a custom action

Actions are just callables registered by name:

```python
from taskpilot.actions.base import ActionContext, registry

@registry.register("greet")
def greet(context: ActionContext, who: str = "world") -> str:
    return f"Hello, {who}!"
```

Reference it from your config:

```yaml
tasks:
  - name: say-hi
    schedule: "0 9 * * 1-5"
    action: greet
    params:
      who: "team"
```

---

## 🧠 Using TaskPilot as a library

```python
from datetime import datetime
from taskpilot import CronSchedule, Task, Scheduler

task = Task(
    name="tick",
    schedule=CronSchedule.parse("*/5 * * * *"),
    action="log",
    params={"message": "tick"},
)

scheduler = Scheduler([task])
results = scheduler.run_pending(datetime.now())
for r in results:
    print(r.as_dict())
```

---

## 🗂 Project layout

```
taskpilot/
├── src/taskpilot/
│   ├── cron.py          # dependency-free cron parser + matcher
│   ├── models.py        # Task / TaskResult dataclasses
│   ├── config.py        # YAML/JSON loader
│   ├── runner.py        # executes a task, captures results
│   ├── scheduler.py     # the polling/scheduling loop
│   ├── cli.py           # argparse-based command line
│   └── actions/         # built-in + registry-based actions
├── tests/               # pytest suite (cron, config, scheduler, actions)
├── examples/tasks.yaml  # sample configuration
└── .github/workflows/   # CI: lint + type-check + tests (3.9–3.12)
```

---

## 🧪 Development

```bash
ruff check .       # lint
mypy               # type-check
pytest --cov=taskpilot --cov-report=term-missing
```

Contributions are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).

---

## 📄 License

Released under the [MIT License](LICENSE).
