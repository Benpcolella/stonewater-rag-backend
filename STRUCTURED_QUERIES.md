# Structured Deal Query API

Clean, filtered access to your deals database with fuzzy search and formatted responses.

## Quick Examples

### Get Cap Rates in Florida (Clean Format)
```bash
curl -H "Authorization: Bearer stonewater_demo_key_123" \
  "http://localhost:5001/api/query/by-state?state=FL&metric=cap_rate&format=text"
```

**Output:**
```
Here are the cap rate we've seen in FL:
  • Marketplace at Altamonte (Altamonte Springs): 5.75%
```

### Search for a Deal (Fuzzy Matching)
```bash
curl -H "Authorization: Bearer stonewater_demo_key_123" \
  "http://localhost:5001/api/search?q=marketplace&format=text"
```

**Output:**
```
**Marketplace at Altamonte**

PROPERTY:
  Location: 130 E Altamonte Dr., Altamonte Springs, FL
  Market: Altamonte Springs
  Units: 383.0
  Rentable SF: N/A

FINANCING:
  Loan Amount: $92.9M
  LTC: 65%
  Interest Rate: N/A

RETURNS:
  Levered IRR: 2.37%
  Equity Multiple: 1.04x
  Exit Cap Rate: 5.75%
  Going-In Cap Rate: 4.35%
```

---

## API Endpoints

### 1. Query by State

Get all deals in a state for a specific metric.

**Endpoint:** `GET /api/query/by-state`

**Parameters:**
- `state` (required): State code (e.g., FL, TX)
- `metric` (required): Metric name or alias (see Metric Aliases below)
- `format` (optional): `json` (default) or `text`

**Examples:**

```bash
# Get cap rates in Florida (text format)
curl -H "Authorization: Bearer stonewater_demo_key_123" \
  "http://localhost:5001/api/query/by-state?state=FL&metric=cap_rate&format=text"

# Get LTC percentages in Texas (JSON format)
curl -H "Authorization: Bearer stonewater_demo_key_123" \
  "http://localhost:5001/api/query/by-state?state=TX&metric=ltc"

# Get IRRs in Florida (JSON)
curl -H "Authorization: Bearer stonewater_demo_key_123" \
  "http://localhost:5001/api/query/by-state?state=FL&metric=irr"
```

**Response (Text):**
```
Here are the cap rate we've seen in FL:
  • Marketplace at Altamonte (Altamonte Springs): 5.75%
```

**Response (JSON):**
```json
{
  "status": "success",
  "query": "FL cap_rate",
  "data": {
    "state": "FL",
    "metric": "project_returns.exit_cap_rate_percent",
    "count": 1,
    "results": [
      {
        "deal": "Marketplace at Altamonte",
        "city": "Altamonte Springs",
        "location": "130 E Altamonte Dr., Altamonte Springs, FL",
        "value": "5.75%"
      }
    ]
  }
}
```

---

### 2. Query by City

Get deals in a specific city for a metric.

**Endpoint:** `GET /api/query/by-city`

**Parameters:**
- `city` (required): City name (fuzzy match supported)
- `state` (optional): State code to narrow down
- `metric` (required): Metric name or alias
- `format` (optional): `json` (default) or `text`

**Examples:**

```bash
# Get cap rates in Dallas
curl -H "Authorization: Bearer stonewater_demo_key_123" \
  "http://localhost:5001/api/query/by-city?city=Dallas&metric=cap_rate&format=text"

# Get LTC in Altamonte Springs, FL
curl -H "Authorization: Bearer stonewater_demo_key_123" \
  "http://localhost:5001/api/query/by-city?city=Altamonte+Springs&state=FL&metric=ltc&format=text"
```

---

### 3. Fuzzy Search for Deals

Search for a deal by name or location with fuzzy matching (handles typos).

**Endpoint:** `GET /api/search`

**Parameters:**
- `q` (required): Search query (deal name or location)
- `format` (optional): `json` (default) or `text`

**Fuzzy Matching:**
- "marketplace" → finds "Marketplace at Altamonte"
- "altamonte" → finds "Altamonte Springs"
- "rivulet" → finds "Rivulet, Phase 1 South"
- "markealplace" → finds "Marketplace at Altamonte" (typo-tolerant)

**Examples:**

```bash
# Search for Marketplace (text format)
curl -H "Authorization: Bearer stonewater_demo_key_123" \
  "http://localhost:5001/api/search?q=marketplace&format=text"

# Search for Rivulet (JSON)
curl -H "Authorization: Bearer stonewater_demo_key_123" \
  "http://localhost:5001/api/search?q=rivulet"

# Search with typo (still works!)
curl -H "Authorization: Bearer stonewater_demo_key_123" \
  "http://localhost:5001/api/search?q=rivulet&format=text"
```

**Response (Text):**
```
**Marketplace at Altamonte**

PROPERTY:
  Location: 130 E Altamonte Dr., Altamonte Springs, FL
  Market: Altamonte Springs
  Units: 383.0
  Rentable SF: N/A

FINANCING:
  Loan Amount: $92.9M
  LTC: 65%
  Interest Rate: N/A

RETURNS:
  Levered IRR: 2.37%
  Equity Multiple: 1.04x
  Exit Cap Rate: 5.75%
  Going-In Cap Rate: 4.35%
```

---

### 4. Compare Metrics

Compare multiple metrics across deals.

**Endpoint:** `GET /api/compare`

**Parameters:**
- `state` (optional): State code to filter deals
- `cities` (optional): City names to filter deals (can be repeated: `?cities=Dallas&cities=Orlando`)
- `metrics` (required): Comma-separated metric names (e.g., `cap_rate,irr,ltc`)
- `format` (optional): `json` (default) or `text`

**Examples:**

```bash
# Compare cap rate, IRR, and LTC across Florida deals
curl -H "Authorization: Bearer stonewater_demo_key_123" \
  "http://localhost:5001/api/compare?state=FL&metrics=cap_rate,irr,ltc&format=text"

# Compare metrics across specific cities
curl -H "Authorization: Bearer stonewater_demo_key_123" \
  "http://localhost:5001/api/compare?cities=Dallas&cities=Altamonte+Springs&metrics=ltc,loan_amount&format=text"

# Compare all deals in Texas
curl -H "Authorization: Bearer stonewater_demo_key_123" \
  "http://localhost:5001/api/compare?state=TX&metrics=units,ltc,irr"
```

---

### 5. Get Deal Metrics

Get specific metrics for a single deal.

**Endpoint:** `GET /api/deal/<deal_name>/metrics`

**Parameters:**
- `metrics` (optional): Comma-separated metric names. If omitted, returns full summary.
- `format` (optional): `json` (default) or `text`

**Examples:**

```bash
# Get all metrics for Rivulet (text format)
curl -H "Authorization: Bearer stonewater_demo_key_123" \
  "http://localhost:5001/api/deal/Rivulet/metrics?format=text"

# Get specific metrics (units, LTC, IRR)
curl -H "Authorization: Bearer stonewater_demo_key_123" \
  "http://localhost:5001/api/deal/Rivulet/metrics?metrics=units,ltc,irr"

# Fuzzy search works here too
curl -H "Authorization: Bearer stonewater_demo_key_123" \
  "http://localhost:5001/api/deal/marketplace/metrics?format=text"
```

---

### 6. Available Metrics

Get list of available metrics and their aliases.

**Endpoint:** `GET /api/metrics/available`

**Examples:**

```bash
curl -H "Authorization: Bearer stonewater_demo_key_123" \
  "http://localhost:5001/api/metrics/available"
```

**Response:**
```json
{
  "status": "success",
  "aliases": {
    "cap_rate": "project_returns.exit_cap_rate_percent",
    "cap_rate_exit": "project_returns.exit_cap_rate_percent",
    "cap_rate_going_in": "project_returns.yield_on_cost_percent",
    "irr": "project_returns.levered_irr_percent",
    "levered_irr": "project_returns.levered_irr_percent",
    "equity_multiple": "project_returns.levered_equity_multiple",
    "ltc": "construction_financing.ltc_percent",
    "interest_rate": "construction_financing.interest_rate_percent",
    "loan_amount": "construction_financing.loan_amount",
    "units": "property_information.total_units",
    "total_units": "property_information.total_units",
    ...
  },
  "metrics": [
    "property_information.project_name",
    "property_information.address",
    "property_information.market",
    ...
  ]
}
```

---

## Metric Aliases

Use these short names instead of full paths:

| Alias | Full Name | Example |
|-------|-----------|---------|
| `cap_rate` | Exit Cap Rate | 5.75% |
| `cap_rate_exit` | Exit Cap Rate | 5.75% |
| `cap_rate_going_in` | Going-In Cap Rate | 4.35% |
| `irr` | Levered IRR | 2.37% |
| `levered_irr` | Levered IRR | 2.37% |
| `equity_multiple` | Equity Multiple | 1.04x |
| `ltc` | Loan-to-Cost % | 65% |
| `interest_rate` | Interest Rate | 7.75% |
| `loan_amount` | Loan Amount | $92.9M |
| `units` | Total Units | 383 |
| `total_units` | Total Units | 383 |
| `rentable_sf` | Rentable SF | 307,250 |
| `gross_sf` | Gross SF | 361,471 |
| `total_cost` | Total Cost | $118.9M |
| `market` | Market | Dallas |
| `address` | Address | Dallas, TX, 75241 |

---

## Response Formats

### JSON Format (Default)
Structured data for programmatic access. Perfect for dashboards, APIs, and integrations.

```bash
curl "http://localhost:5001/api/query/by-state?state=FL&metric=cap_rate"
```

### Text Format (User-Friendly)
Clean, readable format for reports and direct viewing. Supports `&format=text`.

```bash
curl "http://localhost:5001/api/query/by-state?state=FL&metric=cap_rate&format=text"
```

---

## Use Cases

### Market Analysis
```bash
# "What are cap rates across all Florida deals?"
curl -H "Authorization: Bearer stonewater_demo_key_123" \
  "http://localhost:5001/api/query/by-state?state=FL&metric=cap_rate&format=text"
```

### Deal Comparison
```bash
# "Compare Rivulet and Marketplace financing"
curl -H "Authorization: Bearer stonewater_demo_key_123" \
  "http://localhost:5001/api/compare?state=TX&metrics=ltc,loan_amount,irr"
```

### Quick Lookup
```bash
# "Show me everything about Marketplace"
curl -H "Authorization: Bearer stonewater_demo_key_123" \
  "http://localhost:5001/api/search?q=marketplace&format=text"
```

### Investment Criteria
```bash
# "Find all deals with >5% cap rate"
# (Requires post-processing, but API returns all cap rates)
curl -H "Authorization: Bearer stonewater_demo_key_123" \
  "http://localhost:5001/api/query/by-state?state=FL&metric=cap_rate"
```

---

## Frontend Integration Example

```javascript
// Simple JavaScript fetch
async function getFloridaCapRates() {
  const response = await fetch(
    'http://localhost:5001/api/query/by-state?state=FL&metric=cap_rate&format=text',
    {
      headers: {
        'Authorization': 'Bearer stonewater_demo_key_123'
      }
    }
  );

  const text = await response.text();
  document.getElementById('results').innerHTML = `<pre>${text}</pre>`;
}

// With JSON for processing
async function getFloridaCapRatesJSON() {
  const response = await fetch(
    'http://localhost:5001/api/query/by-state?state=FL&metric=cap_rate',
    {
      headers: {
        'Authorization': 'Bearer stonewater_demo_key_123'
      }
    }
  );

  const data = await response.json();
  // Process data.data.results[]
}
```

---

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200 OK` - Successful query
- `400 Bad Request` - Missing required parameters
- `401 Unauthorized` - Invalid API key
- `404 Not Found` - Deal not found (search endpoint)

**Error Response:**
```json
{
  "status": "error",
  "error": "state parameter required"
}
```

---

## Tips

1. **Use metric aliases** - Shorter and easier: `cap_rate` instead of `project_returns.exit_cap_rate_percent`
2. **Format=text for humans** - Easy to read, good for reports
3. **JSON for machines** - Use in dashboards, APIs, integrations
4. **Fuzzy search** - Handles typos and variations (e.g., "marketplace" finds "Marketplace at Altamonte")
5. **Multiple cities** - Use `?cities=Dallas&cities=Orlando` for multiple values
6. **State filtering** - All endpoints support optional state filtering for more specific results

---

## Summary

✅ **Clean formatted responses** - `&format=text` for human-readable output  
✅ **Fuzzy search** - Finds deals even with typos  
✅ **Flexible filtering** - By state, city, or specific deals  
✅ **Metric aliases** - Short names for common metrics  
✅ **JSON or text** - Choose the format that fits your use case  

**The system is ready for frontend integration!**

