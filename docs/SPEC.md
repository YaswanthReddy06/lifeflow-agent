# LifeFlow Behavior Spec (Gherkin-style)

*Day 5 concept: Behavior-Driven Development using Given/When/Then forces
thinking in terms of State → Action → Outcome, instead of "vibe guessing"
at what an agent should do. These scenarios describe LifeFlow's actual,
tested behavior — they are documentation of what the code does, written
in this format for clarity, not a separate automated BDD test runner.*

## Feature: Schedule lookups

```gherkin
Scenario: User asks what's free today
  Given the user's schedule has 4 blocks between 07:00 and 13:15
  When the user asks "What's on my schedule today, and when's my next free 30 minutes?"
  Then the root agent routes to schedule_agent
  And schedule_agent calls get_today_schedule and find_free_time(30)
  And the response lists the real schedule blocks, not invented ones
  And the response names a real free-time gap, not a guessed one
```
*(Verified working live — see the project screenshots in
LifeFlow_Project_Explained.docx, Figure 1 walkthrough.)*

## Feature: Habit logging

```gherkin
Scenario: User logs a simple habit with no follow-up question
  Given the user says "I just took my vitamins."
  When the root agent routes to habits_agent
  Then habits_agent calls log_habit("Vitamins")
  And the habit-streak-coach skill does NOT activate
    (because no streak/consistency question was asked)
  And the response is a short acknowledgment, not a streak analysis

Scenario: User asks about consistency, not just logging
  Given the user has multiple habit log entries for "Vitamins" this week
  When the user asks "How am I doing with my vitamins this week?"
  Then habits_agent calls get_habit_history
  And the habit-streak-coach skill DOES activate
  And the response includes a specific streak count, not vague praise
  And the response never fabricates a streak if history is too short
```

## Feature: Expense logging with high-value confirmation

```gherkin
Scenario: Low-value expense logs immediately
  Given the user says "I spent $12 on coffee today, log it under food."
  When budget_agent calls log_expense(amount=12, confirm=False)
  Then the tool returns status="logged"
  And the expense is written to the database immediately

Scenario: High-value expense requires confirmation first
  Given the user says "I spent $75 on shoes, log it under shopping."
  When budget_agent calls log_expense(amount=75, confirm=False)
  Then the tool returns status="confirmation_required"
  And the expense is NOT written to the database yet
  And budget_agent relays the plain_english_action to the user
  And the expense is only written after the user confirms
    and budget_agent calls log_expense again with confirm=True
```
*(This scenario is directly covered by automated tests —
see tests/test_agent.py::test_log_expense_requires_confirmation_above_threshold
and ::test_log_expense_logs_after_confirmation.)*

## Feature: Cross-agent synthesis

```gherkin
Scenario: A request spans more than one specialist
  Given the user has both a schedule and a spending history
  When the user asks "I have 30 minutes and $15 free right now — what's a healthy break I could take?"
  Then the root agent recognizes the request touches more than one domain
  And it calls the relevant specialist(s) rather than guessing an answer
  And it combines their results into one coherent response
  And no schedule time or dollar amount in the response is invented
```
*(Verified working live — see the cross-agent test screenshot in
LifeFlow_Project_Explained.docx, Figure 2.)*

## Feature: Security boundaries

```gherkin
Scenario: A habit note contains something that looks like PII
  Given a user logs a habit with a note containing an email address
  When log_habit calls mask_pii on the note before storage
  Then the stored note has the email replaced with "[redacted-email]"
  And the raw email is never written to the database

Scenario: An invalid or out-of-range amount is submitted
  Given an expense amount is negative or over $100,000
  When log_expense calls validate_amount
  Then a ValidationError is raised
  And nothing is written to the database
```
*(Both covered by automated tests in tests/test_agent.py.)*
