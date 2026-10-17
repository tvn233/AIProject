"""Business logic for CTXH tools. Demo persistence only; no real school system."""
from __future__ import annotations
import json
import os
import re
from datetime import date
from pathlib import Path

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
    """CTXH.md: 10 points/day; remainder 0..4 => 0, 5 => 0.5, 6..9 => 1 day."""
    if isinstance(points, bool) or not isinstance(points, int) or points < 0 or points > 100000:
        raise ValueError('points phải là số nguyên không âm')
    whole, remainder = divmod(points, 10)
    days = whole + (0 if remainder < 5 else 0.5 if remainder == 5 else 1)
    return {'points':points,'days':days,'points_per_day':10,
            'rounding':'0-4 xuống; 5 = 0.5 ngày; 6-9 lên 1 ngày',
            'source':'CTXH.md, mục II.c (cần đối chiếu DOC0001 trong corpus)'}
