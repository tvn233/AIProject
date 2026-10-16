"""Groq client: timeout, retry và đếm token theo Week 2/6."""
from __future__ import annotations
import os
import time
from dataclasses import dataclass
from typing import Any
from dotenv import load_dotenv

load_dotenv()

@dataclass
class TokenUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    def add(self, usage: Any) -> None:
        if usage is None:
            return
        self.prompt_tokens += int(getattr(usage, "prompt_tokens", 0) or 0)
        self.completion_tokens += int(getattr(usage, "completion_tokens", 0) or 0)
        self.total_tokens += int(getattr(usage, "total_tokens", 0) or 0)

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
