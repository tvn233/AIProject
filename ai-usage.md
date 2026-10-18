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

- **Tôi làm gì:** Chạy một câu có đáp án trong CTXH và một câu hỏi điểm CTXH cá nhân không có trong tài liệu; kết quả báo ĐẠT.
- **Minh chứng:** `src/rag/evaluate_rag.py` và kết quả chạy `python -m src.rag.evaluate_rag`.
#### Chia tài liệu CTXH.md thành chunk

- **Prompt:** “Tài liệu CTXH.md có các mục I–V. Làm thế nào để chia tài liệu theo đề mục, giữ metadata và giới hạn độ dài mỗi chunk?”
- **AI làm gì:** Gợi ý điều chỉnh cách nhận diện đề mục, bỏ chunk chỉ chứa tiêu đề và chia các mục dài thành những chunk có phần chồng lấn. Đoạn code được AI hỗ trợ điều chỉnh:

  ```python
  words = section_content.split()
  step = max_words - overlap_words
  for offset in range(0, len(words), step):
      part = words[offset:offset + max_words]
      chunks.append(DocumentChunk(
          chunk_id=f"{document.doc_id}_CHUNK_{len(chunks) + 1:03d}",
          doc_id=document.doc_id,
          title=document.title,
          section=section,
          content=" ".join(part),
          metadata=dict(document.metadata),
      ))
      if offset + max_words >= len(words):
          break
  ```

- **Tôi làm gì:** Đưa tài liệu `CTXH.md` thầy cung cấp vào corpus, điều chỉnh bộ chia để nhận diện các mục I–V và kiểm tra metadata. Chạy `python -m src.rag.chunking`, kết quả tạo 28 chunk từ tài liệu `CTXH001`.
- **Minh chứng:** `data/corpus/CTXH.md`, `src/rag/chunking.py`, `tests/test_rag.py`; kết quả chạy `python -m src.rag.chunking`.

#### Đọc quy tắc quy đổi từ tài liệu corpus

- **Prompt đã hỏi ở giai đoạn đầu:** “Tôi đã biết quy tắc đổi điểm CTXH nhưng chưa biết làm sao để `convert_ctxh_points_policy` đọc `conversion_policy` từ file Markdown DOC0009 rồi tính số ngày. Tôi cần làm thế nào?” Sau khi chuyển sang tài liệu thầy cung cấp, tôi áp dụng cách làm này cho `CTXH.md`.
- **AI làm gì:** Hướng dẫn đọc YAML frontmatter, lấy tỷ lệ và quy tắc làm tròn từ `conversion_policy`, rồi tính số ngày dựa trên phần nguyên và điểm dư. Đoạn code được AI hỗ trợ:

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

- **Tôi làm gì:** Ghi `conversion_policy` vào frontmatter của `CTXH.md`, đổi đường dẫn trong công cụ quy đổi sang tài liệu này và kiểm tra `convert_ctxh_points_policy(25)`. Kết quả là 2,5 ngày, nguồn `CTXH001, mục II.c`. Quy tắc quy đổi được lấy từ tài liệu CTXH, không phải do AI tự đặt ra.
- **Minh chứng:** `data/corpus/CTXH.md`, `src/mcp/tools.py`, `logs/demo_20261018_205737.jsonl`.

### 2.2. Hà Ngọc Bảo — MCP

#### Xây dựng MCP Server và các công cụ CTXH

- **Prompt:** “Hãy gợi ý khung code Python sử dụng thư viện `mcp.server.fastmcp` để tạo một FastMCP server tên `CTXH Demo`. Cần phác thảo các tool: đăng ký hoạt động (yêu cầu tham số `confirmed` mặc định `False`), kiểm tra trạng thái và quy đổi điểm theo chính sách. Chỉ phác thảo cấu trúc và hàm cơ bản, không viết toàn bộ business logic phức tạp.”
- **AI làm gì:** Đề xuất cách khởi tạo MCP Server bằng `FastMCP`, sử dụng decorator `@mcp.tool()` để khai báo các công cụ thông qua giao thức MCP, phác thảo tham số đầu vào cho chức năng đăng ký hoạt động và đề xuất cơ chế xác nhận thông qua tham số `confirmed`, mặc định là `False`. AI cũng gợi ý cấu trúc cho các tool kiểm tra trạng thái và quy đổi điểm CTXH. Đoạn code được AI gợi ý/phác thảo:

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

- **Tôi làm gì:** Xác định yêu cầu nghiệp vụ của hệ thống CTXH, bao gồm mã sinh viên 24110078 và các quy tắc xác nhận đăng ký. Hoàn thiện logic đăng ký hoạt động, kiểm tra trạng thái và quy đổi điểm theo chính sách. Bổ sung điều kiện kiểm tra dữ liệu đầu vào, yêu cầu xác nhận trước khi ghi dữ liệu, xử lý các trường hợp đăng ký trùng lặp, dữ liệu không hợp lệ và ngoại lệ; sau đó kiểm thử và tích hợp các tool vào hệ thống.
- **Minh chứng:** Mã nguồn MCP Server, các công cụ CTXH trong `src/mcp/tools.py` và các bài kiểm thử liên quan trong thư mục `tests/`.

#### Thiết kế cấu trúc tài liệu và kho dữ liệu RAG (DocumentStore)

- **Prompt:** “Hãy phác thảo các dataclass bằng Python cho một hệ thống RAG tối giản gồm Document, DocumentChunk và DocumentStore. Thêm các phương thức cơ bản như add_document, add_chunks có kiểm tra trùng lặp doc_id và chunk_id.”
- **AI làm gì:** Đề xuất sử dụng dataclass để biểu diễn cấu trúc tài liệu, phác thảo các thuộc tính `doc_id`, `title`, `content` và `metadata`. AI gợi ý thiết kế các lớp `Document`, `DocumentChunk` và `DocumentStore`, các phương thức `add_document`, `add_chunks` để quản lý tài liệu và các đoạn văn bản, đồng thời đề xuất cơ chế kiểm tra trùng lặp mã định danh tài liệu (`doc_id`) và đoạn văn bản (`chunk_id`). Đoạn code được AI sinh/phác thảo:

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

- **Tôi làm gì:** Điều chỉnh cấu trúc dữ liệu theo yêu cầu của hệ thống RAG. Hoàn thiện cách lưu trữ và quản lý tài liệu cùng các chunks tương ứng, bổ sung điều kiện kiểm tra tính hợp lệ và tính duy nhất của mã định danh. Tích hợp Document Store với quy trình xử lý tài liệu và truy xuất thông tin của hệ thống, đồng thời kiểm tra tính nhất quán của dữ liệu trong quá trình thêm và quản lý tài liệu.
- **Minh chứng:** Các lớp `Document`, `DocumentChunk`, `DocumentStore` trong mã nguồn mô-đun RAG và các bài kiểm thử liên quan.

#### Xây dựng kiểm thử tự động (MCPBusinessTests)

- **Prompt:** “Hãy gợi ý một vài test case mẫu dùng unittest để kiểm tra việc gọi tool register_ctxh_activity với cơ chế mock tempfile cho file JSON database. Chỉ phác thảo hàm setup và test xác nhận.”
- **AI làm gì:** Đề xuất sử dụng thư viện `unittest` để xây dựng bộ kiểm thử tự động, sử dụng `tempfile.TemporaryDirectory()` để tạo thư mục tạm thời phục vụ kiểm thử và `unittest.mock.patch` để thay đổi đường dẫn database trong quá trình kiểm thử. AI phác thảo cấu trúc `setUp()` và `tearDown()` để khởi tạo, giải phóng tài nguyên kiểm thử, đồng thời đề xuất các trường hợp kiểm thử cho xác nhận đăng ký, đăng ký trùng lặp và xử lý ngoại lệ. Đoạn code được AI phác thảo:

```python
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

class MCPBusinessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.patch = patch.object(
            tools, "DB_FILE", Path(self.tmp.name) / "db.json"
        )
        self.patch.start()

    def tearDown(self):
        self.patch.stop()
        self.tmp.cleanup()
```
- **Tôi làm gì:** Hoàn thiện các test case dựa trên logic nghiệp vụ thực tế của hệ thống. Điều chỉnh cách mock database và các thành phần phụ thuộc để phù hợp với cấu trúc mã nguồn. Kiểm tra kết quả trả về của các tool trong từng trường hợp kiểm thử, chạy bộ kiểm thử, phân tích lỗi và sửa các trường hợp chưa đáp ứng yêu cầu. Cuối cùng, đánh giá tính đúng đắn của hệ thống trong các tình huống hợp lệ và không hợp lệ.
- **Minh chứng:** Lớp kiểm thử `MCPBusinessTests` và các bài kiểm thử nghiệp vụ MCP trong thư mục `tests/`.

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
- **Tôi làm gì:** Ở giai đoạn trước, nhóm đối chiếu trường hợp này với DOC0009. Sau khi chuyển corpus, nhóm kiểm tra lại quy tắc trong `CTXH.md`. Phép tính 25 điểm = 2,5 ngày không tự chứng minh điểm của một cá nhân đã được duyệt; đây vẫn là giới hạn cần nói rõ khi trả lời.
- **Minh chứng:** `data/corpus/CTXH.md`, `src/agent/agent.py`, `logs/demo_20261018_210439.jsonl`.

#### Kiểm thử Agent và lưu dấu vết

- **Prompt:** “Dựa trên cấu trúc đồ án, hãy hướng dẫn tôi kiểm thử Unit Tests và MCP tool discovery bằng PowerShell. Giải thích ý nghĩa PASS/FAIL và những lỗi thường gặp. Không tự tạo kết quả kiểm thử giả.”
- **AI làm gì:** Hướng dẫn lệnh chạy và cách đọc kết quả. **Prompt này không sinh test hoặc code Agent.**
- **Tôi làm gì:** Chạy và kiểm tra `tests/test_agent.py` với LLM và pipeline giả lập cho ba trường hợp: gọi công cụ rồi trả lời, gọi công cụ không tồn tại và chạm giới hạn bước. `main.py` in tóm tắt trace; `src/agent/logging_utils.py` ghi `steps`, `trace`, `USAGE` vào JSONL. Tôi chạy `python -m unittest discover -s tests -v`, kết quả 16/16 đạt.
- **Minh chứng:** `tests/test_agent.py`, `src/agent/logging_utils.py`, `main.py`, `logs/demo_*.jsonl`, kết quả `python -m unittest discover -s tests -v`.

**Code AI sinh cho Agent:** Không
## 3. Kiểm chứng và trách nhiệm

Nhóm đã đối chiếu các gợi ý với mã nguồn và tài liệu CTXH, chạy `python -m unittest discover -s tests -v`, `python -m src.mcp.mcp_client` cùng các demo. Kết quả 16/16 unit test đạt là kết quả đã cung cấp từ lần chạy thực tế, không phải AI tự tạo. Những đoạn code trích ở trên thuộc bản project được cung cấp.