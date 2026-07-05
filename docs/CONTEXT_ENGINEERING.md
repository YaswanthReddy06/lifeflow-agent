# Context Engineering in LifeFlow

*Day 1 concept: quality depends more on what information an agent has
access to than on clever prompt wording. This file makes that split
explicit for LifeFlow, rather than leaving it implicit in the code.*

## Static context (always loaded, every conversation)

This is context that's present in every single request, regardless of
what the user asks — the "always-on rules."

| Where | What |
|---|---|
| `agent/orchestrator.py` → `instruction=` | The root agent's permanent job description and routing rules. |
| `agent/sub_agents/*.py` → `instruction=` | Each specialist's permanent scope and behavior rules (e.g., habits_agent's standing rule to never give medical advice). |
| `skills/habit-streak-coach/SKILL.md` | Loaded once at import time and folded into `habits_agent`'s static instruction — see the note below on why this is a hybrid case. |

## Dynamic context (loaded only when relevant, per-request)

This is context that's fetched on demand, specific to the current
question — nothing here is "always in memory."

| Where | What |
|---|---|
| `get_today_schedule()` result | Only fetched when a request actually touches scheduling. |
| `find_free_time()` result | Only fetched when a free-time question is asked. |
| `get_habit_history()` result | Only fetched when reviewing past habits, not on every habit log. |
| `get_spending_summary()` result | Only fetched when a spending question is asked, not on every expense log. |

## A hybrid case worth calling out: the Skill file

`skills/habit-streak-coach/SKILL.md` is written as a portable, independently
triggerable skill — in Antigravity, a skill like this would only be loaded
into context when the trigger condition in its description is matched
(true progressive disclosure, per Day 3).

In LifeFlow's current implementation, `habits_agent.py` takes a simpler
approach: it loads the skill's full body once at import time and folds it
permanently into `habits_agent`'s static instruction. This was a
deliberate, pragmatic choice for a small 3-agent project — `habits_agent`
is a narrow specialist, and the added token cost of always having the
streak-coaching procedure available is small.

**The honest tradeoff:** this means the skill's content is technically
static context here, not truly progressively disclosed. A more advanced
version of LifeFlow with many more skills would need real progressive
disclosure — e.g., matching the user's message against each skill's
`description` field first, and only injecting the matching skill's body
for that turn — to avoid the context bloat the course specifically warns
about ("context rot"). This is flagged here rather than glossed over,
since accurately describing the tradeoff is more valuable than overstating
what a 3-agent hobby project actually needs.
