"""
schedule_agent.py — specialist sub-agent for time/calendar questions.

Part of the multi-agent system (Day 1/3 concept). This agent only knows
about scheduling; it doesn't reason about budget or habits. The root
orchestrator agent routes relevant sub-tasks to it. Keeping agents narrow
like this makes each one easier to prompt, test, and reason about.
"""

from google.adk.agents import Agent

from ..mcp_connection import get_lifeflow_toolset

schedule_agent = Agent(
    name="schedule_agent",
    model="gemini-2.5-flash",
    description="Answers questions about today's schedule and finds free time slots.",
    instruction=(
        "You are the Schedule specialist for a personal concierge system. "
        "Use the get_today_schedule and find_free_time tools to answer questions "
        "about the user's day. When asked to fit something new in (e.g. a workout, "
        "a break, a new habit), always call find_free_time first and suggest a "
        "specific gap rather than guessing. Keep answers short and concrete — "
        "times and durations, not vague advice."
    ),
    tools=[get_lifeflow_toolset()],
)
