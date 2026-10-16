import tempfile
import unittest
from pathlib import Path
import numpy as np
from src.rag.chunking import MarkdownChunker
from src.rag.models import Document, DocumentStore
from src.rag.retriever import HybridRetriever

class FakeEmbedder:
    def encode(self, texts):
        return np.asarray([[float('đăng' in t.lower()), float('điểm' in t.lower()), 1.0] for t in texts], dtype=np.float32)

class RAGTests(unittest.TestCase):
    def test_frontmatter(self):
        meta, body = MarkdownChunker.parse_yaml_frontmatter('---\ndoc_id: DOC0001\ntitle: Quy định\n---\n## Mục\nNội dung')
        self.assertEqual(meta['doc_id'], 'DOC0001')
        self.assertIn('Nội dung', body)

    def test_chunk_size_and_metadata(self):
        doc = Document('DOC0001','Quy định','## Điểm\n' + ' '.join(['điểm'] * 620), {'version':'1.0'})
        chunks = MarkdownChunker.chunk_document(doc)
        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(len(c.content.split()) <= 230 for c in chunks))
        self.assertTrue(all(c.doc_id == 'DOC0001' for c in chunks))
        store=DocumentStore();store.add_document(doc);store.add_chunks(chunks)
        self.assertEqual(len(store.all_chunks()), len(chunks))

    def test_dense_and_hybrid(self):
        doc=Document('DOC0001','Quy định','## A\nĐiểm CTXH\n## B\nĐăng ký CTXH')
        chunks=MarkdownChunker.chunk_document(doc)
        fake=FakeEmbedder()
        retriever=HybridRetriever(chunks,fake.encode,embed_query=fake.encode)
        for mode in ('dense','hybrid'):
            results=retriever.search('đăng ký',mode=mode,top_k=2)
            self.assertEqual(len(results),2)
            self.assertEqual(results[0].chunk.doc_id,'DOC0001')

if __name__ == '__main__':
    unittest.main()
