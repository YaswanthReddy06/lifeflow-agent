"""
server.py — the LifeFlow MCP Server.

Concept demonstrated: MCP Server (Day 2).
This exposes a small set of tools over the Model Context Protocol so that
*any* MCP-compatible agent (not just ours) can read/write a person's daily
schedule, habits, and budget — without the agent needing bespoke API code
for each of these. This is the "USB-C for AI tools" idea from the course:
one protocol, many possible callers.

Run standalone for local testing:
    python mcp_server/server.py

The ADK orchestrator (agent/orchestrator.py) connects to this same server
as an MCP client tool source.
"""

from datetime import datetime

from mcp.server.fastmcp import FastMCP

from . import db
from .security import mask_pii, validate_amount, validate_text

mcp = FastMCP("lifeflow-tools")


@mcp.tool()
def get_today_schedule() -> list[dict]:
    """Return today's schedule blocks (title, start_time, end_time, category)."""
    with db.get_conn() as conn:
        rows = conn.execute(
            "SELECT title, start_time, end_time, category FROM schedule ORDER BY start_time"
        ).fetchall()
    return [dict(r) for r in rows]


@mcp.tool()
def find_free_time(min_minutes: int = 30) -> list[dict]:
    """
    Find gaps of at least `min_minutes` between today's scheduled blocks.
    Used by the Schedule sub-agent to suggest when to fit in a new habit
    or task without creating conflicts.
    """
    with db.get_conn() as conn:
        rows = conn.execute(
            "SELECT start_time, end_time FROM schedule ORDER BY start_time"
        ).fetchall()

    def to_minutes(t: str) -> int:
        h, m = map(int, t.split(":"))
        return h * 60 + m

    blocks = [(to_minutes(r["start_time"]), to_minutes(r["end_time"])) for r in rows]
    gaps = []
    day_start, day_end = to_minutes("06:00"), to_minutes("22:00")
    cursor = day_start
    for start, end in blocks:
        if start - cursor >= min_minutes:
            gaps.append({"start": f"{cursor//60:02d}:{cursor%60:02d}",
                         "end": f"{start//60:02d}:{start%60:02d}"})
        cursor = max(cursor, end)
    if day_end - cursor >= min_minutes:
        gaps.append({"start": f"{cursor//60:02d}:{cursor%60:02d}",
                     "end": f"{day_end//60:02d}:{day_end%60:02d}"})
    return gaps


@mcp.tool()
def log_habit(name: str, note: str = "") -> dict:
    """
    Log a completed habit (e.g. 'drank water', 'took medication', 'meditated').
    Security: inputs are validated/sanitized before touching the database
    (Day 4 concept — never trust raw agent-generated strings going into storage).
    """
    name = validate_text(name, max_len=80)
    note = mask_pii(validate_text(note, max_len=200))
    with db.get_conn() as conn:
        conn.execute("INSERT INTO habits (name, note) VALUES (?, ?)", (name, note))
    return {"status": "logged", "name": name, "logged_at": datetime.now().isoformat()}


@mcp.tool()
def get_habit_history(limit: int = 10) -> list[dict]:
    """Return the most recently logged habits."""
    limit = max(1, min(limit, 100))  # clamp — Day 4 "never trust raw params"
    with db.get_conn() as conn:
        rows = conn.execute(
            "SELECT name, logged_at, note FROM habits ORDER BY logged_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


HIGH_VALUE_THRESHOLD = 50.0  # dollars — above this, a human must explicitly confirm


@mcp.tool()
def log_expense(label: str, amount: float, category: str, confirm: bool = False) -> dict:
    """
    Log a spending item with amount and category, for the budget sub-agent.

    Security (Day 4 concept — "Vibe Diff" / human-in-the-loop for high-stakes
    actions): expenses at or above HIGH_VALUE_THRESHOLD are NOT written to
    the database on the first call. Instead, this returns a plain-English
    description of exactly what would happen and asks for explicit
    confirmation. The calling agent must relay that description to the user
    and only call this tool again with confirm=True after the user agrees.
    This mirrors the course's "Vibe Diff" idea: translate a high-stakes
    action into plain language for a human to approve *before* it happens,
    rather than silently trusting the agent's judgment for larger amounts.
    """
    label = validate_text(label, max_len=80)
    category = validate_text(category, max_len=40)
    amount = validate_amount(amount)

    if amount >= HIGH_VALUE_THRESHOLD and not confirm:
        return {
            "status": "confirmation_required",
            "plain_english_action": (
                f"This would log a ${amount:.2f} expense labeled '{label}' "
                f"under the '{category}' category — that's at or above the "
                f"${HIGH_VALUE_THRESHOLD:.0f} review threshold."
            ),
            "next_step": "Ask the user to confirm. If they agree, call log_expense again with confirm=True.",
        }

    with db.get_conn() as conn:
        conn.execute(
            "INSERT INTO expenses (label, amount, category) VALUES (?, ?, ?)",
            (label, amount, category),
        )
    return {"status": "logged", "label": label, "amount": amount, "category": category}


@mcp.tool()
def get_spending_summary() -> dict:
    """Return total spend and a per-category breakdown for today's logged expenses."""
    with db.get_conn() as conn:
        rows = conn.execute(
            "SELECT category, SUM(amount) as total FROM expenses GROUP BY category"
        ).fetchall()
        total = conn.execute("SELECT SUM(amount) FROM expenses").fetchone()[0] or 0.0
    return {
        "total": round(total, 2),
        "by_category": {r["category"]: round(r["total"], 2) for r in rows},
    }


def main():
    db.init_db()
    db.seed_demo_data()
    mcp.run()  # stdio transport by default — matches ADK's MCPToolset expectations


if __name__ == "__main__":
    main()
