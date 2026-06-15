# Contributing to TaskPilot

Thanks for your interest in improving TaskPilot! This project is intentionally
small and dependency-light, which makes it easy to contribute.

## Getting started

```bash
git clone https://github.com/txltedxgod/taskpilot.git
cd taskpilot
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Before you open a pull request

Run the full local check suite — it mirrors CI:

```bash
ruff check .       # lint
mypy               # type-check
pytest             # tests
```

## Adding a new action

1. Add your callable in `src/taskpilot/actions/builtins.py` (or a new module).
2. Decorate it with `@registry.register("your-action-name")`.
3. Accept `context: ActionContext` as the first argument and `**params`.
4. Return a short `str` describing what happened (used in results/logs).
5. Add a test in `tests/test_actions.py`.

## Commit style

Keep commits focused and write descriptive messages. Conventional Commits
(`feat:`, `fix:`, `docs:`, `test:`) are appreciated but not required.
