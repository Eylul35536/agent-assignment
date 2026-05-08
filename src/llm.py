from __future__ import annotations
import os
from openai import OpenAI

DEFAULT_MODEL = "llama-3.3-70b-versatile"

class LLMError(Exception):
    pass

class LLMClient:
    def __init__(self) -> None:
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise LLMError("ANTHROPIC_API_KEY is not set in .env")
        self.model = os.getenv("ANTHROPIC_MODEL", DEFAULT_MODEL)
        self._client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
        )

    def chat(self, messages, tools, system):
        try:
            # Convert Anthropic message format to OpenAI format
            oai_messages = [{"role": "system", "content": system}]
            for m in messages:
                if isinstance(m["content"], str):
                    oai_messages.append({"role": m["role"], "content": m["content"]})
                elif isinstance(m["content"], list):
                    for block in m["content"]:
                        if hasattr(block, "type"):
                            if block.type == "text":
                                oai_messages.append({"role": "assistant", "content": block.text})
                            elif block.type == "tool_use":
                                import json
                                oai_messages.append({
                                    "role": "assistant",
                                    "content": None,
                                    "tool_calls": [{
                                        "id": block.id,
                                        "type": "function",
                                        "function": {
                                            "name": block.name,
                                            "arguments": json.dumps(block.input)
                                        }
                                    }]
                                })
                        elif isinstance(block, dict) and block.get("type") == "tool_result":
                            import json
                            oai_messages.append({
                                "role": "tool",
                                "tool_call_id": block["tool_use_id"],
                                "content": block["content"] if isinstance(block["content"], str) else json.dumps(block["content"])
                            })

            # Convert Anthropic tool schemas to OpenAI format
            oai_tools = []
            for t in tools:
                oai_tools.append({
                    "type": "function",
                    "function": {
                        "name": t["name"],
                        "description": t["description"],
                        "parameters": t["input_schema"]
                    }
                })

            response = self._client.chat.completions.create(
                model=self.model,
                messages=oai_messages,
                tools=oai_tools,
                tool_choice="auto",
            )
            return GroqResponse(response)
        except Exception as exc:
            raise LLMError(str(exc)) from exc


class GroqResponse:
    """Wraps OpenAI response to match Anthropic response interface."""
    def __init__(self, response):
        import json
        self._response = response
        choice = response.choices[0]
        self.content = []

        if choice.message.content:
            self.content.append(TextBlock(choice.message.content))

        if choice.message.tool_calls:
            for tc in choice.message.tool_calls:
                self.content.append(ToolUseBlock(
                    id=tc.id,
                    name=tc.function.name,
                    input=json.loads(tc.function.arguments)
                ))

        finish = choice.finish_reason
        self.stop_reason = "tool_use" if finish == "tool_calls" else "end_turn"


class TextBlock:
    def __init__(self, text):
        self.type = "text"
        self.text = text

class ToolUseBlock:
    def __init__(self, id, name, input):
        self.type = "tool_use"
        self.id = id
        self.name = name
        self.input = input