<div align="center">



```

╔══════════════════════════════════════════════════════╗

║                                                      ║

║    🤖  TASK EXECUTION AI AGENT                       ║

║                                                      ║

║    Plans · Asks · Acts · Recovers                    ║

║                                                      ║

╚══════════════════════════════════════════════════════╝

```



\*\*A fully agentic CLI assistant that completes real-world tasks end-to-end.\*\*  

Tell it what you want. It figures out the rest.



\[!\[Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square\&logo=python\&logoColor=white)](https://python.org)

\[!\[uv](https://img.shields.io/badge/uv-managed-DE5FE9?style=flat-square)](https://docs.astral.sh/uv/)

\[!\[Groq](https://img.shields.io/badge/Groq-LLaMA\_3.3\_70B-F55036?style=flat-square)](https://groq.com)

\[!\[License](https://img.shields.io/badge/license-MIT-22C55E?style=flat-square)](LICENSE)



</div>



\---



\## ✦ What it does



You type a natural language request. The agent:



1\. \*\*Understands\*\* your intent and breaks it into subtasks

2\. \*\*Asks\*\* clarifying questions — one at a time, only when needed

3\. \*\*Calls tools\*\* — searches, checks calendars, books, sets reminders

4\. \*\*Recovers\*\* from errors — retries with corrected inputs automatically

5\. \*\*Reports\*\* a clean summary of everything it did



No hand-holding. No manual tool selection. Just results.



\---



\## ✦ Demo



```

you: Book me a dentist next week after 5pm



? What city are you in?

> Warsaw



\-> search\_service({"category": "dentist", "city": "Warsaw"})

\-> calendar\_check({"start\_date": "2025-06-09", "end\_date": "2025-06-13"})



? I found 2 slots — 17:00 or 18:00 on Tuesday. Which do you prefer?

> 17:00



\-> booking\_service({"option\_id": "dent-001", "when": "2025-06-10 17:00"})

\-> reminder\_create({"title": "Dentist appointment", "when": "2025-06-10 16:30"})



╭─────────────────── Result ───────────────────╮

│                                              │

│  ## Task summary                             │

│  \*\*Requested:\*\* Book dentist after 5pm       │

│  \*\*Done:\*\*                                   │

│  - Booked Smile Dental Clinic — BK-84729103  │

│  - Reminder set for 16:30 — REM-52841        │

│                                              │

╰──────────────────────────────────────────────╯

```



\---



\## ✦ Try these



```bash

uv run python main.py "Book me a dentist next week after 5pm"

uv run python main.py "Find 3 coworking spaces in Warsaw under $20/day"

uv run python main.py "Plan a 2-day trip to Prague under €300"

uv run python main.py "Schedule a meeting with John next Tuesday afternoon"

```



Or launch interactive mode and type freely:



```bash

uv run python main.py

```



\---



\## ✦ Architecture



```

agent-assignment/

├── main.py              ← CLI entry point (rich UI, callbacks)

├── src/

│   ├── agent.py         ← Agentic tool-calling loop

│   ├── llm.py           ← Groq/OpenAI-compatible wrapper

│   ├── prompts.py       ← System prompt \& agent instructions

│   └── tools.py         ← Mock tools + JSON schemas

├── pyproject.toml

├── uv.lock

└── .env.example

```



\### The loop



```

User request

&#x20;    │

&#x20;    ▼

&#x20; LLM call ──► tool\_use? ──► execute tool ──► inject result ──┐

&#x20;    │                                                         │

&#x20;    └──► end\_turn ──► Final answer ◄────────────────────────-┘

```



Every tool response goes back into context. The agent reads errors, adjusts, and retries — all without human intervention.



\---



\## ✦ Tools



| Tool | Description |

|------|-------------|

| `calendar\_check(start, end)` | Returns free \& busy slots across a weekday range |

| `search\_service(query, category?, city?, max\_price?)` | Searches the mock catalogue — dentists, coworking, hotels, transport |

| `booking\_service(option\_id, when?, notes?)` | Books a result from search; 10% failure rate forces retry logic |

| `reminder\_create(title, when, notes?)` | Creates a reminder with a unique ID |

| `ask\_user(question)` | \*\*Pseudo-tool\*\* — pauses the loop and prompts the human |



All tools return `{"ok": true, ...}` or `{"ok": false, "error": "..."}`.  

The agent reads the error message and corrects itself — no crash, no silent failure.



\---



\## ✦ Setup



\### Requirements



\- Python 3.11+

\- \[uv](https://docs.astral.sh/uv/) package manager

\- A \[Groq API key](https://console.groq.com) (free)



\### Install



```bash

git clone https://github.com/Eylul35536/agent-assignment.git

cd agent-assignment



\# Install dependencies

uv sync



\# Configure

cp .env.example .env

\# Edit .env → add your ANTHROPIC\_API\_KEY (Groq key works here)

```



\### Run



```bash

uv run python main.py

```



\---



\## ✦ Configuration



| Variable | Default | Description |

|----------|---------|-------------|

| `ANTHROPIC\_API\_KEY` | — | \*\*Required.\*\* Your Groq or Anthropic API key |

| `ANTHROPIC\_MODEL` | `llama-3.3-70b-versatile` | Any model with tool-calling support |

| `AGENT\_MAX\_STEPS` | `10` | Hard cap on tool iterations per task |



\---



\## ✦ Design decisions



\*\*Why a pseudo-tool for clarifications?\*\*  

Using `ask\_user` as a tool keeps the loop uniform. Every model output is either a final message or a tool call — no special-case parsing needed.



\*\*Why mock data instead of real APIs?\*\*  

Zero credentials required, fully reproducible. Replacing `search\_service` with a real provider is a one-function change — the loop doesn't move.



\*\*Why a 10% booking failure rate?\*\*  

To exercise the recovery path on every demo run. You'll see the agent read the error, retry with corrected arguments, and succeed.



\*\*Why cap at 10 steps?\*\*  

A confused model can loop forever re-checking the calendar. A hard cap is the cheapest safety net.



\---



\## ✦ What's next



\- \[ ] Streaming token output for real-time UX

\- \[ ] Persist bookings/reminders to disk across sessions

\- \[ ] Integration tests with recorded LLM responses (pytest + vcrpy)

\- \[ ] Vector search over the catalogue once it grows past \~50 items

\- \[ ] Swap mock tools for real APIs (Google Calendar, Zocdoc, etc.)



\---



<div align="center">



Built for the \*\*Junior AI Agentic Engineer\*\* take-home assignment  

Python · uv · Groq · LLaMA 3.3 · Rich



</div>

