# LifeFlow — a personal Concierge Agent for daily life

**Track:** Concierge Agents
**Course:** Kaggle 5-Day AI Agents: Intensive Vibe Coding Course with Google

## The problem

Most people juggle three things every day that constantly compete for
attention: **time** (what fits in today), **habits** (the small recurring
things — water, meds, exercise — that are easy to forget), and **money**
(everyday spending decisions made in the moment, without context). Existing
apps solve these one at a time — a calendar app, a habit tracker, a budget
app — and none of them talk to each other or reason across them. So when
someone asks a genuinely everyday question like *"I have 30 minutes and $15,
what should I do for a healthy break?"*, no single app can answer it.

## The solution

LifeFlow is a small multi-agent concierge that reasons across all three
areas at once, backed by a private, local data store — nothing leaves your
machine except the LLM call itself.

- **`schedule_agent`** — reads today's calendar, finds real free-time gaps.
- **`habits_agent`** — logs habits, reviews streaks, stays out of medical advice.
- **`budget_agent`** — logs spending, gives quick category summaries.
- **`root_agent` (orchestrator)** — routes a request to the right
  specialist(s) and combines their answers into one response.

All three specialists share one **MCP server** (`mcp_server/server.py`)
that exposes the actual tools (`get_today_schedule`, `find_free_time`,
`log_habit`, `get_habit_history`, `log_expense`, `get_spending_summary`)
over the Model Context Protocol, backed by a local SQLite database.

See `docs/ARCHITECTURE.md` for a full diagram and concept-to-file mapping.

## Course concepts demonstrated

| Concept | Where |
|---|---|
| Multi-agent system (ADK) | `agent/orchestrator.py` + 3 sub-agents |
| MCP Server | `mcp_server/server.py`, consumed via `agent/mcp_connection.py` |
| Security features | `mcp_server/security.py` — input validation, PII masking, range clamping; sub-agent instructions that scope out medical advice |
| Antigravity | Used for local scaffolding and iteration — see below |
| Deployability | `docs/DEPLOYMENT.md` — Cloud Run packaging via `adk deploy` |

## Where Antigravity fits in this build

Antigravity was used during development for the parts that benefit most
from an agentic IDE workflow:
- Scaffolding the initial `agent/` and `mcp_server/` package layout and
  boilerplate (Day 1/2 workflow: "vibe coding" the skeleton, then hand-
  tuning the tool logic and security code).
- Iterating on the sub-agent instructions using the IDE's chat-driven
  edit loop rather than hand-writing every prompt draft.
- It is **not** used at runtime — once built, the agent runs on plain
  `google-adk` + `mcp`, so it works the same whether or not you have
  Antigravity installed. This was a deliberate choice given Antigravity
  quota limits during the course window; the demo video shows the
  scaffolding step and explains this tradeoff.

## Setup

```bash
git clone <your-repo-url>
cd lifeflow-agent
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then add your Gemini API key from https://aistudio.google.com/app/apikey
```

## Running it

```bash
adk web          # opens a local chat UI against agent/ (root_agent)
# or headless:
adk run agent
```

Try asking it things like:
- "What's on my schedule today, and when's my next free 30 minutes?"
- "I just took my vitamins."
- "I spent $12 on coffee today, log it under food."
- "I have 30 minutes and $15 — what's a healthy break I could take?" (this one exercises all three specialists at once)

## Running the tests (no API key required)

```bash
pip install pytest
pytest tests/ -v
```

These cover the MCP tool logic and the security validation directly,
independent of the LLM, so correctness can be verified without credentials.

## Project layout

```
lifeflow-agent/
├── agent/
│   ├── orchestrator.py       # root_agent — the multi-agent router
│   ├── mcp_connection.py     # ADK <-> MCP server wiring
│   └── sub_agents/
│       ├── schedule_agent.py
│       ├── habits_agent.py
│       └── budget_agent.py
├── mcp_server/
│   ├── server.py             # MCP tools
│   ├── db.py                 # local SQLite persistence
│   └── security.py           # validation + PII masking
├── tests/test_agent.py
├── docs/
│   ├── ARCHITECTURE.md
│   └── DEPLOYMENT.md
├── requirements.txt
├── .env.example
└── README.md
```

## Privacy & security notes

- All personal data (schedule, habits, spending) lives in a local SQLite
  file that never leaves the machine — only tool-call arguments the LLM
  chooses to send go over the network, not raw database contents.
- All tool inputs are validated and length-clamped before touching storage.
- A conservative PII-masking pass strips anything resembling an email,
  phone number, or long ID sequence out of free-text notes before they're
  persisted.
- The habits agent is explicitly instructed not to give medical advice —
  it logs facts, it doesn't interpret them.
- No API keys or secrets are committed; `.env` is git-ignored, `.env.example`
  is the template.
