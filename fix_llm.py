import re

with open('rag_api.py', 'r') as f:
    content = f.read()

# Find and replace the generate_answer function
old_func = '''def generate_answer(question, search_results):
    if not search_results:
        return {
            'answer': 'I could not find relevant documents to answer your question. Please try another query.',
            'citations': [],
            'error': 'No matching documents found'
        }
    
    answer = f"Based on the documents, here is information relevant to your query: "
    answer += " ".join([r.get('text', '')[:100] for r in search_results[:2]])
    
    citations = []
    seen = set()
    for result in search_results:
        meta = result.get('metadata', {})
        file_path = meta.get('file_path')
        if file_path not in seen:
            citations.append(meta)
            seen.add(file_path)
    
    return {'''

new_func = '''def generate_answer(question, search_results):
    if not search_results:
        return {
            'answer': 'I could not find relevant documents to answer your question. Please try another query.',
            'citations': [],
            'error': 'No matching documents found'
        }
    
    context = "\n\n".join([r.get('text', '') for r in search_results[:5]])
    
    llm_provider = os.getenv('LLM_PROVIDER', 'deepseek')
    try:
        if llm_provider == 'deepseek':
            import urllib.request
            import json
            api_key = os.getenv('DEEPSEEK_API_KEY')
            if not api_key:
                return {'answer': 'LLM API key not configured', 'citations': [], 'error': 'Missing DEEPSEEK_API_KEY'}
            
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant for document-based Q&A. Answer questions based on provided documents. Be concise and cite sources."},
                    {"role": "user", "content": f"Based on these documents:\n\n{context}\n\nAnswer this question: {question}"}
                ],
                "temperature": 0.7,
                "max_tokens": 500
            }
            
            req = urllib.request.Request('https://api.deepseek.com/chat/completions',
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {api_key}'},
                method='POST')
            
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                answer = result.get('choices', [{}])[0].get('message', {}).get('content', 'No response from LLM')
        else:
            answer = f"Based on the documents: {context[:300]}..."
    except Exception as e:
        answer = f"Error generating answer: {str(e)}"
    
    citations = []
    seen = set()
    for result in search_results:
        meta = result.get('metadata', {})
        file_path = meta.get('file_path')
        if file_path not in seen:
            citations.append(meta)
            seen.add(file_path)
    
    return {'''

if old_func in content:
    content = content.replace(old_func, new_func)
    with open('rag_api.py', 'w') as f:
        f.write(content)
    print("LLM integration added")
else:
    print("Could not find function to replace")
