from __future__ import annotations
import json, sys
from typing import Any
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from src.agent import Agent
from src.llm import LLMClient, LLMError

console = Console()

def _short(d, limit=120):
    s = json.dumps(d, ensure_ascii=False)
    return s if len(s) <= limit else s[:limit-1] + "..."

def _on_step(name, args, result):
    if name == "ask_user":
        return
    ok = result is None or result.get("ok", True)
    color = "cyan" if ok else "red"
    console.print(f"[{color}]-> {name}[/]([dim]{_short(args)}[/]) [dim]{_short(result or {})}[/]")

def _ask_user(question):
    return Prompt.ask(f"[yellow]?[/] {question}").strip()

def _run_one(agent, request):
    console.print(Panel(request, title="Task", border_style="blue"))
    try:
        answer = agent.run(request)
    except LLMError as exc:
        console.print(f"[red]LLM error:[/] {exc}")
        return
    console.print(Panel(Markdown(answer), title="Result", border_style="green"))

def main():
    load_dotenv()
    try:
        llm = LLMClient()
    except LLMError as exc:
        console.print(f"[red]Setup error:[/] {exc}")
        return 1
    agent = Agent(llm=llm, ask_user=_ask_user, on_step=_on_step)
    if len(sys.argv) > 1:
        _run_one(agent, " ".join(sys.argv[1:]))
        return 0
    console.print(Panel.fit(
        "Task Execution AI Agent\nType your request, or 'exit' to quit.\n\n"
        "[dim]Examples:\n"
        "  - Book me a dentist next week after 5pm\n"
        "  - Find 3 coworking spaces in Warsaw under $20/day\n"
        "  - Plan a 2-day trip to Prague under 300 euro[/dim]",
        border_style="magenta"
    ))
    while True:
        try:
            request = Prompt.ask("\n[bold magenta]you[/]").strip()
        except (EOFError, KeyboardInterrupt):
            return 0
        if not request:
            continue
        if request.lower() in {"exit", "quit", "q"}:
            return 0
        _run_one(agent, request)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())