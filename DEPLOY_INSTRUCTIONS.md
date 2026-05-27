# SWAI Backend Deployment to PythonAnywhere

## What Changed
- ✅ Added CRE (Commercial Real Estate) domain knowledge to LLM
- ✅ Enhanced system prompt with financial terminology definitions
- ✅ Improved response structure for deal metrics
- ✅ Lowered LLM temperature from 0.5 → 0.3 (more focused responses)
- ✅ Increased max_tokens from 1000 → 1200 (allow structured lists)
- ✅ Better cleanup function that preserves financial numbers

## Deployment Steps

### Option 1: Via PythonAnywhere Web Console (Easiest)

1. Log into PythonAnywhere.com
2. Go to **Consoles** → **$ Bash**
3. Run these commands:
   ```bash
   cd /home/Benpcolella/stonewater-rag-backend
   git pull origin main
   echo "✓ Backend updated with CRE training"
   ```

4. Go to **Web** tab → Click **Reload** on your app (https://Benpcolella.pythonanywhere.com)
5. Test at https://Benpcolella.pythonanywhere.com/health (should show updated backend)

### Option 2: Via Command Line (Local)

```bash
cd /Users/bencolella/Desktop/stonewater-rag-backend

# Verify changes locally
python3 -c "
import re
content = open('rag_api.py').read()
if 'SOFR' in content and 'CRE_CONTEXT' in content:
    print('✓ Local file has CRE training')
else:
    print('✗ File missing CRE context')
"

# Push to PythonAnywhere (optional, if you have SSH set up)
# scp rag_api.py Benpcolella@ssh.pythonanywhere.com:/home/Benpcolella/stonewater-rag-backend/
```

## What to Test After Deployment

### Test 1: CRE Terminology
Ask: "What are the construction financing rates?"
Expected: Should see SOFR + spreads and all-in rates from deals

### Test 2: Deal Metrics
Ask: "Tell me about the Rivulet project financing"
Expected: Should show LTC %, loan amount, term, amortization

### Test 3: Market Analysis
Ask: "What are the market absorption rates?"
Expected: Should list specific deals with metrics

## Rollback (if needed)

If something breaks, revert to previous version:
```bash
cd /home/Benpcolella/stonewater-rag-backend
git revert HEAD --no-edit
git push origin main
# Then reload app on PythonAnywhere
```

## Key Improvements in This Release

### Before:
- Verbose, formatted responses with unnecessary markdown
- Generic summaries without specific metrics
- Missing CRE domain knowledge (didn't understand SOFR, LTC, spreads)

### After:
- Concise, structured responses with bullet points
- Specific deal metrics (rates, costs, terms)
- Full CRE domain training embedded in LLM prompt
- Financial numbers preserved (no rounding)
- Optimized for commercial real estate queries

## CRE Terminology Now Understood by LLM:
- SOFR (Secured Overnight Financing Rate)
- LTC (Loan-to-Cost), LTV (Loan-to-Value)
- CoC (Cash-on-Cash return), IRR (Internal Rate of Return)
- Cap Rates, Yields, Spreads (basis points)
- Project metrics: $/Unit, $/SF, unit count, density
- Deal structure: facilities, tranches, amortization, terms
- Market metrics: absorption rates, comparable deals

---

Questions? Check `/tmp/cre_context.txt` for full terminology reference.
