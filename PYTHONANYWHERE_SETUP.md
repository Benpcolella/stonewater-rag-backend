# PythonAnywhere Deployment Setup

## Problem
The WSGI app on PythonAnywhere failed to load because `fuzzywuzzy` and `python-Levenshtein` weren't installed in the Python environment used by the web app.

## Solution: Install Dependencies in the Correct Virtualenv

### Step 1: Pull Latest Code
Log into PythonAnywhere SSH console and pull the latest changes:
```bash
ssh Benpcolella@ssh.pythonanywhere.com
cd /home/Benpcolella/stonewater-rag-backend
git pull origin main
```

### Step 2: Create Virtual Environment (If Not Already Done)
```bash
mkvirtualenv --python=/usr/bin/python3.11 stonewater-env
```
(Replace `3.11` with your actual Python version if different)

### Step 3: Activate the Virtual Environment
```bash
source ~/.virtualenvs/stonewater-env/bin/activate
```

### Step 4: Install Requirements
```bash
pip install -r requirements.txt
```

### Step 5: Configure WSGI File
Edit `/var/www/benpcolella_pythonanywhere_com_wsgi.py` and add these lines at the very top:

```python
import sys
path = '/home/Benpcolella/.virtualenvs/stonewater-env/lib/python3.11/site-packages'
if path not in sys.path:
    sys.path.insert(0, path)
```

Replace `python3.11` with your actual Python version from Step 2.

### Step 6: Reload Web App
Go to https://www.pythonanywhere.com/user/Benpcolella/webapps/ and click the **Reload** button next to your web app.

### Step 7: Test the API
Test with curl:
```bash
curl -H "Authorization: Bearer stonewater_demo_key_123" \
  "https://benpcolella.pythonanywhere.com/api/query/by-state?state=FL&metric=cap_rate&format=text"
```

Expected response:
```
Here are the cap rate we've seen in FL:
  • Marketplace at Altamonte (Altamonte Springs): 5.75%
```

## Troubleshooting

### If dependencies still not found:
1. Check Python version on PythonAnywhere:
   ```bash
   python3 --version
   ```

2. List installed packages in your virtualenv:
   ```bash
   source ~/.virtualenvs/stonewater-env/bin/activate
   pip list | grep -i fuzzy
   ```

3. If `fuzzywuzzy` not in list, reinstall:
   ```bash
   pip install --upgrade fuzzywuzzy python-Levenshtein
   ```

### If WSGI still shows errors:
1. Check error logs in PythonAnywhere web dashboard
2. Look at `/var/log/benpcolella_pythonanywhere_com.error.log`
3. Verify the WSGI file path is correct (should be `/var/www/benpcolella_pythonanywhere_com_wsgi.py`)

## Alternative: Using PythonAnywhere Web UI (Simpler)

If SSH is not working, you can set up the virtualenv through PythonAnywhere's web interface:

1. Go to: https://www.pythonanywhere.com/user/Benpcolella/webapps/
2. Click on your web app (`benpcolella.pythonanywhere.com`)
3. Under "Virtualenv", click "Add a new virtual environment"
4. Choose Python 3.11 (or your version)
5. Click "Create"
6. Once created, click on it and use the "Start web console" option
7. Run the same install commands:
   ```bash
   cd /home/Benpcolella/stonewater-rag-backend
   git pull origin main
   pip install -r requirements.txt
   ```

## What Changed

- Updated `requirements.txt` to include:
  - `fuzzywuzzy==0.18.0` (fuzzy string matching)
  - `python-Levenshtein==0.21.1` (performance optimization for fuzzywuzzy)
- These are now part of the dependency list, so any fresh installation will include them

## Live API Endpoints

Once deployment is fixed, access these endpoints:

**Test by State:**
```
https://benpcolella.pythonanywhere.com/api/query/by-state?state=FL&metric=cap_rate&format=text
```

**Fuzzy Search:**
```
https://benpcolella.pythonanywhere.com/api/search?q=marketplace&format=text
```

**Compare Metrics:**
```
https://benpcolella.pythonanywhere.com/api/compare?state=FL&metrics=cap_rate,irr,ltc&format=text
```

See `STRUCTURED_QUERIES.md` for complete API documentation.
