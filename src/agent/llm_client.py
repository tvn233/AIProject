"""Groq client: timeout, retry và đếm token theo Week 2/6."""
from __future__ import annotations
import os
import time
import json
from datetime import datetime, timezone
from pathlib import Path
from dataclasses import dataclass
from typing import Any
from dotenv import load_dotenv

load_dotenv()

@dataclass
class TokenUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    calls: int = 0
    max_prompt: int = 0
    prompt_history: list[int] = None

    def add(self, usage: Any) -> None:
        if self.prompt_history is None:
            self.prompt_history = []
        if usage is None:
            return
        self.prompt_history.append(int(getattr(usage, "prompt_tokens", 0) or 0))
        self.calls += 1
        self.max_prompt = max(self.max_prompt, int(getattr(usage, "prompt_tokens", 0) or 0))
        self.prompt_tokens += int(getattr(usage, "prompt_tokens", 0) or 0)
        self.completion_tokens += int(getattr(usage, "completion_tokens", 0) or 0)
        self.total_tokens += int(getattr(usage, "total_tokens", 0) or 0)

def log_http_error(exc, attempt, model):
    path = Path("logs/http_errors.jsonl")
    path.parent.mkdir(parents=True, exist_ok=True)

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": "llm_api_error",
        "model": model,
        "error_type": type(exc).__name__,
        "status_code": getattr(exc, "status_code", None),
        "attempt": attempt,
    }

    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

class LLMClient:
    def __init__(self, *, client: Any = None, model: str | None = None,
                 timeout: float = 30.0, max_retries: int = 2):
        self.model = model or os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
        self.max_retries = max_retries
        self.usage = TokenUsage()
        if client is None:
            key = os.getenv("GROQ_API_KEY")
            if not key:
                raise RuntimeError("Thiếu GROQ_API_KEY trong .env")
            from groq import Groq
            client = Groq(api_key=key, timeout=timeout, max_retries=0)
        self.client = client

    def complete(self, messages: list[dict], tools: list[dict] | None = None) -> Any:
        kwargs = {"model": self.model, "messages": messages, "temperature": 0.1}
        if tools:
            kwargs.update({"tools": tools, "tool_choice": "auto"})
        for attempt in range(self.max_retries + 1):
            try:
                response = self.client.chat.completions.create(**kwargs)
                self.usage.add(getattr(response, "usage", None))
                return response.choices[0].message
            except Exception as exc:
                log_http_error(exc, attempt + 1, self.model)
                # Chỉ retry lỗi tạm thời, không retry sai key hay request không hợp lệ.
                status = getattr(exc, "status_code", None)
                temporary = status in (408, 409, 429, 500, 502, 503, 504)
                temporary = temporary or isinstance(exc, (TimeoutError, ConnectionError))
                temporary = temporary or exc.__class__.__name__ in (
                    "APITimeoutError", "APIConnectionError", "RateLimitError", "InternalServerError"
                )
                if not temporary or attempt >= self.max_retries:
                    raise
                time.sleep(min(2 ** attempt, 4))
