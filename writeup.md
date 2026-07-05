# LifeFlow: a private, multi-agent concierge for daily life
### Optimizing time, habits, and money in one conversation — Concierge Agents track

## The problem

Everyday life optimization is fragmented across single-purpose apps: a
calendar app for time, a habit tracker for routines, a budgeting app for
money. None of them can answer a genuinely everyday question that spans
categories — *"I have 30 minutes and $15 free right now, what's a good
healthy break?"* — because none of them can see across the others. Worse,
most of these apps ship your personal schedule, habits, and spending data
to a third-party cloud service just to answer simple questions.

## Why agents

This is a coordination problem, not a single-model problem. Answering a
cross-domain request well means: checking the calendar for a real gap,
checking a spending budget for what's affordable, and possibly logging a
new habit — three distinct lookups with three distinct pieces of domain
judgment. A multi-agent system lets each specialist reason narrowly and
reliably (a schedule agent that only thinks about time, a budget agent
that only thinks about money) while a root orchestrator combines their
outputs into one coherent answer. This is a more reliable pattern than one
large agent trying to hold every domain's nuance in a single prompt.

## Solution: LifeFlow

LifeFlow is a small, local-first concierge built with the Agent
Development Kit (ADK):

- **`root_agent`** — routes each request to the right specialist(s) and
  synthesizes their answers.
- **`schedule_agent`** — reads today's calendar and finds real free-time
  gaps rather than guessing.
- **`habits_agent`** — logs habits (water, medication, exercise) and
  reports streaks, while explicitly staying out of medical advice.
- **`budget_agent`** — logs spending and reports category summaries.

All three specialists connect to a single **MCP server** exposing six
tools (`get_today_schedule`, `find_free_time`, `log_habit`,
`get_habit_history`, `log_expense`, `get_spending_summary`) backed by a
local SQLite database. Nothing about the user's schedule, habits, or
spending leaves the machine — only the specific arguments a specialist
decides are relevant get sent to the LLM as part of the conversation.

## Architecture

```
User → root_agent (orchestrator)
         ├── schedule_agent ─┐
         ├── habits_agent  ──┼──→ LifeFlow MCP Server → SQLite (local)
         └── budget_agent  ─┘
```

Full diagram and concept-to-file mapping in `docs/ARCHITECTURE.md` in the
repo.

## Security

- Every MCP tool validates its inputs (type checks, length clamps, numeric
  range checks) before touching the database — the LLM's output is never
  trusted verbatim.
- A PII-masking pass strips anything resembling an email, phone number, or
  long digit sequence out of free-text notes before they're persisted.
- The habits agent is instructed to log facts only, never interpret or
  advise on medication.
- Expenses at or above $50 require explicit human confirmation before
  being written to the database — `log_expense` returns a plain-English
  description of the action and a `confirmation_required` status instead
  of silently logging it. This mirrors the course's "Vibe Diff" idea:
  translate a high-stakes action into plain language for a human to
  approve before it happens, rather than trusting the agent's judgment
  alone for larger amounts.
- No secrets are committed; API keys load from environment variables via
  `.env` (git-ignored), with `.env.example` as the template.

## Agent Skills

`skills/habit-streak-coach/SKILL.md` is a real, portable skill file (same
format Antigravity uses) that teaches the habits agent how to turn raw
habit-history rows into an honest streak summary — only when the user
asks a consistency/progress question, not on a simple one-off log. It's
loaded and actually used at runtime by `habits_agent.py`, not just a
decorative repo file. `docs/CONTEXT_ENGINEERING.md` documents the honest
tradeoff in how it's loaded (folded into static context at import time,
rather than true per-turn progressive disclosure) — a small project's
pragmatic choice, called out explicitly rather than overstated.

## Evaluation

`tests/run_eval.py` is a lightweight, honestly-labeled evaluation harness
(not the full multi-dimension LLM-as-judge scoring the course describes)
that runs the real agent against 4 scenarios and checks whether the
expected tool was actually called — a basic trajectory check, separate
from the fast/free correctness tests in `tests/test_agent.py`.

## Where Antigravity fit in the build

Antigravity was used for the initial scaffolding of the `agent/` and
`mcp_server/` package structure and for iterating on sub-agent prompt
instructions through its IDE chat-edit loop — the "vibe coding" phase of
the course. The resulting code runs standalone on `google-adk` + `mcp` at
runtime, so the deliverable itself doesn't depend on having Antigravity
installed, which also sidestepped this week's shared quota constraints.

## Deployability

The project is packaged to deploy via `adk deploy cloud_run`, documented
step-by-step in `docs/DEPLOYMENT.md`, including environment variable
handling and cleanup steps to avoid unexpected billing. Deployment wasn't
required for this submission and wasn't executed for the demo, in favor of
a clean local run judges can reproduce exactly from the README.

## What I'd build next

- Move the MCP server to a `StreamableHTTP` transport so it can run as its
  own Cloud Run service, shared across multiple agent front-ends (e.g. a
  mobile app) rather than launched as a local subprocess.
- Add a fourth specialist for meal planning that cross-references the
  budget agent's remaining daily allowance.
- Real calendar integration (Google Calendar MCP) instead of the local
  seeded schedule table, once a production deployment target is settled.

## Try it

Full setup and run instructions are in the repo README — clone, `pip
install -r requirements.txt`, add your own Gemini API key, then `adk web`.
Tests covering the tool logic and security validation run without any API
key: `pytest tests/ -v`.

**Repo:** <ADD YOUR GITHUB LINK HERE>
**Video:** <ADD YOUR YOUTUBE LINK HERE>
