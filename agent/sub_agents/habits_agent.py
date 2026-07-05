"""
habits_agent.py — specialist sub-agent for habit tracking and encouragement.

Day 3 concept demonstrated: Agent Skills. Rather than hand-writing streak
logic directly into this file's instruction string, the actual procedure
lives in a separate, portable skill file at skills/habit-streak-coach/SKILL.md
— the same SKILL.md format used by Antigravity's Skills system. This
agent loads that file's body at import time and folds it into its own
instruction, so the skill is genuinely used at runtime (not just a repo
artifact for show). Keeping it in a separate file means the exact same
skill could be dropped into an Antigravity project, or handed to a
completely different agent, unchanged.
"""

from pathlib import Path

from google.adk.agents import Agent

from ..mcp_connection import get_lifeflow_toolset

SKILL_PATH = Path(__file__).resolve().parent.parent.parent / "skills" / "habit-streak-coach" / "SKILL.md"


def _load_skill_body(path: Path) -> str:
    """
    Read a SKILL.md file and strip its YAML frontmatter, returning just the
    procedural instructions. Falls back to an empty string if the skill
    file is ever missing, so the agent still runs (just without the extra
    streak-coaching behavior) rather than crashing at import time.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            return parts[2].strip()
    return text.strip()


_STREAK_SKILL = _load_skill_body(SKILL_PATH)

habits_agent = Agent(
    name="habits_agent",
    model="gemini-2.5-flash",
    description="Logs habits (water, medication, exercise, meditation) and reviews streaks.",
    instruction=(
        "You are the Habits specialist for a personal concierge system. "
        "Use log_habit to record a completed habit and get_habit_history to review "
        "recent activity. Be warm and encouraging, but do not diagnose or give medical "
        "advice — if the user mentions a medication, only log the fact that they took "
        "it; do not comment on dosage, timing, or interactions. For anything medical "
        "beyond simple logging, suggest they talk to their doctor or pharmacist.\n\n"
        "When the user asks about their consistency or progress (not just a one-off "
        "log), follow this skill precisely:\n\n" + _STREAK_SKILL
    ),
    tools=[get_lifeflow_toolset()],
)
