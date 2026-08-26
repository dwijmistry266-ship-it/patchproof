from __future__ import annotations

import subprocess
from pathlib import Path


class GitError(ValueError):
    """Raised when a repository or revision cannot be used safely."""


def _run_git(repository: Path, arguments: list[str], timeout_seconds: int) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["git", "-C", str(repository), "-c", "color.ui=false", *arguments],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
            check=False,
        )
    except FileNotFoundError as exc:
        raise GitError("git executable was not found") from exc
    except subprocess.TimeoutExpired as exc:
        raise GitError(f"git command timed out after {timeout_seconds} seconds") from exc
    except OSError as exc:
        raise GitError(f"could not run git: {exc}") from exc


def _check_repository(repository: Path, timeout_seconds: int) -> None:
    if not repository.exists():
        raise GitError(f"repository path does not exist: {repository}")
    if not repository.is_dir():
        raise GitError(f"repository path is not a directory: {repository}")
    result = _run_git(repository, ["rev-parse", "--is-inside-work-tree"], timeout_seconds)
    if result.returncode != 0 or result.stdout.strip() != "true":
        message = result.stderr.strip() or "path is not inside a Git work tree"
        raise GitError(f"not inside a Git work tree: {message}")


def _verify_revision(repository: Path, revision: str, timeout_seconds: int) -> str:
    revision = revision.strip()
    if not revision or revision.startswith("-") or any(char.isspace() for char in revision):
        raise GitError("revision must be non-empty, must not start with '-', and must not contain whitespace")
    result = _run_git(repository, ["rev-parse", "--verify", "--end-of-options", f"{revision}^{{commit}}"], timeout_seconds)
    if result.returncode != 0:
        message = result.stderr.strip() or "revision not found"
        raise GitError(f"revision not found or invalid: {revision}: {message}")
    return result.stdout.strip()


def get_unified_diff(repository: Path, base: str, head: str, *, timeout_seconds: int = 30) -> str:
    """Return the binary-aware diff between two verified commit-ish revisions."""
    _check_repository(repository, timeout_seconds)
    verified_base = _verify_revision(repository, base, timeout_seconds)
    verified_head = _verify_revision(repository, head, timeout_seconds)
    result = _run_git(
        repository,
        ["diff", "--no-ext-diff", "--binary", verified_base, verified_head, "--"],
        timeout_seconds,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or "git diff failed"
        raise GitError(message)
    return result.stdout
