# KHAI BÁO SỬ DỤNG AI (AI USAGE DECLARATION)

**Dự án:** Trợ lý CTXH – Quy đổi & Đăng ký  
**Nhóm:** 09  
**Repository:** https://github.com/tvn233/AIProject  
**Ngày cập nhật:** 18/10/2026

## 1. Thành viên và công cụ sử dụng

| Thành viên | Vai trò | Công cụ AI đã khai báo |
|---|---|---|
| Trương Văn Ngọc – 24110111 | Data & RAG | ChatGPT (OpenAI) |
| Hà Ngọc Bảo – 24110078 | MCP | Google Gemini / LLMs  |
| Nguyễn Công Thành – 24110131 | LLM & Agent | ChatGPT (OpenAI) |

Groq API và mô hình E5 là thành phần vận hành chương trình; chúng không phải công cụ nhóm khai báo để sinh code. ChatGPT cũng hỗ trợ biên tập tài liệu này.

**Cách đọc phần code:** Các đoạn trích từ ZIP cho thấy code đang có trong project. Chúng xác định phần việc được AI hỗ trợ theo khai báo của nhóm, nhưng ZIP không lưu câu trả lời AI gốc để chứng minh từng dòng là nguyên văn AI sinh. Đoạn mã nháp do thành viên cung cấp được ghi rõ là *bản nháp*, kể cả khi không xuất hiện trong bản cuối.

## 2. Chi tiết theo từng thành viên

### 2.1. Trương Văn Ngọc — Data & RAG

#### Tạo embedding E5

- **Prompt:** “Làm thế nào để tạo embedding cho tài liệu và câu hỏi bằng mô hình E5?”
- **AI làm gì:** Giải thích việc mã hóa tài liệu và câu hỏi bằng hai tiền tố khác nhau. Đoạn code liên quan trong bản triển khai:

  ```python
  def embed_documents(self, texts: Sequence[str]) -> np.ndarray:
      return self._encode(texts, prefix="passage: ")

  def embed_queries(self, texts: Sequence[str]) -> np.ndarray:
      return self._encode(texts, prefix="query: ")
  ```

- **Tôi làm gì:** Tích hợp `MultilingualE5Embedder` vào pipeline, chạy thử mô hình trong môi trường `.venv` và kiểm tra việc truy xuất trên corpus.
- **Minh chứng:** `src/rag/embeddings.py`, `src/rag/rag.py`, kết quả `python demo_retrieval.py`.

#### Tìm kiếm Dense và Hybrid

- **Prompt:** “Làm thế nào để kết hợp Dense và BM25?”
- **AI làm gì:** Gợi ý tính điểm Dense, BM25 và gộp thứ hạng. Trong bản cuối, nhóm dùng **RRF**, thể hiện ở đoạn:

  ```python
  dense_scores = self._vectors @ query_vector
  bm25_scores = np.asarray(
      self._bm25.get_scores(tokenize_vietnamese(query)), dtype=np.float32
  )
  fused_scores = (
      self.dense_weight / (self.rrf_k + dense_ranks)
      + lexical_weight / (self.rrf_k + bm25_ranks)
  )
  ```

- **Tôi làm gì:** Tích hợp hai chế độ tìm kiếm và xem kết quả thực tế của từng chế độ. Tôi đối chiếu `doc_id` cùng nội dung chunk được trả về; không mô tả RRF là phép cộng trực tiếp hai điểm số thô.
- **Minh chứng:** `src/rag/retriever.py`, `demo_retrieval.py`.


#### Đọc quy tắc quy đổi từ DOC0009

- **Prompt:** “Tôi đã biết quy tắc đổi điểm CTXH nhưng chưa biết làm sao để `convert_ctxh_points_policy` đọc `conversion_policy` từ file Markdown DOC0009 rồi tính số ngày. Tôi cần làm thế nào?”
- **AI làm gì:** Hướng dẫn dùng `MarkdownChunker.parse_yaml_frontmatter` để lấy `conversion_policy`, kiểm tra các giá trị và áp dụng quy tắc trong file. Đây là đoạn **thực tế** trong bản ZIP:

  ```python
  metadata, _ = MarkdownChunker.parse_yaml_frontmatter(
      doc_path.read_text(encoding="utf-8")
  )
  policy = metadata.get("conversion_policy")
  rate = policy.get("points_per_day")
  threshold = policy.get("remainder_threshold")
  rules = policy.get("remainder_rules")

  whole_days, remainder = divmod(points, rate)
  if remainder < threshold:
      extra_days = rules["less_than_5"]
  elif remainder == threshold:
      extra_days = rules["equal_to_5"]
  else:
      extra_days = rules["greater_than_5"]
  days = whole_days + extra_days
  ```

- **Tôi làm gì:** Ghi quy tắc vào DOC0009, đưa phần đọc tài liệu vào hàm quy đổi, kiểm tra lỗi metadata và thử `convert_ctxh_points_policy(25)`: kết quả 2,5 ngày, nguồn DOC0009. Quy tắc được lưu trong dữ liệu; tôi không khai báo AI đã tự xác lập tỷ lệ quy đổi.
- **Minh chứng:** `data/corpus/DOC0009_quy_doi_diem_ctxh.md`, `src/mcp/tools.py`, `logs/demo_20261017_225320.jsonl`.

#### Kiểm tra câu có đáp án và câu không có đáp án

- **Prompt:** “Làm thế nào để kiểm tra RAG có dẫn đúng nguồn và biết từ chối câu hỏi không có đáp án trong corpus?”
- **AI làm gì:** Gợi ý đối chiếu câu trả lời với `doc_id` kỳ vọng và kiểm tra cách từ chối suy đoán. Đoạn trong bản đánh giá:

  ```python
  unknown = pipeline.ask(UNANSWERABLE_QUESTION, top_k=5)
  abstained = any(
      marker in unknown.answer.casefold()
      for marker in ABSTENTION_MARKERS
  )
  passed &= abstained
  ```

- **Tôi làm gì:** Chạy một câu có đáp án trong DOC0001 và một câu hỏi điểm CTXH cá nhân không có trong tài liệu; kết quả báo ĐẠT.
- **Minh chứng:** `src/rag/evaluate_rag.py` và kết quả chạy `python -m src.rag.evaluate_rag`.

### 2.2. Hà Ngọc Bảo — MCP

#### Tham khảo khung dữ liệu cho công cụ

- **Prompt:** “Gợi ý giúp tôi khung cơ bản sử dụng `dataclass` trong Python cho các tham số đầu vào của công cụ đăng ký hoạt động công tác xã hội.”
- **AI làm gì:**  AI tạo **bản nháp**:

  ```python
  from dataclasses import dataclass

  @dataclass
  class RegisterCtxhActivityArgs:
      student_id: str
      activity_code: str
  ```

- **Tôi làm gì:** Tham khảo type hint cho tham số công cụ và hoàn thiện các tham số trong MCP server. Tôi không khai báo class `RegisterCtxhActivityArgs` là code đang có trong ZIP cuối vì bản ZIP không chứa class đó.
- **Minh chứng:** Bản khai báo AI thành viên cung cấp; `src/mcp/mcp_server.py` là file để đối chiếu giao diện công cụ cuối.

#### Tham khảo giao tiếp stdio

- **Prompt:** “Hãy phác thảo sơ bộ đoạn code Python xử lý giao tiếp Stdio JSON-RPC, lưu ý cách bỏ qua dòng trống, bắt ngoại lệ và ghi lỗi ra stderr, đồng thời sử dụng stdout flush.”
- **AI làm gì:** AI đưa đoạn **nháp**:

  ```python
  for line in sys.stdin:
      if not line.strip():
          continue
      try:
          req = json.loads(line)
          res = handle_mcp_request(req)
          sys.stdout.write(json.dumps(res) + "\n")
          sys.stdout.flush()
      except Exception as e:
          sys.stderr.write(f"Error: {e}\n")
  ```

- **Tôi làm gì:** Tham khảo nguyên tắc giữ `stdout` cho giao thức. Bản cuối dùng MCP SDK với `FastMCP` và `ClientSession`, không chạy nguyên đoạn nháp này.
- **Minh chứng:** `src/mcp/mcp_server.py` và `src/mcp/mcp_client.py` trong ZIP cuối.

#### Xác nhận trước khi ghi và đọc lại kết quả

- **Prompt:** “Hãy đọc các file MCP trong dự án. Giải thích vai trò server, client, bridge; kiểm tra cơ chế xác nhận trước khi ghi và cách đọc lại dữ liệu. Không tự sửa code.”
- **AI làm gì:** Phân tích luồng công cụ và chỉ ra các điểm cần kiểm tra. **Prompt này không sinh code.**
- **Tôi làm gì:** Đối chiếu `bridge.py`: model không tự truyền `confirmed`; terminal yêu cầu xác nhận. Sau khi ghi, `register_and_verify` gọi công cụ đọc để đối chiếu bản ghi và trả `ok` theo kết quả xác minh.
- **Minh chứng:** `src/mcp/bridge.py`, `src/mcp/mcp_client.py`, `src/mcp/tools.py`, `tests/test_mcp_integration.py`.

### 2.3. Nguyễn Công Thành — LLM & Agent

#### Hiểu và rà soát vòng lặp Agent

- **Prompt:** “Giải thích luồng Agent nhận câu hỏi, gọi LLM, gọi công cụ RAG/MCP, đưa kết quả công cụ trở lại ngữ cảnh rồi trả lời; chỉ ra cách giới hạn số bước và xử lý lỗi.”
- **AI làm gì:** Giải thích trình tự LLM → tool call → observation → câu trả lời và những trường hợp cần kiểm tra. Không có phản hồi AI sinh code Agent Loop để trích nguyên văn.
- **Tôi làm gì:** Hoàn thiện và rà soát `CTXHAgent.run`, giới hạn `max_steps`, phân tích JSON arguments, xử lý tên công cụ không hợp lệ và ghi trace. Phần code trong project mà tôi cần giải thích khi bảo vệ gồm:

  ```python
  for step in range(1,self.max_steps+1):
      message = self.llm.complete(messages,tools=self.tool_schemas)
      calls = getattr(message,'tool_calls',None) or []
      if not calls:
          answer = (getattr(message,'content',None) or '').strip()
          trace.append({'step':step,'event':'final'})
          return self._result(answer or 'Không có câu trả lời.',step,trace,start)
  ```

  Trích đoạn này cho biết **vị trí code được rà soát**, không nhận rằng prompt trên đã sinh ra nó.
- **Minh chứng:** `src/agent/agent.py`, `prompts/system_prompt.txt`, `tests/test_agent.py`; các log có `steps` và `trace`.

#### Kết nối Groq, xử lý lỗi API và token

- **Prompt:** “Giải thích cho tôi lỗi `GROQ_API_KEY`, phản hồi HTTP và cách kiểm tra kết quả Agent. Nội dung được ghi theo phần việc tôi cung cấp.”
- **AI làm gì:** Giải thích nguyên nhân thường gặp của lỗi khóa API, lỗi request và lỗi tạm thời; hỗ trợ đọc log, không có bằng chứng trong ZIP rằng AI đã sinh hàm `complete`.
- **Tôi làm gì:** Đối chiếu code `LLMClient`: nạp model và khóa từ môi trường, đặt timeout, chỉ retry lỗi tạm thời, ghi HTTP error và cộng token từ phản hồi. Ví dụ đoạn code đang có:

  ```python
  status = getattr(exc, "status_code", None)
  temporary = status in (408, 409, 429, 500, 502, 503, 504)
  temporary = temporary or isinstance(exc, (TimeoutError, ConnectionError))
  if not temporary or attempt >= self.max_retries:
      raise
  time.sleep(min(2 ** attempt, 4))
  ```

- **Minh chứng:** `src/agent/llm_client.py`, `logs/http_errors.jsonl`, trường `USAGE` trong `logs/demo_*.jsonl`.

#### Kiểm tra câu trả lời theo điều kiện nghiệp vụ

- **Prompt:** “Hãy đánh giá câu trả lời của Agent đối với câu hỏi: ‘Tôi có 25 điểm CTXH chưa được duyệt, có đủ điều kiện quy đổi không?’ Đối chiếu với tài liệu corpus, phân biệt kết quả tính điểm và điều kiện phê duyệt. Chỉ phân tích, không tự thay đổi mã nguồn.”
- **AI làm gì:** Chỉ ra phép quy đổi điểm thành ngày không tự chứng minh điểm đó đã được thẩm định. **Prompt này không sinh code.**
- **Tôi làm gì:** Đối chiếu nhận xét với DOC0009, ghi đây là một trường hợp Agent cần làm rõ điều kiện; không trình bày nó như toàn bộ việc phát triển Agent và không nhận đã sửa code từ phiên phân tích này.
- **Minh chứng:** `data/corpus/DOC0009_quy_doi_diem_ctxh.md`, `src/agent/agent.py`.

#### Kiểm thử Agent và lưu dấu vết

- **Prompt:** “Dựa trên cấu trúc đồ án, hãy hướng dẫn tôi kiểm thử Unit Tests và MCP tool discovery bằng PowerShell. Giải thích ý nghĩa PASS/FAIL và những lỗi thường gặp. Không tự tạo kết quả kiểm thử giả.”
- **AI làm gì:** Hướng dẫn lệnh chạy và cách đọc kết quả. **Prompt này không sinh test hoặc code Agent.**
- **Tôi làm gì:** Chạy và kiểm tra `tests/test_agent.py` với LLM và pipeline giả lập cho ba trường hợp: gọi công cụ rồi trả lời, gọi công cụ không tồn tại và chạm giới hạn bước. `main.py` in tóm tắt trace; `src/agent/logging_utils.py` ghi `steps`, `trace`, `USAGE` vào JSONL. Tôi chạy `python -m unittest discover -s tests -v`, kết quả 16/16 đạt.
- **Minh chứng:** `tests/test_agent.py`, `src/agent/logging_utils.py`, `main.py`, `logs/demo_*.jsonl`, kết quả `python -m unittest discover -s tests -v`.

**Code AI sinh cho Agent:** Không
## 3. Kiểm chứng và trách nhiệm

Nhóm đã đối chiếu các gợi ý với mã nguồn và tài liệu CTXH, chạy `python -m unittest discover -s tests -v`, `python -m src.mcp.mcp_client` cùng các demo. Kết quả 16/16 unit test đạt là kết quả đã cung cấp từ lần chạy thực tế, không phải AI tự tạo. Những đoạn code trích ở trên thuộc bản project được cung cấp.