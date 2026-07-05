# Video script — target 4:30–5:00 total

Record your screen with a mic. Read this almost verbatim if you're short
on time; it's timed to fit.

---

**[0:00–0:40] Problem statement**
> "Everyday life optimization is split across apps that can't talk to each
> other. My calendar app doesn't know my budget. My habit tracker doesn't
> know my schedule. So a totally normal question — 'I have 30 minutes and
> $15, what's a healthy break I could take?' — has no app that can answer
> it. That's the problem LifeFlow solves."

**[0:40–1:20] Why agents**
> "This needs coordination across specialists, not one model trying to
> hold every domain in one prompt. So LifeFlow is a multi-agent system: a
> schedule specialist, a habits specialist, a budget specialist, and a
> root agent that routes between them and combines their answers. Each
> agent only has to be good at one narrow thing."

**[1:20–2:30] Architecture (show docs/ARCHITECTURE.md diagram on screen)**
> "Here's the shape of it. [point to diagram] The root agent is built with
> Google's Agent Development Kit — ADK. It has three sub-agents. All three
> connect to one MCP server — this is the Model Context Protocol piece —
> which exposes six tools: read the schedule, find free time, log a habit,
> read habit history, log an expense, get a spending summary. Behind that
> is a local SQLite database — nothing about my schedule or spending
> leaves my machine except what the LLM needs to answer a specific
> question. On the security side [show security.py], every tool input is
> validated and length-checked before it touches the database, and I run
> a PII-masking pass on free-text notes so an email or phone number never
> gets stored raw."

**[2:30–4:00] Live demo**
> "Let's see it work." [run `adk web`, show the chat UI]
> 1. Ask: "What's on my schedule today, and when's my next free 30 minutes?"
>    — show schedule_agent responding with real gap times.
> 2. Ask: "I just took my vitamins." — show habits_agent logging it,
>    note it doesn't comment on dosage.
> 3. Ask: "I spent $12 on coffee today, log it under food." — show
>    budget_agent confirming the log.
> 4. The big one: "I have 30 minutes and $15 free right now — what's a
>    healthy break I could take?" — show the root agent pulling from all
>    three specialists and giving one combined answer.

**[4:00–4:30] The build**
> "I built this with Antigravity for the initial scaffolding — the
> package layout and boilerplate — and for iterating on each agent's
> instructions through its chat-edit loop. At runtime the project just
> needs google-adk and mcp, no Antigravity dependency, since I hit quota
> limits partway through the week like a lot of people this course. It's
> deployable to Cloud Run via `adk deploy` — documented in the repo,
> not executed for this demo to keep things reproducible for judges."

**[4:30–4:50] Close**
> "That's LifeFlow — a private, multi-agent concierge that reasons across
> your day instead of making you check three separate apps. Repo link and
> setup instructions are in the description."

---

## Recording checklist
- [ ] Screen recording software ready (OBS, QuickTime, or Loom)
- [ ] Terminal font size bumped up so it's readable
- [ ] `adk web` running and tested once before recording
- [ ] Diagram from `docs/ARCHITECTURE.md` open/visible for the architecture section
- [ ] Upload to YouTube as **Public** (not Unlisted — Kaggle requires public)
- [ ] Paste the YouTube link into both the Writeup and this repo's README
