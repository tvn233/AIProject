"""Append real per-question JSONL traces without storing credentials."""
from datetime import datetime, timezone
import json
from pathlib import Path


def append_run(log_path, question, result, *, mode='agent', case_id=None):
    path=Path(log_path)
    path.parent.mkdir(parents=True,exist_ok=True)
    record={'timestamp':datetime.now(timezone.utc).isoformat(),
            'case_id':case_id,'mode':mode,'question':question,'answer':result.answer,
            'steps':result.steps,'trace':result.trace,
            'USAGE':{'calls':result.calls,'prompt_tokens':result.prompt_tokens,
                     'completion_tokens':result.completion_tokens,
                     'total_tokens':result.total_tokens,'max_prompt':result.max_prompt}}
    with path.open('a',encoding='utf-8') as f:
        f.write(json.dumps(record,ensure_ascii=False,default=str)+'\n')
    return record
