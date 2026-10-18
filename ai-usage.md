# Báo cáo Sử dụng AI (`ai-usage.md`)


## 1. Tỷ lệ phân chia công việc (AI vs. Human)

| Phân khúc công việc | Tỷ lệ đóng góp | Mô tả vai trò |
|---|:---:|---|
| **AI** | **60%** | Hỗ trợ phác thảo cấu trúc MCP Server, thiết kế các lớp dữ liệu cho Document Store, đề xuất cách triển khai các tool và gợi ý các trường hợp kiểm thử tự động. |
| **Human** | **40%** | Xác định yêu cầu nghiệp vụ, hoàn thiện logic xử lý, kiểm tra dữ liệu, xử lý ngoại lệ, kiểm thử và tích hợp các thành phần vào hệ thống. |

---

## 2. Chi tiết ứng dụng AI theo từng thành phần

### A. Mô-đun MCP Server & Tools

**Phần công việc:** Xây dựng cấu trúc ban đầu cho MCP Server quản lý hoạt động Công tác xã hội. Thành phần này cung cấp các tool phục vụ đăng ký hoạt động CTXH, kiểm tra trạng thái đăng ký và quy đổi điểm CTXH theo chính sách.

**Công cụ AI sử dụng:** Mô hình ngôn ngữ lớn (LLM) hỗ trợ lập trình Python.

**Prompt chính:**

> Hãy gợi ý khung code Python sử dụng thư viện `mcp.server.fastmcp` để tạo một FastMCP server tên `CTXH Demo`. Cần phác thảo các tool: đăng ký hoạt động (yêu cầu tham số `confirmed` mặc định `False`), kiểm tra trạng thái và quy đổi điểm theo chính sách. Chỉ phác thảo cấu trúc và hàm cơ bản, không viết toàn bộ business logic phức tạp.

**Đoạn code do AI gợi ý/phác thảo:**

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("CTXH Demo")


@mcp.tool()
def register_ctxh_activity_tool(
    student_id: str,
    activity_code: str,
    confirmed: bool = False
) -> str:
    """Register CTXH activity in demo DB.
    
    Explicit user confirmation is required.
    """
    # Phác thảo cấu trúc xử lý đăng ký hoạt động
    pass
```

**Nội dung AI hỗ trợ:**

- Đề xuất cách khởi tạo MCP Server bằng `FastMCP`.
- Gợi ý sử dụng decorator `@mcp.tool()` để khai báo các công cụ thông qua giao thức MCP.
- Phác thảo tham số đầu vào cho chức năng đăng ký hoạt động.
- Đề xuất cơ chế xác nhận thông qua tham số `confirmed`, mặc định là `False`.
- Gợi ý cấu trúc cho các tool kiểm tra trạng thái và quy đổi điểm CTXH.

**Nội dung Human thực hiện:**

- Xác định yêu cầu nghiệp vụ của hệ thống CTXH, bao gồm mã sinh viên `24110078` và các quy tắc xác nhận đăng ký.
- Hoàn thiện logic đăng ký hoạt động, kiểm tra trạng thái và quy đổi điểm theo chính sách.
- Bổ sung điều kiện kiểm tra dữ liệu đầu vào và yêu cầu xác nhận trước khi ghi dữ liệu.
- Xử lý các trường hợp đăng ký trùng lặp, dữ liệu không hợp lệ và ngoại lệ.
- Kiểm thử và tích hợp các tool với hệ thống thực tế.

---

### B. Cấu trúc tài liệu và kho dữ liệu RAG (`DocumentStore`)

**Phần công việc:** Thiết kế cấu trúc dữ liệu cho mô-đun quản lý kho tài liệu của hệ thống RAG. Thành phần này quản lý tài liệu, các đoạn văn bản được chia nhỏ (chunks) và metadata liên quan.

**Công cụ AI sử dụng:** Mô hình ngôn ngữ lớn (LLM) hỗ trợ lập trình Python.

**Prompt chính:**

> Hãy phác thảo các `dataclass` bằng Python cho một hệ thống RAG tối giản gồm `Document`, `DocumentChunk` và `DocumentStore`. Thêm các phương thức cơ bản như `add_document`, `add_chunks` có kiểm tra trùng lặp `doc_id` và `chunk_id`.

**Đoạn code do AI sinh/phác thảo:**

```python
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Document:
    doc_id: str
    title: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
```

**Nội dung AI hỗ trợ:**

- Đề xuất sử dụng `dataclass` để biểu diễn cấu trúc tài liệu.
- Phác thảo các thuộc tính `doc_id`, `title`, `content` và `metadata`.
- Gợi ý thiết kế các lớp `Document`, `DocumentChunk` và `DocumentStore`.
- Đề xuất các phương thức `add_document` và `add_chunks` để quản lý tài liệu và các đoạn văn bản.
- Gợi ý cơ chế kiểm tra trùng lặp mã định danh tài liệu (`doc_id`) và đoạn văn bản (`chunk_id`).

**Nội dung Human thực hiện:**

- Điều chỉnh cấu trúc dữ liệu theo yêu cầu của hệ thống RAG.
- Hoàn thiện cách lưu trữ và quản lý tài liệu cùng các chunks tương ứng.
- Bổ sung các điều kiện kiểm tra tính hợp lệ và tính duy nhất của mã định danh.
- Tích hợp Document Store với quy trình xử lý tài liệu và truy xuất thông tin của hệ thống.
- Kiểm tra tính nhất quán của dữ liệu trong quá trình thêm và quản lý tài liệu.

---

### C. Mô-đun kiểm thử tự động (`MCPBusinessTests`)

**Phần công việc:** Xây dựng cấu trúc unit test để kiểm tra các kịch bản nghiệp vụ của MCP Server, bao gồm yêu cầu xác nhận trước khi ghi dữ liệu, ngăn chặn đăng ký trùng lặp và xử lý ngoại lệ.

**Công cụ AI sử dụng:** Mô hình ngôn ngữ lớn (LLM) hỗ trợ sinh test case Python.

**Prompt chính:**

> Hãy gợi ý một vài test case mẫu dùng `unittest` để kiểm tra việc gọi tool `register_ctxh_activity` với cơ chế mock `tempfile` cho file JSON database. Chỉ phác thảo hàm setup và test xác nhận.

**Đoạn code do AI phác thảo:**

```python
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


class MCPBusinessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.patch = patch.object(
            tools,
            "DB_FILE",
            Path(self.tmp.name) / "db.json"
        )
        self.patch.start()

    def tearDown(self):
        self.patch.stop()
        self.tmp.cleanup()
```

**Nội dung AI hỗ trợ:**

- Đề xuất sử dụng thư viện `unittest` để xây dựng bộ kiểm thử tự động.
- Gợi ý sử dụng `tempfile.TemporaryDirectory()` để tạo thư mục tạm thời phục vụ kiểm thử.
- Đề xuất sử dụng `unittest.mock.patch` để thay đổi đường dẫn database trong quá trình kiểm thử.
- Phác thảo cấu trúc `setUp()` và `tearDown()` để khởi tạo và giải phóng tài nguyên kiểm thử.
- Đề xuất các trường hợp kiểm thử cho xác nhận đăng ký, đăng ký trùng lặp và xử lý ngoại lệ.

**Nội dung Human thực hiện:**

- Hoàn thiện các test case dựa trên logic nghiệp vụ thực tế của hệ thống.
- Điều chỉnh cách mock database và các thành phần phụ thuộc để phù hợp với cấu trúc mã nguồn.
- Kiểm tra kết quả trả về của các tool trong từng trường hợp kiểm thử.
- Chạy bộ kiểm thử, phân tích lỗi và sửa các trường hợp chưa đáp ứng yêu cầu.
- Đánh giá tính đúng đắn của hệ thống trong các tình huống hợp lệ và không hợp lệ.

---