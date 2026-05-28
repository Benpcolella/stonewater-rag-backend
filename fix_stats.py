with open('rag_api.py', 'r') as f:
    content = f.read()

old_get_stats = '''    def get_stats(self):
        unique_docs = set()
        by_type = defaultdict(int)
        for chunk in self.chunks:
            meta = chunk.get('metadata', {})
            unique_docs.add(meta.get('file_path'))
            doc_type = meta.get('doc_type', 'Unknown')
            by_type[doc_type] += 1
        return {
            'total_chunks': len(self.chunks),
            'unique_documents': len(unique_docs),
            'vocab_size': len(self.vocab),
            'chunks_by_type': dict(by_type)'''

new_get_stats = '''    def get_stats(self):
        unique_docs = set()
        by_type = defaultdict(int)
        for chunk in self.chunks:
            meta = chunk.get('metadata', {})
            file_path = meta.get('file_path')
            if file_path:
                unique_docs.add(file_path)
            doc_type = meta.get('doc_type', 'Unknown')
            by_type[doc_type] += 1
        return {
            'total_chunks': len(self.chunks),
            'unique_documents': len(unique_docs),
            'vocab_size': len(self.vocab),
            'chunks_by_type': dict(by_type)'''

content = content.replace(old_get_stats, new_get_stats)

with open('rag_api.py', 'w') as f:
    f.write(content)

print("Stats endpoint fixed")
