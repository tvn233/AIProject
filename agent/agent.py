"""Agent Loop tự viết: LLM -> tool -> observation -> LLM (Week 6)."""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "search_ctxh_documents",
        "description": "Tra cứu quy định CTXH từ corpus bằng Dense hoặc Hybrid. Phải gọi trước khi trả lời câu hỏi về quy định CTXH.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Câu hỏi cần tra cứu"},
                "mode": {"type": "string", "enum": ["dense", "hybrid"]},
                "top_k": {"type": "integer", "minimum": 1, "maximum": 5}
            },
            "required": ["query"]
        }
    }
}

@dataclass
class AgentResult:
    answer: str
    steps: int
    trace: list[dict] = field(default_factory=list)
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

class CTXHAgent:
    def __init__(self, llm: Any, pipeline: Any, *, max_steps: int = 5,
                 prompt_path: str | Path = "prompts/system_prompt.txt"):
        if max_steps < 1:
            raise ValueError("max_steps phải >= 1")
        self.llm = llm
        self.pipeline = pipeline
        self.max_steps = max_steps
        self.system_prompt = Path(prompt_path).read_text(encoding="utf-8")
        # Ngày 3 thêm công cụ MCP tại đây, không phải viết lại agent loop.
        self.tools: dict[str, Callable[..., Any]] = {
            "search_ctxh_documents": self.search_ctxh_documents
        }
        self.tool_schemas = [SEARCH_TOOL]

    def search_ctxh_documents(self, query: str, mode: str = "hybrid", top_k: int = 3) -> dict:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query không được rỗng")
        if mode not in ("dense", "hybrid"):
            raise ValueError("mode chỉ nhận dense hoặc hybrid")
        if not isinstance(top_k, int) or not 1 <= top_k <= 5:
            raise ValueError("top_k phải trong khoảng 1..5")
        results = self.pipeline.retrieve(query, mode=mode, top_k=top_k)
        return {
            "query": query,
            "mode": mode,
            "sources": [
                {"doc_id": r.chunk.doc_id, "chunk_id": r.chunk.chunk_id,
                 "section": r.chunk.section, "title": r.chunk.title,
                 "version": str(r.chunk.metadata.get("version", "?")),
                 "content": r.chunk.content[:1500]}
                for r in results
            ],
            "note": "Nếu không có bằng chứng trực tiếp, phải trả lời chưa đủ thông tin."
        }

    def run(self, question: str) -> AgentResult:
        if not question.strip():
            raise ValueError("Câu hỏi không được rỗng")
        messages: list[dict] = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": question}
        ]
        trace: list[dict] = []
        start_usage = (
            self.llm.usage.prompt_tokens, self.llm.usage.completion_tokens,
            self.llm.usage.total_tokens
        )
        for step in range(1, self.max_steps + 1):
            message = self.llm.complete(messages, tools=self.tool_schemas)
            calls = getattr(message, "tool_calls", None) or []
            if not calls:
                answer = (getattr(message, "content", None) or "").strip()
                trace.append({"step": step, "event": "final"})
                return self._result(answer or "AI chưa trả về câu trả lời.", step, trace, start_usage)

            # Ghi nguyên assistant tool_calls để tool_call_id khớp kết quả.
            messages.append({
                "role": "assistant", "content": getattr(message, "content", None),
                "tool_calls": [
                    {"id": c.id, "type": "function", "function": {
                        "name": c.function.name, "arguments": c.function.arguments}}
                    for c in calls
                ]
            })
            for call in calls:
                name = call.function.name
                try:
                    args = json.loads(call.function.arguments or "{}")
                    if not isinstance(args, dict):
                        raise ValueError("arguments phải là JSON object")
                    if name not in self.tools:
                        raise ValueError(f"Công cụ không được phép: {name}")
                    observation = self.tools[name](**args)
                    trace.append({"step": step, "event": "tool", "name": name,
                                  "args": args, "ok": True})
                except (ValueError, TypeError, KeyError) as exc:
                    observation = {"error": str(exc)}
                    trace.append({"step": step, "event": "tool", "name": name,
                                  "ok": False, "error": str(exc)})
                messages.append({"role": "tool", "tool_call_id": call.id,
                                 "content": json.dumps(observation, ensure_ascii=False)})
        return self._result("Đã đạt giới hạn bước xử lý. Vui lòng thử lại.",
                            self.max_steps, trace, start_usage)

    def _result(self, answer: str, steps: int, trace: list[dict], start: tuple) -> AgentResult:
        usage = self.llm.usage
        return AgentResult(answer=answer, steps=steps, trace=trace,
                           prompt_tokens=usage.prompt_tokens-start[0],
                           completion_tokens=usage.completion_tokens-start[1],
                           total_tokens=usage.total_tokens-start[2])
