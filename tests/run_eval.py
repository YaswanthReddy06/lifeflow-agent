"""
run_eval.py — a lightweight evaluation harness for LifeFlow.

Day 3/4 concept demonstrated: skills and agents must be evaluated before
being trusted with more autonomy — the course's "golden dataset + scoring
before promotion to Action-Allowed" idea, and Day 4's "evaluation across
multiple dimensions, not just pass/fail."

This is a genuinely simplified version of that idea — it is NOT the full
LLM-as-judge, multi-dimension trajectory scoring described in the course.
It is honestly labeled as a lighter-weight pattern check: for each
scenario, it runs the REAL agent against the REAL Gemini API (this needs
your GOOGLE_API_KEY in .env) and checks whether the expected tool(s) were
actually called during the run — a basic but real trajectory check, not
just a check of the final text.

Run it with:
    python tests/run_eval.py

This is separate from tests/test_agent.py (which is fast, free, and needs
no API key) because it makes real LLM calls and is meant to be run
occasionally, not on every commit.
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from google.adk.runners import InMemoryRunner
from google.genai import types

from agent.orchestrator import root_agent

SCENARIOS = [
    {
        "name": "schedule_lookup",
        "prompt": "What's on my schedule today, and when's my next free 30 minutes?",
        "expected_tool_calls": ["get_today_schedule", "find_free_time"],
    },
    {
        "name": "simple_habit_log",
        "prompt": "I just took my vitamins.",
        "expected_tool_calls": ["log_habit"],
    },
    {
        "name": "low_value_expense",
        "prompt": "I spent $12 on coffee today, log it under food.",
        "expected_tool_calls": ["log_expense"],
    },
    {
        "name": "cross_agent_synthesis",
        "prompt": "I have 30 minutes and $15 free right now — what's a healthy break I could take?",
        "expected_tool_calls": ["transfer_to_agent"],
    },
]


def _extract_tool_calls(events) -> list[str]:
    names = []
    for event in events:
        for call in getattr(event, "get_function_calls", lambda: [])():
            names.append(call.name)
    return names


async def run_scenario(runner: InMemoryRunner, scenario: dict) -> dict:
    session = await runner.session_service.create_session(
        app_name=runner.app_name, user_id="eval_user"
    )
    message = types.Content(role="user", parts=[types.Part(text=scenario["prompt"])])

    events = []
    async for event in runner.run_async(
        user_id="eval_user", session_id=session.id, new_message=message
    ):
        events.append(event)

    called = _extract_tool_calls(events)
    expected = scenario["expected_tool_calls"]
    hit = any(exp in called for exp in expected)

    final_text = ""
    for event in reversed(events):
        if event.content and event.content.parts:
            texts = [p.text for p in event.content.parts if getattr(p, "text", None)]
            if texts:
                final_text = texts[-1]
                break

    return {
        "scenario": scenario["name"],
        "prompt": scenario["prompt"],
        "expected_tool_calls": expected,
        "actual_tool_calls": called,
        "trajectory_ok": hit,
        "final_response": final_text,
        "no_fabrication_note": "Manually verify: does final_response reference only data that came from a real tool result above?",
    }


async def main():
    runner = InMemoryRunner(agent=root_agent, app_name="lifeflow_eval")
    results = []
    for scenario in SCENARIOS:
        print(f"Running: {scenario['name']}...")
        result = await run_scenario(runner, scenario)
        results.append(result)
        status = "PASS" if result["trajectory_ok"] else "FAIL"
        print(f"  [{status}] expected one of {result['expected_tool_calls']}, got {result['actual_tool_calls']}")

    passed = sum(1 for r in results if r["trajectory_ok"])
    print(f"\n{passed}/{len(results)} scenarios called an expected tool.")
    print("Note: this checks TRAJECTORY (were the right tools used), not final wording quality —")
    print("read each final_response below and judge for yourself if it's a good answer.")

    out_path = Path(__file__).resolve().parent / "eval_results.json"
    out_path.write_text(json.dumps(results, indent=2))
    print(f"\nFull results (including final_response text) written to {out_path}")


if __name__ == "__main__":
    asyncio.run(main())
