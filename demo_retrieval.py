"""Chạy truy xuất dense và hybrid từ thư mục gốc dự án."""

from src.rag.chunking import MarkdownChunker
from src.rag.embeddings import MultilingualE5Embedder
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

    for mode in ("dense", "hybrid"):
        print(f"\n=== {mode.upper()} ===")
        for result in retriever.search(query, mode=mode, top_k=3):
            version = result.chunk.metadata.get("version", "chưa rõ")
            print(
                f"{result.chunk.doc_id} v{version} | {result.chunk.section} "
                f"| điểm={result.score:.4f} "
                f"(dense={result.dense_score:.4f}, BM25={result.bm25_score:.4f})"
            )
            print(result.chunk.content[:450].replace("\n", " "))


if __name__ == "__main__":
    main()
