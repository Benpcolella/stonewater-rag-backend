#!/usr/bin/env python3
"""
Test script to verify the Stonewater RAG API is working correctly.
Run this after reloading the app on PythonAnywhere.
"""

import requests
import json
import time

# Configuration
API_URL = "https://Benpcolella.pythonanywhere.com"
API_KEY = "stonewater_demo_key_123"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def test_health():
    """Test the health endpoint."""
    print("Testing /health endpoint...")
    response = requests.get(f"{API_URL}/health")
    print(f"  Status: {response.status_code}")
    data = response.json()
    print(f"  Response: {json.dumps(data, indent=2)}")
    chunks = data.get('vector_store_chunks', 0)
    print(f"  Vector store chunks: {chunks}")
    return chunks > 0

def test_stats():
    """Test the stats endpoint."""
    print("\nTesting /api/stats endpoint...")
    response = requests.get(f"{API_URL}/api/stats", headers=headers)
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Total documents: {data.get('documents', {}).get('total', 'N/A')}")
        print(f"  Total chunks indexed: {data.get('vector_store', {}).get('total_chunks', 'N/A')}")
        return True
    else:
        print(f"  Error: {response.text[:200]}")
        return False

def test_query():
    """Test the query endpoint with a sample question."""
    print("\nTesting /api/query endpoint...")
    question = "What is Stonewater Group?"
    payload = {"question": question}

    response = requests.post(f"{API_URL}/api/query", json=payload, headers=headers)
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Question: {data.get('question')}")
        print(f"  Answer preview: {data.get('answer', 'N/A')[:150]}...")
        print(f"  Citations found: {len(data.get('citations', []))}")
        return True
    else:
        print(f"  Error: {response.text[:200]}")
        return False

def test_documents():
    """Test the documents endpoint."""
    print("\nTesting /api/documents endpoint...")
    response = requests.get(f"{API_URL}/api/documents", headers=headers)
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        count = data.get('count', 0)
        print(f"  Documents tracked: {count}")
        if count > 0 and 'documents' in data:
            first_doc = data['documents'][0]
            print(f"  First document: {first_doc.get('file_name', 'N/A')}")
        return count > 0
    else:
        print(f"  Error: {response.text[:200]}")
        return False

if __name__ == '__main__':
    print(f"Testing Stonewater RAG API at {API_URL}\n")

    results = {
        "Health": False,
        "Stats": False,
        "Documents": False,
        "Query": False
    }

    try:
        results["Health"] = test_health()
        results["Stats"] = test_stats()
        results["Documents"] = test_documents()
        results["Query"] = test_query()
    except Exception as e:
        print(f"\nError during testing: {e}")

    print("\n" + "="*50)
    print("Test Results:")
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {test_name}: {status}")

    all_passed = all(results.values())
    if all_passed:
        print("\n✓ All tests passed! The API is ready for use.")
    else:
        print("\n✗ Some tests failed. Check the errors above.")
