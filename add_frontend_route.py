import sys

# Read the current rag_api.py
with open('rag_api.py', 'r') as f:
    content = f.read()

# Read the frontend HTML
with open('/tmp/frontend.html', 'r') as f:
    html_content = f.read()

# Escape the HTML content for Python
html_escaped = html_content.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')

# Find where to insert the HTML (after imports, before @app.route definitions)
# Look for the line with @app.route('/health'
insert_pos = content.find("@app.route('/health'")

if insert_pos == -1:
    print("Could not find insertion point")
    sys.exit(1)

# Create the new route code
frontend_route = '''# Serve frontend HTML
_FRONTEND_HTML = """''' + html_content.replace('"""', '""" + \'"""\'  + """') + '''"""

@app.route('/', methods=['GET'])
@app.route('/index.html', methods=['GET'])
def serve_frontend():
    """Serve the frontend HTML"""
    return _FRONTEND_HTML, 200, {'Content-Type': 'text/html'}

'''

# Insert the route before the health check
new_content = content[:insert_pos] + frontend_route + content[insert_pos:]

# Write back
with open('rag_api.py', 'w') as f:
    f.write(new_content)

print("Frontend route added successfully")
