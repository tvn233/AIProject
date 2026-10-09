import sys
import json
import os
from typing import Dict, Any

DB_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/ctxh_db.json"))
def load_db() -> Dict[str, Any]:
    if not os.path.exists(DB_FILE):
        return {"registrations": {}}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"registrations": {}}

def save_db(data: Dict[str, Any]):
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def handle_mcp_request(request: dict) -> dict:
    method = request.get("method")
    params = request.get("params", {})
    
    if method == "tools/list":
        return {
            "tools": [
                {
                    "name": "register_ctxh_activity",
                    "description": "Đăng ký hoạt động CTXH cho sinh viên (Write Tool - Side Effect)",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "student_id": {"type": "string"},
                            "activity_code": {"type": "string"},
                            "registration_date": {"type": "string"}
                        },
                        "required": ["student_id", "activity_code"]
                    }
                },
                {
                    "name": "get_ctxh_registration_status",
                    "description": "Tra cứu trạng thái đăng ký CTXH để kiểm tra/xác nhận (Read Tool - Verify Step)",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "student_id": {"type": "string"},
                            "activity_code": {"type": "string"}
                        },
                        "required": ["student_id", "activity_code"]
                    }
                }
            ]
        }
    
    elif method == "tools/call":
        name = params.get("name")
        args = params.get("arguments", {})
        db = load_db()
        
        if name == "register_ctxh_activity":
            key = f"{args.get('student_id')}_{args.get('activity_code')}"
            db["registrations"][key] = {
                "student_id": args.get("student_id"),
                "activity_code": args.get("activity_code"),
                "registration_date": args.get("registration_date", "2026-10-08"),
                "status": "REGISTERED_SUCCESS"
            }
            save_db(db)
            return {"content": [{"type": "text", "text": f"Đã đăng ký thành công hoạt động {args.get('activity_code')} cho SV {args.get('student_id')}."}]}
            
        elif name == "get_ctxh_registration_status":
            key = f"{args.get('student_id')}_{args.get('activity_code')}"
            record = db["registrations"].get(key)
            if record:
                return {"content": [{"type": "text", "text": json.dumps(record, ensure_ascii=False)}]}
            return {"content": [{"type": "text", "text": f"Không tìm thấy dữ liệu đăng ký cho SV {args.get('student_id')} tại mã {args.get('activity_code')}."}]}

    return {"error": "Method not found"}

if __name__ == "__main__":
    for line in sys.stdin:
        if not line.strip(): 
            continue
        try:
            req = json.loads(line)
            res = handle_mcp_request(req)
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()
        except Exception as e:
            sys.stderr.write(f"Error: {str(e)}\n")