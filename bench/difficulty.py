"""Score every problem's difficulty and store it in langs/catalog.json.

The score (0-100) ranks each problem against the others on three things:
branching in the Java reference solution (40%), its size (40%) and the
length of the four level specs (20%). `honepad web` sorts the problem
list by it and labels each one Easy, Medium or Hard.

    python3 bench/difficulty.py          # print the table
    python3 bench/difficulty.py --write  # also update langs/catalog.json

Run it with --write after registering a new problem.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from problem_bench import mask  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "langs" / "catalog.json"
DECISION = re.compile(r"\b(?:if|for|while|case|catch)\b|&&|\|\||\?")


def metrics(problem: str) -> dict[str, int]:
    solution = ROOT / "langs" / "java" / "problems" / problem / "solution.java"
    masked = mask(solution.read_text(encoding="utf-8"))
    specs = sorted((ROOT / "problems" / problem / "spec").glob("level*.md"))
    return {
        "lines": sum(1 for line in masked.splitlines() if line.strip()),
        "decisions": len(DECISION.findall(masked)),
        "words": sum(len(path.read_text(encoding="utf-8").split()) for path in specs),
    }


def scores(problems: list[str]) -> tuple[dict[str, int], dict[str, dict[str, int]]]:
    rows = {p: metrics(p) for p in problems}
    span = max(len(rows) - 1, 1)

    def rank(key: str) -> dict[str, float]:
        values = [row[key] for row in rows.values()]
        return {p: sum(v < row[key] for v in values) / span for p, row in rows.items()}

    lines, decisions, words = rank("lines"), rank("decisions"), rank("words")
    score = {p: round(100 * (0.4 * decisions[p] + 0.4 * lines[p] + 0.2 * words[p])) for p in rows}
    return score, rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true", help="update langs/catalog.json")
    args = parser.parse_args()
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    score, rows = scores(list(catalog["problems"]))
    for p in sorted(score, key=score.get):
        r = rows[p]
        print(
            f"{p:20} score={score[p]:3} decisions={r['decisions']:3} "
            f"lines={r['lines']:4} spec_words={r['words']:5}"
        )
    if args.write:
        catalog["difficulty"] = {p: score[p] for p in catalog["problems"]}
        CATALOG.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
        print(f"OK: wrote difficulty for {len(score)} problems to {CATALOG.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
