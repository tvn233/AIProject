# AI USAGE DECLARATION

**Đồ án:** Trợ lý CTXH – Quy đổi & Đăng ký  
**Nhóm:** 09
**Repository:** https://github.com/tvn233/AIProject  
**Ngày cập nhật:** [17/10/2026]


## 1. Công cụ AI đã sử dụng

| Công cụ | Vai trò thực tế | Bằng chứng |
|---|---|---|
| ChatGPT (OpenAI) | Giải thích cấu trúc dự án, hỗ trợ rà soát MCP, hướng dẫn kiểm thử, phân tích lỗi chạy chương trình và Git. Hỗ trợ gợi ý sửa bug, các câu lệnh chạy trong terminal... | https://chatgpt.com/share/6ad3aead-b7a0-83ec-bff0-f4b6f3f55dcf |


## 2. AI hỗ trợ phần nào?

| Hạng mục | Phạm vi hỗ trợ thực tế | File liên quan | Trạng thái |
|---|---|---|---|
| Rà soát MCP | Giải thích khác biệt giữa MCP SDK và server cũ; kiểm tra xác nhận trước thao tác ghi | `src/mcp/mcp_server.py`, `src/mcp/mcp_client.py`, `src/mcp/bridge.py` | Đã Thực Thi |
| Kiểm thử | Hướng dẫn chạy Unit Tests và kiểm tra MCP tool discovery | `tests/`, `main.py` | Đã Thực Thi |
| Xử lý lỗi | Phân tích lỗi `GROQ_API_KEY`, HTTP 401 và kết quả Agent chưa xét trạng thái điểm | `src/agent/llm_client.py`, `src/agent/agent.py`, `main.py` | Đã Thực Thi |


## 3. Prompt chính và bằng chứng

### P01 — Rà soát kiến trúc MCP
- **Thời điểm:** 13/10/2026
- **Prompt đã gửi:** Hãy đọc các file MCP trong dự án tôi đã tải lên. Giải thích vai trò của `mcp_server.py`, `mcp_client.py` và `bridge.py`. Kiểm tra cơ chế xác nhận trước khi ghi dữ liệu và chỉ ra các rủi ro nếu có. Không tự sửa code, chỉ đưa nhận xét dựa trên mã nguồn.
- **Mục đích:** Xác định luồng MCP chính thức, phân biệt mã cũ và kiểm tra bước xác nhận trước ghi dữ liệu.
- **Phần được hỗ trợ:** `src/mcp/mcp_server.py`, `src/mcp/mcp_client.py`, `src/mcp/bridge.py`.
- **Kết quả đã áp dụng:** Sử dụng các nhận xét từ ChatGPT để rà soát kiến trúc MCP, xác định MCP Server chính thức sử dụng SDK, kiểm tra cơ chế xác nhận trước thao tác đăng ký và quy trình đọc lại dữ liệu để xác minh kết quả. Nhóm đã đối chiếu các nhận xét với mã nguồn và loại bỏ phiên bản MCP cũ không còn phù hợp với luồng xử lý chính.
- **Minh chứng:** [\[LINK SHARE CHATGPT\]](https://chatgpt.com/share/6ad3ac3c-7b10-83ec-a92f-d4cf38f78f1f)

### P02 — Hướng dẫn kiểm thử và tái hiện lỗi
- **Thời điểm:** 14/10/2026
- **Prompt đã gửi:** Dựa trên cấu trúc đồ án, hãy hướng dẫn tôi kiểm thử Unit Tests và MCP tool discovery bằng PowerShell. Giải thích ý nghĩa của kết quả PASS/FAIL và những lỗi thường gặp. Không tự tạo kết quả kiểm thử giả.
- **Mục đích:** Hướng dẫn chạy `python -m unittest discover -s tests -v` và kiểm tra danh sách MCP tools.
- **Kết quả đã áp dụng:** Nhóm tham khảo hướng dẫn của ChatGPT để thực hiện kiểm thử chương trình trong môi trường Python 3.11. Kết quả ghi nhận 16/16 Unit Tests PASS. Đồng thời, nhóm kiểm tra MCP tool discovery và xác nhận hệ thống nhận diện được 4 công cụ: register_ctxh_activity_tool, get_ctxh_registration_status_tool, convert_ctxh_points_tool và convert_ctxh_points_policy_tool. Các kết quả được sử dụng để kiểm tra khả năng hoạt động của hệ thống trước khi hoàn thiện đồ án.
- **Minh chứng:** [\[LINK SHARE CHATGPT\]](https://chatgpt.com/share/6ad3ac3c-7b10-83ec-a92f-d4cf38f78f1f)

### P03 — Phân tích lỗi Groq/Agent
- **Thời điểm:** 15/10/2026
- **Prompt đã gửi:** Hãy đánh giá câu trả lời của Agent đối với câu hỏi: "Tôi có 25 điểm CTXH chưa được duyệt, có đủ điều kiện quy đổi không?" Đối chiếu với tài liệu corpus, phân biệt kết quả tính điểm và điều kiện phê duyệt. Chỉ phân tích, không tự thay đổi mã nguồn.
- **Mục đích:** Giải thích và phân tích trường hợp câu trả lời quy đổi điểm bỏ sót trạng thái chưa duyệt.
- **Kết quả đã áp dụng:** Nhóm sử dụng ChatGPT để phân tích kết quả thử nghiệm của Agent. Trong trường hợp người dùng có 25 điểm CTXH chưa được duyệt, hệ thống gọi công cụ quy đổi và trả về kết quả 2,5 ngày CTXH nhưng chưa làm rõ điều kiện phê duyệt điểm. Qua phân tích, nhóm nhận diện được hạn chế về khả năng xử lý ngữ cảnh nghiệp vụ và ghi nhận trường hợp này để phục vụ đánh giá hệ thống, đề xuất cải thiện trong tương lai. Trong phạm vi prompt này, nhóm chưa thực hiện chỉnh sửa mã nguồn.
- **Minh chứng:** [\[LINK SHARE CHATGPT\]](https://chatgpt.com/share/6ad3ac3c-7b10-83ec-a92f-d4cf38f78f1f)



## 4. Đoạn code nào do AI sinh?

Trong các phiên hỗ trợ P01, P02 và P03, nhóm sử dụng ChatGPT để rà soát mã nguồn, tham khảo ý kiến kỹ thuật, hướng dẫn kiểm thử và phân tích kết quả đầu ra. Các phiên này không yêu cầu AI tạo hoặc chỉnh sửa mã nguồn.

| Phần được hỗ trợ | Đoạn code do AI sinh trong phiên | Công cụ | Minh chứng | Cách kiểm chứng |
|---|---|---|---|---|
| MCP | Không có | ChatGPT | [https://chatgpt.com/share/6ad3b062-d53c-83ec-aa87-6e842f6fe952] | Đối chiếu nhận xét với mã nguồn |
| Unit Tests và MCP discovery | Không có | ChatGPT | [https://chatgpt.com/share/6ad3b062-d53c-83ec-aa87-6e842f6fe952] | Chạy kiểm thử thực tế |
| Agent | Không có | ChatGPT | [https://chatgpt.com/share/6ad3b062-d53c-83ec-aa87-6e842f6fe952] | Đối chiếu kết quả với corpus |

**Lưu ý:** Kết luận trên chỉ áp dụng cho các phiên P01–P03. Nhóm cần khai báo bổ sung nếu đã sử dụng code do AI tạo trong những phiên phát triển khác.

### 4.1. Các đoạn code AI hỗ trợ tạo bổ sung

| File | Hàm/đoạn code do AI sinh | Công cụ | Prompt hoặc link | Cách nhóm xử lý, kiểm chứng |
|---|---|---|---|---|
| [Sinh hàm định dạng kết quả quy đổi CTXH] | [format_ctxh_days(days)] | ChatGPT | [https://chatgpt.com/share/6ad3b0e4-53cc-83ec-bde8-26920072a70f] | [ĐÃ ÁP DỤNG VÀ KIỂM THỬ / CHỈ THAM KHẢO] |
| [Sinh hàm kiểm tra dữ liệu đầu vào] | [validate_ctxh_points(points)] | ChatGPT | [https://chatgpt.com/share/6ad3b0e4-53cc-83ec-bde8-26920072a70f] | [ĐÃ ÁP DỤNG VÀ KIỂM THỬ / CHỈ THAM KHẢO] |
| [Sinh hàm định dạng timestamp trong log] | [format_log_timestamp(timestamp)] | ChatGPT | [https://chatgpt.com/share/6ad3b0e4-53cc-83ec-bde8-26920072a70f] | [ĐÃ ÁP DỤNG VÀ KIỂM THỬ / CHỈ THAM KHẢO] |
| [Sinh Unit Test cho hàm tiện ích] | [Unit Test] | ChatGPT | [https://chatgpt.com/share/6ad3b0e4-53cc-83ec-bde8-26920072a70f] | [ĐÃ ÁP DỤNG VÀ KIỂM THỬ / CHỈ THAM KHẢO] |



## 5. Kiểm chứng và trách nhiệm

- Các thành viên tự chạy và kiểm tra mã nguồn trong môi trường Python của nhóm.
- Kiểm thử bằng `python -m unittest discover -s tests -v` và `python -m src.mcp.mcp_client`; ghi kết quả thực tế tại [LINK LOG/ẢNH].
- Những gợi ý của AI không được xem là kết quả đúng nếu chưa đối chiếu code, tài liệu CTXH hoặc chạy kiểm thử.
- Nhóm chịu trách nhiệm về mã nguồn, dữ liệu, kết quả demo và nội dung báo cáo.

## 6. Danh sách minh chứng

- **Link Project ChatGPT:** [\[LINK PROJECT HOẶC GHI KHÔNG CÓ\]](https://chatgpt.com/share/6ad3ac3c-7b10-83ec-a92f-d4cf38f78f1f)

