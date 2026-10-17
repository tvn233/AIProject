"""Chạy từ thư mục gốc: python -m main"""
from pathlib import Path
from src.agent.agent import CTXHAgent
from src.agent.llm_client import LLMClient
from src.rag.rag import RAGPipeline


def main() -> None:
    root = Path(__file__).resolve().parent
    print("Đang nạp dữ liệu CTXH và mô hình embedding...")
    pipeline = RAGPipeline.from_corpus(root / "data" / "corpus")
    llm = LLMClient()
    agent = CTXHAgent(llm, pipeline, prompt_path=root / "prompts" / "system_prompt.txt")
    print("Trợ lý CTXH sẵn sàng. Gõ 'exit' để thoát.")
    while True:
        try:
            question = input("\nBạn: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nKết thúc.")
            break
        if question.lower() in ("exit", "quit"):
            break
        if not question:
            continue
        try:
            result = agent.run(question)
            print("\nAI:", result.answer)
            print(f"Steps={result.steps} | Tokens={result.total_tokens}")
            for event in result.trace:
                print("TRACE:", event)
        except Exception as exc:
            print(f"Lỗi: {type(exc).__name__}: {exc}")

if __name__ == "__main__":
    main()
