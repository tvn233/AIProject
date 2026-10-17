import tempfile
import unittest
from pathlib import Path
from src.agent.agent import CTXHAgent

class NoLLM:
    def __init__(self):
        self.calls=0
    def complete(self,*a,**k):
        self.calls+=1
        raise AssertionError('Policy fast-path should not call Groq')

class PatchTests(unittest.TestCase):
    def test_policy_25_points_without_llm(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'prompt.txt';p.write_text('demo',encoding='utf-8')
            llm=NoLLM()
            agent=CTXHAgent(llm,None,prompt_path=p,extra_tools={
                'convert_ctxh_points_policy_tool':lambda points:{'days':2.5,'rounding':'5 = 0.5 ngày','source':'CTXH.md II.c'}
            })
            result=agent.run('Theo quy chế CTXH, 25 điểm được quy đổi thành bao nhiêu ngày?')
            self.assertIn('2.5 ngày',result.answer)
            self.assertEqual(result.trace[0]['name'],'convert_ctxh_points_policy_tool')
            self.assertEqual(llm.calls,0)

if __name__=='__main__':unittest.main()
