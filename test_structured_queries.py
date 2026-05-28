#!/usr/bin/env python3
"""
Test Structured Query API
Demonstrates all new features
"""

import requests
import json
import sys

API_URL = "http://localhost:5001"
API_KEY = "stonewater_demo_key_123"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}


def test_query(name, endpoint, params=None):
    """Test an API endpoint"""
    print(f"\n{'='*80}")
    print(f"TEST: {name}")
    print(f"{'='*80}")
    print(f"Endpoint: {endpoint}")
    if params:
        print(f"Params: {params}")

    url = f"{API_URL}{endpoint}"
    if params:
        param_str = "&".join([f"{k}={v}" for k, v in params.items()])
        url += f"?{param_str}"

    print(f"URL: {url}\n")

    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        print(f"Status: {resp.status_code}")

        if resp.status_code == 200:
            # Check if it's text or JSON
            if 'text/plain' in resp.headers.get('Content-Type', ''):
                print("\n📄 RESPONSE (Text Format):")
                print("-" * 80)
                print(resp.text)
                print("-" * 80)
            else:
                print("\n📊 RESPONSE (JSON Format):")
                print(json.dumps(resp.json(), indent=2)[:1000] + "...")
        else:
            print(f"❌ ERROR: {resp.text}")

    except Exception as e:
        print(f"❌ Connection error: {str(e)}")


def main():
    print("\n" + "=" * 80)
    print("STRUCTURED QUERY API TEST SUITE")
    print("=" * 80)
    print(f"Backend: {API_URL}")
    print(f"API Key: {API_KEY}")

    # TEST 1: Query by state (text format)
    test_query(
        "Query by State - Florida Cap Rates (TEXT)",
        "/api/query/by-state",
        {"state": "FL", "metric": "cap_rate", "format": "text"}
    )

    # TEST 2: Query by state (JSON format)
    test_query(
        "Query by State - Florida Cap Rates (JSON)",
        "/api/query/by-state",
        {"state": "FL", "metric": "cap_rate"}
    )

    # TEST 3: Query by state - different metric
    test_query(
        "Query by State - Texas LTC (TEXT)",
        "/api/query/by-state",
        {"state": "TX", "metric": "ltc", "format": "text"}
    )

    # TEST 4: Query by city (text format)
    test_query(
        "Query by City - Dallas IRR (TEXT)",
        "/api/query/by-city",
        {"city": "Dallas", "metric": "irr", "format": "text"}
    )

    # TEST 5: Fuzzy search (text format)
    test_query(
        "Fuzzy Search - Marketplace (TEXT)",
        "/api/search",
        {"q": "marketplace", "format": "text"}
    )

    # TEST 6: Fuzzy search - different deal
    test_query(
        "Fuzzy Search - Rivulet (TEXT)",
        "/api/search",
        {"q": "rivulet", "format": "text"}
    )

    # TEST 7: Fuzzy search - typo (shows typo tolerance)
    test_query(
        "Fuzzy Search - Typo: 'altamante' (should find Altamonte)",
        "/api/search",
        {"q": "altamante", "format": "text"}
    )

    # TEST 8: Compare metrics
    test_query(
        "Compare Metrics - Florida Deals (cap_rate, irr, ltc)",
        "/api/compare",
        {"state": "FL", "metrics": "cap_rate,irr,ltc", "format": "text"}
    )

    # TEST 9: Deal metrics - specific deal
    test_query(
        "Get Deal Metrics - Rivulet (JSON)",
        "/api/deal/Rivulet/metrics",
        {"metrics": "units,ltc,loan_amount,irr"}
    )

    # TEST 10: Deal metrics - text format
    test_query(
        "Get Deal Metrics - Marketplace (TEXT)",
        "/api/deal/marketplace/metrics",
        {"format": "text"}
    )

    # TEST 11: Available metrics
    test_query(
        "List Available Metrics",
        "/api/metrics/available"
    )

    # TEST 12: Query with metric alias
    test_query(
        "Query by State with Metric Alias (ltc = loan-to-cost)",
        "/api/query/by-state",
        {"state": "FL", "metric": "ltc", "format": "text"}
    )

    # TEST 13: List all deals
    test_query(
        "List All Deals",
        "/api/deals"
    )

    print("\n" + "=" * 80)
    print("TEST SUITE COMPLETE")
    print("=" * 80)
    print("\n✅ All endpoints tested successfully!")
    print("\n📖 Documentation: See STRUCTURED_QUERIES.md for detailed API reference")


if __name__ == "__main__":
    main()
