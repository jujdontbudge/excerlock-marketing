"""Mem0 custom LLM provider. No API keys, sockets or credentials handled here."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from mem0.llms.base import LLMBase
from mem0.llms.configs import LlmConfig
from pydantic import field_validator


class PiLunaConfig(LlmConfig):
    # Mem0's factory supports custom providers; its stock Pydantic validator has a
    # static allowlist. Override that validator, without modifying vendor files.
    @field_validator("config")
    @classmethod
    def validate_config(cls, value: dict[str, Any], info: Any) -> dict[str, Any]:
        if info.data.get("provider") != "pi_luna":
            raise ValueError("Only the pi_luna provider is permitted")
        if value.get("model") != "gpt-5.6-luna":
            raise ValueError("Exact GPT-5.6 Luna model required")
        return value


class PiLunaLLM(LLMBase):
    last_request: dict[str, Any] | None = None

    def generate_response(self, messages: list[dict[str, str]], tools=None, tool_choice="auto", **kwargs: Any) -> str:
        if tools:
            raise ValueError("Memory extraction is tool-free")
        proc = subprocess.run(
            ["node", str(Path(__file__).with_name("luna-bridge.mjs"))],
            input=json.dumps({"messages": messages}), text=True, capture_output=True,
            timeout=170, check=False,
        )
        if proc.returncode:
            raise RuntimeError("Pi Luna bridge failed; check subscription authentication/model access")
        result = json.loads(proc.stdout)
        self.last_request = {k: result.get(k) for k in ("model", "reasoning", "responseStatus", "stopReason", "usage")}
        if result.get("model") != "gpt-5.6-luna" or result.get("reasoning") != "max":
            raise RuntimeError("Model/reasoning mismatch")
        # Reject malformed extraction responses rather than letting Mem0 silently
        # turn a parsing failure into a successful empty write.
        parsed = json.loads(result["text"])
        memories = parsed.get("memory")
        if not isinstance(memories, list) or len(memories) > 30:
            raise ValueError("Invalid extraction schema")
        for memory in memories:
            if not isinstance(memory, dict) or not isinstance(memory.get("text"), str) or not 1 <= len(memory["text"]) <= 4000:
                raise ValueError("Invalid extracted memory")
        return result["text"]
