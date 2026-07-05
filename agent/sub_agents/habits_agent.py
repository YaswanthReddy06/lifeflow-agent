"""
habits_agent.py — specialist sub-agent for habit tracking and encouragement.
"""

from google.adk.agents import Agent

from ..mcp_connection import get_lifeflow_toolset

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
        "beyond simple logging, suggest they talk to their doctor or pharmacist."
    ),
    tools=[get_lifeflow_toolset()],
)
