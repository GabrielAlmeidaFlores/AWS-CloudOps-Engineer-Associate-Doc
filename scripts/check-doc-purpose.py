#!/usr/bin/env python3
"""Flag documentation whose first block after the H1 is not a purpose paragraph.

The rule is defined in AGENTS.md section 29. The root README is exempt because
its purpose sits in the "What this is" section below the centered title block.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXEMPT = {"AGENTS.md", "README.md"}
MIN_LEN = 120
SIGNALS = (
    "This document",
    "This file",
    "This page",
    "This folder",
    "This set",
    "This project",
    "This README",
    "This guide",
)


def first_block(lines, start):
    i = start
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    if i >= len(lines):
        return None, i
    if lines[i].startswith(("##", ">", "```", "|")):
        return None, i
    if re.match(r"^(?:[-*+]|\d+\.)\s", lines[i]):
        return None, i
    j = i
    while j < len(lines) and lines[j].strip() != "":
        j += 1
    return "\n".join(lines[i:j]).strip(), i


def main():
    problems = []
    for path in sorted(ROOT.rglob("*.md")):
        rel = path.relative_to(ROOT).as_posix()
        if rel in EXEMPT or "node_modules" in rel:
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        h1 = next((i for i, line in enumerate(lines) if re.match(r"^# ", line)), None)
        if h1 is None:
            problems.append((rel, "no H1"))
            continue
        block, _ = first_block(lines, h1 + 1)
        if block is None:
            problems.append((rel, "first block is not a paragraph"))
        elif len(block) < MIN_LEN:
            problems.append((rel, f"purpose paragraph is shorter than {MIN_LEN} characters"))
        elif not any(signal in block for signal in SIGNALS):
            problems.append((rel, "purpose paragraph does not say what the file is"))

    if problems:
        print(f"{len(problems)} document(s) need a purpose paragraph:")
        for rel, reason in problems:
            print(f"  {rel}: {reason}")
        return 1
    print("All documents open with a purpose paragraph.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
