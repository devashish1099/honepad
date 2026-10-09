#!/usr/bin/env python3
"""Register a new problem with Honepad so `honepad start <id> java` finds it.

Adds the id to langs/catalog.json and to the class table in
src/honepad/workstub.py. Safe to run twice. Run from the repo root:

    python3 bench/register_problem.py order_book
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    for problem in sys.argv[1:]:
        solution = ROOT / "langs" / "java" / "problems" / problem / "solution.java"
        if not (ROOT / "problems" / problem).is_dir() or not solution.is_file():
            print(f"FAIL: {problem}: problems/{problem}/ or its Java solution is missing")
            return 1
        found = re.search(r"public\s+class\s+(\w+)", solution.read_text(encoding="utf-8"))
        class_name = found.group(1) if found else "Simulation"

        catalog_path = ROOT / "langs" / "catalog.json"
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        if problem not in catalog["problems"]:
            catalog["problems"].append(problem)
            catalog_path.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
            print(f"OK: {problem} added to langs/catalog.json")

        stub_path = ROOT / "src" / "honepad" / "workstub.py"
        text = stub_path.read_text(encoding="utf-8")
        if f'"{problem}":' not in text:
            table = re.search(r"_CLASS = \{\n(.*?)\n\}", text, re.DOTALL)
            if table is None:
                print("FAIL: cannot find _CLASS in src/honepad/workstub.py; add the entry by hand")
                return 1
            entry = f'\n    "{problem}": "{class_name}",'
            text = text[: table.end(1)] + entry + text[table.end(1) :]
            stub_path.write_text(text, encoding="utf-8")
            print(f"OK: {problem} -> {class_name} added to src/honepad/workstub.py")
        print(f"DONE: {problem} registered")
    return 0


if __name__ == "__main__":
    sys.exit(main())
