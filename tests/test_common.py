import json,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from src.agent.agent import CTXHAgent
from src.agent.llm_client import TokenUsage
from src.agent.logging_utils import append_run
from src.mcp.tools import convert_ctxh_points_policy
from scripts.evaluate import load_cases

class FakeLLM:
    def __init__(self,messages):self.messages=messages;self.usage=TokenUsage()
    def complete(self,messages,tools=None):
        self.usage.add(SimpleNamespace(prompt_tokens=10,completion_tokens=4,total_tokens=14))
        return self.messages.pop(0)

class CommonTests(unittest.TestCase):
    def test_policy_rounding(self):
        self.assertEqual([convert_ctxh_points_policy(n)['days'] for n in [14,15,16,25,26]],
                         [1,1.5,2,2.5,3])
    def test_testset_size(self):
        cases=load_cases()
        self.assertGreaterEqual(len(cases),12)
        self.assertGreaterEqual(sum(c['no_answer'] for c in cases),4)
    def test_mcp_tool_dispatch_and_trace(self):
        with tempfile.TemporaryDirectory() as tmp:
            prompt=Path(tmp)/'prompt.txt';prompt.write_text('demo',encoding='utf-8')
            call=SimpleNamespace(id='c1',function=SimpleNamespace(name='demo_read',arguments='{}'))
            llm=FakeLLM([SimpleNamespace(content=None,tool_calls=[call]),
                         SimpleNamespace(content='Đã tra cứu demo',tool_calls=[])])
            schema={'type':'function','function':{'name':'demo_read','description':'demo',
                    'parameters':{'type':'object','properties':{}}}}
            agent=CTXHAgent(llm,None,prompt_path=prompt,
                            extra_tools={'demo_read':lambda: {'found':True}},extra_schemas=[schema])
            result=agent.run('Kiểm tra')
            self.assertEqual(result.trace[0]['result'],{'found':True})
            self.assertEqual(result.calls,2)
            log=Path(tmp)/'run.jsonl';append_run(log,'Kiểm tra',result)
            saved=json.loads(log.read_text(encoding='utf-8'))
            self.assertEqual(saved['USAGE']['calls'],2)
    def test_invalid_tool_arguments_no_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            prompt=Path(tmp)/'p.txt';prompt.write_text('demo',encoding='utf-8')
            call=SimpleNamespace(id='c1',function=SimpleNamespace(name='demo_read',arguments='{oops'))
            llm=FakeLLM([SimpleNamespace(content=None,tool_calls=[call]),SimpleNamespace(content='Không thể',tool_calls=[])])
            agent=CTXHAgent(llm,None,prompt_path=prompt)
            result=agent.run('Demo')
            self.assertFalse(result.trace[0]['ok'])

if __name__=='__main__':unittest.main()
