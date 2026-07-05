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
        "number, ask for it once, briefly. Keep summaries to 2-3 sentences.\n\n"
        "IMPORTANT — high-value expense confirmation: if log_expense returns "
        "status='confirmation_required', do NOT treat the expense as logged. "
        "Relay the exact plain_english_action text to the user and ask them to "
        "confirm. Only call log_expense again (with confirm=True) if the user "
        "clearly agrees in their next message. If they decline or don't respond "
        "clearly, do not log it."
    ),
    tools=[get_lifeflow_toolset()],
)
