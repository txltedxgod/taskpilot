"""Built-in actions and the action registry.

Actions are plain callables registered by name. Each receives the runtime
``context`` plus the task's ``params`` and returns a string describing what
it did (used for logging/results).
"""

from __future__ import annotations

from taskpilot.actions.base import Action, ActionContext, registry
from taskpilot.actions import builtins as _builtins  # noqa: F401  (registers actions)

__all__ = ["Action", "ActionContext", "registry"]
