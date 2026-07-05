---
name: habit-streak-coach
description: Use this skill whenever a user logs a habit AND asks about their consistency, streak, or progress over time — not for a single one-off log with no follow-up question. Triggers on phrases like "how am I doing with", "what's my streak", "have I been consistent with", or a habit log immediately followed by a progress question.
---

# Habit Streak Coach

This skill teaches an agent how to turn raw habit-history rows (from
`get_habit_history`) into an encouraging, honest streak summary — instead
of just dumping a list of timestamps back at the user.

## When to use this

Trigger this skill only when the user's request needs *interpretation* of
habit history, not just a log action. Examples that SHOULD trigger it:
- "How am I doing with my vitamins this week?"
- "Have I been consistent with meditation lately?"
- "What's my water-drinking streak?"

Examples that should NOT trigger it (just use `log_habit` directly, no
interpretation needed):
- "I just took my vitamins." (a simple log — no streak question asked)
- "Log that I meditated." (same — direct action, not a progress question)

## How to compute a streak (procedural steps)

1. Call `get_habit_history` for the specific habit name the user asked about.
   If they didn't name one, ask which habit before proceeding — don't guess.
2. Sort the returned entries by `logged_at`, oldest to newest.
3. A "streak" is the count of consecutive calendar days with at least one
   log of that habit, counting backward from today. A single gap day
   breaks the streak back to zero for the purpose of the current count,
   but the longest historical streak can still be reported separately.
4. Do not fabricate a streak number if `get_habit_history` returns fewer
   than 2 entries — say there isn't enough history yet instead of guessing.

## How to phrase the response

- Lead with the number, then one honest, specific observation — not
  generic cheerleading. Good: "You're on a 4-day streak with vitamins —
  nice consistency this week." Avoid: "Great job, keep it up!!!" with no
  actual number attached.
- If the streak broke recently, say so plainly and without judgment:
  "Your streak reset yesterday — you're back to day 1 today." Never guilt
  or shame the user about a gap; the goal is honest tracking, not pressure.
- Keep the whole response to 1-2 sentences. This is a daily-use assistant,
  not a wellness essay.

## Example

**User:** "How am I doing with my vitamins this week?"

**Reasoning:** This asks for interpretation of history, not a log action
→ this skill applies. Call `get_habit_history`, filter for "Vitamins"
entries in the last 7 days, count consecutive days.

**Good response:** "You've logged vitamins 5 of the last 7 days, including
today — a 3-day streak right now after one gap on Tuesday."
