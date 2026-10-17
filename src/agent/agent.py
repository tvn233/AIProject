"""Hand-written LLM -> tools -> observation loop, including dynamically discovered MCP tools."""
from __future__ import annotations
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

SEARCH_TOOL = {"type":"function","function":{"name":"search_ctxh_documents","description":"Search CTXH corpus; cite document IDs and avoid unsupported assertions.","parameters":{"type":"object","properties":{"query":{"type":"string"},"mode":{"type":"string","enum":["dense","hybrid"]},"top_k":{"type":"integer","minimum":1,"maximum":5}},"required":["query"]}}}

@dataclass
class AgentResult:
    answer: str
    steps: int
    trace: list[dict] = field(default_factory=list)
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    calls: int = 0
    max_prompt: int = 0

class CTXHAgent:
    def __init__(self, llm: Any, pipeline: Any, *, max_steps: int = 5,
                 prompt_path: str | Path = 'prompts/system_prompt.txt',
                 extra_tools: dict[str, Callable[..., Any]] | None = None,
                 extra_schemas: list[dict] | None = None):
        if max_steps < 1:
            raise ValueError('max_steps phải >= 1')
        self.llm, self.pipeline, self.max_steps = llm, pipeline, max_steps
        self.system_prompt = Path(prompt_path).read_text(encoding='utf-8')
        self.tools = {'search_ctxh_documents': self.search_ctxh_documents}
        self.tools.update(extra_tools or {})
        self.tool_schemas = [SEARCH_TOOL] + (extra_schemas or [])

    def search_ctxh_documents(self, query: str, mode: str = 'hybrid', top_k: int = 3) -> dict:
        if not isinstance(query, str) or not query.strip():
            raise ValueError('query không được rỗng')
        if mode not in ('dense','hybrid'):
            raise ValueError('mode không hợp lệ')
        if isinstance(top_k, bool) or not isinstance(top_k, int) or not 1 <= top_k <= 5:
            raise ValueError('top_k phải từ 1 đến 5')
        results = self.pipeline.retrieve(query, mode=mode, top_k=min(top_k, 3))
        return {'query':query,'mode':mode,'sources':[
            {'doc_id':r.chunk.doc_id,'chunk_id':r.chunk.chunk_id,'section':r.chunk.section,
             'title':r.chunk.title,'version':str(r.chunk.metadata.get('version','?')),
             'content':r.chunk.content[:650]} for r in results],
            'note':'Nếu tài liệu không trực tiếp hỗ trợ kết luận, nói chưa đủ thông tin.'}

    def run(self, question: str) -> AgentResult:
        if not question.strip():
            raise ValueError('Câu hỏi không được rỗng')
        # Deterministic fast-path for explicit CTXH policy conversion: one MCP tool call,
        # zero Groq requests. This is intentionally visible in trace, not disguised as LLM reasoning.
        policy_match = re.search(r'(?<!\d)(\d{1,6})\s*điểm\b', question, flags=re.IGNORECASE)
        wants_days = bool(re.search(r'quy\s*đổi|bao\s*nhiêu\s*ngày|tính\s*ngày', question, re.IGNORECASE))
        policy_tool = self.tools.get('convert_ctxh_points_policy_tool')
        if policy_match and wants_days and policy_tool is not None:
            points = int(policy_match.group(1))
            try:
                observation = policy_tool(points=points)
                ok = isinstance(observation, dict) and observation.get('days') is not None and observation.get('ok') is not False
                trace = [{'step': 1, 'event': 'tool', 'name': 'convert_ctxh_points_policy_tool',
                          'args': {'points': points}, 'ok': ok, 'result': observation}]
                if not ok:
                    return AgentResult('Không thể quy đổi: công cụ MCP trả về lỗi.', 1, trace)
                answer = (f"Theo công cụ quy đổi CTXH (dữ liệu DEMO), {points} điểm = "
                          f"{observation['days']} ngày CTXH. "
                          f"Quy tắc: {observation.get('rounding', 'xem quy chế')}. "
                          f"Nguồn: {observation.get('source', 'quy tắc nội bộ')}. "
                          'Cần đối chiếu với quy định chính thức trước khi áp dụng thực tế.')
                return AgentResult(answer, 1, trace)
            except Exception as exc:
                return AgentResult('Công cụ quy đổi MCP bị lỗi: ' + str(exc)[:180], 1,
                                   [{'step':1,'event':'tool','name':'convert_ctxh_points_policy_tool',
                                     'ok':False,'error':str(exc)[:180]}])
        messages = [{'role':'system','content':self.system_prompt},{'role':'user','content':question}]
        trace = []
        usage = self.llm.usage
        start = (usage.prompt_tokens,usage.completion_tokens,usage.total_tokens,
                 getattr(usage,'calls',0),len(getattr(usage,'prompt_history',None) or []))
        for step in range(1,self.max_steps+1):
            try:
                message = self.llm.complete(messages,tools=self.tool_schemas)
            except Exception as exc:
                trace.append({'step':step,'event':'llm_error','error':str(exc)[:300]})
                return self._result('Error: LLM API không khả dụng. Vui lòng thử lại.',step,trace,start)
            calls = getattr(message,'tool_calls',None) or []
            if not calls:
                answer = (getattr(message,'content',None) or '').strip()
                trace.append({'step':step,'event':'final'})
                return self._result(answer or 'Không có câu trả lời.',step,trace,start)
            messages.append({'role':'assistant','content':getattr(message,'content',None),
                'tool_calls':[{'id':c.id,'type':'function','function':
                    {'name':c.function.name,'arguments':c.function.arguments}} for c in calls]})
            for call in calls:
                name = call.function.name
                try:
                    args = json.loads(call.function.arguments or '{}')
                    if not isinstance(args,dict):
                        raise ValueError('arguments phải là JSON object')
                    if name not in self.tools:
                        raise ValueError('Công cụ không được phép: '+name)
                    if name == 'search_ctxh_documents' and any(
                        x.get('name') == 'search_ctxh_documents' and x.get('ok') for x in trace
                    ):
                        observation = {'note':'Đã tra cứu tài liệu ở bước trước; hãy trả lời từ nguồn đã có hoặc nói không đủ thông tin.', 'sources': []}
                    else:
                        observation = self.tools[name](**args)
                    ok = not (isinstance(observation,dict) and
                              (observation.get('ok') is False or 'error' in observation))
                    trace.append({'step':step,'event':'tool','name':name,'args':args,
                                  'ok':ok,'result':observation})
                except Exception as exc:
                    observation = 'Error: '+str(exc)[:300]
                    trace.append({'step':step,'event':'tool','name':name,'ok':False,'error':str(exc)[:300]})
                messages.append({'role':'tool','tool_call_id':call.id,
                                 'content':json.dumps(observation,ensure_ascii=False,default=str)})
        return self._result('Đã đạt giới hạn bước xử lý. Vui lòng thử lại.',self.max_steps,trace,start)

    def _result(self,answer,steps,trace,start):
        u=self.llm.usage
        return AgentResult(answer,steps,trace,u.prompt_tokens-start[0],
                           u.completion_tokens-start[1],u.total_tokens-start[2],
                           getattr(u,'calls',0)-start[3],
                           max((getattr(u,'prompt_history',None) or [])[start[4]:],default=0))
