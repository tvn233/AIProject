# AI USAGE DECLARATION

**Đồ án:** Trợ lý CTXH – Quy đổi & Đăng ký  
**Nhóm:** 09  
**Repository:** https://github.com/tvn233/AIProject  
**Ngày cập nhật:** 18/10/2026

## 1. Công cụ AI đã sử dụng

| Công cụ | Mục đích sử dụng | Minh chứng |
|---|---|---|
| ChatGPT (OpenAI) | Tham khảo kiến trúc RAG, Agent và MCP; rà soát mã nguồn; hướng dẫn kiểm thử, phân tích lỗi API và kết quả đầu ra; đề xuất một số hàm tiện ích và bài kiểm thử; hỗ trợ biên tập tài liệu. | https://chatgpt.com/share/6ad3aead-b7a0-83ec-bff0-f4b6f3f55dcf |

ChatGPT được sử dụng trong quá trình hỗ trợ phát triển và kiểm tra dự án. Groq API và mô hình embedding E5 là thành phần vận hành của sản phẩm, không đồng nghĩa với việc các thành phần đó đã tự động sinh mã nguồn cho nhóm.

## 2. Phần việc được AI hỗ trợ

| Hạng mục | Phạm vi hỗ trợ | Thành phần liên quan | Kết quả ghi nhận |
|---|---|---|---|
| Data & RAG | Tham khảo cách tổ chức corpus, embedding E5, Dense/Hybrid Retrieval, BM25, Hit@3, trích dẫn nguồn và câu hỏi không có đáp án. | `src/rag/`, `data/`, dữ liệu đánh giá | Hỗ trợ phân tích cách truy xuất và diễn giải các chỉ số đánh giá. |
| LLM & Agent | Giải thích luồng Agent, tích hợp truy xuất và công cụ, xử lý lỗi API, đánh giá nội dung câu trả lời. | `src/agent/`, `prompts/`, `main.py` | Ghi nhận tình huống Agent tính 25 điểm thành 2,5 ngày nhưng chưa làm rõ trạng thái chưa duyệt. |
| MCP | Rà soát SDK MCP, vai trò Server/Client/Bridge, xác nhận trước khi ghi dữ liệu và đọc lại kết quả. | `src/mcp/` | Hỗ trợ phân biệt luồng MCP chính thức với phiên bản cũ. |
| Testing & Logs | Hướng dẫn Unit Tests, MCP tool discovery, giải thích PASS/FAIL và dữ liệu log. | `tests/`, `logs/` | Đã ghi nhận một lần kiểm thử 16/16 Unit Tests PASS và phát hiện 4 MCP tools. |
| Hàm tiện ích | Đề xuất các hàm định dạng, kiểm tra dữ liệu và Unit Tests nhỏ. | Các đoạn mã tiện ích được nhóm xem xét | Nhóm cho biết đã tham khảo và tích hợp; vị trí mã nguồn cụ thể chưa được đối chiếu độc lập. |
| Tài liệu | Hỗ trợ rà soát và trình bày bản khai báo AI. | `ai-usage.md` | Tài liệu này được ChatGPT hỗ trợ biên tập. |

### Phân công phần việc trong nhóm

| Vai trò | Phần việc kỹ thuật | Nội dung AI có liên quan |
|---|---|---|
| Người 1 – Data & RAG | Mô hình dữ liệu, tài liệu CTXH, chunking, embedding, Dense/Hybrid BM25, tìm kiếm và trích dẫn. | Rà soát và giải thích RAG, đánh giá truy xuất. |
| Người 2 – LLM & Agent | API, retry/timeout, Agent Loop, tích hợp RAG và chương trình chính. | Phân tích luồng Agent, lỗi vận hành và câu trả lời. |
| Người 3 – MCP & Testing | MCP Server/Client, đăng ký và quy đổi CTXH, kiểm thử, evaluation, logs. | Rà soát MCP, hướng dẫn kiểm thử và phân tích log. |

Bảng trên thể hiện phân công kỹ thuật và phạm vi AI hỗ trợ tương ứng, không khẳng định mỗi thành viên đã trực tiếp sử dụng một tài khoản ChatGPT riêng.

## 3. Prompt chính và minh chứng

### P01 — Rà soát kiến trúc MCP

**Thời điểm khai báo:** 13/10/2026  
**Prompt:** Hãy đọc các file MCP trong dự án tôi đã tải lên. Giải thích vai trò của `mcp_server.py`, `mcp_client.py` và `bridge.py`. Kiểm tra cơ chế xác nhận trước khi ghi dữ liệu và chỉ ra các rủi ro nếu có. Không tự sửa code, chỉ đưa nhận xét dựa trên mã nguồn.  
**Phần được hỗ trợ:** `src/mcp/mcp_server.py`, `src/mcp/mcp_client.py`, `src/mcp/bridge.py`.  
**Kết quả sử dụng:** Tham khảo nhận xét để rà soát luồng MCP SDK, bước xác nhận trước đăng ký và cách đọc lại dữ liệu để kiểm chứng.  
**Mã nguồn phát sinh từ prompt:** Không yêu cầu sinh mã nguồn.  
**Minh chứng:** https://chatgpt.com/share/6ad3ac3c-7b10-83ec-a92f-d4cf38f78f1f

### P02 — Hướng dẫn kiểm thử và MCP tool discovery

**Thời điểm khai báo:** 14/10/2026  
**Prompt:** Dựa trên cấu trúc đồ án, hãy hướng dẫn tôi kiểm thử Unit Tests và MCP tool discovery bằng PowerShell. Giải thích ý nghĩa của kết quả PASS/FAIL và những lỗi thường gặp. Không tự tạo kết quả kiểm thử giả.  
**Phần được hỗ trợ:** `tests/`, `src/mcp/`, `main.py`.  
**Kết quả sử dụng:** Nhóm thực hiện lệnh `python -m unittest discover -s tests -v` và đã ghi nhận 16/16 Unit Tests PASS. Một lần kiểm tra MCP liệt kê bốn công cụ: `register_ctxh_activity_tool`, `get_ctxh_registration_status_tool`, `convert_ctxh_points_tool`, `convert_ctxh_points_policy_tool`. Đây là kết quả được ghi nhận tại thời điểm thử nghiệm, không mặc nhiên xác nhận mọi phiên bản sau đó.  
**Mã nguồn phát sinh từ prompt:** Không yêu cầu sinh mã nguồn.  
**Minh chứng:** https://chatgpt.com/share/6ad3ac3c-7b10-83ec-a92f-d4cf38f78f1f

### P03 — Phân tích kết quả Agent

**Thời điểm khai báo:** 15/10/2026  
**Prompt:** Hãy đánh giá câu trả lời của Agent đối với câu hỏi: "Tôi có 25 điểm CTXH chưa được duyệt, có đủ điều kiện quy đổi không?" Đối chiếu với tài liệu corpus, phân biệt kết quả tính điểm và điều kiện phê duyệt. Chỉ phân tích, không tự thay đổi mã nguồn.  
**Phần được hỗ trợ:** `src/agent/`, corpus CTXH.  
**Kết quả sử dụng:** Agent trả về phép quy đổi 25 điểm tương đương 2,5 ngày CTXH theo dữ liệu demo, nhưng chưa làm rõ trạng thái chưa duyệt. Nhóm ghi nhận đây là hạn chế cần đối chiếu quy định và đánh giá thêm; không khẳng định đã sửa mã nguồn qua phiên này.  
**Mã nguồn phát sinh từ prompt:** Không yêu cầu sinh mã nguồn.  
**Minh chứng:** https://chatgpt.com/share/6ad3ac3c-7b10-83ec-a92f-d4cf38f78f1f

### P04 — Rà soát hệ thống RAG

**Nội dung prompt:** Yêu cầu đọc `src/rag/`, phân tích embedding E5, Dense/Hybrid Retrieval, BM25, Hit@3, xử lý `no_answer` và nhận xét chất lượng truy xuất dựa trên mã nguồn, dữ liệu đánh giá; không tạo hoặc sửa code.  
**Phần được hỗ trợ:** `src/rag/`, corpus, kết quả đánh giá.  
**Kết quả sử dụng:** Nội dung tham khảo phục vụ giải thích pipeline RAG và diễn giải chỉ số truy xuất. Kết quả đã ghi nhận trong dự án gồm Dense Hit@3 = 0,875 và Hybrid Hit@3 = 0,75; các con số này là kết quả đánh giá dự án, không phải kết quả ChatGPT tự chạy trong phiên hỏi đáp.  
**Mã nguồn phát sinh từ prompt:** Prompt chỉ yêu cầu phân tích, không yêu cầu sinh code.  
**Minh chứng:** https://chatgpt.com/share/6ad3b062-d53c-83ec-aa87-6e842f6fe952

### Phiên tham khảo về hàm tiện ích và Unit Tests

**Nội dung yêu cầu:** Đề xuất hàm `format_ctxh_days(days)`, `validate_ctxh_points(points)`, `format_log_timestamp(timestamp)` và một số Unit Tests cho hàm tiện ích.  
**Mục đích:** Tham khảo cách định dạng kết quả CTXH, kiểm tra dữ liệu đầu vào, định dạng thời gian log và kiểm thử trường hợp biên.  
**Minh chứng:** https://chatgpt.com/share/6ad3b0e4-53cc-83ec-bde8-26920072a70f

## 4. Đoạn code do AI sinh

### 4.1. Các phiên phân tích không yêu cầu sinh code

| Phiên | Thành phần | Mã nguồn được yêu cầu sinh | Cách sử dụng |
|---|---|---|---|
| P01 | MCP | Không | Tham khảo nhận xét và đối chiếu mã nguồn. |
| P02 | Unit Tests và MCP discovery | Không | Thực hiện kiểm thử bằng lệnh được hướng dẫn. |
| P03 | Agent | Không | Đối chiếu kết quả Agent với dữ liệu CTXH. |
| P04 | RAG | Không | Tham khảo giải thích pipeline và chỉ số đánh giá. |

### 4.2. Các đoạn mã AI đề xuất

| Đoạn mã được đề xuất | Chức năng | Công cụ | Nguồn prompt | Trạng thái khai báo |
|---|---|---|---|---|
| `format_ctxh_days(days)` | Định dạng số ngày CTXH để hiển thị. | ChatGPT | https://chatgpt.com/share/6ad3b0e4-53cc-83ec-bde8-26920072a70f | Nhóm xác nhận đã tham khảo và tích hợp; chưa đối chiếu vị trí hàm trong repository. |
| `validate_ctxh_points(points)` | Kiểm tra dữ liệu điểm CTXH đầu vào. | ChatGPT | https://chatgpt.com/share/6ad3b0e4-53cc-83ec-bde8-26920072a70f | Nhóm xác nhận đã tham khảo và tích hợp; chưa đối chiếu vị trí hàm trong repository. |
| `format_log_timestamp(timestamp)` | Định dạng thời gian trong log. | ChatGPT | https://chatgpt.com/share/6ad3b0e4-53cc-83ec-bde8-26920072a70f | Nhóm xác nhận đã tham khảo và tích hợp; chưa đối chiếu vị trí hàm trong repository. |
| Unit Tests cho hàm tiện ích | Kiểm tra đầu vào hợp lệ, không hợp lệ và trường hợp biên. | ChatGPT | https://chatgpt.com/share/6ad3b0e4-53cc-83ec-bde8-26920072a70f | Nhóm xác nhận đã tham khảo và tích hợp; chưa xác định tên bài test cụ thể trong repository. |

Các tên hàm trên là tên được nêu trong phiên trao đổi với AI. Chưa có căn cứ độc lập để khẳng định chúng tồn tại nguyên tên trong phiên bản Git cuối cùng. Việc khai báo đã tích hợp phản ánh thông tin nhóm cung cấp; không thay thế kiểm tra mã nguồn và commit thực tế.

## 5. Kiểm chứng và trách nhiệm

Nhóm chịu trách nhiệm kiểm tra, điều chỉnh và quyết định sử dụng các gợi ý AI. Các kết quả kiểm thử được thực hiện trong môi trường của nhóm, không phải kết quả do ChatGPT tự giả lập. Lệnh kiểm thử chính là `python -m unittest discover -s tests -v`; lệnh kiểm tra MCP là `python -m src.mcp.mcp_client`. Thư mục `tests/` và `logs/` được dùng làm nơi đối chiếu dữ liệu kiểm thử và lần chạy thực tế.

Không công khai khóa API, nội dung bí mật của `.env` hoặc thông tin nhạy cảm trong các cuộc trò chuyện chia sẻ. Nhóm chịu trách nhiệm về tính chính xác của mã nguồn, tài liệu, kết quả demo và báo cáo.

## 6. Danh sách minh chứng

**Repository:** https://github.com/tvn233/AIProject  
**Trao đổi hỗ trợ chung:** https://chatgpt.com/share/6ad3aead-b7a0-83ec-bff0-f4b6f3f55dcf  
**Rà soát MCP, kiểm thử và Agent:** https://chatgpt.com/share/6ad3ac3c-7b10-83ec-a92f-d4cf38f78f1f  
**Rà soát RAG và các phần liên quan:** https://chatgpt.com/share/6ad3b062-d53c-83ec-aa87-6e842f6fe952  
**Đề xuất hàm tiện ích và Unit Tests:** https://chatgpt.com/share/6ad3b0e4-53cc-83ec-bde8-26920072a70f
