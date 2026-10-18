# TRỢ LÝ CTXH – QUY ĐỔI & ĐĂNG KÝ

**Đồ án AI – Nhóm 09**
**Mã nguồn:** https://github.com/tvn233/AIProject
**Ngôn ngữ:** Python 3.11+
**Thành phần:** RAG (Dense/Hybrid), Agent Loop, Groq LLM, MCP SDK (stdio), dữ liệu đăng ký DEMO JSON.

> **Lưu ý:** Hệ thống phục vụ học tập và trình diễn; **không kết nối** cổng đăng ký CTXH chính thức của trường. Thao tác đăng ký chỉ ghi vào dữ liệu DEMO cục bộ. Các quy định CTXH trong corpus phải được đối chiếu nguồn chính thức trước khi sử dụng thực tế.

## 1. Mục tiêu và chức năng

Hệ thống hỗ trợ sinh viên tra cứu tài liệu CTXH bằng RAG, hỏi đáp với Agent, quy đổi điểm sang ngày CTXH theo công cụ quy đổi, đăng ký hoạt động DEMO sau khi người dùng xác nhận, và kiểm tra trạng thái đăng ký. Agent có thể lựa chọn công cụ RAG hoặc MCP tùy theo câu hỏi.

**Luồng tổng quát:** `Người dùng → main.py → Agent → RAG / MCP Client → MCP Server → dữ liệu DEMO → kết quả → người dùng`.

## 2. Yêu cầu môi trường

- Python **3.11 trở lên** và `pip`.
- Kết nối Internet khi tải thư viện/mô hình embedding và khi gọi Groq API.
- API key Groq hợp lệ để chạy các câu hỏi cần LLM; lấy từ tài khoản Groq của người chạy.
- Máy Windows có PowerShell **không bắt buộc cài GNU Make**. Nếu có GNU Make, có thể sử dụng các lệnh `make` tương ứng.
- Chạy mọi lệnh tại **thư mục gốc dự án** (nơi có `main.py`, `Makefile`, `requirements.txt`).

## 3. Cài đặt từ đầu (Windows PowerShell)

**Bước 1 — Tải mã nguồn:**

```powershell
git clone https://github.com/tvn233/AIProject.git
cd AIProject
```

Nếu dùng file ZIP thay vì Git, giải nén và mở PowerShell tại thư mục chứa `main.py`.

**Bước 2 — Tạo môi trường Python:**

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version
```

Nếu PowerShell chặn kích hoạt môi trường, có thể chạy Python trực tiếp bằng `.\.venv\Scripts\python.exe` thay cho `python` trong các lệnh tiếp theo. Nếu máy không có lệnh `py -3.11`, dùng bản Python 3.11+ đã cài đặt để tạo môi trường.

**Bước 3 — Cài thư viện:**

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Lần chạy đầu có thể mất thời gian để tải mô hình embedding.

**Bước 4 — Tạo file cấu hình:**

```powershell
Copy-Item .env.example .env
```

Mở `.env` và thay giá trị mẫu bằng API key **của người chạy**:

```dotenv
GROQ_API_KEY=YOUR_VALID_GROQ_API_KEY
GROQ_MODEL=openai/gpt-oss-20b
```

Không đưa `.env` hoặc API key thật lên GitHub, ảnh chụp màn hình, báo cáo hay log chia sẻ. Nếu gặp `401 invalid_api_key`, kiểm tra lại key và quyền truy cập mô hình; đây là lỗi xác thực, không đồng nghĩa hết token.

**Bước 5 — Kiểm tra dữ liệu:**

Đảm bảo thư mục `data/corpus/` có các file tài liệu `DOC*.md`, thư mục `tests/` có `testset.jsonl`, và các thư mục `src/`, `prompts/` có trong bản mã nguồn. Nếu thiếu corpus, chương trình RAG sẽ không thể nạp dữ liệu đúng cách.

## 4. Lệnh chạy demo duy nhất

Sau khi cài đặt và cấu hình, chạy:

```powershell
python -m main
```

Chờ thông báo nạp embedding và danh sách MCP tools, sau đó nhập câu hỏi tại `Bạn:`. Nhập `exit` hoặc `quit` để thoát.

**Chạy một câu hỏi không tương tác:**

```powershell
python -m main --question "Quy định chung về CTXH đối với sinh viên là gì?"
```

Chế độ `--question` không cho phép xác nhận thao tác ghi đăng ký; dùng chế độ tương tác nếu muốn demo đăng ký.

**Một số câu hỏi demo gợi ý:**

1. `Quy định chung về CTXH đối với sinh viên là gì?` — hỏi đáp có truy xuất tài liệu.
2. `Có những mã hoạt động CTXH nào?` — tìm thông tin trong corpus.
3. `Quy đổi 25 điểm CTXH theo quy chế thành bao nhiêu ngày?` — kiểm tra công cụ quy đổi (phân biệt phép tính với trạng thái điểm đã duyệt).
4. `Đăng ký hoạt động 001101 cho sinh viên SV001` — demo đăng ký. Hệ thống phải yêu cầu nhập chính xác `YES` trước khi ghi; cần kiểm tra mã hoạt động có tồn tại trong DB demo.
5. `Mua iPhone có được cộng 100 điểm CTXH không?` — kiểm tra phản hồi khi không có căn cứ trong tài liệu.

> Không sử dụng dữ liệu sinh viên thật. Với đăng ký DEMO, dữ liệu có thể đã tồn tại từ lần chạy trước; dùng bản sao DB demo hoặc kiểm tra trạng thái trước khi thử đăng ký trùng.

## 5. Chạy kiểm thử tự động

```powershell
python -m unittest discover -s tests -v
```

Kết quả `OK` nghĩa là các bài kiểm thử đã chạy trong môi trường hiện tại không phát hiện lỗi. Nếu xuất hiện `FAIL` hoặc `ERROR`, cần đọc tên bài test và traceback, không ghi nhận là PASS. Số bài test có thể thay đổi khi cập nhật repository; **không giả định cố định 16/16 cho mọi phiên bản**.

**Kiểm tra MCP SDK và tool discovery:**

```powershell
python -m src.mcp.mcp_client
```

Danh sách công cụ dự kiến trong bản mã nguồn được rà soát:

```text
register_ctxh_activity_tool
get_ctxh_registration_status_tool
convert_ctxh_points_tool
convert_ctxh_points_policy_tool
```

Đây là kiểm tra kết nối/discovery; việc nhìn thấy 4 công cụ không tự chứng minh toàn bộ nghiệp vụ đăng ký đã chạy thành công.

## 6. Chạy đánh giá (eval)

Bộ dữ liệu `tests/testset.jsonl` có **12 câu hỏi**, trong đó **4 câu `no_answer`**. Script đánh giá hỗ trợ hai chế độ truy xuất `dense` và `hybrid`.

**Đánh giá retrieval (không gọi Groq):**

```powershell
python -m scripts.evaluate
```

Lệnh này tính **Retrieval Hit@3** trên các câu có tài liệu kỳ vọng, xuất báo cáo dạng `logs/eval_<timestamp>.csv` và `logs/eval_<timestamp>.json`. Bốn câu `no_answer` không có tài liệu kỳ vọng nên không được tính vào Hit@3. **Hit@3 không phải độ chính xác câu trả lời hoặc faithfulness.**

**Đánh giá Agent bằng LLM thật (có dùng Groq API):**

```powershell
python -m scripts.evaluate --agent
```

Mặc định đánh giá 12 câu × 2 chế độ = tối đa **24 lượt Agent**; có thể phát sinh chi phí, giới hạn tốc độ hoặc lỗi API. Kết quả tiến độ lưu tại `logs/eval_live_progress.csv` và `logs/eval_live_progress.jsonl`.

**Chạy từng phần để tránh tốn quota:**

```powershell
python -m scripts.evaluate --agent --max-cases 4
```

**Tiếp tục từ checkpoint:**

```powershell
python -m scripts.evaluate --agent --resume
```

Sau khi đánh giá, nhóm phải **tự đối chiếu corpus và điền nhận xét** cho `refusal_review` và `faithfulness_review`; script không tự xác nhận hai tiêu chí này. Không dùng số lượt chạy không lỗi để thay thế đánh giá chất lượng câu trả lời.

## 7. Lệnh tương đương bằng GNU Make

Nếu máy đã cài GNU Make và đang đứng tại thư mục gốc:

| Mục đích | Lệnh Make | Lệnh Python tương đương |
|---|---|---|
| Cài phụ thuộc | `make setup` | `python -m pip install -r requirements.txt` |
| Demo tương tác | `make demo` | `python -m main` |
| Unit Tests | `make test` | `python -m unittest discover -s tests -v` |
| MCP discovery | `make mcp-check` | `python -m src.mcp.mcp_client` |
| Retrieval evaluation | `make eval` | `python -m scripts.evaluate` |
| Agent evaluation | `make eval-live` | `python -m scripts.evaluate --agent` |

**Tái lập nhanh trên máy đã cấu hình:**

```bash
make setup
make demo
make eval
```

Trên Windows không có `make`, dùng ba lệnh Python tương đương ở bảng trên.

## 8. Logs và minh chứng cần nộp

Mỗi lần chạy demo CLI, chương trình tạo log theo dạng `logs/demo_YYYYMMDD_HHMMSS.jsonl`. Khi chuẩn bị nộp, nhóm cần có **ít nhất 3 lần chạy demo thật**, mỗi lần có file JSONL tương ứng, ghi nhận thời gian, các bước xử lý, tool args/kết quả và thông tin usage theo khả năng thực tế của lượt chạy.

**Lưu ý khi đọc usage:** `Tokens=0` hoặc `Calls=0` có thể xuất hiện ở đường xử lý không gọi LLM; không được tự thay bằng số khác. Kiểm tra nội dung log thực tế để biết có `prompt_tokens`, `completion_tokens`, `calls` hay không. Nếu một log chưa đáp ứng yêu cầu giảng viên, hãy chạy và ghi lại một lượt demo phù hợp, **không tự tạo số liệu**.

Có thể liệt kê log demo trên PowerShell:

```powershell
Get-ChildItem .\logs\demo_*.jsonl | Sort-Object LastWriteTime -Descending
```

Và xem log mới nhất:

```powershell
Get-Content (Get-ChildItem .\logs\demo_*.jsonl | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName
```

Trước khi đưa log vào bộ nộp, rà soát để không lộ API key hoặc thông tin cá nhân. Log giả lập lỗi HTTP hoặc dữ liệu test không được thay thế cho 3 lượt demo thực tế.

## 9. Cấu trúc thư mục chính

```text
AIProject/
├── main.py                     # CLI chạy demo
├── Makefile                    # Lệnh setup/demo/test/eval
├── requirements.txt            # Thư viện Python
├── .env.example                # Mẫu cấu hình (không chứa key thật)
├── prompts/                    # Prompt hệ thống cho Agent
├── data/
│   ├── corpus/                 # Tài liệu CTXH DOC*.md cho RAG
│   └── ctxh_db.json            # Dữ liệu đăng ký DEMO
├── src/
│   ├── agent/                  # Agent Loop, Groq client, logging
│   ├── rag/                    # Dense/Hybrid retrieval
│   └── mcp/                    # MCP Server, Client, bridge, tools
├── scripts/
│   └── evaluate.py             # Đánh giá retrieval và Agent
├── tests/
│   ├── testset.jsonl           # 12 câu, 4 no_answer
│   └── test_*.py               # Unit/integration tests
├── logs/                       # Demo và evaluation outputs
├── ai-usage.md                 # Khai báo sử dụng AI
└── README.md                   # Tài liệu hướng dẫn này
```

## 10. Lỗi thường gặp

| Hiện tượng | Kiểm tra / cách xử lý |
|---|---|
| `python` không tìm thấy | Cài Python 3.11+, mở terminal mới, kiểm tra `python --version` |
| `ModuleNotFoundError` | Kích hoạt `.venv`, cài `requirements.txt`, chạy tại thư mục gốc |
| Không tìm thấy `GROQ_API_KEY` | Tạo `.env` từ `.env.example` và nhập key hợp lệ |
| HTTP `401 invalid_api_key` | Kiểm tra key/quyền truy cập, không đăng key lên chat hoặc Git |
| HTTP `429` | Kiểm tra rate limit/quota, giảm tần suất và thử lại phù hợp |
| MCP không hiện 4 tools | Kiểm tra `mcp` trong requirements, chạy `python -m src.mcp.mcp_client`, xem traceback |
| Không có corpus hoặc truy xuất rỗng | Kiểm tra `data/corpus/DOC*.md` và quyền đọc file |
| Lỗi `make` không được nhận diện | Dùng lệnh Python tương đương; GNU Make không bắt buộc |
| Agent quy đổi nhưng bỏ qua tình trạng điểm chưa duyệt | Ghi nhận hạn chế, đối chiếu quy chế; không mặc nhiên coi điểm chưa duyệt là đủ điều kiện |

## 11. Giới hạn và lưu ý học thuật

- Đăng ký chỉ là **DEMO**, không có giá trị trên hệ thống CTXH thật.
- Các tài liệu corpus và quy tắc quy đổi phải được đối chiếu với quy định có hiệu lực.
- Agent/LLM có thể trả lời thiếu điều kiện nghiệp vụ; kết quả RAG retrieval không bảo đảm faithfulness.
- Kết quả eval, log, token usage và test phải lấy từ lần chạy thực tế.
- Xem `ai-usage.md` để biết công cụ AI được sử dụng hỗ trợ phát triển và phạm vi hỗ trợ.
- Khi nộp repository, giữ lịch sử commit Git để giảng viên có thể kiểm tra đóng góp.

## 12. Danh sách sản phẩm nộp

| Sản phẩm | Yêu cầu |
|---|---|
| `report.docx` | Báo cáo 8–9 trang |
| Repository Git | Có lịch sử commit; cung cấp link hoặc ZIP theo yêu cầu |
| `logs/` | Ít nhất 3 log demo thực tế, có trace và usage |
| `tests/testset.jsonl` | Ít nhất 12 câu, gồm ít nhất 4 `no_answer` |
| `ai-usage.md` | Khai báo công cụ AI, phạm vi, prompt và code AI sinh nếu có |
| `README.md` | Lệnh chạy duy nhất để tái lập demo và lệnh `make eval` |

---

**Lệnh cần nhớ khi bảo vệ:** `python -m main` (demo), `python -m unittest discover -s tests -v` (tests), `python -m src.mcp.mcp_client` (MCP), `python -m scripts.evaluate` (eval). Nếu có GNU Make: `make demo`, `make test`, `make mcp-check`, `make eval`.
