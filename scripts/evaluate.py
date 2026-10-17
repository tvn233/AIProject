"""CTXH retrieval evaluation + optional live Agent evaluation with progress/checkpoint.

Retrieval hit@k is NOT answer accuracy/faithfulness. Review no-answer manually.
"""
import argparse
import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from src.agent.logging_utils import append_run

ROOT = Path(__file__).resolve().parents[1]
FIELDS = [
    'id', 'mode', 'no_answer', 'expected_docs', 'retrieved_docs',
    'hit_at_k', 'answer', 'refusal_review', 'faithfulness_review',
    'calls', 'prompt_tokens', 'completion_tokens', 'max_prompt',
    'agent_status', 'agent_error', 'elapsed_seconds',
]


def load_cases():
    path = ROOT / 'tests' / 'testset.jsonl'
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def save_csv(path, rows):
    """Write checkpoint atomically after each evaluated case."""
    temp = path.with_suffix('.tmp')
    with temp.open('w', newline='', encoding='utf-8-sig') as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)
    temp.replace(path)


def load_progress(path):
    if not path.exists():
        return {}
    with path.open('r', newline='', encoding='utf-8-sig') as file:
        return {(row['id'], row['mode']): row for row in csv.DictReader(file)}


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--agent', action='store_true', help='Run live Groq Agent evaluation')
    parser.add_argument('--top-k', type=int, default=3)
    parser.add_argument('--mode', choices=['dense', 'hybrid', 'both'], default='both')
    parser.add_argument('--max-cases', type=int, default=0,
                        help='Maximum NEW live agent calls in this run (0=all)')
    parser.add_argument('--resume', action='store_true',
                        help='Resume from logs/eval_live_progress.csv; skip successful cases')
    args = parser.parse_args()
    if args.top_k < 1 or args.max_cases < 0:
        parser.error('--top-k must be >= 1 and --max-cases must be >= 0')

    from src.rag.rag import RAGPipeline
    print('Loading retrieval pipeline...', flush=True)
    pipeline = RAGPipeline.from_corpus(ROOT / 'data' / 'corpus')
    cases = load_cases()
    case_by_id = {str(c['id']): c for c in cases}
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    out = ROOT / 'logs'
    out.mkdir(exist_ok=True)
    modes = ['dense', 'hybrid'] if args.mode == 'both' else [args.mode]
    progress_path = out / 'eval_live_progress.csv'
    prior = load_progress(progress_path) if args.agent and args.resume else {}

    rows = []
    for mode in modes:
        for case in cases:
            retrieved = pipeline.retrieve(case['question'], mode=mode, top_k=args.top_k)
            doc_ids = list(dict.fromkeys(r.chunk.doc_id for r in retrieved))
            expected = case['expected_doc_ids']
            hit = bool(set(expected) & set(doc_ids)) if expected else None
            row = dict.fromkeys(FIELDS, '')
            row.update(id=str(case['id']), mode=mode, no_answer=case['no_answer'],
                       expected_docs='|'.join(expected), retrieved_docs='|'.join(doc_ids),
                       hit_at_k=hit)
            old = prior.get((row['id'], mode))
            if old:
                for field in ('answer', 'refusal_review', 'faithfulness_review', 'calls',
                              'prompt_tokens', 'completion_tokens', 'max_prompt',
                              'agent_status', 'agent_error', 'elapsed_seconds'):
                    row[field] = old.get(field, '')
            rows.append(row)

    if args.agent:
        from main import build_agent
        agent = build_agent(enable_mcp=True, interactive=False)
        log = out / 'eval_live_progress.jsonl'
        save_csv(progress_path, rows)
        pending = [r for r in rows if r['agent_status'] != 'ok']
        if args.max_cases:
            pending = pending[:args.max_cases]
        print(f'Agent evaluation: {len(pending)} pending attempts; {len(rows)} total rows.', flush=True)
        for i, row in enumerate(pending, 1):
            case = case_by_id[row['id']]
            question = case['question'] + ('\nHãy sử dụng tìm kiếm chế độ ' + row['mode'] + ' trước khi trả lời.')
            print(f'[{i}/{len(pending)}] {row["mode"]} | case {row["id"]}: {case["question"]}', flush=True)
            started = time.monotonic()
            try:
                result = agent.run(question)
                answer = str(getattr(result, 'answer', '') or '')
                if answer.strip().lower().startswith('error:'):
                    raise RuntimeError(answer)
                append_run(log, question, result, mode=row['mode'], case_id=row['id'])
                row.update(answer=answer, calls=getattr(result, 'calls', ''),
                           prompt_tokens=getattr(result, 'prompt_tokens', ''),
                           completion_tokens=getattr(result, 'completion_tokens', ''),
                           max_prompt=getattr(result, 'max_prompt', ''),
                           agent_status='ok', agent_error='')
                print(f'  OK in {time.monotonic()-started:.1f}s', flush=True)
            except KeyboardInterrupt:
                row.update(agent_status='interrupted', agent_error='KeyboardInterrupt')
                print('  Interrupted; saving checkpoint.', flush=True)
                break
            except Exception as exc:
                row.update(agent_status='error', agent_error=f'{type(exc).__name__}: {exc}')
                print(f'  ERROR: {type(exc).__name__}: {exc}', flush=True)
            finally:
                row['elapsed_seconds'] = round(time.monotonic() - started, 2)
                save_csv(progress_path, rows)
        print('Checkpoint:', progress_path, flush=True)

    csv_path = out / ('eval_' + stamp + '.csv')
    save_csv(csv_path, rows)
    summary = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'total_cases': len(cases),
        'no_answer_cases': sum(bool(c['no_answer']) for c in cases),
        'top_k': args.top_k,
        'live_agent': args.agent,
        'modes': {},
    }
    for mode in modes:
        subset = [r for r in rows if r['mode'] == mode and not r['no_answer']]
        summary['modes'][mode] = {
            'retrieval_hit_at_k': sum(bool(r['hit_at_k']) for r in subset) / len(subset) if subset else None,
            'count_answerable': len(subset),
        }
    if args.agent:
        summary['agent_completed'] = sum(r['agent_status'] == 'ok' for r in rows)
        summary['agent_errors'] = sum(r['agent_status'] == 'error' for r in rows)
        summary['agent_pending'] = sum(r['agent_status'] not in ('ok', 'error') for r in rows)
    (out / ('eval_' + stamp + '.json')).write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    print('CSV:', csv_path, flush=True)
    if args.agent:
        print('QUAN TRỌNG: refusal_review/faithfulness_review cần đánh giá thủ công.', flush=True)


if __name__ == '__main__':
    run()
