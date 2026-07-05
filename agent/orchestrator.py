"""
orchestrator.py — LifeFlow root agent.

Concept demonstrated: Agent / Multi-agent system (ADK), Day 1 & 3.

The root agent doesn't do any domain work itself. It's a router: given a
user's message, it decides whether this is a scheduling question, a habit
to log, a spending question, or a mix, and delegates to the right
sub_agent(s). This mirrors the "Factory Model" idea from Day 5 — the
human (you) defines the system of specialists and hands-off criteria;
the agents do the work.

Run it with the ADK CLI/dev UI:
    adk web        # opens a local chat UI against this agent
    adk run agent  # headless run in the terminal
"""

from google.adk.agents import Agent

from .sub_agents.budget_agent import budget_agent
from .sub_agents.habits_agent import habits_agent
from .sub_agents.schedule_agent import schedule_agent

root_agent = Agent(
    name="lifeflow_concierge",
    model="gemini-2.5-flash",
    description=(
        "A personal concierge agent that helps a user optimize their day across "
        "schedule, habits, and everyday spending — while keeping all personal "
        "data local and private."
    ),
    instruction=(
        "You are LifeFlow, a personal daily-life concierge. You coordinate three "
        "specialists: schedule_agent (calendar and free time), habits_agent "
        "(habit logging and streaks), and budget_agent (everyday spending). "
        "Route the user's request to the right specialist(s) and combine their "
        "answers into one clear, friendly response. If a request touches more "
        "than one area — e.g. 'I have $15 and 30 free minutes, what should I do "
        "for a healthy break?' — call multiple specialists and synthesize. "
        "Never fabricate data (schedule times, spending totals, habit history); "
        "always retrieve it through the specialists' tools. Keep replies concise "
        "and actionable — this is a daily-use assistant, not an essay writer."
    ),
    sub_agents=[schedule_agent, habits_agent, budget_agent],
)
