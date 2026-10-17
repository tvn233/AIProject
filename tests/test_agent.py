"""Unit test không cần API key và không tải mô hình E5."""
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from src.agent.agent import CTXHAgent
from src.agent.llm_client import TokenUsage

class FakeLLM:
    def __init__(self, messages):
        self.messages = list(messages)
        self.usage = TokenUsage()
        self.history = []
    def complete(self, messages, tools=None):
        self.history.append(list(messages))
        self.usage.add(SimpleNamespace(prompt_tokens=10, completion_tokens=5, total_tokens=15))
        return self.messages.pop(0)

class FakePipeline:
    def retrieve(self, question, mode="hybrid", top_k=3):
        chunk = SimpleNamespace(doc_id="DOC0001", chunk_id="DOC0001_01",
            section="Quy định chung", title="Quy chế", metadata={"version": "2.0"},
            content="Thông tin minh họa")
        return [SimpleNamespace(chunk=chunk)]

def tool_message(name="search_ctxh_documents", args=None):
    call = SimpleNamespace(id="call_1", function=SimpleNamespace(
        name=name, arguments=json.dumps(args or {"query": "CTXH"})))
    return SimpleNamespace(content=None, tool_calls=[call])

def final_message(text="Trả lời [DOC0001]"):
    return SimpleNamespace(content=text, tool_calls=[])

class AgentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.prompt = Path(self.temp.name) / "prompt.txt"
        self.prompt.write_text("Chỉ trả lời theo công cụ", encoding="utf-8")
    def tearDown(self):
        self.temp.cleanup()
    def test_tool_then_final(self):
        llm = FakeLLM([tool_message(), final_message()])
        result = CTXHAgent(llm, FakePipeline(), prompt_path=self.prompt).run("CTXH?")
        self.assertEqual(result.steps, 2)
        self.assertEqual(result.total_tokens, 30)
        self.assertEqual(result.trace[0]["name"], "search_ctxh_documents")
        self.assertEqual(llm.history[1][-1]["tool_call_id"], "call_1")
    def test_unknown_tool_handled(self):
        llm = FakeLLM([tool_message("bad_tool"), final_message()])
        result = CTXHAgent(llm, FakePipeline(), prompt_path=self.prompt).run("CTXH?")
        self.assertFalse(result.trace[0]["ok"])
    def test_max_steps(self):
        llm = FakeLLM([tool_message()])
        result = CTXHAgent(llm, FakePipeline(), max_steps=1, prompt_path=self.prompt).run("CTXH?")
        self.assertIn("giới hạn", result.answer)

if __name__ == "__main__":
    unittest.main()
