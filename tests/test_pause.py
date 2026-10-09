import io
import json
import time
from pathlib import Path

from honepad.cli import main
from honepad.console import dispatch, render_banner
from honepad.session import (
    clock_left,
    is_paused,
    load_session,
    pause_clock,
    resume_clock,
    save_session,
)


def _write_session(path: Path, problem: str = "bank_system", **extra: object) -> dict:
    payload = {
        "problem": problem,
        "lang": "python3",
        "started_at": int(time.time()),
        "minutes": 90,
        "unlocked": 1,
        **extra,
    }
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
    return payload


def test_pause_freezes_clock_and_resume_skips_the_gap(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("HONEPAD_SESSION", str(tmp_path / "session.json"))
    session = {"problem": "bank_system", "lang": "python3", "started_at": 1000, "minutes": 90}
    session["unlocked"] = 1
    assert pause_clock(session, now=1600)
    assert is_paused(session)
    assert clock_left(session, now=1600) == 90 * 60 - 600
    assert clock_left(session, now=99_999) == 90 * 60 - 600
    assert not pause_clock(session, now=1700)
    assert resume_clock(session, now=4600)
    assert not is_paused(session)
    assert session["started_at"] == 4000
    assert clock_left(session, now=4600) == 90 * 60 - 600
    assert not resume_clock(session, now=4700)


def test_pause_is_refused_once_time_is_up(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("HONEPAD_SESSION", str(tmp_path / "session.json"))
    session = {"problem": "bank_system", "lang": "python3", "started_at": 0, "minutes": 1}
    session["unlocked"] = 1
    assert not pause_clock(session, now=60)
    assert not is_paused(session)


def test_paused_at_round_trips_for_active_and_parked_desks(monkeypatch, tmp_path: Path) -> None:
    path = tmp_path / "session.json"
    monkeypatch.setenv("HONEPAD_SESSION", str(path))
    parked = {"lang": "python3", "started_at": 10, "minutes": 90, "unlocked": 1, "paused_at": 20}
    session = {
        "problem": "bank_system",
        "lang": "python3",
        "started_at": 100,
        "minutes": 90,
        "unlocked": 1,
        "paused_at": 160,
        "desks": {"workers": parked},
    }
    save_session(session, path)
    loaded = load_session(path)
    assert loaded is not None
    assert loaded["paused_at"] == 160
    assert loaded["desks"]["workers"]["paused_at"] == 20
    assert loaded["desks"]["bank_system"]["paused_at"] == 160


def test_bad_paused_at_is_dropped(monkeypatch, tmp_path: Path) -> None:
    path = tmp_path / "session.json"
    monkeypatch.setenv("HONEPAD_SESSION", str(path))
    _write_session(path, paused_at=True)
    loaded = load_session(path)
    assert loaded is not None
    assert "paused_at" not in loaded


def test_cli_pause_blocks_work_runs_until_resume(monkeypatch, tmp_path: Path, capsys) -> None:
    path = tmp_path / "session.json"
    monkeypatch.setenv("HONEPAD_SESSION", str(path))
    _write_session(path)

    assert main(["pause"]) == 0
    assert "OK: paused with" in capsys.readouterr().out
    assert main(["pause"]) == 0
    assert "already paused" in capsys.readouterr().out

    assert main(["run", "bank_system", "--kind", "work"]) == 1
    out = capsys.readouterr().out
    assert "PAUSED: clock is stopped" in out
    assert "resume" in out

    assert main(["submit", "bank_system", "--kind", "work", "--confirm", "y"]) == 1
    assert "PAUSED: clock is stopped" in capsys.readouterr().out

    assert main(["timer"]) == 0
    assert "PAUSED: timer 90m" in capsys.readouterr().out

    assert main(["resume"]) == 0
    assert "OK: resumed with" in capsys.readouterr().out
    assert main(["resume"]) == 0
    assert "not paused" in capsys.readouterr().out
    assert not is_paused(load_session(path))


def test_cli_pause_still_allows_reference_runs(monkeypatch, tmp_path: Path, capsys) -> None:
    path = tmp_path / "session.json"
    monkeypatch.setenv("HONEPAD_SESSION", str(path))
    _write_session(path)
    assert main(["pause"]) == 0
    capsys.readouterr()
    assert main(["run", "bank_system", "--kind", "solution"]) == 0
    assert "PAUSED" not in capsys.readouterr().out


def test_cli_pause_without_session_fails(monkeypatch, tmp_path: Path, capsys) -> None:
    monkeypatch.setenv("HONEPAD_SESSION", str(tmp_path / "missing.json"))
    assert main(["pause"]) == 1
    assert "FAIL: no session" in capsys.readouterr().out


def test_console_p_toggles_and_banner_says_paused(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("NO_COLOR", "1")
    path = tmp_path / "session.json"
    monkeypatch.setenv("HONEPAD_SESSION", str(path))
    _write_session(path)
    session = load_session(path)
    assert session is not None
    out = io.StringIO()
    assert dispatch("p", session, out) == 0
    assert "OK: paused with" in out.getvalue()
    assert "PAUSED " in render_banner(load_session(path))
    out = io.StringIO()
    assert dispatch("p", load_session(path), out) == 0
    assert "OK: resumed with" in out.getvalue()
    assert "PAUSED" not in render_banner(load_session(path))
