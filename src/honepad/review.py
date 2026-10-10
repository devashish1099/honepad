"""Review pack: one markdown file with everything a reviewer needs.

The file is written for a human-in-the-loop review in claude.ai or ChatGPT,
or for `claude -p` from the web UI. Hidden traces are only spelled out once
the attempt is over (final submit, cleared, or out of time).
"""

from __future__ import annotations

import json
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

from honepad.catalog import language
from honepad.runner import run
from honepad.session import (
    attempt_over,
    clock_left,
    is_ended,
    is_paused,
    max_level,
    session_path,
    work_src,
)
from honepad.term import HONEPAD_ERRORS
from honepad.traces import load_cases, load_hidden_cases, method_name, problem_dir

CLAUDE_TIMEOUT_S = 300

BRIEF = """\
You are reviewing a practice attempt at a CodeSignal Industry Coding Assessment (ICA).
The real test is one class built up over 4 levels in about 90 minutes; each level adds
methods and the code from earlier levels must keep working. Grading is by hidden tests.

Please review the attempt below and give:

1. **Correctness**: explain each failing case (why the code returns what it does, and the
   spec rule it breaks). Point to the exact lines.
2. **Missed edge cases** that the visible tests did not catch.
3. **Code structure and readability** as an ICA grader would see it: data structures,
   naming, duplication, method size.
4. **Extensibility**: would this design survive the next level? What would make it easier?
5. **Time management**, given the level reached and the time used.
6. **One concrete refactor**, shown as a short before/after snippet.
7. **What to practise next** (2-3 bullets).

Be specific and kind. Do not rewrite the whole solution; small targeted snippets only.
"""

_CLAUDE_INSTRUCTION = (
    "Review the CodeSignal ICA practice attempt on stdin. Follow the reviewer brief at the "
    "top of it. Answer in markdown."
)


def _fmt_value(value: Any) -> str:
    return json.dumps(value)


def _fmt_call(method: str, args: list[Any]) -> str:
    return f"{method}({', '.join(_fmt_value(a) for a in args)})"


def _case_block(case: dict[str, Any], fail: Any | None, naming: str) -> list[str]:
    lines = [f"Case `{case['id']}` (level {case.get('level', '?')}):", "```"]
    for i, call in enumerate(case["calls"]):
        shown = _fmt_call(method_name(str(call["m"]), naming), list(call["a"]))
        if fail is not None and i == fail.index:
            actual = fail.actual
            if isinstance(actual, str) and actual.startswith("exc:"):
                got = f"threw {actual[4:]}"
            else:
                got = f"returned {_fmt_value(actual)}"
            lines.append(f"{shown} -> expected {_fmt_value(call['e'])}   <-- {got}")
            if i + 1 < len(case["calls"]):
                lines.append(f"... {len(case['calls']) - i - 1} more calls not run")
            break
        lines.append(f"{shown} -> {_fmt_value(call['e'])}")
    lines.append("```")
    return lines


def _results(
    title: str,
    problem: str,
    lang: str,
    level: int,
    cases: list[dict[str, Any]],
    naming: str,
    *,
    detail: bool,
) -> tuple[list[str], dict[str, Any]]:
    out = [f"## {title}", ""]
    if not cases:
        out += ["(none for this level)", ""]
        return out, {"passed": 0, "total": 0}
    try:
        report = run(problem, lang, level, kind="work", cases=cases)
    except HONEPAD_ERRORS + (NotImplementedError,) as exc:
        out += [
            "The code did not compile or crashed before any case ran:",
            "```",
            str(exc),
            "```",
            "",
        ]
        return out, {"passed": 0, "total": len(cases), "error": str(exc)}
    total = report.passed + len(report.failed)
    out.append(f"Passed {report.passed} of {total} cases through level {level}.")
    out.append("")
    if report.failed and detail:
        by_id = {str(case["id"]): case for case in cases}
        for fail in report.failed:
            case = by_id.get(str(fail.case))
            if case is not None:
                out += _case_block(case, fail, naming)
                out.append("")
    elif report.failed:
        out += ["(hidden cases withheld until the attempt is finished)", ""]
    if report.debug.strip():
        out += ["Debug output:", "```", report.debug.strip(), "```", ""]
    return out, {"passed": report.passed, "total": total}


def build_review(session: dict[str, Any], now: int | None = None) -> tuple[str, dict[str, Any]]:
    problem = str(session["problem"])
    lang = str(session["lang"])
    unlocked = int(session["unlocked"])
    top = max_level(problem)
    minutes = int(session["minutes"])
    left = clock_left(session, now)
    used = minutes * 60 - left
    cleared = bool(session.get("cleared"))
    finished = attempt_over(session, now)
    row = language(lang)
    naming = str(row["naming"])
    fence = "python" if row["ext"] == "py" else str(row["ext"])

    lines = [f"# Review request: {problem} ({row.get('name', lang)})", "", BRIEF, "## Attempt"]
    lines += [
        f"- Problem: `{problem}`, language: {row.get('name', lang)}",
        f"- Level reached: {unlocked} of {top}" + (" (all levels cleared)" if cleared else ""),
        f"- Time used: {used // 60}m {used % 60}s of {minutes}m"
        + (" (clock ran out)" if left == 0 and not cleared else ""),
        "- Status: "
        + ("finished" if finished else "in progress")
        + (" (final submit)" if is_ended(session) else "")
        + (", clock paused" if is_paused(session) else ""),
    ]
    if naming != "snake":
        lines.append(
            "- The spec names methods in snake_case; in this language they are "
            f"`{method_name('create_account', naming)}`-style (`create_account` in the spec)."
        )
    lines.append("")

    lines.append("## Specification (levels reached)")
    lines.append("")
    for level in range(1, unlocked + 1):
        path = problem_dir(problem) / "spec" / f"level{level}.md"
        if path.is_file():
            text = path.read_text(encoding="utf-8").strip()
            # Nest the spec's own headings under this section.
            lines += ["##" + ln if ln.startswith("#") else ln for ln in text.splitlines()]
            lines.append("")

    lines += ["## The candidate's code", ""]
    work = work_src(problem, lang)
    if work.is_file() and not work.is_symlink():
        lines += [f"```{fence}", work.read_text(encoding="utf-8").rstrip(), "```", ""]
    else:
        lines += ["(work file missing)", ""]

    public, pub_meta = _results(
        "Public test results",
        problem,
        lang,
        unlocked,
        load_cases(problem, unlocked),
        naming,
        detail=True,
    )
    lines += public
    hidden, hid_meta = _results(
        "Hidden test results",
        problem,
        lang,
        unlocked,
        load_hidden_cases(problem, unlocked),
        naming,
        detail=finished,
    )
    lines += hidden
    meta = {
        "problem": problem,
        "lang": lang,
        "level": unlocked,
        "finished": finished,
        "public": pub_meta,
        "hidden": hid_meta,
    }
    return "\n".join(lines).rstrip() + "\n", meta


def save_review(markdown: str, session: dict[str, Any]) -> Path:
    folder = session_path().parent / "reviews"
    folder.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    name = f"{session['problem']}-{session['lang']}-L{session['unlocked']}-{stamp}.md"
    path = folder / name
    path.write_text(markdown, encoding="utf-8")
    return path


def claude_available() -> bool:
    return shutil.which("claude") is not None


def ask_claude(markdown: str) -> str:
    """Text-only review from the local Claude Code CLI. No tools are enabled."""
    exe = shutil.which("claude")
    if exe is None:
        raise RuntimeError("Claude Code (`claude`) is not on PATH")
    workdir = session_path().parent
    workdir.mkdir(parents=True, exist_ok=True)
    try:
        proc = subprocess.run(
            [exe, "-p", _CLAUDE_INSTRUCTION, "--tools", ""],
            input=markdown,
            capture_output=True,
            text=True,
            timeout=CLAUDE_TIMEOUT_S,
            cwd=str(workdir),
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"Claude Code did not answer within {CLAUDE_TIMEOUT_S}s") from exc
    if proc.returncode != 0 or not proc.stdout.strip():
        detail = (proc.stderr or proc.stdout or "").strip() or f"exit {proc.returncode}"
        raise RuntimeError(f"Claude Code failed: {detail}")
    return proc.stdout.strip()
