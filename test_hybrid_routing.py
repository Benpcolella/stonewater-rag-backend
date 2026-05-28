#!/usr/bin/env python3
"""
Test hybrid deals DB + RAG routing
"""

import requests
import json
import sys

# Configure
API_URL = "http://localhost:5000"
API_KEY = "stonewater_demo_key_123"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

def test_endpoint(name, method, endpoint, data=None):
    """Test an API endpoint."""
    print(f"\n{'='*80}")
    print(f"TEST: {name}")
    print(f"{'='*80}")
    print(f"Endpoint: {method} {endpoint}")

    url = f"{API_URL}{endpoint}"

    try:
        if method == "GET":
            resp = requests.get(url, headers=HEADERS)
        else:  # POST
            print(f"Payload: {json.dumps(data, indent=2)}")
            resp = requests.post(url, headers=HEADERS, json=data)

        print(f"Status: {resp.status_code}")

        if resp.status_code == 200:
            result = resp.json()
            print(f"✓ SUCCESS")

            # Pretty print response
            if 'answer' in result:
                print(f"\nAnswer:\n{result['answer'][:500]}..." if len(result['answer']) > 500 else f"\nAnswer:\n{result['answer']}")

            if 'route' in result:
                print(f"\nRoute: {result['route']}")

            if 'deal' in result and result['deal']:
                print(f"Deal: {result['deal']}")

            if 'count' in result:
                print(f"\nDeals found: {result['count']}")
                if result.get('deals'):
                    for deal in result['deals'][:3]:  # Show first 3
                        print(f"  - {deal['name']} (Market: {deal['market']}, Units: {deal['units']}, Date: {deal['underwriting_date']})")

            return True
        else:
            print(f"✗ ERROR: {resp.text}")
            return False

    except Exception as e:
        print(f"✗ Connection error: {str(e)}")
        print("\n⚠ Backend might not be running. Start it with:")
        print("  cd /Users/bencolella/Desktop/stonewater-rag-backend")
        print("  python3 rag_api.py")
        return False

def main():
    print("\n" + "="*80)
    print("SWAI HYBRID ROUTING TEST SUITE")
    print("="*80)
    print(f"Backend URL: {API_URL}")
    print(f"API Key: {API_KEY}")

    tests = [
        # Test 1: List all deals
        ("List All Deals", "GET", "/api/deals", None),

        # Test 2: Get specific deal
        ("Get Rivulet Deal (Direct)", "GET", "/api/deal/Rivulet, Phase 1 South", None),

        # Test 3: Deal-specific query (should route to deals_db)
        ("Query: Rivulet Capital Stack (Deal-Specific)", "POST", "/api/query",
         {"question": "What is the Rivulet capital stack?"}),

        # Test 4: Another deal-specific query
        ("Query: Rivulet Financing (Deal-Specific)", "POST", "/api/query",
         {"question": "Tell me about Rivulet's construction financing"}),

        # Test 5: Market query (should route to RAG)
        ("Query: Absorption Rates (Market-Specific)", "POST", "/api/query",
         {"question": "What are the absorption rates in these markets?"}),

        # Test 6: Hybrid query
        ("Query: Rivulet vs Market (Hybrid)", "POST", "/api/query",
         {"question": "How does Rivulet's financing compare to market standards?"}),

        # Test 7: Health check
        ("Health Check", "GET", "/health", None),
    ]

    passed = 0
    failed = 0

    for test in tests:
        if test_endpoint(*test):
            passed += 1
        else:
            failed += 1

    # Summary
    print(f"\n{'='*80}")
    print(f"TEST SUMMARY")
    print(f"{'='*80}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total:  {passed + failed}")

    if failed == 0:
        print("\n✓ All tests passed!")
    else:
        print(f"\n✗ {failed} test(s) failed")

    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
