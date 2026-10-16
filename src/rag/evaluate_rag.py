"""Kiểm tra hai trường hợp: tài liệu có và không có thông tin trả lời."""

from __future__ import annotations

import re

from src.rag.rag import RAGPipeline


ANSWERABLE_QUESTION = "Sinh viên cần tối thiểu bao nhiêu điểm CTXH để xét tốt nghiệp?"
UNANSWERABLE_QUESTION = "Điểm CTXH cá nhân hiện tại của tôi là bao nhiêu?"

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
    passed = True

    print("=== CÂU HỎI CÓ ĐÁP ÁN ===")
    known = pipeline.ask(ANSWERABLE_QUESTION, top_k=5)

    doc1_rank = next(
        (
            index
            for index, source in enumerate(known.sources, start=1)
            if source.chunk.doc_id == "DOC0001"
        ),
        None,
    )
    has_expected_source = doc1_rank is not None
    has_answer_40 = bool(
        re.search(r"\b40\b|bốn mươi", known.answer, re.IGNORECASE)
    )
    cites_expected_source = bool(
        doc1_rank and f"[S{doc1_rank}]" in known.answer
    )

    print("Câu hỏi:", known.question)
    print("Nguồn:", known.source_doc_ids)
    print("Trả lời:", known.answer)
    print("Tìm thấy DOC0001:", has_expected_source)
    print("Có đáp án 40:", has_answer_40)
    print("Có trích dẫn DOC0001:", cites_expected_source)

    passed &= (
        has_expected_source
        and has_answer_40
        and cites_expected_source
    )

    print("\n=== CÂU HỎI KHÔNG CÓ ĐÁP ÁN TRONG TÀI LIỆU ===")
    unknown = pipeline.ask(UNANSWERABLE_QUESTION, top_k=5)

    abstained = any(
        marker in unknown.answer.casefold()
        for marker in ABSTENTION_MARKERS
    )

    print("Câu hỏi:", unknown.question)
    print("Nguồn:", unknown.source_doc_ids)
    print("Trả lời:", unknown.answer)
    print("Từ chối suy đoán:", abstained)

    passed &= abstained

    print("\nKẾT QUẢ:", "ĐẠT" if passed else "CHƯA ĐẠT")
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
