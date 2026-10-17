# CTXH – DATA & RAG (Người 1)

Đây là phần RAG của đồ án, không phải Agent/MCP hoàn chỉnh.

## Chuẩn bị
- Python >=3.11; cài `python -m pip install -r requirements.txt`
- Đặt 8 file DOC0001–DOC0008 Markdown từ repo gốc vào `data/corpus/`. Không tự tạo dữ liệu giả để thay thế.
- Để chạy Groq: sao chép `.env.example` thành `.env` và điền khóa API (không commit `.env`).

## Chạy
- `python -m unittest discover -s tests -v`
- `python -m demo_retrieval`
- `python -m demo_groq_rag`

## Bàn giao cho Người 2
- `RAGPipeline.from_corpus('data/corpus')` nạp tài liệu và embedding.
- `pipeline.retrieve(question, mode='dense'|'hybrid', top_k=3)` trả về `list[SearchResult]`.
- `pipeline.ask(question, mode='hybrid')` trả về `RAGAnswer(question, answer, sources)`.
- Nguồn: `source.chunk.doc_id`, `.metadata['version']`, `.section`.

## Giới hạn
- Chunking theo heading ##, chia tiếp theo tối đa 230 từ và overlap 30 từ. Giới hạn từ không tương đương giới hạn token; cần đo tokenizer E5 khi dữ liệu lớn.
- RAG luôn truy xuất top-k, chưa có bộ phân loại no_answer độc lập. Prompt Groq yêu cầu từ chối khi thiếu chứng cứ; cần đánh giá 4 câu no_answer bằng testset và kiểm tra thực tế.
- Mô hình embedding tải lần đầu có thể lâu. Không có kết quả kiểm thử API thật trong gói này.
