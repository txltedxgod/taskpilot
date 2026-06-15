"""Action protocol and a tiny name-based registry."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict


@dataclass
class ActionContext:
    """Runtime context passed to every action invocation."""

    task_name: str
    dry_run: bool = False
    env: Dict[str, str] = field(default_factory=dict)


# An action is any callable taking (context, **params) and returning a str.
Action = Callable[..., str]


class ActionRegistry:
    """Maps action names to callables."""

    def __init__(self) -> None:
        self._actions: Dict[str, Action] = {}

    def register(self, name: str, action: Action | None = None):
        """Register an action. Usable directly or as a decorator."""
        if action is not None:
            self._actions[name] = action
            return action

        def decorator(func: Action) -> Action:
            self._actions[name] = func
            return func

        return decorator

    def get(self, name: str) -> Action:
        try:
            return self._actions[name]
        except KeyError as exc:
            available = ", ".join(sorted(self._actions)) or "<none>"
            raise KeyError(
                f"Unknown action {name!r}. Available actions: {available}"
            ) from exc

    def names(self) -> list[str]:
        return sorted(self._actions)

    def run(self, name: str, context: ActionContext, params: Dict[str, Any]) -> str:
        return self.get(name)(context, **params)


# A single module-level registry shared across the package.
registry = ActionRegistry()
