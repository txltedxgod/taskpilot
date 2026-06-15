"""Built-in actions shipped with TaskPilot.

These cover the most common automation needs without third-party deps:

* ``log``     - write a message to the log (great for testing schedules).
* ``shell``   - run a shell command and capture its output.
* ``http``    - perform an HTTP request (uses the stdlib ``urllib``).
* ``webhook`` - POST a JSON payload to a URL (a thin wrapper over ``http``).
"""

from __future__ import annotations

import json
import subprocess
import urllib.request
from typing import Any, Optional

from taskpilot.actions.base import ActionContext, registry


@registry.register("log")
def log_action(context: ActionContext, message: str = "", **_: Any) -> str:
    """Return a log message. Useful as a no-op for testing schedules."""
    return message or f"task {context.task_name!r} fired"


@registry.register("shell")
def shell_action(
    context: ActionContext,
    command: str,
    timeout: Optional[float] = 60.0,
    check: bool = True,
    **_: Any,
) -> str:
    """Run *command* in a shell and return its combined output."""
    if context.dry_run:
        return f"[dry-run] would run: {command}"

    completed = subprocess.run(  # noqa: S602 - shell use is intentional here
        command,
        shell=True,
        capture_output=True,
        text=True,
        timeout=timeout,
        env={**context.env} or None,
    )
    output = (completed.stdout or "") + (completed.stderr or "")
    if check and completed.returncode != 0:
        raise RuntimeError(
            f"command exited with {completed.returncode}: {output.strip()}"
        )
    return output.strip()


@registry.register("http")
def http_action(
    context: ActionContext,
    url: str,
    method: str = "GET",
    headers: Optional[dict[str, str]] = None,
    body: Any = None,
    timeout: float = 30.0,
    **_: Any,
) -> str:
    """Perform an HTTP request and return ``"<status> <bytes> bytes"``."""
    if context.dry_run:
        return f"[dry-run] would {method} {url}"

    data: Optional[bytes] = None
    request_headers = dict(headers or {})
    if body is not None:
        if isinstance(body, (dict, list)):
            data = json.dumps(body).encode("utf-8")
            request_headers.setdefault("Content-Type", "application/json")
        else:
            data = str(body).encode("utf-8")

    request = urllib.request.Request(  # noqa: S310 - http(s) URLs are expected
        url, data=data, headers=request_headers, method=method.upper()
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
        payload = response.read()
        return f"{response.status} {len(payload)} bytes"


@registry.register("webhook")
def webhook_action(
    context: ActionContext,
    url: str,
    payload: Optional[dict[str, Any]] = None,
    **_: Any,
) -> str:
    """POST a JSON *payload* to *url*. Handy for Slack/Telegram webhooks."""
    return http_action(
        context,
        url=url,
        method="POST",
        body=payload or {},
    )
