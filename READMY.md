# Bàn giao Ngày 2 — LLM & Agent

Chép `src/agent/`, `prompts/`, `main.py` và `tests/test_agent.py` vào **thư mục gốc** của dự án Người 1. Giữ nguyên `src/rag/`, `data/corpus/`, `src/mcp/`.

Cài thư viện nếu cần: `python -m pip install groq python-dotenv` (các thư viện RAG đã cài từ ngày 1).

`.env` ở thư mục gốc phải có `GROQ_API_KEY=...` và `GROQ_MODEL=openai/gpt-oss-20b`. Không push `.env`.

Chạy `python -m unittest discover -s tests -v` và `python -m main`.

Ngày 2 chỉ có tool đọc RAG. Ngày 3 tích hợp MCP và tool ghi sau khi có xác nhận của người dùng.
