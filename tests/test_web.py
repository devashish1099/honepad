import json
import shutil
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from honepad.catalog import problems, repo_root
from honepad.web import make_server


@pytest.fixture
def web(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("HONEPAD_SESSION", str(tmp_path / "session.json"))
    server = make_server(0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield server
    server.shutdown()
    server.server_close()


def _call(server, method: str, path: str, body=None, *, token=None, host=None):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(f"http://127.0.0.1:{server.port}{path}", data=data, method=method)
    req.add_header("X-Honepad-Token", server.token if token is None else token)
    req.add_header("Content-Type", "application/json")
    if host is not None:
        req.add_header("Host", host)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode()


def test_api_needs_the_token_and_a_local_host(web) -> None:
    assert _call(web, "GET", "/api/state", token="nope")[0] == 403
    assert _call(web, "GET", "/api/state", host="evil.example:80")[0] == 403
    assert _call(web, "GET", "/?t=wrong")[0] == 403
    status, page = _call(web, "GET", f"/?t={web.token}")
    assert status == 200
    assert web.token in page
    assert "__HONEPAD_TOKEN__" not in page


def test_state_lists_every_problem_and_no_session(web) -> None:
    status, raw = _call(web, "GET", "/api/state")
    assert status == 200
    state = json.loads(raw)
    assert [row["id"] for row in state["problems"]] == problems()
    assert state["session"] is None
    assert "python3" in state["langs"]


def test_start_edit_run_submit_pause_round_trip(web) -> None:
    status, raw = _call(web, "POST", "/api/start", {"problem": "bank_system", "lang": "python3"})
    assert status == 200 and json.loads(raw)["ok"], raw

    state = json.loads(_call(web, "GET", "/api/state")[1])
    assert state["session"]["problem"] == "bank_system"
    assert state["session"]["unlocked"] == 1
    assert state["session"]["paused"] is False

    spec = json.loads(_call(web, "GET", "/api/spec")[1])
    assert spec["level"] == 1 and "Bank system level 1" in spec["markdown"]
    work = json.loads(_call(web, "GET", "/api/work")[1])
    assert "class Simulation" in work["code"]

    solution = (
        repo_root() / "langs" / "python3" / "problems" / "bank_system" / "solution.py"
    ).read_text(encoding="utf-8")
    ran = json.loads(_call(web, "POST", "/api/run", {"code": solution})[1])
    assert ran["ok"], ran["output"]
    assert "PASS" in ran["output"]
    assert json.loads(_call(web, "GET", "/api/work")[1])["code"] == solution

    sub = json.loads(_call(web, "POST", "/api/submit", {"code": solution})[1])
    assert sub["ok"], sub["output"]
    assert json.loads(_call(web, "GET", "/api/state")[1])["session"]["unlocked"] == 2

    assert json.loads(_call(web, "POST", "/api/pause", {})[1])["ok"]
    assert json.loads(_call(web, "GET", "/api/state")[1])["session"]["paused"] is True
    blocked = json.loads(_call(web, "POST", "/api/run", {"code": "changed"})[1])
    assert not blocked["ok"]
    assert "PAUSED" in blocked["output"]
    saved = json.loads(_call(web, "PUT", "/api/work", {"code": "changed"})[1])
    assert "paused" in saved["error"]
    assert json.loads(_call(web, "GET", "/api/work")[1])["code"] != "changed"
    assert json.loads(_call(web, "POST", "/api/resume", {})[1])["ok"]


def test_start_rejects_unknown_problem(web) -> None:
    res = json.loads(_call(web, "POST", "/api/start", {"problem": "../etc", "lang": "java"})[1])
    assert "error" in res


def test_unknown_routes_404(web) -> None:
    assert _call(web, "GET", "/api/nope")[0] == 404
    assert _call(web, "POST", "/api/delete", {})[0] == 404


def test_state_marks_the_original_problems(web) -> None:
    state = json.loads(_call(web, "GET", "/api/state")[1])
    originals = [row["id"] for row in state["problems"] if row["original"]]
    assert originals[0] == "bank_system"
    assert len(originals) == 10
    assert "library" not in originals
    assert state["originals_total"] == 10
    assert state["originals_done"] == 0
    assert isinstance(state["claude_available"], bool)


def test_run_report_lists_every_failure_and_cases_use_user_naming(web) -> None:
    assert json.loads(
        _call(web, "POST", "/api/start", {"problem": "bank_system", "lang": "python3"})[1]
    )["ok"]
    cases = json.loads(_call(web, "GET", "/api/cases")[1])
    assert cases["level"] == 1
    assert cases["report"] is None
    assert cases["cases"][0]["calls"][0]["m"] == "create_account"

    ran = json.loads(_call(web, "POST", "/api/run", {})[1])
    assert not ran["ok"]
    report = ran["report"]
    assert report["total"] == len(cases["cases"])
    assert len(report["failed"]) > 1
    first = report["failed"][0]
    assert {"case", "index", "method", "expected", "actual", "args"} <= first.keys()
    again = json.loads(_call(web, "GET", "/api/cases")[1])
    assert again["report"]["failed"] == report["failed"]


@pytest.mark.skipif(shutil.which("javac") is None, reason="javac not on PATH")
def test_cases_use_camel_case_for_java(web) -> None:
    assert json.loads(
        _call(web, "POST", "/api/start", {"problem": "bank_system", "lang": "java"})[1]
    )["ok"]
    cases = json.loads(_call(web, "GET", "/api/cases")[1])
    assert cases["cases"][0]["calls"][0]["m"] == "createAccount"


def test_review_withholds_hidden_cases_mid_test(web, tmp_path: Path) -> None:
    assert json.loads(
        _call(web, "POST", "/api/start", {"problem": "bank_system", "lang": "python3"})[1]
    )["ok"]
    res = json.loads(_call(web, "POST", "/api/review", {})[1])
    text = res["markdown"]
    assert "You are reviewing a practice attempt" in text
    assert "### Bank system level 1" in text
    assert "class Simulation" in text
    assert "## Public test results" in text
    assert "<-- " in text
    assert "hidden cases withheld" in text
    assert "hid-l1" not in text
    assert "solution" not in res["path"]
    assert Path(res["path"]).parent == tmp_path / "reviews"
    assert Path(res["path"]).read_text(encoding="utf-8") == text
    assert res["meta"]["finished"] is False


def test_review_shows_hidden_cases_once_time_is_up(web, tmp_path: Path) -> None:
    assert json.loads(
        _call(web, "POST", "/api/start", {"problem": "bank_system", "lang": "python3"})[1]
    )["ok"]
    path = tmp_path / "session.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["started_at"] -= 91 * 60
    path.write_text(json.dumps(data), encoding="utf-8")
    text = json.loads(_call(web, "POST", "/api/review", {})[1])["markdown"]
    assert "clock ran out" in text
    assert "hid-l1" in text
    assert "hidden cases withheld" not in text


def test_review_claude_reports_missing_cli(web, monkeypatch) -> None:
    assert json.loads(
        _call(web, "POST", "/api/start", {"problem": "bank_system", "lang": "python3"})[1]
    )["ok"]
    monkeypatch.setattr("honepad.review.shutil.which", lambda name: None)
    res = json.loads(_call(web, "POST", "/api/review/claude", {})[1])
    assert "not on PATH" in res["error"]


def _start(web, lang: str = "python3") -> None:
    res = json.loads(_call(web, "POST", "/api/start", {"problem": "bank_system", "lang": lang})[1])
    assert res["ok"], res


def test_earlier_levels_open_and_later_ones_wait_for_the_end(web) -> None:
    _start(web)
    spec = json.loads(_call(web, "GET", "/api/spec?level=1")[1])
    assert spec["level"] == 1 and spec["visible"] == 1 and spec["levels"] == 4
    assert "locked" in json.loads(_call(web, "GET", "/api/spec?level=2")[1])["error"]
    for path in ("/api/solution", "/api/cases?scope=all"):
        assert "finish the attempt first" in json.loads(_call(web, "GET", path)[1])["error"]
    res = json.loads(_call(web, "POST", "/api/check-all", {})[1])
    assert "finish the attempt first" in res["error"]


def test_broken_code_run_has_no_report(web) -> None:
    _start(web)
    ran = json.loads(_call(web, "POST", "/api/run", {"code": "class Simulation(:\n"})[1])
    assert ran["ok"] is False
    assert ran["report"] is None
    assert "FAIL" in ran["output"]


def test_final_submit_opens_every_level_and_the_solution(web) -> None:
    _start(web)
    fin = json.loads(_call(web, "POST", "/api/finish", {})[1])
    assert fin["ok"], fin["output"]
    assert "DONE: attempt finished" in fin["output"]
    assert fin["report"]["failed"]
    session = json.loads(_call(web, "GET", "/api/state")[1])["session"]
    assert session["ended"] is True and session["over"] is True

    assert "level 4" in json.loads(_call(web, "GET", "/api/spec?level=4")[1])["markdown"].lower()
    cases = json.loads(_call(web, "GET", "/api/cases?scope=all")[1])["cases"]
    assert {c["level"] for c in cases} == {1, 2, 3, 4}
    assert any(c["hidden"] for c in cases) and any(c["id"].startswith("hid-l1") for c in cases)
    sol = json.loads(_call(web, "GET", "/api/solution")[1])
    assert sol["path"].endswith("solution.py") and "class Simulation" in sol["code"]

    checked = json.loads(_call(web, "POST", "/api/check-all", {})[1])
    assert checked["ok"] is False
    assert checked["report"]["total"] == len(cases)
    failed = {f["case"] for f in checked["report"]["failed"]}
    assert any(case.startswith("hid-") for case in failed)
    assert any(case.startswith(("l4-", "hid-l4")) for case in failed)

    sub = json.loads(_call(web, "POST", "/api/submit", {})[1])
    assert not sub["ok"] and "attempt finished" in sub["output"]
    text = json.loads(_call(web, "POST", "/api/review", {})[1])["markdown"]
    assert "final submit" in text
    assert "hidden cases withheld" not in text
