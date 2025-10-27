#!/usr/bin/env python3
"""Small terminal styling helpers (ANSI) with TTY detection and fallback."""

from __future__ import annotations

import os
import sys


def _enabled() -> bool:
    if os.environ.get("NO_COLOR") is not None:
        return False
    try:
        return sys.stdout.isatty()
    except Exception:
        return False


_ENABLED = _enabled()

ANSI = {
    "reset": "\x1b[0m",
    "bold": "\x1b[1m",
    "red": "\x1b[31m",
    "green": "\x1b[32m",
    "yellow": "\x1b[33m",
    "blue": "\x1b[34m",
    "magenta": "\x1b[35m",
    "cyan": "\x1b[36m",
    "grey": "\x1b[90m",
}


def stylize(text: str, color: str | None = None, bold: bool = False) -> str:
    if not _ENABLED or not color:
        return text
    seq = ""
    if bold:
        seq += ANSI["bold"]
    seq += ANSI.get(color, "")
    return f"{seq}{text}{ANSI['reset']}"


def header(text: str) -> str:
    return stylize(text, "cyan", bold=True)


def action(text: str) -> str:
    return stylize(text, "green")


def note(text: str) -> str:
    return stylize(text, "yellow")


def warn(text: str) -> str:
    return stylize(text, "red")


def meta(text: str) -> str:
    return stylize(text, "grey")
