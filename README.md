# Trợ lý CTXH: Quy đổi & Đăng ký (T5)

**Đồ án AIPR W1–W7.** Agent Loop Python tự viết, Groq LLM, RAG Dense/Hybrid, MCP stdio, đăng ký DEMO JSON có xác nhận và read-after-write verification.

> **Giới hạn:** Không liên kết cổng đăng ký HCMUTE. Đăng ký chỉ lưu vào `data/ctxh_db.json` trên máy chạy. Các tài liệu DOC0001–DOC0008 phải là corpus nhóm tự biên soạn/được phép sử dụng; ZIP tích hợp **không** chứa corpus gốc của máy bạn.

## Cấu hình

- Python **3.11 trở lên** (máy từng dùng Python 3.10 cần nâng cấp). Windows cần `make` (GNU Make), hoặc dùng lệnh Python tương đương phía dưới.
- Sao chép các file trong gói vào repo đã có **`data/corpus/DOC0001_...md` đến `DOC0008_...md`**, không xóa corpus. Cấu trúc `data/corpus/*.md` bắt buộc.
- Tạo `.env` từ `.env.example`, nhập `GROQ_API_KEY` hợp lệ. Không commit `.env`.
- `make setup && make demo` (máy có GNU Make); Windows PowerShell nếu không có make: `py -3.11 -m pip install -r requirements.txt` rồi `py -3.11 -m main`.

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

`make eval` không gọi Groq: đo **retrieval hit@3** trên 8 câu có tài liệu kỳ vọng; 4 câu no_answer không có expected_doc_ids, nên không tính vào hit@3. `make eval-live` gọi Groq 24 lần (12 câu × 2 chế độ), xuất câu trả lời, token và trace. Điền thủ công hai cột `refusal_review`, `faithfulness_review` sau khi đối chiếu tài liệu; không đánh đồng retrieval hit với faithfulness.

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

1. `Quy chế CTXH là gì?` → Agent gọi RAG, trả lời kèm `DOC...`.
2. `Mua iPhone có được cộng 100 điểm CTXH không?` → tra cứu rồi nói không có căn cứ.
3. `Quy đổi 26 điểm CTXH theo quy chế thành ngày?` → tool policy dự kiến 3 ngày (phải đối chiếu bản DOC0001 thực tế).
4. `Đăng ký hoạt động 001101 cho sinh viên SV001` → terminal hỏi xác nhận; chỉ nhập **YES** mới ghi DB demo; sau đó MCP đọc lại xác minh. Nhập khác YES → không ghi.
5. Đăng ký lần hai cùng mã → từ chối trùng.

## Dữ liệu và logs

- `data/ctxh_db.json` là file phát sinh, gitignored, không chứa dữ liệu thật.
- `logs/demo_*.jsonl`: log từ các phiên CLI thật; `logs/eval_*.csv`, `logs/eval_live_*.jsonl` từ đánh giá. **Tự chạy ít nhất 3 phiên demo thật** và lưu 3 file jsonl có timestamp, tool args, kết quả và USAGE. Vì logs bị gitignore, sao chép ba file đã rà soát dữ liệu cá nhân vào bộ nộp, hoặc force-add các log đã làm sạch theo yêu cầu GV.
- Không lưu API key, CCCD, mã OTP, dữ liệu sinh viên thật.
- `CTXH.md` gốc có quy đổi 10 điểm/ngày và quy tắc làm tròn: dư dưới 5 xuống, đúng 5 thành 0.5 ngày, trên 5 lên 1 ngày. **Xác minh `DOC0001` nhóm trước khi báo cáo công thức này**.

## Đóng góp, nguồn và giới hạn

Điền commit hash thực tế và người phụ trách trong `REPORT_OUTLINE.md`; không tạo lịch sử Git giả. Điền `ai-usage.md` trung thực. Đọc `CHECKLIST_BAO_VE.md` trước khi bảo vệ.

Giới hạn: JSON demo không phải hệ thống đăng ký trường; retrieval hit@k không bảo đảm câu trả lời trung thực; dữ liệu/metadata và chính sách phải được kiểm chứng trước khi áp dụng thực tế.
