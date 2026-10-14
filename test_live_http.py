"""
Live HTTP test of running FastAPI server
"""

import requests
import json

base_url = "http://127.0.0.1:8000"

# 1. Health check
res = requests.get(f"{base_url}/api/health")
print("Health response:", res.status_code, res.json())
assert res.status_code == 200

# 2. Test chat questions
queries = [
    "Hi",
    "Hello",
    "What can I do on this website?",
    "What features does this website provide?",
    "What is Python?",
    "Tell me a joke",
    "What is the website's contact number?",
    "asdfghjkl",
    "Thank you",
    "What is the minimum attendance requirement?",
    "Show CSE and CSM syllabus"
]

print("\n--- Live HTTP /api/chat Responses ---")
for q in queries:
    resp = requests.post(f"{base_url}/api/chat", json={"question": q})
    assert resp.status_code == 200
    data = resp.json()
    print(f"\n[QUERY] '{q}'")
    print(f"  -> Intent: {data.get('intent')}")
    print(f"  -> Source: {data.get('source')}")
    print(f"  -> Answer: {data.get('answer')[:90]}...")

print("\nLIVE HTTP API TESTS COMPLETE AND VERIFIED!")
