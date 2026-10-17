"""Unified CLI: RAG + hand-written Agent Loop + MCP over stdio."""
import argparse
from datetime import datetime
from pathlib import Path
from src.agent.agent import CTXHAgent
from src.agent.llm_client import LLMClient
from src.agent.logging_utils import append_run
from src.rag.rag import RAGPipeline

ROOT=Path(__file__).resolve().parent

def confirm_write(student_id,activity_code):
    print(f'\nXÁC NHẬN: ghi đăng ký DEMO cho {student_id}, hoạt động {activity_code}?')
    return input('Nhập chính xác YES để đồng ý: ').strip() == 'YES'

def build_agent(*, enable_mcp=True, interactive=True):
    print('Đang nạp dữ liệu CTXH và mô hình embedding...')
    pipeline=RAGPipeline.from_corpus(ROOT/'data'/'corpus')
    schemas,handlers=[],{}
    if enable_mcp:
        from src.mcp.bridge import discover_mcp_tools
        schemas,handlers=discover_mcp_tools(confirm_write if interactive else None)
        print('MCP tools:',list(handlers))
    return CTXHAgent(LLMClient(),pipeline,prompt_path=ROOT/'prompts'/'system_prompt.txt',
                     extra_tools=handlers,extra_schemas=schemas)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--no-mcp',action='store_true')
    parser.add_argument('--question',help='Single-shot noninteractive question; write confirmation disabled')
    args=parser.parse_args()
    agent=build_agent(enable_mcp=not args.no_mcp,interactive=args.question is None)
    log_path=ROOT/'logs'/('demo_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'.jsonl')
    print("Trợ lý CTXH sẵn sàng. Gõ 'exit' để thoát. DB đăng ký chỉ là DEMO.")
    while True:
        try:
            question=args.question if args.question is not None else input('\nBạn: ').strip()
        except (EOFError,KeyboardInterrupt):
            print('\nKết thúc.');break
        if question.lower() in ('exit','quit'):
            break
        if question:
            result=agent.run(question)
            print('\nAI:',result.answer)
            print(f'Steps={result.steps} | Tokens={result.total_tokens} | Calls={result.calls}')
            for e in result.trace:
                # Console summary only; detailed trace is still saved to logs/*.jsonl.
                compact = {k:e[k] for k in ('step','event','name','args','ok','error') if k in e}
                if e.get('name') == 'search_ctxh_documents' and isinstance(e.get('result'),dict):
                    compact['sources'] = [x.get('doc_id') for x in e['result'].get('sources',[])]
                if e.get('name') == 'convert_ctxh_points_policy_tool' and isinstance(e.get('result'),dict):
                    compact['days'] = e['result'].get('days')
                if e.get('name') == 'register_ctxh_activity_tool' and isinstance(e.get('result'),dict):
                    compact['verified'] = bool(e['result'].get('verify',{}).get('found'))
                print('TRACE:',compact)
            append_run(log_path,question,result)
            print('Log:',log_path)
        if args.question is not None:
            break

if __name__=='__main__':
    main()
