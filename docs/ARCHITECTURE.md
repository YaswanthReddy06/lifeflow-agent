# LifeFlow Architecture

```
                         ┌─────────────────────────┐
                         │        User              │
                         └────────────┬─────────────┘
                                      │ natural language request
                                      ▼
                       ┌───────────────────────────────┐
                       │   root_agent (lifeflow_concierge) │
                       │   ADK orchestrator — routes to     │
                       │   the right specialist(s)          │
                       └───────┬───────────┬───────────┬────┘
                               │           │           │
                 ┌─────────────┘     ┌─────┘     ┌─────┘
                 ▼                   ▼                 ▼
        ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
        │ schedule_agent  │  │ habits_agent    │  │ budget_agent    │
        │ (ADK sub-agent) │  │ (ADK sub-agent) │  │ (ADK sub-agent) │
        └────────┬────────┘  └────────┬────────┘  └────────┬────────┘
                  │                    │                    │
                  └──────────┬─────────┴──────────┬─────────┘
                             ▼                    ▼
                   ┌─────────────────────────────────────┐
                   │      LifeFlow MCP Server (stdio)      │
                   │  tools: get_today_schedule,            │
                   │  find_free_time, log_habit,            │
                   │  get_habit_history, log_expense,       │
                   │  get_spending_summary                  │
                   │  + security.py input validation/PII    │
                   └───────────────────┬───────────────────┘
                                       ▼
                             ┌───────────────────┐
                             │  SQLite (local)     │
                             │  schedule / habits / │
                             │  expenses tables      │
                             └───────────────────┘
```

## Why this shape

- **One root agent, three narrow specialists.** Each sub-agent has a single
  job (schedule, habits, budget), a short focused instruction, and access to
  only the tools it needs. This is easier to prompt reliably and easier to
  evaluate than one giant agent trying to do everything.
- **All tool access goes through one MCP server**, not three separate ones.
  This mirrors a realistic setup where a household/personal MCP server is
  the single source of truth for "my data," and different agents (or even
  different apps) can connect to it the same way.
- **Data never leaves the machine.** No external API calls happen inside
  the MCP server itself — only the LLM call (Gemini) goes out, and only
  with the specific arguments each specialist decides to send, not raw
  database contents. This is the core "safe and secure" requirement for
  the Concierge Agents track.

## Where each course concept lives

| Concept | File(s) |
|---|---|
| Multi-agent system (ADK) | `agent/orchestrator.py`, `agent/sub_agents/*.py` |
| MCP Server | `mcp_server/server.py`, `agent/mcp_connection.py` |
| Security features | `mcp_server/security.py` (validation + PII masking), instructions in each sub-agent that constrain scope (e.g. habits_agent refusing medical advice) |
| Antigravity | Used during development — see main README "Where Antigravity fits" |
| Deployability | `docs/DEPLOYMENT.md` — Cloud Run packaging |
| Agent Skills / Agents CLI | `adk web` / `adk run` lifecycle commands, noted in README |
