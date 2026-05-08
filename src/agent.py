from __future__ import annotations
import json
import os
from typing import Any, Callable
from src.llm import LLMClient
from src.prompts import SYSTEM
from src.tools import TOOL_FUNCTIONS, TOOL_SCHEMAS

MAX_STEPS = int(os.getenv("AGENT_MAX_STEPS", "10"))

class Agent:
    def __init__(self, llm: LLMClient, ask_user: Callable, on_step: Callable) -> None:
        self._llm = llm
        self._ask_user = ask_user
        self._on_step = on_step
        self._messages = []

    def run(self, user_request: str) -> str:
        self._messages = [{"role": "user", "content": user_request}]
        return self._loop()

    def _loop(self) -> str:
        for _ in range(MAX_STEPS):
            response = self._llm.chat(messages=self._messages, tools=TOOL_SCHEMAS, system=SYSTEM)
            if response.stop_reason == "end_turn":
                text = self._extract_text(response.content)
                self._messages.append({"role": "assistant", "content": response.content})
                return text
            if response.stop_reason == "tool_use":
                self._messages.append({"role": "assistant", "content": response.content})
                tool_results = self._execute_all(response.content)
                self._messages.append({"role": "user", "content": tool_results})
                continue
            return f"[Agent stopped: stop_reason={response.stop_reason}]"
        return "Reached maximum steps without completing the task."

    def _execute_all(self, content_blocks) -> list:
        results = []
        for block in content_blocks:
            if block.type != "tool_use":
                continue
            result_content = self._execute_one(block.name, block.input, block.id)
            results.append({"type": "tool_result", "tool_use_id": block.id, "content": result_content})
        return results

    def _execute_one(self, name: str, args: dict, tool_use_id: str) -> str:
        if name == "ask_user":
            question = args.get("question", "")
            self._on_step(name, args, None)
            answer = self._ask_user(question)
            return json.dumps({"ok": True, "answer": answer})
        fn = TOOL_FUNCTIONS.get(name)
        if fn is None:
            result = {"ok": False, "error": f"Unknown tool: '{name}'."}
            self._on_step(name, args, result)
            return json.dumps(result)
        try:
            result = fn(**args)
        except Exception as exc:
            result = {"ok": False, "error": str(exc)}
        self._on_step(name, args, result)
        return json.dumps(result, default=str)

    @staticmethod
    def _extract_text(content_blocks) -> str:
        return "\n".join(b.text for b in content_blocks if hasattr(b, "text")).strip()