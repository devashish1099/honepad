import json
import time
from pathlib import Path

from honepad.cli import main
from honepad.session import (
    attempt_over,
    clock_left,
    end_attempt,
    ensure_session,
    is_ended,
    load_session,
    pause_clock,
    save_session,
)


def _write_session(path: Path, **extra: object) -> None:
    payload = {
        "problem": "bank_system",
        "lang": "python3",
        "started_at": int(time.time()),
        "minutes": 90,
        "unlocked": 1,
        **extra,
    }
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def test_end_attempt_freezes_the_clock_once(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("HONEPAD_SESSION", str(tmp_path / "session.json"))
    session = {"problem": "bank_system", "lang": "python3", "started_at": 1000, "minutes": 90}
    session["unlocked"] = 1
    assert not attempt_over(session, now=1600)
    assert end_attempt(session, now=1600)
    assert is_ended(session) and attempt_over(session, now=1600)
    assert clock_left(session, now=99_999) == 90 * 60 - 600
    assert not end_attempt(session, now=1700)
    assert not pause_clock(session, now=1700)


def test_paused_attempt_ends_at_its_pause(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("HONEPAD_SESSION", str(tmp_path / "session.json"))
    session = {"problem": "bank_system", "lang": "python3", "started_at": 1000, "minutes": 90}
    session["unlocked"] = 1
    assert pause_clock(session, now=1300)
    assert end_attempt(session, now=5000)
    assert "paused_at" not in session
    assert session["ended_at"] == 1300


def test_ended_at_round_trips_and_reset_clears_it(monkeypatch, tmp_path: Path) -> None:
    path = tmp_path / "session.json"
    monkeypatch.setenv("HONEPAD_SESSION", str(path))
    parked = {"lang": "python3", "started_at": 10, "minutes": 90, "unlocked": 1, "ended_at": 20}
    session = {
        "problem": "bank_system",
        "lang": "python3",
        "started_at": int(time.time()),
        "minutes": 90,
        "unlocked": 2,
        "ended_at": int(time.time()),
        "desks": {"workers": parked},
    }
    save_session(session, path)
    loaded = load_session(path)
    assert loaded is not None
    assert is_ended(loaded)
    assert loaded["desks"]["workers"]["ended_at"] == 20
    # Reopening the same problem keeps the finished attempt; --reset starts a new one.
    assert is_ended(ensure_session("bank_system", "python3"))
    assert not is_ended(ensure_session("bank_system", "python3", reset=True))


def test_cli_finish_grades_then_blocks_submit(monkeypatch, tmp_path: Path, capsys) -> None:
    path = tmp_path / "session.json"
    monkeypatch.setenv("HONEPAD_SESSION", str(path))
    assert main(["start", "bank_system", "python3", "--no-console", "--yes"]) == 0
    capsys.readouterr()
    report = tmp_path / "report.json"
    assert main(["finish", "--report-json", str(report)]) == 0
    out = capsys.readouterr().out
    assert "passed=" in out
    assert "DONE: attempt finished, reached LEVEL 1 of" in out
    assert json.loads(report.read_text(encoding="utf-8"))["failed"]
    assert is_ended(load_session(path))

    assert main(["finish"]) == 0
    assert "already finished" in capsys.readouterr().out
    assert main(["submit", "bank_system", "--kind", "work", "--confirm", "y"]) == 1
    assert "attempt finished" in capsys.readouterr().out
    assert main(["pause"]) == 1
    assert main(["timer"]) == 0
    assert "FINISHED: timer" in capsys.readouterr().out
    # Run still works after the end, for experimenting.
    assert main(["run", "bank_system", "--kind", "work"]) == 1
    assert "passed=" in capsys.readouterr().out


def test_cli_finish_without_session_fails(monkeypatch, tmp_path: Path, capsys) -> None:
    monkeypatch.setenv("HONEPAD_SESSION", str(tmp_path / "missing.json"))
    assert main(["finish"]) == 1
    assert "FAIL: no session" in capsys.readouterr().out


def test_clearing_every_level_stops_the_clock(monkeypatch, tmp_path: Path) -> None:
    from honepad.session import lock_to_level, mark_cleared

    monkeypatch.setenv("HONEPAD_SESSION", str(tmp_path / "session.json"))
    session = {"problem": "bank_system", "lang": "python3", "started_at": int(time.time())}
    session.update(minutes=90, unlocked=4)
    mark_cleared(session)
    assert is_ended(session) and attempt_over(session)
    # Stepping back a level reopens the attempt.
    lock_to_level(session, 3)
    assert not is_ended(session) and not attempt_over(session)


def test_web_state_stops_the_clock_of_an_already_cleared_attempt(monkeypatch, tmp_path) -> None:
    from honepad.web import state

    path = tmp_path / "session.json"
    monkeypatch.setenv("HONEPAD_SESSION", str(path))
    _write_session(path, unlocked=4, cleared=True)
    assert state()["session"]["over"] is True
    assert is_ended(load_session(path))
