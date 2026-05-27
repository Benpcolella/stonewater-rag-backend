import pdfplumber
from typing import List, Dict

class PDFProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def extract_text_with_pages(self, pdf_path: str) -> List[Dict]:
        pages = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        pages.append({
                            'text': text,
                            'page_number': page_num
                        })
        except Exception as e:
            print(f"Error processing {pdf_path}: {e}")
            return []
        return pages

    def _split_into_tokens(self, text: str) -> List[str]:
        return text.split()

    def _tokens_to_text(self, tokens: List[str]) -> str:
        return ' '.join(tokens)

    def create_chunks(self, pages: List[Dict], file_metadata: Dict) -> List[Dict]:
        chunks = []
        combined_text = ""
        current_page = None
        for page in pages:
            if combined_text and current_page != page['page_number']:
                pass
            current_page = page['page_number']
            combined_text += " " + page['text']
        tokens = self._split_into_tokens(combined_text)
        if not tokens:
            return []
        stride = self.chunk_size - self.chunk_overlap
        for i in range(0, len(tokens), stride):
            chunk_tokens = tokens[i : i + self.chunk_size]
            if not chunk_tokens:
                break
            chunk_text = self._tokens_to_text(chunk_tokens)
            token_start = i
            token_end = min(i + self.chunk_size, len(tokens))
            token_ratio_start = token_start / len(tokens) if len(tokens) > 0 else 0
            token_ratio_end = token_end / len(tokens) if len(tokens) > 0 else 0
            page_start = 1
            page_end = len(pages)
            if pages:
                page_start = max(1, int(token_ratio_start * len(pages)) + 1)
                page_end = min(len(pages), int(token_ratio_end * len(pages)) + 1)
            chunk = {
                'text': chunk_text,
                'metadata': {
                    'file_name': file_metadata.get('file_name'),
                    'doc_type': file_metadata.get('doc_type'),
                    'client_project': file_metadata.get('client_project'),
                    'page_start': page_start,
                    'page_end': page_end,
                    'file_path': file_metadata.get('file_path')
                }
            }
            chunks.append(chunk)
        return chunks

    def process_pdf(self, pdf_path: str, file_metadata: Dict) -> List[Dict]:
        pages = self.extract_text_with_pages(pdf_path)
        if not pages:
            return []
        chunks = self.create_chunks(pages, file_metadata)
        return chunks
