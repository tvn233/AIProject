import sys
import os
import json

# Thêm thư mục gốc vào PYTHONPATH để import được src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.mcp.server import handle_mcp_request

def test_mcp_server():
    print("--- [BẢO TEST] BẮT ĐẦU KIỂM TRA MCP SERVER ---")
    
    # Test 1: Kiểm tra danh sách Tools (tools/list)
    res_list = handle_mcp_request({"method": "tools/list"})
    assert len(res_list.get("tools", [])) == 2
    print("[OK] 1. tools/list trả về đủ 2 tools.")

    # Test 2: Thực thi Write Tool (register_ctxh_activity)
    req_write = {
        "method": "tools/call",
        "params": {
            "name": "register_ctxh_activity",
            "arguments": {"student_id": "SV24110078", "activity_code": "CTXH001"}
        }
    }
    res_write = handle_mcp_request(req_write)
    assert "Đã đăng ký thành công" in res_write["content"][0]["text"]
    print("[OK] 2. register_ctxh_activity ghi dữ liệu thành công.")

    # Test 3: Thực thi Read Tool (get_ctxh_registration_status)
    req_read = {
        "method": "tools/call",
        "params": {
            "name": "get_ctxh_registration_status",
            "arguments": {"student_id": "SV24110078", "activity_code": "CTXH001"}
        }
    }
    res_read = handle_mcp_request(req_read)
    assert "REGISTERED_SUCCESS" in res_read["content"][0]["text"]
    print("[OK] 3. get_ctxh_registration_status đọc lại dữ liệu chính xác.")

    print("\n TẤT CẢ TEST CASE CỦA BẢO ĐỀU PASS! SẴN SÀNG BÀN GIAO.")

if __name__ == "__main__":
    test_mcp_server()