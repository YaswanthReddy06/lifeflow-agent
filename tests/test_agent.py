"""
test_agent.py — offline tests that don't require a Gemini API key.

These cover the parts of the system that are pure logic (security
validation, PII masking, free-time-gap finding) so CI/judges can verify
correctness without needing to configure credentials.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from mcp_server import db, security
from mcp_server.server import find_free_time


@pytest.fixture(autouse=True)
def fresh_db(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.db")
    db.init_db()
    yield


def test_validate_text_truncates_long_input():
    result = security.validate_text("a" * 500, max_len=50)
    assert len(result) == 50


def test_validate_text_rejects_non_string():
    with pytest.raises(security.ValidationError):
        security.validate_text(42)


def test_validate_amount_rejects_negative():
    with pytest.raises(security.ValidationError):
        security.validate_amount(-5)


def test_validate_amount_rejects_absurdly_large():
    with pytest.raises(security.ValidationError):
        security.validate_amount(1_000_000)


def test_mask_pii_redacts_email_and_phone():
    text = security.mask_pii("Reach me at a@b.com or 555-867-5309")
    assert "a@b.com" not in text
    assert "555-867-5309" not in text
    assert "[redacted-email]" in text
    assert "[redacted-phone]" in text


def test_find_free_time_returns_gaps():
    with db.get_conn() as conn:
        conn.execute(
            "INSERT INTO schedule (title, start_time, end_time, category) "
            "VALUES ('Meeting', '09:00', '10:00', 'work')"
        )
    gaps = find_free_time(min_minutes=30)
    assert any(g["start"] == "06:00" for g in gaps)
    assert any(g["start"] == "10:00" for g in gaps)


def test_log_expense_rejects_bad_amount():
    from mcp_server.server import log_expense

    with pytest.raises(security.ValidationError):
        log_expense(label="Something", amount=-10, category="misc")
