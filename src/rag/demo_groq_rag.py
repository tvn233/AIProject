"""End-to-end demo: hybrid retrieval followed by grounded Groq generation."""

from src.rag.chunking import MarkdownChunker
from src.rag.embeddings import MultilingualE5Embedder
from src.rag.generator import answer_with_groq
from src.rag.retriever import HybridRetriever


def main() -> None:
    chunks = MarkdownChunker("data/corpus").process_all()
    embedder = MultilingualE5Embedder()
    retriever = HybridRetriever(
        chunks,
        embedder.embed_documents,
        embed_query=embedder.embed_queries,
    )

    query = input("Nhập câu hỏi CTXH: ").strip()
    if not query:
        raise SystemExit("Câu hỏi không được để trống.")

    results = retriever.search(query, mode="hybrid", top_k=3)
    print("\n=== NGUỒN ĐƯỢC TRUY XUẤT ===")
    for index, result in enumerate(results, start=1):
        chunk = result.chunk
        print(
            f"[S{index}] {chunk.doc_id} v{chunk.metadata.get('version', '?')} "
            f"| {chunk.section} | score={result.score:.4f}"
        )

    print("\n=== CÂU TRẢ LỜI ===")
    print(answer_with_groq(query, results))


if __name__ == "__main__":
    main()
