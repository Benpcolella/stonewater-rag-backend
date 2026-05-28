#!/bin/bash

echo "=========================================="
echo "SWAI Hybrid Architecture Deployment Script"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "rag_api.py" ]; then
    echo "❌ Error: Must be run from backend directory"
    echo "   cd /Users/bencolella/Desktop/stonewater-rag-backend"
    exit 1
fi

echo "✅ Working directory: $(pwd)"
echo ""

# Step 1: Verify files exist
echo "Step 1: Verifying files..."
echo "─────────────────────────"

files=("rag_api.py" "deals_database_comprehensive.json" "test_hybrid_routing.py" "HYBRID_INTEGRATION.md")

missing=0
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (MISSING)"
        missing=$((missing + 1))
    fi
done

if [ $missing -gt 0 ]; then
    echo ""
    echo "❌ $missing file(s) missing. Cannot proceed."
    exit 1
fi

echo ""

# Step 2: Python syntax check
echo "Step 2: Syntax verification..."
echo "─────────────────────────────"

if python3 -m py_compile rag_api.py 2>/dev/null; then
    echo "  ✅ rag_api.py syntax valid"
else
    echo "  ❌ rag_api.py has syntax errors"
    exit 1
fi

if python3 -c "import json; json.load(open('deals_database_comprehensive.json'))" 2>/dev/null; then
    echo "  ✅ deals_database_comprehensive.json valid JSON"
else
    echo "  ❌ deals_database_comprehensive.json invalid"
    exit 1
fi

echo ""

# Step 3: Git status
echo "Step 3: Git status..."
echo "────────────────────"

if ! git status > /dev/null 2>&1; then
    echo "  ⚠ Not a git repository"
    echo ""
else
    echo "  Modified files:"
    git status --short | grep " M " || echo "    (none)"
    echo ""
    echo "  Untracked files:"
    git status --short | grep "^??" || echo "    (none)"
    echo ""
    
    # Ask for commit
    read -p "Ready to commit changes? (y/n) " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add -A
        
        read -p "Enter commit message: " commit_msg
        if [ -z "$commit_msg" ]; then
            commit_msg="Add hybrid deals DB + RAG routing"
        fi
        
        git commit -m "$commit_msg"
        
        read -p "Push to origin/main? (y/n) " -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git push origin main
            echo "✅ Changes pushed to GitHub"
        else
            echo "⚠ Changes committed but not pushed"
        fi
    else
        echo "⚠ Skipping git operations"
    fi
fi

echo ""

# Step 4: Test instructions
echo "Step 4: Testing..."
echo "─────────────────"
echo ""
echo "To test the hybrid routing locally:"
echo ""
echo "  Terminal 1 (Start Backend):"
echo "    cd $(pwd)"
echo "    python3 rag_api.py"
echo ""
echo "  Terminal 2 (Run Tests):"
echo "    cd $(pwd)"
echo "    python3 test_hybrid_routing.py"
echo ""

# Step 5: PythonAnywhere instructions
echo "Step 5: PythonAnywhere Deployment"
echo "────────────────────────────────"
echo ""
echo "When ready to deploy to PythonAnywhere:"
echo ""
echo "  1. SSH to server:"
echo "     ssh Benpcolella@ssh.pythonanywhere.com"
echo ""
echo "  2. Pull changes:"
echo "     cd /home/Benpcolella/stonewater-rag-backend"
echo "     git pull origin main"
echo ""
echo "  3. Verify database:"
echo "     ls -la deals_database_comprehensive.json"
echo ""
echo "  4. Reload app:"
echo "     Use PythonAnywhere web dashboard"
echo ""
echo "  5. Test live:"
echo "     curl -H 'Authorization: Bearer stonewater_demo_key_123' \\"
echo "          https://your-domain/api/deals"
echo ""

echo "=========================================="
echo "✅ Deployment script complete"
echo "=========================================="

