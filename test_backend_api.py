"""
Backend API integration test suite for GVPCEW Connect (Direct handler invocation)
"""

import sys
from api_server import health_check, list_documents, chat_endpoint, ChatRequest

def test_health():
    res = health_check()
    assert res["status"] == "online"
    print("[PASS] health_check() returned online status")

def test_documents():
    res = list_documents()
    assert isinstance(res, dict)
    print(f"[PASS] list_documents() returned {len(res)} categories")

def test_chat_endpoints():
    test_suite = [
        # (input_text, expected_intent, expected_snippet)
        ("Hi", "greeting", "Hi! How can I help you with this website?"),
        ("Hello", "greeting", "Hello! What would you like to know about our website?"),
        ("What can I do on this website?", "website_question", "On the **GVPCEW Connect** website, you can:"),
        ("What features does this website provide?", "website_question", "The **GVPCEW Connect** website provides the following verified features:"),
        ("What is Python?", "out_of_scope", "I'm here to answer questions about this website. Is there anything about the website I can help you with?"),
        ("Tell me a joke", "out_of_scope", "I'm designed to assist with questions about this website. Feel free to ask me about its features or content."),
        ("What is the website's contact number?", "website_unavailable", "I couldn't find a contact number in the available website information."),
        ("asdfghjkl", "unclear", "I couldn't understand your message. Could you please clarify or rephrase what you'd like to know about the website?"),
        ("Thank you", "greeting", "You're welcome! Let me know if you have any other questions about the website."),
        ("Hey", "greeting", "Hey! How can I assist you?"),
        ("How are you?", "greeting", "I'm doing well, thanks! How can I help you with the website?"),
        ("Bye", "greeting", "Goodbye! Have a great day."),
        ("Who is Virat Kohli?", "out_of_scope", "I can help with information about this website. What would you like to know about it?"),
        ("What is the weather today?", "out_of_scope", "I can help with information available on this website, but I can't answer unrelated questions."),
        ("What is the minimum attendance requirement?", "website_question", "75% aggregate attendance"),
        ("Show CSE and CSM syllabus", "website_question", "Syllabus"),
    ]

    all_passed = True
    print("\n--- Running chat_endpoint Test Suite ---")
    for question, expected_intent, expected_snippet in test_suite:
        req = ChatRequest(question=question)
        data = chat_endpoint(req)
        
        intent = data.get("intent")
        answer = data.get("answer", "")
        source = data.get("source", "")
        
        intent_ok = intent == expected_intent
        snippet_ok = expected_snippet.lower() in answer.lower()
        
        if intent_ok and snippet_ok:
            print(f"[PASS] '{question}' -> Intent: {intent} | Source: {source}")
        else:
            print(f"[FAIL] '{question}'")
            print(f"       Expected intent: {expected_intent}, got: {intent}")
            print(f"       Expected snippet: '{expected_snippet}'")
            print(f"       Actual answer: '{answer[:100]}...'")
            all_passed = False

    if not all_passed:
        sys.exit(1)

if __name__ == "__main__":
    print("=" * 60)
    print("RUNNING GVPCEW CONNECT BACKEND INTEGRATION TESTS")
    print("=" * 60)
    test_health()
    test_documents()
    test_chat_endpoints()
    print("=" * 60)
    print("ALL BACKEND API TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)
