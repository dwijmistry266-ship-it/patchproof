from __future__ import annotations

import subprocess
import time
from typing import Any

from .models import CommandResult


def run_commands(commands: list[dict[str, Any]], *, timeout_seconds: int, max_output_bytes: int, cwd: str | None = None) -> tuple[CommandResult, ...]:
    results: list[CommandResult] = []
    for item in commands:
        name = item["name"]
        command = tuple(item["command"])
        started = time.perf_counter()
        timed_out = False
        exit_code: int | None = None
        try:
            completed = subprocess.run(
                list(command),
                cwd=cwd,
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=timeout_seconds,
                check=False,
            )
            exit_code = completed.returncode
            raw_output = completed.stdout[:max_output_bytes]
            truncated = len(completed.stdout) > max_output_bytes
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            raw_output = (exc.stdout or b"")[:max_output_bytes]
            truncated = bool(exc.stdout and len(exc.stdout) > max_output_bytes)
        except OSError as exc:
            raw_output = str(exc).encode("utf-8", errors="replace")[:max_output_bytes]
            truncated = False
            exit_code = 127
        duration_ms = int((time.perf_counter() - started) * 1000)
        output = raw_output.decode("utf-8", errors="replace")
        if truncated:
            output += "\n[output truncated by PatchProof]"
        if timed_out:
            output += "\n[command timed out by PatchProof]"
        results.append(CommandResult(name, command, exit_code, duration_ms, timed_out, output, truncated))
    return tuple(results)
