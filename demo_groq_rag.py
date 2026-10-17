"""Chạy hỏi đáp CTXH với RAG."""

from src.rag.rag import RAGPipeline


def main() -> None:
    pipeline = RAGPipeline.from_corpus("data/corpus")

    question = input("Nhập câu hỏi CTXH: ").strip()
    if not question:
        raise SystemExit("Câu hỏi không được để trống.")

    result = pipeline.ask(question, mode="hybrid", top_k=3)

    print("\n=== NGUỒN ĐƯỢC TRUY XUẤT ===")
    for index, source in enumerate(result.sources, start=1):
        chunk = source.chunk
        version = chunk.metadata.get("version", "?")
        print(
            f"[S{index}] {chunk.doc_id} v{version} "
            f"| {chunk.section} | điểm={source.score:.4f}"
        )

    print("\n=== CÂU TRẢ LỜI ===")
    print(result.answer)


if __name__ == "__main__":
    main()
