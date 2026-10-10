"""Local browser UI: pick a problem, read the spec, edit, run, submit, pause,
finish, then look back over every level and the reference solution.

Every action shells out to the same CLI the terminal uses, so grading,
unlocks, hidden traces and the pause rule behave identically. The server
binds 127.0.0.1 only and every API call must carry the per-launch token.
"""

from __future__ import annotations

import json
import os
import platform
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from honepad import packspec, review
from honepad.catalog import language, load_catalog, problems, repo_root
from honepad.runner import run, spec_src
from honepad.session import (
    _replace_text,
    attempt_over,
    clock_left,
    end_attempt,
    is_ended,
    is_paused,
    load_session,
    max_level,
    session_path,
    work_src,
)
from honepad.term import HONEPAD_ERRORS
from honepad.traces import load_cases, load_hidden_cases, method_name, problem_dir

MAX_BODY = 1_000_000
ACTION_TIMEOUT_S = 600
_ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]|\x1b\]8;;[^\x1b]*\x1b\\")
_PAGE = Path(__file__).resolve().parent / "static" / "web.html"
# Last public-trace report per (problem, lang), so the Tests tab survives a reload.
_LAST_REPORTS: dict[tuple[str, str, str], dict[str, Any]] = {}
_NOT_OVER = {"error": "finish the attempt first (Final Submit)"}


def _report_key(problem: str, lang: str) -> tuple[str, str, str]:
    return (str(session_path()), problem, lang)


def _runnable_langs() -> list[str]:
    from honepad.cli import _runner_ids

    ids = _runner_ids()
    return ["java", *[i for i in ids if i != "java"]] if "java" in ids else ids


def _cli(*args: str) -> tuple[int, str]:
    """Run the honepad CLI in a child process and return (exit code, plain text)."""
    env = os.environ.copy()
    env["NO_COLOR"] = "1"
    env.pop("FORCE_COLOR", None)
    src = str(Path(__file__).resolve().parents[1])
    env["PYTHONPATH"] = src + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "honepad", *args],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=ACTION_TIMEOUT_S,
            env=env,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return 1, f"FAIL: honepad {args[0]} timed out after {ACTION_TIMEOUT_S}s"
    text = _ANSI.sub("", (proc.stdout or "") + (proc.stderr or ""))
    return proc.returncode, text.strip()


def _session() -> dict[str, Any] | None:
    try:
        return load_session()
    except HONEPAD_ERRORS:
        return None


def _tier(score: int | None) -> str:
    """Label for the difficulty score bench/difficulty.py writes to the catalog."""
    if score is None:
        return ""
    return "Easy" if score < 25 else "Medium" if score < 60 else "Hard"


def state() -> dict[str, Any]:
    session = _session()
    if session is not None and session.get("cleared") and not is_ended(session):
        # Cleared before clearing stopped the clock: stop it now.
        end_attempt(session)
    desks = (session or {}).get("desks") or {}
    catalog = load_catalog()
    originals = set(catalog.get("original_problems", []))
    scores = catalog.get("difficulty") or {}
    rows = []
    for pid in problems():
        desk = desks.get(pid) or {}
        rows.append(
            {
                "id": pid,
                "levels": max_level(pid),
                "unlocked": int(desk.get("unlocked", 0)),
                "lang": desk.get("lang"),
                "cleared": bool(desk.get("cleared")),
                "ended": desk.get("ended_at") is not None,
                "original": pid in originals,
                "difficulty": scores.get(pid),
                "tier": _tier(scores.get(pid)),
            }
        )
    active = None
    if session is not None:
        active = {
            "problem": session["problem"],
            "lang": session["lang"],
            "unlocked": int(session["unlocked"]),
            "levels": max_level(str(session["problem"])),
            "minutes": int(session["minutes"]),
            "left": clock_left(session),
            "paused": is_paused(session),
            "cleared": bool(session.get("cleared")),
            "ended": is_ended(session),
            "over": attempt_over(session),
            "last_run": session.get("last_run"),
        }
    return {
        "problems": rows,
        "originals_done": sum(1 for r in rows if r["original"] and r["cleared"]),
        "originals_total": sum(1 for r in rows if r["original"]),
        "langs": _runnable_langs(),
        "session": active,
        "claude_available": review.claude_available(),
    }


def _view_case(case: dict[str, Any], naming: str, hidden: bool = False) -> dict[str, Any]:
    return {
        "id": str(case["id"]),
        "level": int(case.get("level", 0)),
        "hidden": hidden,
        "calls": [
            {"m": method_name(str(c["m"]), naming), "a": c["a"], "e": c["e"]} for c in case["calls"]
        ],
    }


def _every_case(problem: str) -> list[tuple[dict[str, Any], bool]]:
    top = max_level(problem)
    return [(c, False) for c in load_cases(problem, top)] + [
        (c, True) for c in load_hidden_cases(problem, top)
    ]


def cases_view(scope: str = "level") -> dict[str, Any]:
    """Public traces through the unlocked level, in the user's method naming.
    scope=all (only once the attempt is over): every level, hidden cases too."""
    session = _session()
    if session is None:
        return {"error": "no session"}
    problem, lang = str(session["problem"]), str(session["lang"])
    naming = str(language(lang)["naming"])
    if scope == "all":
        if not attempt_over(session):
            return dict(_NOT_OVER)
        cases = [_view_case(c, naming, hidden) for c, hidden in _every_case(problem)]
        return {"scope": "all", "level": max_level(problem), "cases": cases}
    level = int(session["unlocked"])
    cases = [_view_case(case, naming) for case in load_cases(problem, level)]
    return {
        "scope": "level",
        "level": level,
        "cases": cases,
        "report": _LAST_REPORTS.get(_report_key(problem, lang)),
    }


def check_all() -> dict[str, Any]:
    """Run the work code against every public and hidden case of every level."""
    from honepad.cli import report_dict

    session = _session()
    if session is None:
        return {"error": "no session"}
    if not attempt_over(session):
        return dict(_NOT_OVER)
    problem, lang = str(session["problem"]), str(session["lang"])
    cases = [case for case, _hidden in _every_case(problem)]
    try:
        report = run(problem, lang, max_level(problem), kind="work", cases=cases)
    except HONEPAD_ERRORS + (NotImplementedError,) as exc:
        return {"error": str(exc)}
    return {"ok": not report.failed, "report": report_dict(report, lang)}


def solution_view() -> dict[str, Any]:
    """The reference solution, once the attempt is over."""
    session = _session()
    if session is None:
        return {"error": "no session"}
    if not attempt_over(session):
        return dict(_NOT_OVER)
    problem, lang = str(session["problem"]), str(session["lang"])
    path: Path | None = None
    try:
        spec = packspec.run_spec(lang)
        if spec is not None:
            path = spec_src(lang, problem, "solution", spec)
        else:
            found = sorted((repo_root() / "langs" / lang / "problems" / problem).glob("solution.*"))
            path = found[0] if found else None
    except HONEPAD_ERRORS:
        path = None
    if path is None or not path.is_file() or path.is_symlink():
        return {"missing": True}
    return {"path": str(path), "code": path.read_text(encoding="utf-8")}


def make_review(ask_claude: bool = False) -> dict[str, Any]:
    session = _session()
    if session is None:
        return {"error": "no session"}
    markdown, meta = review.build_review(session)
    path = review.save_review(markdown, session)
    result: dict[str, Any] = {"markdown": markdown, "path": str(path), "meta": meta}
    if ask_claude:
        result["review"] = review.ask_claude(markdown)
    return result


def spec_text(level: int | None = None) -> dict[str, Any]:
    """One level's spec. Levels past the unlocked one open once the attempt is over."""
    session = _session()
    if session is None:
        return {"error": "no session"}
    problem = str(session["problem"])
    unlocked = int(session["unlocked"])
    top = max_level(problem)
    visible = top if attempt_over(session) else unlocked
    level = unlocked if level is None else level
    if not 1 <= level <= visible:
        return {"error": f"level {level} is locked", "visible": visible, "levels": top}
    path = problem_dir(problem) / "spec" / f"level{level}.md"
    if not path.is_file():
        return {"error": f"missing spec level {level}"}
    return {
        "level": level,
        "unlocked": unlocked,
        "visible": visible,
        "levels": top,
        "markdown": path.read_text(encoding="utf-8"),
    }


def _work_path(session: dict[str, Any]) -> Path:
    path = work_src(str(session["problem"]), str(session["lang"]))
    if path.is_symlink():
        raise ValueError(f"work file is a symlink: {path}")
    return path


def read_work() -> dict[str, Any]:
    session = _session()
    if session is None:
        return {"error": "no session"}
    path = _work_path(session)
    if not path.is_file():
        return {"error": f"work file missing: {path}"}
    return {"path": str(path), "code": path.read_text(encoding="utf-8")}


def save_work(code: str) -> dict[str, Any]:
    session = _session()
    if session is None:
        return {"error": "no session"}
    if is_paused(session):
        return {"error": "paused: resume first"}
    path = _work_path(session)
    if not path.parent.is_dir():
        return {"error": f"work folder missing: {path.parent}"}
    _replace_text(path, code)
    return {"ok": True, "path": str(path)}


def _action(kind: str, body: dict[str, Any]) -> dict[str, Any]:
    if kind == "start":
        problem = str(body.get("problem", ""))
        lang = str(body.get("lang") or "java")
        if problem not in problems() or lang not in _runnable_langs():
            return {"error": "unknown problem or language"}
        args = ["start", problem, lang, "--no-console", "--yes"]
        _LAST_REPORTS.pop(_report_key(problem, lang), None)
        if body.get("reset"):
            args.append("--reset")
        code, out = _cli(*args)
        return {"ok": code == 0, "output": out}
    if kind in {"pause", "resume"}:
        code, out = _cli(kind)
        return {"ok": code == 0, "output": out}
    if kind == "check-all":
        return check_all()
    session = _session()
    if session is None:
        return {"error": "no session"}
    problem, lang = str(session["problem"]), str(session["lang"])
    if "code" in body and not is_paused(session):
        saved = save_work(str(body["code"]))
        if "error" in saved:
            return saved
    with tempfile.TemporaryDirectory(prefix="honepad-web-") as tmp:
        report_path = Path(tmp) / "report.json"
        extra = ["--report-json", str(report_path)]
        if kind == "run":
            code, out = _cli("run", problem, "--lang", lang, "--kind", "work", *extra)
        elif kind == "finish":
            code, out = _cli("finish", *extra)
        else:
            code, out = _cli(
                "submit", problem, "--lang", lang, "--kind", "work", "--confirm", "y", *extra
            )
        report = None
        if report_path.is_file():
            try:
                report = json.loads(report_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                report = None
    if report is not None:
        _LAST_REPORTS[_report_key(problem, lang)] = report
    return {"ok": code == 0, "output": out, "report": report}


class _Server(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, port: int) -> None:
        super().__init__(("127.0.0.1", port), _Handler)
        self.token = secrets.token_urlsafe(24)
        self.action_lock = threading.Lock()

    @property
    def port(self) -> int:
        return int(self.server_address[1])

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self.port}/?t={self.token}"


class _Handler(BaseHTTPRequestHandler):
    server: _Server

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        pass  # keep the terminal quiet

    def _send(self, status: int, body: bytes, ctype: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, payload: dict[str, Any]) -> None:
        self._send(status, json.dumps(payload).encode("utf-8"), "application/json")

    def _host_ok(self) -> bool:
        port = self.server.port
        return self.headers.get("Host", "") in {f"127.0.0.1:{port}", f"localhost:{port}"}

    def _token_ok(self, query_token: str | None = None) -> bool:
        given = query_token if query_token is not None else self.headers.get("X-Honepad-Token", "")
        return secrets.compare_digest(given.encode(), self.server.token.encode())

    def _guard(self, query_token: str | None = None) -> bool:
        if not self._host_ok() or not self._token_ok(query_token):
            self._json(403, {"error": "forbidden"})
            return False
        return True

    def _body(self) -> dict[str, Any] | None:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = -1
        if length < 0 or length > MAX_BODY:
            self._json(413, {"error": "body too large"})
            return None
        raw = self.rfile.read(length) if length else b"{}"
        try:
            data = json.loads(raw or b"{}")
        except json.JSONDecodeError:
            self._json(400, {"error": "bad json"})
            return None
        if not isinstance(data, dict):
            self._json(400, {"error": "bad json"})
            return None
        return data

    def do_GET(self) -> None:  # noqa: N802
        url = urlparse(self.path)
        if url.path == "/":
            token = (parse_qs(url.query).get("t") or [""])[0]
            if not self._guard(token):
                return
            page = _PAGE.read_text(encoding="utf-8").replace("__HONEPAD_TOKEN__", self.server.token)
            self._send(200, page.encode("utf-8"), "text/html; charset=utf-8")
            return
        if not self._guard():
            return
        try:
            query = parse_qs(url.query)
            if url.path == "/api/state":
                self._json(200, state())
            elif url.path == "/api/spec":
                raw = (query.get("level") or [""])[0]
                self._json(200, spec_text(int(raw) if raw.isdigit() else None))
            elif url.path == "/api/work":
                self._json(200, read_work())
            elif url.path == "/api/cases":
                self._json(200, cases_view((query.get("scope") or ["level"])[0]))
            elif url.path == "/api/solution":
                self._json(200, solution_view())
            else:
                self._json(404, {"error": "not found"})
        except HONEPAD_ERRORS as exc:
            self._json(200, {"error": str(exc)})

    def do_PUT(self) -> None:  # noqa: N802
        if not self._guard():
            return
        if urlparse(self.path).path != "/api/work":
            self._json(404, {"error": "not found"})
            return
        body = self._body()
        if body is None:
            return
        try:
            self._json(200, save_work(str(body.get("code", ""))))
        except HONEPAD_ERRORS as exc:
            self._json(200, {"error": str(exc)})

    def do_POST(self) -> None:  # noqa: N802
        if not self._guard():
            return
        kind = urlparse(self.path).path.removeprefix("/api/")
        actions = {"start", "run", "submit", "finish", "check-all", "pause", "resume"}
        if kind not in actions | {"review", "review/claude"}:
            self._json(404, {"error": "not found"})
            return
        body = self._body()
        if body is None:
            return
        if not self.server.action_lock.acquire(blocking=False):
            self._json(409, {"error": "another action is still running"})
            return
        try:
            if kind.startswith("review"):
                self._json(200, make_review(ask_claude=kind == "review/claude"))
            else:
                self._json(200, _action(kind, body))
        except HONEPAD_ERRORS + (NotImplementedError,) as exc:
            self._json(200, {"error": str(exc)})
        finally:
            self.server.action_lock.release()


def make_server(port: int = 0) -> _Server:
    return _Server(port)


def _open(url: str) -> None:
    if "microsoft" in platform.release().lower() and shutil.which("explorer.exe"):
        # WSL: hand the URL to the Windows default browser.
        subprocess.Popen(
            ["explorer.exe", url],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return
    webbrowser.open(url)


def serve(port: int = 0, open_browser: bool = True) -> int:
    server = make_server(port)
    print(f"OK: honepad web at {server.url}")
    print("NOTE: open that link in Chrome. Ctrl+C here stops the server.")
    sys.stdout.flush()
    if open_browser:
        _open(server.url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nOK: stopped")
    finally:
        server.server_close()
    return 0
