# AI Usage Transparency Report

**Project:** AI-powered Student Social Work (CTXH) Activity Registration Agent  
**Student Name:** Hà Ngọc Bảo  
**Student ID:** 24110078

---

## 1. Công cụ AI sử dụng và phương thức phối hợp

- **Công cụ:** Google Gemini / LLMs.
- **Phương thức:** Sử dụng AI để gợi ý phác thảo cấu trúc và viết sơ bộ (draft) các đoạn code cơ bản. Sau đó, con người (Human) trực tiếp tinh chỉnh logic, tối ưu đường dẫn, tự viết Unit Test, thực hiện tích hợp và quản lý mã nguồn thực tế trên Git/GitHub.

## 2. Chi tiết đóng góp, prompt gợi ý và mã nguồn hoàn thiện

### A. Phần Data Models (`src/models.py`)

- **Phần việc:** Xây dựng cấu trúc dữ liệu sử dụng Type Hinting cho các tham số đầu vào của MCP Tool.
- **Prompt gợi ý / Viết sơ bộ:**

  > Gợi ý giúp tôi khung cơ bản sử dụng `dataclass` trong Python cho các tham số đầu vào của công cụ đăng ký hoạt động công tác xã hội.

- **Mã nguồn do Human hoàn thiện dựa trên gợi ý:**

```python
from dataclasses import dataclass


@dataclass
class RegisterCtxhActivityArgs:
    student_id: str
    activity_code: str
    registration_date: str = "2026-10-08"
```

### B. Phần MCP Server và Stdio Communication (`src/mcp/server.py`)

- **Phần việc:** Xây dựng vòng lặp giao tiếp qua Stdio, xử lý đường dẫn database bằng đường dẫn tuyệt đối, đảm bảo `stdout` chỉ chứa dữ liệu giao tiếp theo giao thức và ghi lỗi ra `stderr`.
- **Prompt gợi ý / Viết sơ bộ:**

  > Hãy phác thảo sơ bộ đoạn code Python xử lý giao tiếp Stdio JSON-RPC, lưu ý cách bỏ qua dòng trống, bắt ngoại lệ và ghi lỗi ra stderr, đồng thời sử dụng stdout flush.

- **Mã nguồn do Human kiểm chỉnh và tích hợp thực tế:**

```python
DB_FILE = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../../data/ctxh_db.json"
    )
)

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

- **Phần việc:** Hiện thực hóa Write Tool (`register_ctxh_activity`) để ghi nhận đăng ký hoạt động và Read Tool (`get_ctxh_registration_status`) để đọc lại, kiểm chứng trạng thái đăng ký.
- **Prompt gợi ý / Viết sơ bộ:**

  > Cho tôi ý tưởng và code mẫu ngắn gọn về cách viết hàm xử lý tool ghi nhận trạng thái vào từ điển hoặc file JSON, cùng với hàm đọc lại để kiểm chứng.

- **Mã nguồn do Human tinh chỉnh logic:**

```python
if name == "register_ctxh_activity":
    key = f"{args.get('student_id')}_{args.get('activity_code')}"

    db["registrations"][key] = {
        "student_id": args.get("student_id"),
        "activity_code": args.get("activity_code"),
        "registration_date": args.get(
            "registration_date",
            "2026-10-08"
        ),
        "status": "REGISTERED_SUCCESS"
    }

    save_db(db)

    return {
        "content": [
            {
                "type": "text",
                "text": (
                    "Đã đăng ký thành công hoạt động "
                    f"cho sinh viên {args.get('student_id')}"
                )
            }
        ]
    }
```

---

## 3. Cam kết về tính minh bạch

AI được sử dụng như một công cụ hỗ trợ tham khảo ý tưởng, phác thảo cấu trúc và đề xuất code ban đầu. Mã nguồn cuối cùng được kiểm tra, điều chỉnh và tích hợp vào dự án bởi sinh viên. Các nội dung mô tả trên phản ánh phạm vi sử dụng AI trong quá trình phát triển dự án.