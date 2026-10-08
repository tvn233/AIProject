from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class ToolCall:
    name: str
    arguments: Dict[str, Any]

@dataclass
class RegisterCTXHActivityArgs:
    """Dataclass tham số cho Write Tool: Đăng ký hoạt động CTXH"""
    student_id: str
    activity_code: str
    registration_date: str = "2026-10-08"

@dataclass
class GetCTXHRegistrationStatusArgs:
    """Dataclass tham số cho Read Tool: Tra cứu trạng thái đăng ký"""
    student_id: str
    activity_code: str