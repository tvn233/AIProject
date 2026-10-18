# Trợ lý CTXH: Quy đổi & Đăng ký (T5)

**Đồ án AIPR W1–W7.** Agent Loop Python tự viết, Groq LLM, RAG Dense/Hybrid, MCP stdio, đăng ký DEMO JSON có xác nhận và read-after-write verification.

> **Giới hạn:** Không liên kết cổng đăng ký HCMUTE. Đăng ký chỉ lưu vào `data/ctxh_db.json` trên máy chạy. Corpus trong `data/corpus/CTXH.md` dựa trên tài liệu CTXH do giảng viên cung cấp; nhóm bổ sung YAML metadata để chương trình đọc và truy xuất.

## Cấu hình

- Python **3.11 trở lên**; dùng một môi trường ảo riêng cho project. Windows có thể dùng GNU Make hoặc các lệnh Python tương đương phía dưới.
- Đặt tài liệu giảng viên cung cấp tại `data/corpus/CTXH.md`. File có YAML frontmatter với `doc_id: CTXH001`, `title`, `version`, `owner` và `conversion_policy`; nội dung quy định nằm sau frontmatter.
- Tạo `.env` từ `.env.example`, nhập `GROQ_API_KEY` hợp lệ. Chương trình đọc `.env` ở gốc project, `data/.env` hoặc `../data/.env`. Không commit khóa API.
- `make setup && make demo` (máy có GNU Make); trên Windows PowerShell sau khi kích hoạt `.venv`: `python -m pip install -r requirements.txt` rồi `python -m main`.

## Các lệnh kiểm tra

| Mục đích | GNU Make | Windows PowerShell |
|---|---|---|
| Cài thư viện | `make setup` | `python -m pip install -r requirements.txt` |
| Demo tương tác | `make demo` | `python -m main` |
| Kiểm thử unit | `make test` | `python -m unittest discover -s tests -v` |
| MCP client discovery | `make mcp-check` | `python -m src.mcp.mcp_client` |
| So sánh Dense/Hybrid | `make eval` | `python -m scripts.evaluate` |
| Eval LLM thật, tốn API | `make eval-live` | `python -m scripts.evaluate --agent` |
| Demo 1 câu không tương tác | — | `python -m main --question "Quy định CTXH?"` |

`make eval` không gọi Groq: đo **retrieval hit@3** trên 8 câu có tài liệu kỳ vọng; 4 câu `no_answer` không có `expected_doc_ids`, nên không tính vào hit@3. Corpus hiện chỉ có một `doc_id` là `CTXH001`: Hit@3 theo tài liệu không chứng minh đã chọn đúng chunk. Cần đối chiếu nội dung chunk, trích dẫn và câu trả lời. `make eval-live` đánh giá 12 câu theo hai chế độ (24 lượt); số lần gọi Groq phụ thuộc luồng Agent. Điền thủ công hai cột `refusal_review`, `faithfulness_review` sau khi đối chiếu tài liệu; không đánh đồng retrieval hit với faithfulness.

## Cấu trúc và kiến trúc

- `src/rag/`: chunk Markdown + metadata, E5-small embeddings, BM25 và Dense/Hybrid.
- `src/agent/llm_client.py`: Groq API, timeout/retry, token usage.
- `src/agent/agent.py`: hand-written Agent Loop, `MAX_STEPS`, tool-call JSON parser, lỗi `Error: ...`, trace.
- `src/mcp/mcp_server.py`: MCP FastMCP stdio, 4 công cụ (đăng ký, trạng thái, quy đổi tỷ lệ giả định, quy đổi theo quy chế).
- `src/mcp/mcp_client.py`: MCP SDK ClientSession, `list_tools`/`list_tool_specs`, `call_tool`, read-after-write.
- `src/mcp/bridge.py`: khám phá schema từ MCP Server, đăng ký cần người dùng nhập **YES** tại terminal; model không tự bật `confirmed`.
- `main.py`: giao diện CLI tích hợp. `scripts/evaluate.py`: Dense vs Hybrid + tùy chọn đánh giá LLM. `tests/testset.jsonl`: 12 câu, 4 no_answer.

Luồng: `user → LLM Agent → RAG hoặc MCP Client → MCP Server → JSON DEMO → Read Verify → LLM → user`. MCP chạy qua stdio; stdout của server dành riêng cho protocol, không `print` debug.

## Các tình huống demo

1. `Quy chế CTXH là gì?` → Agent gọi RAG, trả lời kèm nguồn `CTXH001`.
2. `Hiện tại cá nhân tôi đã tích lũy được bao nhiêu ngày CTXH?` → tra cứu rồi nói tài liệu không có dữ liệu cá nhân để xác định.
3. `25 điểm CTXH đã tích lũy tương đương bao nhiêu ngày?` → công cụ quy đổi trả 2,5 ngày theo `CTXH001`, mục II.c.
4. `Đăng ký hoạt động 001101 cho sinh viên SV001` → terminal hỏi xác nhận; chỉ nhập **YES** mới ghi DB demo; sau đó MCP đọc lại xác minh. Nhập khác YES → không ghi.
5. Đăng ký lần hai cùng mã → từ chối trùng.

## Dữ liệu và logs

- `data/ctxh_db.json` là file phát sinh, gitignored, không chứa dữ liệu thật.
- `logs/demo_*.jsonl`: log từ các phiên CLI thật; `logs/eval_*.csv`, `logs/eval_live_*.jsonl` từ đánh giá. **Chọn ít nhất 3 phiên demo thật đã chạy đạt** và lưu 3 file JSONL có timestamp, tool args, kết quả và USAGE. Rà soát dữ liệu cá nhân và khóa API trước khi đưa log vào bộ nộp; không chọn các log chạy lỗi làm minh chứng kết quả đạt.
- Không lưu API key, CCCD, mã OTP, dữ liệu sinh viên thật.
- `data/corpus/CTXH.md` quy định lấy tổng điểm CTXH đã tích lũy chia cho 10; phần dư dưới 5 làm tròn xuống, đúng 5 tính nửa ngày, trên 5 làm tròn lên một ngày. YAML `conversion_policy` do nhóm bổ sung để công cụ đọc quy tắc này.

## Đóng góp, nguồn và giới hạn

Điền commit hash thực tế và người phụ trách trong `REPORT_OUTLINE.md`; không tạo lịch sử Git giả. Điền `ai-usage.md` trung thực. Đọc `CHECKLIST_BAO_VE.md` trước khi bảo vệ.

Giới hạn: JSON demo không phải hệ thống đăng ký trường; retrieval hit@k không bảo đảm câu trả lời trung thực; dữ liệu/metadata và chính sách phải được kiểm chứng trước khi áp dụng thực tế.