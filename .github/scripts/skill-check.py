#!/usr/bin/env python3
"""Fail a pull request when a changed skill file is missing required fields."""

from __future__ import annotations

import os
import re
import subprocess
import sys

VERSION_RE = re.compile(r"^Version:\s+\S.*$", re.MULTILINE)
CHANGELOG_RE = re.compile(r"^## Change log\s*$", re.MULTILINE)
NAME_RE = re.compile(r"^name:[ \t]*\S", re.MULTILINE)
DESC_RE = re.compile(r"^description:[ \t]*\S", re.MULTILINE)


def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], capture_output=True, text=True)


def changed_skill_files(base_sha: str, head_sha: str) -> list[str]:
    result = git("diff", "--name-only", "--diff-filter=ACMR", base_sha, head_sha)
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        raise SystemExit(2)
    files = []
    for path in result.stdout.splitlines():
        if path.startswith(".apm/skills/") and path.endswith("/SKILL.md"):
            files.append(path)
    return files


def read_at(ref: str, path: str) -> str | None:
    result = git("show", f"{ref}:{path}")
    if result.returncode != 0:
        return None
    return result.stdout


def check_frontmatter(text: str) -> str | None:
    if not text.startswith("---"):
        return "missing YAML frontmatter"
    parts = text.split("---", 2)
    if len(parts) < 3:
        return "YAML frontmatter is not closed"
    frontmatter = parts[1]
    if not NAME_RE.search(frontmatter):
        return "YAML frontmatter is missing a name"
    if not DESC_RE.search(frontmatter):
        return "YAML frontmatter is missing a description"
    return None


def version_line(text: str) -> str | None:
    match = VERSION_RE.search(text)
    return match.group(0).strip() if match else None


def main() -> int:
    base_sha = os.environ.get("BASE_SHA", "").strip()
    head_sha = os.environ.get("HEAD_SHA", "").strip()
    if not base_sha or not head_sha:
        print("BASE_SHA and HEAD_SHA must be set", file=sys.stderr)
        return 2

    paths = changed_skill_files(base_sha, head_sha)
    if not paths:
        print("No skill files changed; skill-check passed.")
        return 0

    errors: list[str] = []
    for path in paths:
        new_text = read_at(head_sha, path)
        if new_text is None:
            errors.append(f"{path}: could not read the file on the pull request head")
            continue

        problem = check_frontmatter(new_text)
        if problem:
            errors.append(f"{path}: {problem}")

        new_version = version_line(new_text)
        if not new_version:
            errors.append(f"{path}: missing a Version: line")

        if not CHANGELOG_RE.search(new_text):
            errors.append(f"{path}: missing a ## Change log section")

        old_text = read_at(base_sha, path)
        if old_text is None:
            print(f"{path}: new skill file")
            continue
        old_version = version_line(old_text)
        if new_version and old_version == new_version:
            errors.append(
                f"{path}: Version line did not change versus the base branch ({new_version})"
            )

    if errors:
        print("skill-check failed:")
        for item in errors:
            print(f"- {item}")
        return 1

    print("skill-check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
