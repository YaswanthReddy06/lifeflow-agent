"""
budget_agent.py — specialist sub-agent for everyday spending decisions.
"""

from google.adk.agents import Agent

from ..mcp_connection import get_lifeflow_toolset

budget_agent = Agent(
    name="budget_agent",
    model="gemini-2.5-flash",
    description="Logs expenses and gives a quick spending summary by category.",
    instruction=(
        "You are the Budget specialist for a personal concierge system. "
        "Use log_expense to record spending and get_spending_summary to report "
        "totals by category. Never invent amounts — if the user doesn't give a "
        "number, ask for it once, briefly. Keep summaries to 2-3 sentences."
    ),
    tools=[get_lifeflow_toolset()],
)
