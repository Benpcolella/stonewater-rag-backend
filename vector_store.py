import json
import os
import math
from typing import List, Dict, Tuple
from collections import defaultdict

class VectorStore:
    def __init__(self, store_file: str = "vector_store.json"):
        self.store_file = store_file
        self.chunks = []
        self.vocab = {}
        self.idf = {}
        self.load()

    def load(self):
        if os.path.exists(self.store_file):
            try:
                with open(self.store_file, 'r') as f:
                    data = json.load(f)
                    self.chunks = data.get('chunks', [])
                    self.vocab = {k: int(v) for k, v in data.get('vocab', {}).items()}
                    self.idf = data.get('idf', {})
                    if self.chunks:
                        self._rebuild_idf()
            except Exception as e:
                print(f"Error loading vector store: {e}")
                self.chunks = []

    def save(self):
        with open(self.store_file, 'w') as f:
            json.dump({'chunks': self.chunks, 'vocab': self.vocab, 'idf': self.idf}, f, indent=2)

    def _tokenize(self, text: str) -> List[str]:
        import re
        tokens = re.findall(r'\b\w+\b', text.lower())
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been', 'it', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'we', 'they', 'what', 'which', 'who', 'when', 'where', 'why', 'how'}
        return [t for t in tokens if t not in stop_words and len(t) > 2]

    def _build_vocab(self):
        self.vocab = {}
        word_idx = 0
        for chunk in self.chunks:
            tokens = self._tokenize(chunk['text'])
            for token in tokens:
                if token not in self.vocab:
                    self.vocab[token] = word_idx
                    word_idx += 1

    def _rebuild_idf(self):
        if not self.chunks:
            self.idf = {}
            return
        self._build_vocab()
        doc_freq = defaultdict(int)
        for chunk in self.chunks:
            tokens = set(self._tokenize(chunk['text']))
            for token in tokens:
                doc_freq[token] += 1
        num_docs = len(self.chunks)
        self.idf = {}
        for word, freq in doc_freq.items():
            self.idf[word] = math.log(num_docs / (1 + freq))

    def _get_tf_vector(self, text: str) -> Dict[int, float]:
        tokens = self._tokenize(text)
        tf_dict = defaultdict(int)
        for token in tokens:
            if token in self.vocab:
                tf_dict[self.vocab[token]] += 1
        if tokens:
            for word_idx in tf_dict:
                tf_dict[word_idx] /= len(tokens)
        return dict(tf_dict)

    def _cosine_similarity(self, vec1: Dict[int, float], vec2: Dict[int, float]) -> float:
        dot_product = 0
        for idx in vec1:
            if idx in vec2:
                dot_product += vec1[idx] * vec2[idx]
        if dot_product == 0:
            return 0
        mag1 = math.sqrt(sum(v ** 2 for v in vec1.values()))
        mag2 = math.sqrt(sum(v ** 2 for v in vec2.values()))
        if mag1 == 0 or mag2 == 0:
            return 0
        return dot_product / (mag1 * mag2)

    def add_chunks(self, chunks: List[Dict]):
        self.chunks.extend(chunks)
        self._rebuild_idf()
        self.save()

    def clear(self):
        self.chunks = []
        self.vocab = {}
        self.idf = {}
        self.save()

    def search(self, query: str, top_k: int = 5) -> List[Tuple[Dict, float]]:
        if not self.chunks or not self.vocab:
            return []
        try:
            query_vector = self._get_tf_vector(query)
            query_tfidf = {}
            for word_idx, tf in query_vector.items():
                word = next((w for w, idx in self.vocab.items() if idx == word_idx), None)
                if word and word in self.idf:
                    query_tfidf[word_idx] = tf * self.idf[word]
                else:
                    query_tfidf[word_idx] = tf
            results = []
            for chunk in self.chunks:
                chunk_vector = self._get_tf_vector(chunk['text'])
                chunk_tfidf = {}
                for word_idx, tf in chunk_vector.items():
                    word = next((w for w, idx in self.vocab.items() if idx == word_idx), None)
                    if word and word in self.idf:
                        chunk_tfidf[word_idx] = tf * self.idf[word]
                    else:
                        chunk_tfidf[word_idx] = tf
                similarity = self._cosine_similarity(query_tfidf, chunk_tfidf)
                if similarity > 0:
                    results.append((chunk, similarity))
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:top_k]
        except Exception as e:
            print(f"Error searching: {e}")
            return []

    def get_stats(self) -> Dict:
        doc_types = {}
        for chunk in self.chunks:
            doc_type = chunk.get('metadata', {}).get('doc_type', 'Unknown')
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
        return {
            'total_chunks': len(self.chunks),
            'chunks_by_type': doc_types,
            'unique_documents': len(set(c.get('metadata', {}).get('file_name') for c in self.chunks)),
            'vocab_size': len(self.vocab)
        }
