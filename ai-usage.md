# AI Usage Transparency Report

**Project:** AI-powered Student Social Work (CTXH) Activity Registration Agent  
**Student Name:** Hà Ngọc Bảo  
**Student ID:** 24110078  

---

## 1. Công cụ AI sử dụng và phương thức phối hợp

- **Công cụ:** Google Gemini / LLMs.
- **Phương thức:** Sử dụng AI để gợi ý cấu trúc và viết sơ bộ (draft) một số đoạn code cơ bản. Sau đó, Human trực tiếp kiểm tra, tinh chỉnh logic, xử lý đường dẫn, viết Unit Test, tích hợp các thành phần và quản lý mã nguồn trên Git/GitHub.

## 2. Chi tiết đóng góp, prompt gợi ý và mã nguồn phác thảo từ AI

### A. Phần Data Models (`src/models.py`)

- **Phần việc:** Xây dựng cấu trúc dữ liệu sử dụng Type Hinting cho các tham số đầu vào của MCP Tool.
- **Prompt gợi ý / Viết sơ bộ:**

  > Gợi ý giúp tôi khung cơ bản sử dụng `dataclass` trong Python cho các tham số đầu vào của công cụ đăng ký hoạt động công tác xã hội.

- **Mã nguồn phác thảo do AI gợi ý (Draft):**

```python
from dataclasses import dataclass


@dataclass
class RegisterCtxhActivityArgs:
    student_id: str
    activity_code: str
```

### B. Phần MCP Server và Stdio Communication (`src/mcp/server.py`)

- **Phần việc:** Xây dựng vòng lặp giao tiếp qua Stdio, xử lý request JSON, sử dụng đường dẫn database tuyệt đối và tách thông báo lỗi sang `stderr` để tránh làm nhiễu dữ liệu giao tiếp trên `stdout`.

- **Prompt gợi ý / Viết sơ bộ:**

  > Hãy phác thảo sơ bộ đoạn code Python xử lý giao tiếp Stdio JSON-RPC, lưu ý cách bỏ qua dòng trống, bắt ngoại lệ và ghi lỗi ra stderr, đồng thời sử dụng stdout flush.

- **Mã nguồn phác thảo do AI gợi ý (Draft):**

```python
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
```

### C. Phần Side-Effect Tool và Verification Tool (`src/mcp/server.py`)

- **Phần việc:** Xây dựng Write Tool (`register_ctxh_activity`) để ghi nhận đăng ký hoạt động và Read Tool (`get_ctxh_registration_status`) để đọc lại, kiểm chứng trạng thái đăng ký.

- **Prompt gợi ý / Viết sơ bộ:**

  > Cho tôi ý tưởng và code mẫu ngắn gọn về cách viết hàm xử lý tool ghi nhận trạng thái vào từ điển hoặc file JSON, cùng với hàm đọc lại để kiểm chứng.

- **Mã nguồn phác thảo do AI gợi ý (Draft):**

```python
if name == "register_ctxh_activity":
    student_id = args.get("student_id")
    activity_code = args.get("activity_code")

    key = f"{student_id}_{activity_code}"

    db["registrations"][key] = {
        "student_id": student_id,
        "activity_code": activity_code,
        "status": "REGISTERED"
    }

    save_db(db)

    return {
        "content": [
            {
                "type": "text",
                "text": "Đăng ký thành công"
            }
        ]
    }
```

