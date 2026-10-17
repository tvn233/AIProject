# Nội dung báo cáo 8–9 trang – cần thay các chỗ [ĐIỀN]

1. **Vấn đề/phạm vi/giả định (0.5–1 trang):** T5 Trợ lý CTXH, đối tượng sinh viên. Tra quy chế, mã hoạt động, quy đổi, đăng ký demo, xác nhận. Không tích hợp cổng HCMUTE thật, không xử lý dữ liệu nhạy cảm.
2. **Kiến trúc (1 trang):** CLI → Groq LLM/Agent Loop → RAG Dense/Hybrid hoặc MCP client → MCP server stdio → JSON demo → verify. Mô tả 1 câu hỏi và 1 thao tác ghi.
3. **RAG (1.5 trang):** DOC0001–DOC0008 metadata, Markdown chunk theo heading `##`, cắt 230 từ, overlap 30 từ; E5 multilingual, cosine, BM25, RRF. Lý do: giữ ngữ nghĩa tiểu mục, chunk ngắn phù hợp context, overlap hạn chế mất ngữ cảnh ở biên. [ĐIỀN số chunk thật và ví dụ].
4. **Agent & tool (2 trang):** Dataclass `AgentResult`, `TokenUsage`, tool schema, `MAX_STEPS=5`, parse JSON, tool lỗi trả `Error:`, xác nhận YES trước khi ghi, read-after-write verify, trace thật [CHÈN LOG].
5. **MCP (1 trang):** `FastMCP`, `ClientSession` stdio, discovery schemas, 4 tool; JSON demo, chống trùng, kiểm tra đầu vào. stdout protocol sạch.
6. **Đánh giá (1.5 trang):** 12 câu, 4 no_answer; bảng Dense vs Hybrid hit@3 lấy từ `logs/eval_*.json`; log 3 lần chạy thật, token calls/prompt/completion/max_prompt; refusal_review và faithfulness_review **chấm tay** từ `logs/eval_*.csv`. Phân tích ít nhất một ca thất bại [ĐIỀN]. Không điền số liệu chưa chạy.
7. **Hạn chế (0.5 trang):** dữ liệu JSON demo không phải HCMUTE; kết quả LLM không tuyệt đối tin cậy; kiểm thử chưa bao phủ mọi trường hợp.
8. **Phân công (0.5 trang):** Người 1 RAG/README [commit hash]; Người 2 LLM/Agent/main [commit hash]; Người 3 MCP/test/eval [commit hash]. Ghi đóng góp thực tế.
9. **Phụ lục:** system_prompt.txt, 3 file log thật, ai-usage.md, screenshot terminal, Git history.

> Không đưa các số liệu placeholder vào báo cáo nộp. Thầy yêu cầu 8–9 trang Word, nhóm cần thêm ảnh minh họa và số liệu thực tế rồi dàn trang.
