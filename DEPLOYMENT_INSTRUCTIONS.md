# Stonewater RAG - Deployment Status & Instructions

## Current Status (May 27, 2026)

### ✅ Completed
- **Backend Code**: Pushed to GitHub with embedded vector store data (56 chunks from 5 PDFs)
  - Repository: https://github.com/Benpcolella/stonewater-rag-backend
  - Contains: rag_api.py, vector_store_init.py (with base64-encoded data), all required modules
  - API URL: https://Benpcolella.pythonanywhere.com
  - API Key: `stonewater_demo_key_123`

- **Frontend Build**: React app built and deploying to GitHub Pages
  - Repository: https://github.com/Benpcolella/stonewater-rag-ui
  - Frontend URL: https://Benpcolella.github.io/stonewater-rag-ui/
  - Configure with API URL and API Key on login page

### ⏳ Pending - ACTION REQUIRED

#### 1. **Reload PythonAnywhere Web App** (CRITICAL)
The embedded vector store data is pushed to GitHub but the app on PythonAnywhere needs to be reloaded to pick up the changes.

**Steps to reload:**
1. Go to https://www.pythonanywhere.com/user/Benpcolella/webapps/
2. Find "Benpcolella.pythonanywhere.com" web app
3. Click on it
4. Click the green **"Reload"** button in the upper right
5. Wait a few seconds for the reload to complete

**What happens after reload:**
- The app will import `vector_store_init.py` on startup
- It will automatically extract and write `vector_store.json` and `local_metadata.json`
- Your 56 chunks from the 5 synced PDFs will be loaded into memory
- The API will be fully functional

#### 2. **Test the Backend**
After reloading, verify the API is working:

```bash
cd /Users/bencolella/Desktop/stonewater-rag-backend
python3 test_api.py
```

This will test:
- ✓ Health check (verify vector store is loaded)
- ✓ Stats endpoint (verify 56 chunks are indexed)
- ✓ Documents endpoint (verify PDF metadata)
- ✓ Query endpoint (test a sample question)

## Team Access Instructions

Once both the app reload and frontend deployment are complete, share these with your team:

### For Your Team
1. **Frontend URL**: https://Benpcolella.github.io/stonewater-rag-ui/
2. **API URL**: https://Benpcolella.pythonanywhere.com
3. **API Key**: `stonewater_demo_key_123`

### How to Use
1. Open the frontend URL in a browser
2. Click "Connect"
3. Leave API URL as default: `https://Benpcolella.pythonanywhere.com`
4. Enter API Key: `stonewater_demo_key_123`
5. Click "Connect"
6. Click "📊 Sync Documents" button (optional - your PDFs are already synced)
7. Ask questions in the chat box!

## Architecture

```
Your Mac (Local)
├─ PDFs in files/ folder
├─ local_sync.py (run periodically)
└─ Generates: vector_store.json, local_metadata.json

GitHub
├─ stonewater-rag-backend repo
│  └─ Contains embedded vector store data
└─ stonewater-rag-ui repo
   └─ React app on GitHub Pages

PythonAnywhere (Always-on Backend)
├─ Runs Flask API 24/7
├─ Loads vector_store from embedded data
└─ Serves queries with citations

Team Members
└─ Access via GitHub Pages frontend + PythonAnywhere API
```

## Regular Syncing Workflow

To update the vector store with new/modified PDFs:

1. Add or update PDFs in `files/` folder on your Mac
2. Run sync script:
   ```bash
   cd /Users/bencolella/Desktop/stonewater-rag-backend
   python3 ~/Desktop/stonewater-rag-backend/local_sync.py
   ```
3. This generates updated `vector_store.json` and `local_metadata.json`
4. Commit and push to GitHub:
   ```bash
   git add vector_store.json local_metadata.json
   git commit -m "Update vector store with new PDFs"
   git push
   ```
5. Reload the PythonAnywhere app again (same steps as above)

## API Endpoints

All endpoints require Bearer token authentication with the API key.

```
GET /health
  → Check if API is running and vector store is loaded

GET /api/stats
  → Get document statistics and indexing info

GET /api/documents
  → List all tracked PDFs with metadata

POST /api/query
  → Query the vector store with a question
  → Returns: answer + citations to source PDFs

POST /api/sync
  → Scan files/ folder and reindex (only works if files/ folder exists)
```

## Troubleshooting

### "Vector store is empty"
- Reload the PythonAnywhere app
- Check that `vector_store_init.py` was pushed to GitHub
- Run `test_api.py` to verify

### "API returns 401 Unauthorized"
- Check that API Key matches: `stonewater_demo_key_123`
- Verify Authorization header format: `Bearer stonewater_demo_key_123`

### "Frontend won't connect"
- Check that both API URL and API Key are set correctly
- Verify PythonAnywhere app is reloaded and running
- Open browser console (F12) to see error messages

## Next Steps

1. ✅ Reload the PythonAnywhere web app (see "Pending" section above)
2. ✅ Run test_api.py to verify everything works
3. ✅ Share GitHub Pages URL with your team
4. ✅ Set up regular sync routine for new PDFs
