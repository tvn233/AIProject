"""Kiểm tra câu có đáp án và câu không có dữ liệu trong CTXH.md."""

from __future__ import annotations

import re

from src.rag.rag import RAGPipeline


ANSWERABLE_QUESTION = (
    "Theo quy tắc làm tròn trong tài liệu, "
    "25 điểm CTXH đã tích lũy tương đương bao nhiêu ngày?"
)
UNANSWERABLE_QUESTION = (
    "Hiện tại cá nhân tôi đã tích lũy được bao nhiêu ngày CTXH?"
)

ABSTENTION_MARKERS = (
    "không cung cấp",
    "chưa cung cấp",
    "không có thông tin",
    "không có dữ liệu",
    "không thể xác định",
    "không thể biết",
)


def main() -> None:
    pipeline = RAGPipeline.from_corpus("data/corpus")

    print("=== CÂU HỎI CÓ ĐÁP ÁN ===")
    known = pipeline.ask(ANSWERABLE_QUESTION, top_k=5)

    relevant_ranks = [
        index
        for index, source in enumerate(known.sources, start=1)
        if source.chunk.doc_id == "CTXH001"
        and (
            "chia cho 10" in source.chunk.content.casefold()
            or "tròn 5 điểm" in source.chunk.content.casefold()
        )
    ]
    has_answer = bool(
        re.search(r"(?<!\d)2[,.]5(?!\d)|hai\s+ngày\s+rưỡi", known.answer.casefold())
    )
    cites_relevant_source = any(
        f"[S{index}]" in known.answer for index in relevant_ranks
    )

    print("Câu hỏi:", known.question)
    print("Nguồn:", known.source_doc_ids)
    print("Trả lời:", known.answer)
    print("Có đoạn chứa quy tắc quy đổi:", bool(relevant_ranks))
    print("Có đáp án 2,5 ngày:", has_answer)
    print("Có trích dẫn đoạn liên quan:", cites_relevant_source)

    print("\n=== CÂU HỎI KHÔNG CÓ DỮ LIỆU CÁ NHÂN ===")
    unknown = pipeline.ask(UNANSWERABLE_QUESTION, top_k=5)
    abstained = any(
        marker in unknown.answer.casefold()
        for marker in ABSTENTION_MARKERS
    )

    print("Câu hỏi:", unknown.question)
    print("Trả lời:", unknown.answer)
    print("Từ chối suy đoán:", abstained)

    passed = bool(relevant_ranks) and has_answer and cites_relevant_source and abstained
    print("\nKẾT QUẢ:", "PASS" if passed else "FAIL")
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()