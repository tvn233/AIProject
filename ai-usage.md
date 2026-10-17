# AI USAGE DECLARATION

**Đồ án:** Trợ lý CTXH – Quy đổi & Đăng ký  
**Nhóm:** 09  
**Repository:** https://github.com/tvn233/AIProject  
**Ngày cập nhật:** 17/10/2026 *(điều chỉnh nếu cập nhật vào ngày khác)*

## 1. Công cụ AI đã sử dụng

| Công cụ | Vai trò trong quá trình thực hiện | Minh chứng |
|---|---|---|
| ChatGPT (OpenAI) | Tham khảo giải thích kiến trúc, rà soát MCP và RAG, hướng dẫn kiểm thử, phân tích đầu ra Agent, hỗ trợ chẩn đoán lỗi môi trường/API và Git; đề xuất một số hàm tiện ích độc lập để nhóm xem xét. | [Cuộc trò chuyện hỗ trợ](https://chatgpt.com/share/6ad3aead-b7a0-83ec-bff0-f4b6f3f55dcf) |

*Phạm vi khai báo:* Phân biệt việc AI **nhận xét/hướng dẫn** với việc AI **sinh đoạn mã**. Đoạn mã do AI đề xuất không đồng nghĩa đã được tích hợp vào repository.

## 2. AI hỗ trợ phần nào?

| Hạng mục | Phạm vi hỗ trợ | File/thành phần liên quan | Kết quả hoặc trạng thái |
|---|---|---|---|
| MCP | Giải thích MCP SDK, phân biệt server cũ và luồng chính thức; rà soát xác nhận trước thao tác ghi. | `src/mcp/mcp_server.py`, `src/mcp/mcp_client.py`, `src/mcp/bridge.py` | Đã tham khảo để rà soát; đối chiếu lại trạng thái xóa mã cũ trong Git. |
| Kiểm thử | Hướng dẫn lệnh Unit Tests và MCP tool discovery. | `tests/`, `main.py`, `src/mcp/` | Đã ghi nhận 16/16 Unit Tests PASS và 4 MCP tools trong lần kiểm thử được báo cáo. |
| Agent và lỗi vận hành | Hỗ trợ phân tích lỗi khóa API/HTTP 401 và câu trả lời về điểm CTXH chưa duyệt. | `src/agent/llm_client.py`, `src/agent/agent.py`, `main.py` | Đã phân tích; tình huống điểm chưa duyệt được ghi nhận là hạn chế cần đối chiếu quy định. |
| RAG | Giải thích embedding E5, Dense/Hybrid Retrieval, Hit@3 và `no_answer`. | `src/rag/`, corpus, dữ liệu đánh giá | [BỔ SUNG KẾT QUẢ THỰC SỰ ĐÃ ĐỐI CHIẾU SAU PHIÊN P04]. |
| Hàm tiện ích/kiểm thử | Yêu cầu AI đề xuất hàm định dạng, kiểm tra dữ liệu và Unit Tests nhỏ. | [CHỈ GHI ĐƯỜNG DẪN FILE NẾU ĐÃ TẠO/TÍCH HỢP] | Chưa xác nhận trạng thái tích hợp; xem mục 4.2. |
| Tài liệu | Hỗ trợ rà soát cách trình bày khai báo sử dụng AI. | `ai-usage.md` | Có sử dụng AI để hỗ trợ soạn/chỉnh sửa tài liệu này. |

## 3. Prompt chính và bằng chứng

### P01 — Rà soát kiến trúc MCP

- **Thời điểm:** 13/10/2026 *(xác nhận theo lịch sử trò chuyện)*.
- **Prompt đã gửi:** Hãy đọc các file MCP trong dự án tôi đã tải lên. Giải thích vai trò của `mcp_server.py`, `mcp_client.py` và `bridge.py`. Kiểm tra cơ chế xác nhận trước khi ghi dữ liệu và chỉ ra các rủi ro nếu có. Không tự sửa code, chỉ đưa nhận xét dựa trên mã nguồn.
- **Mục đích:** Xác định luồng MCP chính thức, phân biệt mã cũ và kiểm tra bước xác nhận trước ghi dữ liệu.
- **Phần được hỗ trợ:** `src/mcp/mcp_server.py`, `src/mcp/mcp_client.py`, `src/mcp/bridge.py`.
- **Kết quả sử dụng:** Tham khảo nhận xét để đối chiếu MCP SDK, cơ chế xác nhận trước thao tác đăng ký và việc đọc lại dữ liệu để xác minh. Việc loại bỏ server cũ chỉ được coi là hoàn tất khi xác nhận trong phiên bản Git cuối cùng.
- **Code sinh từ prompt này:** Không yêu cầu sinh code.
- **Minh chứng:** [Cuộc trò chuyện P01](https://chatgpt.com/share/6ad3ac3c-7b10-83ec-a92f-d4cf38f78f1f).

### P02 — Hướng dẫn kiểm thử và tái hiện lỗi

- **Thời điểm:** 14/10/2026 *(xác nhận theo lịch sử trò chuyện)*.
- **Prompt đã gửi:** Dựa trên cấu trúc đồ án, hãy hướng dẫn tôi kiểm thử Unit Tests và MCP tool discovery bằng PowerShell. Giải thích ý nghĩa của kết quả PASS/FAIL và những lỗi thường gặp. Không tự tạo kết quả kiểm thử giả.
- **Mục đích:** Hướng dẫn chạy `python -m unittest discover -s tests -v` và kiểm tra danh sách MCP tools.
- **Kết quả sử dụng:** Theo kết quả nhóm đã ghi nhận, 16/16 Unit Tests PASS; MCP tool discovery liệt kê `register_ctxh_activity_tool`, `get_ctxh_registration_status_tool`, `convert_ctxh_points_tool`, `convert_ctxh_points_policy_tool`. Đây là kết quả của lần chạy được ghi nhận, không mặc nhiên đại diện cho mọi commit về sau.
- **Code sinh từ prompt này:** Không yêu cầu sinh code.
- **Minh chứng:** [Cuộc trò chuyện P02](https://chatgpt.com/share/6ad3ac3c-7b10-83ec-a92f-d4cf38f78f1f).
- **Bằng chứng thực thi bổ sung:** [ĐIỀN LOG/ẢNH KẾT QUẢ NẾU CÓ].

### P03 — Phân tích câu trả lời Agent

- **Thời điểm:** 15/10/2026 *(xác nhận theo lịch sử trò chuyện)*.
- **Prompt đã gửi:** Hãy đánh giá câu trả lời của Agent đối với câu hỏi: "Tôi có 25 điểm CTXH chưa được duyệt, có đủ điều kiện quy đổi không?" Đối chiếu với tài liệu corpus, phân biệt kết quả tính điểm và điều kiện phê duyệt. Chỉ phân tích, không tự thay đổi mã nguồn.
- **Mục đích:** Đánh giá câu trả lời quy đổi điểm có xem xét đầy đủ trạng thái chưa duyệt hay không.
- **Kết quả sử dụng:** Agent trả lời 25 điểm tương đương 2,5 ngày CTXH theo công cụ demo nhưng chưa làm rõ tình trạng chưa được duyệt. Nhóm ghi nhận đây là tình huống cần kiểm tra nghiệp vụ và đối chiếu corpus; không khẳng định đã sửa lỗi bằng prompt này.
- **Code sinh từ prompt này:** Không yêu cầu sinh code.
- **Minh chứng:** [Cuộc trò chuyện P03](https://chatgpt.com/share/6ad3ac3c-7b10-83ec-a92f-d4cf38f78f1f).

### P04 — Rà soát và đánh giá hệ thống RAG

- **Thời điểm:** 16/10/2026.
- **Prompt chính:** Yêu cầu phân tích `src/rag/`, embedding E5, Dense/Hybrid Retrieval, chỉ số Hit@3 và các câu hỏi `no_answer` dựa trên mã nguồn và kết quả đánh giá; không tạo hoặc sửa code.
- **Mục đích:** Tham khảo ý kiến kỹ thuật về quy trình truy xuất và chất lượng RAG.
- **Phần được hỗ trợ:** `src/rag/`, corpus và kết quả đánh giá.
- **Kết quả sử dụng:** [ĐIỀN NHẬN XÉT ĐÃ THỰC SỰ KIỂM CHỨNG/ÁP DỤNG].
- **Code sinh từ prompt này:** [XÁC NHẬN TỪ NỘI DUNG PHẢN HỒI; NẾU CHỈ PHÂN TÍCH THÌ GHI “KHÔNG CÓ”].
- **Minh chứng:** [Cuộc trò chuyện RAG](https://chatgpt.com/share/6ad3b062-d53c-83ec-aa87-6e842f6fe952) *(kiểm tra link có chứa phiên P04)*.

### Các phiên hỗ trợ khác

- **Phạm vi:** Phân tích lỗi Groq API 401, Git, README, logs hoặc chuẩn bị bảo vệ, nếu đã thực hiện.
- **Prompt/link:** [BỔ SUNG PROMPT THỰC TẾ VÀ LINK TƯƠNG ỨNG NẾU CẦN].
- **Kết quả:** [BỔ SUNG CHỈ KHI CÓ MINH CHỨNG].

## 4. Đoạn code nào do AI sinh?

### 4.1. Các phiên chỉ rà soát, phân tích hoặc hướng dẫn

Các phiên P01–P03 không yêu cầu ChatGPT trực tiếp sinh hoặc chỉnh sửa mã nguồn. Đối với P04, cần xác nhận phản hồi thực tế trước khi kết luận.

| Phần được hỗ trợ | Mã nguồn phát sinh từ phiên | Công cụ | Minh chứng | Cách nhóm kiểm chứng |
|---|---|---|---|---|
| MCP (P01) | Không yêu cầu sinh code | ChatGPT | [Xem minh chứng](https://chatgpt.com/share/6ad3b062-d53c-83ec-aa87-6e842f6fe952) | Đối chiếu nhận xét với mã nguồn MCP. |
| Unit Tests/MCP discovery (P02) | Không yêu cầu sinh code | ChatGPT | [Xem minh chứng](https://chatgpt.com/share/6ad3b062-d53c-83ec-aa87-6e842f6fe952) | Chạy lệnh kiểm thử thực tế. |
| Agent (P03) | Không yêu cầu sinh code | ChatGPT | [Xem minh chứng](https://chatgpt.com/share/6ad3b062-d53c-83ec-aa87-6e842f6fe952) | Đối chiếu output với corpus. |
| RAG (P04) | [XÁC NHẬN: KHÔNG CÓ NẾU CHỈ PHÂN TÍCH] | ChatGPT | [Xem minh chứng](https://chatgpt.com/share/6ad3b062-d53c-83ec-aa87-6e842f6fe952) | Rà soát truy xuất và kết quả Dense/Hybrid thực tế. |

### 4.2. Các đoạn mã do AI đề xuất trong phiên khác

Các mục dưới đây là **đề xuất cần xác minh**. Không ghi là “đã áp dụng” nếu đoạn mã chỉ xuất hiện trong câu trả lời của AI mà chưa được đưa vào repository.

| Đề xuất | Hàm/đoạn code AI đề xuất | Công cụ | Prompt hoặc link | File thực tế và trạng thái kiểm chứng |
|---|---|---|---|---|
| Định dạng ngày CTXH | `format_ctxh_days(days)` | ChatGPT | [Cuộc trò chuyện sinh code](https://chatgpt.com/share/6ad3b0e4-53cc-83ec-bde8-26920072a70f) | [FILE THỰC TẾ / CHỈ THAM KHẢO / ĐÃ TÍCH HỢP VÀ TEST]. |
| Kiểm tra điểm đầu vào | `validate_ctxh_points(points)` | ChatGPT | [Cuộc trò chuyện sinh code](https://chatgpt.com/share/6ad3b0e4-53cc-83ec-bde8-26920072a70f) | [FILE THỰC TẾ / CHỈ THAM KHẢO / ĐÃ TÍCH HỢP VÀ TEST]. |
| Định dạng thời gian log | `format_log_timestamp(timestamp)` | ChatGPT | [Cuộc trò chuyện sinh code](https://chatgpt.com/share/6ad3b0e4-53cc-83ec-bde8-26920072a70f) | [FILE THỰC TẾ / CHỈ THAM KHẢO / ĐÃ TÍCH HỢP VÀ TEST]. |
| Unit Tests cho hàm tiện ích | [TÊN HÀM TEST CỤ THỂ] | ChatGPT | [Cuộc trò chuyện sinh code](https://chatgpt.com/share/6ad3b0e4-53cc-83ec-bde8-26920072a70f) | [FILE TEST THỰC TẾ / CHỈ THAM KHẢO / ĐÃ CHẠY TEST]. |

**Nguyên tắc xác nhận:** Nếu không có đoạn mã nào trong bảng 4.2 được tích hợp, ghi rõ: “Các đoạn mã được AI đề xuất chỉ phục vụ tham khảo, chưa được đưa vào mã nguồn sản phẩm”. Nếu có tích hợp, điền chính xác đường dẫn file, hàm, commit và kết quả kiểm thử. Nhóm cũng cần khai báo các đoạn mã AI sinh trong những phiên phát triển khác, nếu có.

## 5. Kiểm chứng và trách nhiệm

- Nhóm tự thực hiện kiểm thử và đối chiếu các nhận xét của AI với mã nguồn, corpus và kết quả chạy thực tế.
- Lệnh kiểm thử tham khảo: `python -m unittest discover -s tests -v`; kiểm tra MCP: `python -m src.mcp.mcp_client`.
- Bằng chứng kết quả kiểm thử/log: [ĐIỀN ĐƯỜNG DẪN FILE HOẶC LINK THỰC TẾ].
- Các kết quả 16/16 PASS và 4 MCP tools chỉ phản ánh lần chạy đã ghi nhận; cần chạy lại trên commit cuối trước khi nộp.
- Không đưa API key, nội dung `.env` hoặc dữ liệu nhạy cảm vào đường dẫn chia sẻ.
- Nhóm chịu trách nhiệm về mã nguồn, dữ liệu, kết quả demo và nội dung báo cáo.

## 6. Danh sách minh chứng

- **Repository:** https://github.com/tvn233/AIProject
- **Cuộc trò chuyện hỗ trợ tổng quát:** https://chatgpt.com/share/6ad3aead-b7a0-83ec-bff0-f4b6f3f55dcf
- **Cuộc trò chuyện P01–P03:** https://chatgpt.com/share/6ad3ac3c-7b10-83ec-a92f-d4cf38f78f1f
- **Cuộc trò chuyện rà soát RAG và các phần khác:** https://chatgpt.com/share/6ad3b062-d53c-83ec-aa87-6e842f6fe952
- **Cuộc trò chuyện đề xuất hàm tiện ích:** https://chatgpt.com/share/6ad3b0e4-53cc-83ec-bde8-26920072a70f
