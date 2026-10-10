import json
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
