# Khai báo sử dụng AI – cần xác nhận trước khi nộp

- Công cụ: ChatGPT (OpenAI), sử dụng hỗ trợ lập trình và soạn tài liệu.
- Phần RAG: hỗ trợ đọc/kiểm tra `src/rag/*`, unit tests, chunking và README (đánh dấu chính xác các phần nhóm đã thực sự dùng AI).
- Phần Agent: AI hỗ trợ tạo `src/agent/agent.py`, `src/agent/llm_client.py`, `prompts/system_prompt.txt`, `main.py`, `tests/test_agent.py`.
- Phần MCP: AI hỗ trợ thiết kế/bổ sung `src/mcp/tools.py`, `mcp_server.py`, `mcp_client.py`, `bridge.py`, `tests/test_mcp_integration.py`.
- Phần chung: AI hỗ trợ `scripts/evaluate.py`, `tests/testset.jsonl`, `src/agent/logging_utils.py`, `tests/test_common.py`, `README.md`, `Makefile`, tài liệu báo cáo.
- Prompt chính (tóm tắt): "Hướng dẫn hoàn thiện đồ án CTXH Python W1–W7; tích hợp RAG/Agent/MCP; testset >=12 câu, >=4 no_answer; trace token, evaluation; báo cáo theo yêu cầu giảng viên".
- Kiểm tra độc lập của nhóm: [điền test thực tế, lỗi đã sửa, người review, ngày].
- Phần do từng thành viên tự chỉnh sửa: [điền trung thực file/commit].

**Chú ý:** Đây là bản nháp khai báo, nhóm phải rà soát cho khớp quá trình sử dụng AI thực tế, không sao chép nguyên nếu không chính xác.
