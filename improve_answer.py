with open('rag_api.py', 'r') as f:
    lines = f.readlines()

# Find the generate_answer function and replace the user message part
new_lines = []
i = 0
while i < len(lines):
    if 'user_msg = f"Based on these documents' in lines[i]:
        # Replace this line with improved version
        new_lines.append('            user_msg = f"Question: {question}\\n\\nBased on these documents, provide a comprehensive, specific answer. Include numbers, dates, and deal details. Exclude irrelevant boilerplate.\\n\\nDocuments:\\n{context}"\n')
        i += 1
    elif 'temperature": 0.7' in lines[i]:
        # Lower temperature for more consistent answers
        new_lines.append('                "temperature": 0.5,\n')
        i += 1
    elif '"max_tokens": 500' in lines[i]:
        # Increase token limit for comprehensive answers
        new_lines.append('                "max_tokens": 1000\n')
        i += 1
    elif 'context = ' in lines[i] and "join" in lines[i]:
        # Improved context joining
        new_lines.append('    context = "\\n---\\n".join([r.get("text", "")[:800] for r in search_results[:10]])\n')
        i += 1
    else:
        new_lines.append(lines[i])
        i += 1

# Also change the search top_k
for i in range(len(new_lines)):
    if 'top_k=5' in new_lines[i]:
        new_lines[i] = new_lines[i].replace('top_k=5', 'top_k=10')

with open('rag_api.py', 'w') as f:
    f.writelines(new_lines)

print("✓ Improved generate_answer function")
