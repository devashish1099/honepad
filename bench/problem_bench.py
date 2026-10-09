#!/usr/bin/env python3
"""Quality benchmark for Honepad problem packs (Java).

Scores a problem on four things and prints a report:

  gates       structure, schema, registration, level progression, spec/solution
              agreement, reference solution passes, stub fails
  strength    mutation score: small bugs are injected into the reference
              solution and the tests must catch them
  difficulty  size and branching of the reference solution, spec length
  novelty     how much the API overlaps with every other problem

Stdlib only. Needs `javac` and `java` on PATH. Run from the repo root:

    python3 bench/problem_bench.py                  # every problem
    python3 bench/problem_bench.py parking_lot      # one problem
    python3 bench/problem_bench.py --calibrate      # rewrite bench/baseline.json
    python3 bench/problem_bench.py new_one --harder # also require above-baseline difficulty

Exit code 0 when every checked problem is accepted, 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import zlib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

LEVELS = (1, 2, 3, 4)
RUN_TIMEOUT_S = 20
COMPILE_TIMEOUT_S = 120
SNAKE = re.compile(r"^[a-z][a-z0-9]*(_[a-z0-9]+)*$")
BASELINE_FILE = "baseline.json"

# Bars a problem must clear. --calibrate replaces the ones marked (calibrated)
# with values measured on the baseline problems.
DEFAULT_BARS = {
    "min_kill_all": 0.80,  # (calibrated) mutants caught by public + hidden tests
    "min_kill_public": 0.60,  # (calibrated) mutants caught by public tests alone
    "max_stub_pass": 0.25,  # share of cases the untouched stub may pass
    "max_api_overlap": 0.50,  # Jaccard overlap of method names with any other problem
    "min_cases_per_level": 3,  # public cases in each level
    "min_hidden_calls_per_level": 6,
    "harder_min_decisions": 0,  # (calibrated) --harder: branching of the solution
    "harder_min_code_lines": 0,  # (calibrated) --harder: size of the solution
    "legacy_spec_examples": [],  # (calibrated) shipped problems with fragment-style examples
}


# --------------------------------------------------------------------------
# Loading
# --------------------------------------------------------------------------


def camel(snake: str) -> str:
    parts = snake.split("_")
    return parts[0] + "".join(p.title() for p in parts[1:])


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


class Pack:
    def __init__(self, root: Path, problem: str) -> None:
        self.root = root
        self.problem = problem
        self.dir = root / "problems" / problem
        self.java = root / "langs" / "java" / "problems" / problem
        self.public: dict[int, list[dict[str, Any]]] = {}
        self.hidden: dict[int, list[dict[str, Any]]] = {}
        self.spec: dict[int, str] = {}
        self.solution = ""
        self.stub = ""
        self.load_errors: list[str] = []
        for level in LEVELS:
            for kind, store in (("cases", self.public), ("hidden", self.hidden)):
                path = self.dir / kind / f"level{level}.json"
                try:
                    data = read_json(path)
                    if not isinstance(data, list):
                        raise ValueError("must be a JSON list")
                    store[level] = data
                except (OSError, ValueError) as exc:
                    self.load_errors.append(f"{kind}/level{level}.json: {exc}")
                    store[level] = []
            path = self.dir / "spec" / f"level{level}.md"
            try:
                self.spec[level] = path.read_text(encoding="utf-8")
            except OSError as exc:
                self.load_errors.append(f"spec/level{level}.md: {exc}")
                self.spec[level] = ""
        for name in ("solution", "stub"):
            path = self.java / f"{name}.java"
            try:
                setattr(self, name, path.read_text(encoding="utf-8"))
            except OSError as exc:
                self.load_errors.append(f"langs/java/problems/{problem}/{name}.java: {exc}")

    @property
    def class_name(self) -> str:
        found = re.search(r"public\s+(?:final\s+)?class\s+([A-Za-z_]\w*)", self.solution)
        return found.group(1) if found else "Simulation"

    def all_cases(self, kind: str) -> list[dict[str, Any]]:
        store = self.public if kind == "public" else self.hidden
        return [case for level in LEVELS for case in store[level]]

    def methods_at(self, level: int, store: dict[int, list[dict[str, Any]]]) -> set[str]:
        return {
            str(call.get("m"))
            for case in store[level]
            if isinstance(case, dict)
            for call in case.get("calls", [])
            if isinstance(call, dict)
        }


# --------------------------------------------------------------------------
# Java harness
# --------------------------------------------------------------------------


def clean_env() -> dict[str, str]:
    env = os.environ.copy()
    env.pop("JAVA_TOOL_OPTIONS", None)
    return env


class Harness:
    """Compile the Honepad Java adapter once, then run candidate sources against cases."""

    def __init__(self, root: Path) -> None:
        self.pack = root / "langs" / "java"
        self.tmp = Path(tempfile.mkdtemp(prefix="honepad-bench-"))
        self.adapter = self.tmp / "adapter"
        self.adapter.mkdir()
        proc = subprocess.run(
            [
                "javac",
                "-nowarn",
                "-d",
                str(self.adapter),
                str(self.pack / "Adapter.java"),
                str(self.pack / "MiniJson.java"),
            ],
            capture_output=True,
            text=True,
            timeout=COMPILE_TIMEOUT_S,
            env=clean_env(),
        )
        if proc.returncode != 0:
            raise RuntimeError(f"adapter did not compile: {proc.stderr[:400]}")
        self._n = 0

    def close(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run(self, source: str, class_name: str, cases: list[dict[str, Any]]) -> dict[str, Any]:
        """Return {compiled, timeout, failed: {case id, ...}, error}."""
        self._n += 1
        work = self.tmp / f"run{self._n}-{zlib.crc32(source.encode()):08x}"
        work.mkdir()
        try:
            (work / f"{class_name}.java").write_text(source, encoding="utf-8")
            (work / "cases.json").write_text(json.dumps(cases), encoding="utf-8")
            try:
                comp = subprocess.run(
                    [
                        "javac",
                        "-nowarn",
                        "-cp",
                        str(self.adapter),
                        "-d",
                        str(work),
                        str(work / f"{class_name}.java"),
                    ],
                    capture_output=True,
                    text=True,
                    timeout=COMPILE_TIMEOUT_S,
                    env=clean_env(),
                )
            except subprocess.TimeoutExpired:
                return {"compiled": False, "timeout": True, "failed": set(), "error": "javac timeout"}
            if comp.returncode != 0:
                return {
                    "compiled": False,
                    "timeout": False,
                    "failed": set(),
                    "error": comp.stderr.strip()[:600],
                }
            try:
                proc = subprocess.run(
                    [
                        "java",
                        "--add-opens",
                        "java.base/java.io=ALL-UNNAMED",
                        "-cp",
                        f"{work}{os.pathsep}{self.adapter}",
                        "Adapter",
                        str(work / "cases.json"),
                        class_name,
                    ],
                    capture_output=True,
                    text=True,
                    timeout=RUN_TIMEOUT_S,
                    env=clean_env(),
                )
            except subprocess.TimeoutExpired:
                return {
                    "compiled": True,
                    "timeout": True,
                    "failed": {c["id"] for c in cases},
                    "error": "run timeout",
                }
            report = None
            for line in reversed(proc.stdout.strip().splitlines()):
                try:
                    parsed = json.loads(line)
                except ValueError:
                    continue
                if isinstance(parsed, dict) and "failed" in parsed:
                    report = parsed
                    break
            if report is None:
                # Crashed before reporting (bad cast, stack overflow, System.exit).
                return {
                    "compiled": True,
                    "timeout": False,
                    "failed": {c["id"] for c in cases},
                    "error": (proc.stderr.strip() or "no report")[:600],
                    "rows": [],
                }
            return {
                "compiled": True,
                "timeout": False,
                "failed": {str(row["case"]) for row in report["failed"]},
                "error": "",
                "rows": report["failed"],
            }
        finally:
            shutil.rmtree(work, ignore_errors=True)


def tagged_cases(pack: Pack) -> list[dict[str, Any]]:
    """Every public and hidden case with an id that says where it came from."""
    out = []
    for kind, store in (("pub", pack.public), ("hid", pack.hidden)):
        for level in LEVELS:
            for i, case in enumerate(store[level]):
                out.append(
                    {"id": f"{kind}:{level}:{i}:{case.get('id')}", "calls": case.get("calls", [])}
                )
    return out


# --------------------------------------------------------------------------
# Gates
# --------------------------------------------------------------------------


def java_value_ok(value: Any) -> bool:
    """Values the Java JUnit generator can emit: null, bool, int, str, flat/nested lists."""
    if value is None or isinstance(value, (bool, int, str)):
        return True
    if isinstance(value, list):
        return all(java_value_ok(item) for item in value)
    return False


def check_schema(pack: Pack) -> list[str]:
    problems: list[str] = []
    seen: set[str] = set()
    for kind, store in (("cases", pack.public), ("hidden", pack.hidden)):
        for level in LEVELS:
            for case in store[level]:
                where = f"{kind}/level{level}.json"
                if not isinstance(case, dict) or not isinstance(case.get("calls"), list):
                    problems.append(f"{where}: case is not an object with calls")
                    continue
                cid = str(case.get("id", ""))
                if not cid:
                    problems.append(f"{where}: case without id")
                if (kind, cid) in seen:
                    problems.append(f"{where}: duplicate id {cid}")
                seen.add((kind, cid))
                if case.get("level") != level:
                    problems.append(f"{where}: {cid} says level {case.get('level')}")
                if not case["calls"]:
                    problems.append(f"{where}: {cid} has no calls")
                for call in case["calls"]:
                    if not isinstance(call, dict) or set(call) != {"m", "a", "e"}:
                        problems.append(f"{where}: {cid} call must have exactly m, a, e")
                        continue
                    if not SNAKE.match(str(call["m"])):
                        problems.append(f"{where}: {cid} method {call['m']!r} is not snake_case")
                    if not isinstance(call["a"], list) or not java_value_ok(call["a"]):
                        problems.append(f"{where}: {cid} {call['m']} has unsupported argument")
                    if None in call["a"]:
                        problems.append(f"{where}: {cid} {call['m']} passes null as an argument")
                    if not java_value_ok(call["e"]):
                        problems.append(f"{where}: {cid} {call['m']} expects an unsupported type")
    return problems


def check_registration(pack: Pack) -> list[str]:
    problems = []
    try:
        catalog = read_json(pack.root / "langs" / "catalog.json")
        if pack.problem not in catalog.get("problems", []):
            problems.append('not listed in langs/catalog.json "problems"')
    except (OSError, ValueError) as exc:
        problems.append(f"langs/catalog.json unreadable: {exc}")
    try:
        text = (pack.root / "src" / "honepad" / "workstub.py").read_text(encoding="utf-8")
        found = re.search(rf'"{re.escape(pack.problem)}"\s*:\s*"(\w+)"', text)
        if not found:
            problems.append("no class entry in src/honepad/workstub.py _CLASS")
        elif found.group(1) != pack.class_name:
            problems.append(f"_CLASS says {found.group(1)}, solution declares {pack.class_name}")
    except OSError as exc:
        problems.append(f"workstub.py unreadable: {exc}")
    return problems


def check_progression(pack: Pack) -> tuple[list[str], dict[int, list[str]]]:
    problems = []
    known: set[str] = set()
    new_by_level: dict[int, list[str]] = {}
    for level in LEVELS:
        here = pack.methods_at(level, pack.public)
        fresh = sorted(here - known)
        new_by_level[level] = fresh
        if not fresh:
            problems.append(f"level {level} public cases introduce no new method")
        known |= here
        extra = pack.methods_at(level, pack.hidden) - known
        if extra:
            problems.append(
                f"hidden level {level} calls {sorted(extra)} that no public case has unlocked"
            )
        for name in fresh:
            if not re.search(rf"\b{re.escape(name)}\b", pack.spec[level]):
                problems.append(f"spec/level{level}.md never mentions new method {name}")
    return problems, new_by_level


def check_sources(pack: Pack, methods: set[str]) -> tuple[list[str], list[str]]:
    problems, warnings = [], []
    for kind in ("solution", "stub"):
        text = getattr(pack, kind)
        for name in sorted(methods):
            if not re.search(rf"\bpublic\s+[\w<>\[\], ?]+\s+{re.escape(camel(name))}\s*\(", text):
                problems.append(f"{kind}.java has no public method {camel(name)}")
    for name in sorted(methods):
        found = re.search(
            rf"\bpublic\s+([\w<>\[\], ?]+?)\s+{re.escape(camel(name))}\s*\(", pack.solution
        )
        if found and re.search(r"\b(long|Long|double|Double|float|Float|Map|Set)\b", found.group(1)):
            warnings.append(
                f"{camel(name)} returns {found.group(1).strip()}: the generated JUnit "
                "assertEquals may not match int or List literals"
            )
    if re.search(r"\b(Random|currentTimeMillis|nanoTime|LocalDate|Instant)\b", pack.solution):
        problems.append("solution.java uses randomness or the wall clock")
    if re.search(r"\b(java\.io|java\.nio|java\.net|Runtime|ProcessBuilder|System\.exit)\b", pack.solution):
        problems.append("solution.java touches files, network, processes or System.exit")
    return problems, warnings


SPEC_LINE = re.compile(r"^\s*([a-z][a-z0-9_]*)\((.*)\)\s*->\s*(.+?)\s*$")


def spec_examples(pack: Pack) -> tuple[list[dict[str, Any]], list[str]]:
    """The example blocks of one spec file, in order, replayed on one fresh instance.

    Convention for new problems: every level spec has example lines of the form
    `method(args) -> value` that work from an empty system, top to bottom.
    """
    cases, problems = [], []
    for level in LEVELS:
        blocks = re.findall(r"```[^\n]*\n(.*?)```", pack.spec[level], re.DOTALL)
        found_any = False
        merged: list[dict[str, Any]] = []
        for block in blocks:
            calls = []
            for line in block.splitlines():
                if not line.strip():
                    continue
                match = SPEC_LINE.match(line)
                if not match:
                    calls = []
                    break
                try:
                    args = json.loads(f"[{match.group(2)}]")
                    expected = json.loads(match.group(3))
                except ValueError:
                    problems.append(f"spec/level{level}.md: cannot parse example line {line.strip()!r}")
                    calls = []
                    break
                calls.append({"m": match.group(1), "a": args, "e": expected})
            if calls:
                found_any = True
                merged.extend(calls)
        if merged:
            cases.append({"id": f"spec:{level}:0", "calls": merged})
        if not found_any:
            problems.append(f"spec/level{level}.md has no replayable example block")
    return cases, problems


def check_duplicates(pack: Pack) -> list[str]:
    problems = []
    public = {json.dumps(case.get("calls"), sort_keys=True) for case in pack.all_cases("public")}
    for case in pack.all_cases("hidden"):
        if json.dumps(case.get("calls"), sort_keys=True) in public:
            problems.append(f"hidden case {case.get('id')} repeats a public case")
    return problems


# --------------------------------------------------------------------------
# Mutation
# --------------------------------------------------------------------------


def mask(source: str) -> str:
    """Same-length copy with comments, strings and char literals blanked out."""
    out = list(source)
    i, n = 0, len(source)
    while i < n:
        two = source[i : i + 2]
        if two == "//":
            j = source.find("\n", i)
            j = n if j < 0 else j
        elif two == "/*":
            j = source.find("*/", i + 2)
            j = n if j < 0 else j + 2
        elif source[i] in "\"'":
            quote = source[i]
            j = i + 1
            while j < n and source[j] != quote:
                j += 2 if source[j] == "\\" else 1
            j = min(j + 1, n)
        else:
            i += 1
            continue
        for k in range(i, j):
            if out[k] != "\n":
                out[k] = " "
        i = j
    return "".join(out)


def _bump(match: re.Match[str]) -> str:
    return str(int(match.group(0)) + 1)


OPERATORS: list[tuple[str, str, Any]] = [
    ("boundary", r"(?<=\s)<=(?=\s)", "<"),
    ("boundary", r"(?<=\s)>=(?=\s)", ">"),
    ("boundary", r"(?<=\s)<(?=\s)", "<="),
    ("boundary", r"(?<=\s)>(?=\s)", ">="),
    ("equality", r"==", "!="),
    ("equality", r"!=", "=="),
    ("logic", r"&&", "||"),
    ("logic", r"\|\|", "&&"),
    ("arithmetic", r"(?<=\s)\+(?=\s)", "-"),
    ("arithmetic", r"(?<=\s)-(?=\s)", "+"),
    ("arithmetic", r"(?<=\s)\*(?=\s)", "/"),
    ("arithmetic", r"\+=", "-="),
    ("arithmetic", r"-=", "+="),
    ("boolean", r"\btrue\b", "false"),
    ("boolean", r"\bfalse\b", "true"),
    ("constant", r"(?<![\w.])\d+(?![\w.])", _bump),
    ("negation", r"!(?=[A-Za-z_(])", ""),
]


def mutants(source: str, limit: int, seed: str) -> list[dict[str, Any]]:
    masked = mask(source)
    sites: dict[str, list[dict[str, Any]]] = {}
    for kind, pattern, repl in OPERATORS:
        for match in re.finditer(pattern, masked):
            new = repl(match) if callable(repl) else repl
            line = source.count("\n", 0, match.start()) + 1
            sites.setdefault(kind, []).append(
                {
                    "kind": kind,
                    "line": line,
                    "change": f"{match.group(0)} -> {new or '(removed)'}",
                    "text": source.splitlines()[line - 1].strip(),
                    "source": source[: match.start()] + new + source[match.end() :],
                }
            )
    rng = random.Random(zlib.crc32(seed.encode()))
    for group in sites.values():
        rng.shuffle(group)
    picked: list[dict[str, Any]] = []
    # Round-robin across operator kinds so one kind cannot crowd out the rest.
    while len(picked) < limit and any(sites.values()):
        for kind in sorted(sites):
            if sites[kind] and len(picked) < limit:
                picked.append(sites[kind].pop())
    return picked


CACHE_FILE = ".cache.json"


def mutation_score(
    harness: Harness, pack: Pack, cases: list[dict[str, Any]], limit: int, jobs: int
) -> dict[str, Any]:
    """Cached on the solution, the cases and the mutant budget; any edit reruns it."""
    cache_path = Path(__file__).resolve().parent / CACHE_FILE
    key = f"{zlib.crc32((pack.solution + json.dumps(cases, sort_keys=True)).encode()):08x}-{limit}"
    try:
        cache = read_json(cache_path)
    except (OSError, ValueError):
        cache = {}
    if cache.get(pack.problem, {}).get("key") == key:
        return cache[pack.problem]["result"]
    result = _mutation_score(harness, pack, cases, limit, jobs)
    cache[pack.problem] = {"key": key, "result": result}
    cache_path.write_text(json.dumps(cache) + "\n", encoding="utf-8")
    return result


def _mutation_score(
    harness: Harness, pack: Pack, cases: list[dict[str, Any]], limit: int, jobs: int
) -> dict[str, Any]:
    chosen = mutants(pack.solution, limit, pack.problem)

    def one(mutant: dict[str, Any]) -> dict[str, Any]:
        result = harness.run(mutant["source"], pack.class_name, cases)
        return {**{k: mutant[k] for k in ("kind", "line", "change", "text")}, **result}

    with ThreadPoolExecutor(max_workers=jobs) as pool:
        results = list(pool.map(one, chosen))
    valid = [r for r in results if r["compiled"]]
    killed_all = [r for r in valid if r["failed"]]
    killed_public = [r for r in valid if any(cid.startswith("pub:") for cid in r["failed"])]
    survivors = [r for r in valid if not r["failed"]]
    hidden_only = len(killed_all) - len(killed_public)
    total = len(valid)
    return {
        "generated": len(chosen),
        "valid": total,
        "killed_all": len(killed_all),
        "killed_public": len(killed_public),
        "killed_by_hidden_only": hidden_only,
        "kill_all": round(len(killed_all) / total, 3) if total else 0.0,
        "kill_public": round(len(killed_public) / total, 3) if total else 0.0,
        "survivors": [
            {"line": r["line"], "kind": r["kind"], "change": r["change"], "text": r["text"]}
            for r in sorted(survivors, key=lambda r: r["line"])
        ],
    }


# --------------------------------------------------------------------------
# Difficulty and novelty
# --------------------------------------------------------------------------


def difficulty(pack: Pack, methods: set[str]) -> dict[str, Any]:
    masked = mask(pack.solution)
    code_lines = sum(1 for line in masked.splitlines() if line.strip())
    decisions = len(re.findall(r"\b(?:if|for|while|case|catch)\b|&&|\|\||\?", masked))
    return {
        "code_lines": code_lines,
        "decisions": decisions,
        "methods": len(methods),
        "spec_words": sum(len(pack.spec[level].split()) for level in LEVELS),
    }


def api_overlap(pack: Pack, others: dict[str, set[str]]) -> dict[str, Any]:
    mine = {m for level in LEVELS for m in pack.methods_at(level, pack.public)}
    best, nearest = 0.0, ""
    for name, theirs in others.items():
        if name == pack.problem or not (mine | theirs):
            continue
        score = len(mine & theirs) / len(mine | theirs)
        if score > best:
            best, nearest = score, name
    return {"max_overlap": round(best, 3), "nearest": nearest}


# --------------------------------------------------------------------------
# One problem
# --------------------------------------------------------------------------


def evaluate(
    root: Path,
    problem: str,
    harness: Harness,
    bars: dict[str, Any],
    others: dict[str, set[str]],
    mutant_limit: int,
    jobs: int,
    harder: bool,
) -> dict[str, Any]:
    pack = Pack(root, problem)
    gates: list[dict[str, Any]] = []
    warnings: list[str] = []

    def gate(name: str, issues: list[str]) -> bool:
        gates.append({"gate": name, "ok": not issues, "issues": issues[:8]})
        return not issues

    files_ok = gate("files present", pack.load_errors)
    gate("case schema", check_schema(pack))
    gate("registered", check_registration(pack))
    progression, new_by_level = check_progression(pack)
    gate("level progression", progression)
    gate("hidden differs from public", check_duplicates(pack))
    methods = {m for level in LEVELS for m in pack.methods_at(level, pack.public)}
    source_issues, source_warnings = check_sources(pack, methods)
    warnings += source_warnings
    gate("java sources", source_issues)

    volume = []
    for level in LEVELS:
        if len(pack.public[level]) < bars["min_cases_per_level"]:
            volume.append(
                f"level {level}: {len(pack.public[level])} public cases, "
                f"need {bars['min_cases_per_level']}"
            )
        hidden_calls = sum(len(case.get("calls", [])) for case in pack.hidden[level])
        if hidden_calls < bars["min_hidden_calls_per_level"]:
            volume.append(
                f"level {level}: {hidden_calls} hidden calls, "
                f"need {bars['min_hidden_calls_per_level']}"
            )
    gate("test volume", volume)

    result: dict[str, Any] = {
        "problem": problem,
        "new_methods_by_level": new_by_level,
        "cases": {
            "public": [len(pack.public[level]) for level in LEVELS],
            "hidden": [len(pack.hidden[level]) for level in LEVELS],
            "calls": sum(
                len(case.get("calls", []))
                for kind in ("public", "hidden")
                for case in pack.all_cases(kind)
            ),
        },
        "difficulty": difficulty(pack, methods),
        "novelty": api_overlap(pack, others),
    }

    if files_ok and pack.solution and pack.stub:
        cases = tagged_cases(pack)
        examples, example_issues = spec_examples(pack)
        solved = harness.run(pack.solution, pack.class_name, cases + examples)
        if not solved["compiled"]:
            gate("solution passes every case", [f"does not compile: {solved['error']}"])
        else:
            bad_cases = sorted(c for c in solved["failed"] if not c.startswith("spec:"))
            gate("solution passes every case", [f"fails {c}" for c in bad_cases])
            for row in solved.get("rows", []):
                if str(row["case"]).startswith("spec:"):
                    level = str(row["case"]).split(":")[1]
                    example_issues.append(
                        f"spec/level{level}.md example: {row['method']} call {row['index'] + 1} "
                        f"says {json.dumps(row['expected'])}, solution returns "
                        f"{json.dumps(row['actual'])}"
                    )
        if problem in bars.get("legacy_spec_examples", []):
            # Shipped before the replayable-example convention; report, do not reject.
            warnings.extend(f"(legacy spec) {issue}" for issue in example_issues[:3])
            example_issues = []
        gate("spec examples match solution", example_issues)

        stubbed = harness.run(pack.stub, pack.class_name, cases)
        if not stubbed["compiled"]:
            gate("stub compiles and fails", [f"does not compile: {stubbed['error']}"])
            result["stub_pass"] = None
        else:
            share = 1 - len(stubbed["failed"]) / len(cases) if cases else 1.0
            result["stub_pass"] = round(share, 3)
            gate(
                "stub compiles and fails",
                []
                if share <= bars["max_stub_pass"]
                else [f"untouched stub passes {share:.0%} of cases"],
            )

        if solved["compiled"] and not [c for c in solved["failed"] if not c.startswith("spec:")]:
            mutation = mutation_score(harness, pack, cases, mutant_limit, jobs)
            result["mutation"] = mutation
            strength = []
            if mutation["valid"] < 10:
                strength.append(f"only {mutation['valid']} usable mutants; solution too small")
            if mutation["kill_all"] < bars["min_kill_all"]:
                strength.append(
                    f"public+hidden catch {mutation['kill_all']:.0%} of injected bugs, "
                    f"need {bars['min_kill_all']:.0%}"
                )
            if mutation["kill_public"] < bars["min_kill_public"]:
                strength.append(
                    f"public tests alone catch {mutation['kill_public']:.0%}, "
                    f"need {bars['min_kill_public']:.0%}"
                )
            gate("test strength", strength)

    overlap = result["novelty"]
    gate(
        "novelty",
        []
        if overlap["max_overlap"] <= bars["max_api_overlap"]
        else [f"{overlap['max_overlap']:.0%} of the API overlaps with {overlap['nearest']}"],
    )

    if harder:
        diff = result["difficulty"]
        short = []
        if diff["decisions"] < bars["harder_min_decisions"]:
            short.append(
                f"{diff['decisions']} decision points, need {bars['harder_min_decisions']}"
            )
        if diff["code_lines"] < bars["harder_min_code_lines"]:
            short.append(
                f"{diff['code_lines']} solution lines, need {bars['harder_min_code_lines']}"
            )
        gate("harder than baseline", short)

    result["gates"] = gates
    result["warnings"] = warnings
    result["accepted"] = all(g["ok"] for g in gates)
    return result


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------


def pct(value: Any) -> str:
    return "-" if value is None else f"{value:.0%}"


def render(results: list[dict[str, Any]], bars: dict[str, Any], verbose: bool) -> str:
    lines = [
        "| Problem | Verdict | Bugs caught (all) | Bugs caught (public) | Stub passes | "
        "Decisions | Code lines | Cases pub/hid | API overlap |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for r in results:
        m = r.get("mutation", {})
        d = r["difficulty"]
        lines.append(
            f"| {r['problem']} | {'ACCEPT' if r['accepted'] else 'REJECT'} | "
            f"{pct(m.get('kill_all'))} ({m.get('killed_all', '-')}/{m.get('valid', '-')}) | "
            f"{pct(m.get('kill_public'))} | {pct(r.get('stub_pass'))} | {d['decisions']} | "
            f"{d['code_lines']} | {sum(r['cases']['public'])}/{sum(r['cases']['hidden'])} | "
            f"{pct(r['novelty']['max_overlap'])} |"
        )
    lines.append("")
    lines.append(
        f"Bars: bugs caught (all) >= {bars['min_kill_all']:.0%}, (public) >= "
        f"{bars['min_kill_public']:.0%}, stub passes <= {bars['max_stub_pass']:.0%}, "
        f"API overlap <= {bars['max_api_overlap']:.0%}; --harder needs decisions >= "
        f"{bars['harder_min_decisions']} and code lines >= {bars['harder_min_code_lines']}."
    )
    for r in results:
        failed = [g for g in r["gates"] if not g["ok"]]
        survivors = r.get("mutation", {}).get("survivors", [])
        if not failed and not r["warnings"] and not (verbose and survivors):
            continue
        lines.append("")
        lines.append(f"## {r['problem']}")
        for g in failed:
            lines.append(f"- FAIL {g['gate']}")
            lines.extend(f"  - {issue}" for issue in g["issues"])
        lines.extend(f"- WARN {w}" for w in r["warnings"])
        if survivors and (verbose or failed):
            lines.append(f"- {len(survivors)} injected bugs no test caught (add cases for these):")
            lines.extend(
                f"  - solution.java:{s['line']} `{s['change']}` in `{s['text'][:90]}`"
                for s in survivors[:25]
            )
    return "\n".join(lines) + "\n"


def calibrate(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Bars for new problems, taken from what the shipped problems achieve."""
    scored = [r for r in results if "mutation" in r]
    kill_all = sorted(r["mutation"]["kill_all"] for r in scored)
    kill_public = sorted(r["mutation"]["kill_public"] for r in scored)
    decisions = sorted(r["difficulty"]["decisions"] for r in results)
    code_lines = sorted(r["difficulty"]["code_lines"] for r in results)
    q3 = lambda xs: statistics.quantiles(xs, n=4)[2] if len(xs) > 1 else xs[0]  # noqa: E731
    bars = dict(DEFAULT_BARS)
    bars.update(
        {
            # A new problem must be tested at least as well as the typical shipped one.
            # Capped at 90% because some injected bugs cannot change behaviour at all.
            "min_kill_all": round(
                min(0.90, max(DEFAULT_BARS["min_kill_all"], statistics.median(kill_all))), 2
            ),
            # Public tests alone must beat the weakest quarter of shipped problems.
            "min_kill_public": round(
                max(DEFAULT_BARS["min_kill_public"], statistics.quantiles(kill_public, n=4)[0]), 2
            ),
            "legacy_spec_examples": sorted(
                r["problem"]
                for r in results
                if any(
                    g["gate"] == "spec examples match solution" and not g["ok"] for g in r["gates"]
                )
            ),
            # "Harder" means above the upper quartile of the shipped problems.
            "harder_min_decisions": int(q3(decisions)),
            "harder_min_code_lines": int(q3(code_lines)),
        }
    )
    return {
        "bars": bars,
        "baseline": {
            r["problem"]: {
                "kill_all": r.get("mutation", {}).get("kill_all"),
                "kill_public": r.get("mutation", {}).get("kill_public"),
                "stub_pass": r.get("stub_pass"),
                **r["difficulty"],
            }
            for r in results
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("problems", nargs="*", help="problem ids (default: all in the catalog)")
    parser.add_argument("--root", default=None, help="Honepad checkout (default: parent of bench/)")
    parser.add_argument("--mutants", type=int, default=40, help="injected bugs per problem")
    parser.add_argument("--jobs", type=int, default=os.cpu_count() or 2)
    parser.add_argument("--harder", action="store_true", help="require above-baseline difficulty")
    parser.add_argument("--calibrate", action="store_true", help="measure and write the baseline")
    parser.add_argument("--verbose", action="store_true", help="list uncaught bugs for every problem")
    parser.add_argument("--json", default=None, help="write full results here")
    parser.add_argument("--md", default=None, help="write the report here")
    args = parser.parse_args()

    here = Path(__file__).resolve().parent
    root = Path(args.root).resolve() if args.root else here.parent
    for tool in ("javac", "java"):
        if shutil.which(tool) is None:
            print(f"FAIL: {tool} not on PATH")
            return 2
    catalog = read_json(root / "langs" / "catalog.json")["problems"]
    on_disk = sorted(p.name for p in (root / "problems").iterdir() if p.is_dir())
    universe = list(dict.fromkeys([*catalog, *on_disk]))
    targets = args.problems or catalog
    unknown = [p for p in targets if not (root / "problems" / p).is_dir()]
    if unknown:
        print(f"FAIL: no problems/ folder for {unknown}")
        return 2

    bars = dict(DEFAULT_BARS)
    baseline_path = here / BASELINE_FILE
    if baseline_path.is_file() and not args.calibrate:
        bars.update(read_json(baseline_path)["bars"])
    elif not args.calibrate:
        print("NOTE: no bench/baseline.json; using default bars. Run --calibrate first.")

    others = {}
    for name in universe:
        pack = Pack(root, name)
        others[name] = {m for level in LEVELS for m in pack.methods_at(level, pack.public)}

    harness = Harness(root)
    results = []
    try:
        for problem in targets:
            print(f"... {problem}", file=sys.stderr, flush=True)
            results.append(
                evaluate(
                    root, problem, harness, bars, others, args.mutants, args.jobs, args.harder
                )
            )
    finally:
        harness.close()

    if args.calibrate:
        payload = calibrate(results)
        baseline_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        bars = payload["bars"]
        print(f"wrote {baseline_path}")
    report = render(results, bars, args.verbose)
    print(report)
    if args.md:
        Path(args.md).write_text(report, encoding="utf-8")
    if args.json:
        Path(args.json).write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    return 0 if all(r["accepted"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
