"""Business logic for CTXH tools. Demo persistence only; no real school system."""
from __future__ import annotations
import json
import os
import re
from datetime import date
from pathlib import Path
from src.rag.chunking import MarkdownChunker

DB_FILE = Path(os.getenv('CTXH_DB_FILE', str(Path(__file__).resolve().parents[2] / 'data' / 'ctxh_db.json')))

def _read():
    if not DB_FILE.exists():
        return {'registrations': {}}
    data = json.loads(DB_FILE.read_text(encoding='utf-8'))
    if not isinstance(data.get('registrations'), dict):
        raise ValueError('Database không hợp lệ')
    return data

def _save(db):
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    temp = DB_FILE.with_suffix('.tmp')
    temp.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding='utf-8')
    temp.replace(DB_FILE)

def _validate(student_id, activity_code):
    if not isinstance(student_id, str) or not re.fullmatch(r'[A-Za-z0-9_-]{2,32}', student_id):
        raise ValueError('student_id không hợp lệ')
    if not isinstance(activity_code, str) or not re.fullmatch(r'[A-Za-z0-9_-]{2,32}', activity_code):
        raise ValueError('activity_code không hợp lệ')

def register_ctxh_activity(student_id: str, activity_code: str, confirmed: bool = False) -> dict:
    _validate(student_id, activity_code)
    if confirmed is not True:
        return {'ok': False, 'error': 'Cần xác nhận rõ ràng từ người dùng trước khi đăng ký'}
    db = _read()
    key = json.dumps([student_id, activity_code], ensure_ascii=False)
    if key in db['registrations']:
        return {'ok': False, 'error': 'Hoạt động đã được đăng ký', 'record': db['registrations'][key]}
    record = {'student_id': student_id, 'activity_code': activity_code,
              'registration_date': date.today().isoformat(), 'status': 'REGISTERED_SUCCESS'}
    db['registrations'][key] = record
    _save(db)
    return {'ok': True, 'record': record, 'note': 'Chỉ lưu vào dữ liệu demo nội bộ, không phải hệ thống HCMUTE'}

def get_ctxh_registration_status(student_id: str, activity_code: str) -> dict:
    _validate(student_id, activity_code)
    key = json.dumps([student_id, activity_code], ensure_ascii=False)
    record = _read()['registrations'].get(key)
    return {'found': record is not None, 'record': record}

def convert_ctxh_points(points: float, points_per_day: float) -> dict:
    """No default exchange rate: use only a rate verified against DOC0001."""
    if isinstance(points, bool) or isinstance(points_per_day, bool):
        raise ValueError('Tham số phải là số')
    points, points_per_day = float(points), float(points_per_day)
    if not (0 <= points <= 100000) or not (0 < points_per_day <= 100000):
        raise ValueError('Điểm hoặc tỷ lệ quy đổi không hợp lệ')
    return {'points': points, 'points_per_day': points_per_day,
            'days': points / points_per_day,
            'warning': 'Tỷ lệ do người gọi cung cấp; cần đối chiếu quy chế DOC0001'}

def convert_ctxh_points_policy(points: int) -> dict:
    if isinstance(points, bool) or not isinstance(points, int) or not 0 <= points <= 100000:
        raise ValueError("points phải là số nguyên từ 0 đến 100000")

    doc_path = (
        Path(__file__).resolve().parents[2]
        / "data"
        / "corpus"
        / "DOC0009_quy_doi_diem_ctxh.md"
    )
    if not doc_path.is_file():
        raise FileNotFoundError(f"Không tìm thấy chính sách quy đổi: {doc_path}")

    metadata, _ = MarkdownChunker.parse_yaml_frontmatter(
        doc_path.read_text(encoding="utf-8")
    )
    policy = metadata.get("conversion_policy")
    if not isinstance(policy, dict):
        raise ValueError("DOC0009 thiếu metadata conversion_policy")

    rate = policy.get("points_per_day")
    threshold = policy.get("remainder_threshold")
    rules = policy.get("remainder_rules")

    if isinstance(rate, bool) or not isinstance(rate, int) or rate <= 0:
        raise ValueError("points_per_day trong DOC0009 không hợp lệ")
    if isinstance(threshold, bool) or not isinstance(threshold, int) or not 0 < threshold < rate:
        raise ValueError("remainder_threshold trong DOC0009 không hợp lệ")
    if not isinstance(rules, dict):
        raise ValueError("remainder_rules trong DOC0009 không hợp lệ")

    whole_days, remainder = divmod(points, rate)
    if remainder < threshold:
        extra_days = rules["less_than_5"]
    elif remainder == threshold:
        extra_days = rules["equal_to_5"]
    else:
        extra_days = rules["greater_than_5"]

    days = whole_days + extra_days
    return {
        "points": points,
        "days": days,
        "points_per_day": rate,
        "source": f"{metadata['doc_id']}, mục 2. Cách làm tròn",
    }
