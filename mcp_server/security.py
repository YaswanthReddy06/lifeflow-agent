"""
security.py — lightweight "safety harness" utilities.

Concept demonstrated: Security features (Day 4 — Data pillar: PII masking
and input sanitization; App/Runtime pillar: rejecting malformed tool input
before it reaches the database).

This project intentionally keeps everything local (SQLite, no external
network calls from the MCP server) so there is a small, auditable blast
radius. The two protections below are the concrete, code-level pieces:

1. validate_text / validate_amount — reject or truncate malformed tool
   arguments instead of trusting whatever the LLM decided to pass in.
2. mask_pii — a conservative regex-based scrubber so that if a user's
   habit note happens to contain something that looks like an email,
   phone number, or long digit sequence (e.g. accidentally pasting an
   ID), it never gets persisted verbatim.
"""

import re

_EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_PHONE_RE = re.compile(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b")
_LONG_DIGIT_RE = re.compile(r"\b\d{6,}\b")  # catches SSNs, card numbers, etc.


class ValidationError(ValueError):
    """Raised when tool input fails validation. Caught at the MCP tool boundary."""


def validate_text(value: str, max_len: int = 200) -> str:
    if not isinstance(value, str):
        raise ValidationError("Expected a string.")
    value = value.strip()
    if len(value) > max_len:
        value = value[:max_len]
    # Strip anything that looks like an attempt at SQL/command injection.
    # (Belt-and-suspenders — we already use parameterized queries everywhere.)
    value = value.replace("--", "").replace(";", "")
    return value


def validate_amount(value: float) -> float:
    try:
        value = float(value)
    except (TypeError, ValueError):
        raise ValidationError("Amount must be numeric.")
    if value < 0 or value > 100_000:
        raise ValidationError("Amount out of allowed range.")
    return round(value, 2)


def mask_pii(text: str) -> str:
    text = _EMAIL_RE.sub("[redacted-email]", text)
    text = _PHONE_RE.sub("[redacted-phone]", text)
    text = _LONG_DIGIT_RE.sub("[redacted-id]", text)
    return text
