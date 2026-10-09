import os
import re
import yaml
from typing import List, Dict, Any
from dataclasses import dataclass, asdict

# [Mục 2.3] Sử dụng @dataclass để định nghĩa cấu trúc dữ liệu Chunk có Type Hint
@dataclass
class TextChunk:
    chunk_id: str
    doc_id: str
    title: str
    section: str
    content: str
    metadata: Dict[str, Any]

class MarkdownChunker:
    """
    [Mục 2.5] Chiến lược Chunking (Giải thích 3-5 dòng):
    1. Cắt văn bản dựa trên các thẻ Tiêu đề Markdown (Header Level 2 - `##`).
    2. Lý do chọn cắt theo Tiêu đề: Các tài liệu quy chế CTXH HCMUTE được tổ chức theo từng điều khoản/mục riêng biệt. 
       Việc cắt theo Tiêu đề giữ trọn vẹn ngữ cảnh của từng quy định/mã hoạt động thay vì cắt cố định theo số lượng từ (token size).
    3. Giữ lại YAML Front Matter metadata (doc_id, title, owner...) để gắn kèm vào từng chunk phục vụ việc trích dẫn nguồn sau này.
    """
    
    def __init__(self, corpus_dir: str):
        self.corpus_dir = corpus_dir

    def parse_yaml_frontmatter(self, file_content: str):
        """Tách YAML Front Matter metadata ở đầu file Markdown."""
        yaml_pattern = r"^---\s*\n(.*?)\n---\s*\n"
        match = re.search(yaml_pattern, file_content, re.DOTALL)
        if match:
            yaml_text = match.group(1)
            metadata = yaml.safe_load(yaml_text)
            content_without_yaml = file_content[match.end():].strip()
            return metadata, content_without_yaml
        return {}, file_content.strip()

    def process_file(self, file_path: str) -> List[TextChunk]:
        """Đọc file .md, tách metadata và cắt thành các chunk theo Header ##."""
        with open(file_path, "r", encoding="utf-8") as f:
            raw_content = f.read()

        metadata, body_content = self.parse_yaml_frontmatter(raw_content)
        doc_id = metadata.get("doc_id", "UNKNOWN")
        doc_title = metadata.get("title", "")

        # Tách nội dung theo tiêu đề ## (Header level 2)
        sections = re.split(r"\n(?=##\s+)", body_content)
        chunks: List[TextChunk] = []

        for idx, sec in enumerate(sections):
            sec = sec.strip()
            if not sec:
                continue

            lines = sec.split("\n")
            if lines[0].startswith("##"):
                section_title = lines[0].replace("##", "").strip()
            else:
                section_title = "Tổng quan"

            chunk_id = f"{doc_id}_CHUNK_{idx+1:02d}"
            
            chunk = TextChunk(
                chunk_id=chunk_id,
                doc_id=doc_id,
                title=doc_title,
                section=section_title,
                content=sec,
                metadata=metadata
            )
            chunks.append(chunk)

        return chunks

    def process_all(self) -> List[TextChunk]:
        """Duyệt qua tất cả 8 file .md trong thư mục data/corpus/."""
        all_chunks = []
        for filename in sorted(os.listdir(self.corpus_dir)):
            if filename.endswith(".md"):
                file_path = os.path.join(self.corpus_dir, filename)
                chunks = self.process_file(file_path)
                all_chunks.extend(chunks)
        return all_chunks

if __name__ == "__main__":
    # Test thử module chunking
    corpus_directory = "data/corpus"
    if os.path.exists(corpus_directory):
        chunker = MarkdownChunker(corpus_directory)
        result_chunks = chunker.process_all()
        print(f" Đã xử lý thành công {len(result_chunks)} chunks từ dữ liệu Corpus.")
        if result_chunks:
            print("--- Mẫu Chunk đầu tiên ---")
            print(result_chunks[0])
    else:
        print(f" Không tìm thấy thư mục: {corpus_directory}")