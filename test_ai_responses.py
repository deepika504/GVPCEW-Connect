"""
Comprehensive test script for GVPCEW Connect Website AI response logic
"""

import sys
from website_ai import generate_ai_response, classify_user_intent, IntentType

test_cases = [
    # Required in prompt:
    ("Hi", IntentType.GREETING, "Natural greeting"),
    ("Hello", IntentType.GREETING, "Natural greeting"),
    ("What can I do on this website?", IntentType.WEBSITE_QUESTION, "Actual website capabilities"),
    ("What features does this website provide?", IntentType.WEBSITE_QUESTION, "Verified features"),
    ("Who are you?", IntentType.GREETING, "Broader assistant identity"),
    ("What is Python?", IntentType.OUT_OF_SCOPE, "Out-of-scope response"),
    ("Tell me a joke", IntentType.OUT_OF_SCOPE, "Out-of-scope response"),
    ("What is the website's contact number?", IntentType.WEBSITE_UNAVAILABLE, "Unavailable contact number"),
    ("asdfghjkl", IntentType.UNCLEAR, "Meaningless text / gibberish clarification"),
    ("???", IntentType.UNCLEAR, "Punctuation only clarification"),
    ("Thank you", IntentType.GREETING, "Natural acknowledgment"),
    
    # Additional conversational & scope tests:
    ("Hey", IntentType.GREETING, "Natural greeting"),
    ("How are you?", IntentType.GREETING, "Conversational pleasantry"),
    ("Bye", IntentType.GREETING, "Farewell acknowledgment"),
    ("Who is Virat Kohli?", IntentType.OUT_OF_SCOPE, "Celebrity out-of-scope"),
    ("What is the weather today?", IntentType.OUT_OF_SCOPE, "Weather out-of-scope"),
    ("What is the minimum attendance requirement?", IntentType.WEBSITE_QUESTION, "Attendance rules"),
    ("When are semester exams and mid timetables?", IntentType.WEBSITE_QUESTION, "Exam details"),
    ("Show CSE and CSM syllabus", IntentType.WEBSITE_QUESTION, "Syllabus details"),
    ("What are the campus placement packages and recruiters?", IntentType.WEBSITE_QUESTION, "Placement details"),
    ("What sports are available at college?", IntentType.WEBSITE_QUESTION, "Sports facilities"),
    ("How can I join cultural activities?", IntentType.WEBSITE_QUESTION, "Cultural activities"),
    ("Does the college have basketball and chess?", IntentType.WEBSITE_QUESTION, "Specific sports"),
    ("What happens on Traditional Day and Freshers' Welcome?", IntentType.WEBSITE_QUESTION, "Specific cultural events"),
    ("What technical workshops and events are conducted?", IntentType.WEBSITE_QUESTION, "Technical activities"),
    ("Where can students find hall-ticket notices?", IntentType.WEBSITE_QUESTION, "Student notices"),
    ("What internship opportunities are available?", IntentType.WEBSITE_QUESTION, "Internships"),
    ("How do I check my results and SGPA?", IntentType.WEBSITE_UNAVAILABLE, "Personal results"),
    ("Where can I find fee structure and scholarship information?", IntentType.WEBSITE_UNAVAILABLE, "Fees and scholarships"),
    ("What is the principal's phone number?", IntentType.WEBSITE_UNAVAILABLE, "Unavailable phone number"),
]

print("=" * 70)
print("TESTING GVPCEW CONNECT WEBSITE AI ENGINE")
print("=" * 70)

all_passed = True
for query, expected_intent, description in test_cases:
    intent, meta = classify_user_intent(query)
    res = generate_ai_response(query)
    
    status = "PASS" if intent == expected_intent else "FAIL"
    if status == "FAIL":
        all_passed = False
    
    print(f"\n[{status}] Query: '{query}'")
    print(f"       Expected: {expected_intent.value} | Got: {intent.value} ({description})")
    print(f"       Answer snippet: {res['answer'][:120]}...")
    print(f"       Source: {res['source']}")

response_checks = [
    ("What sports are available at college?", "Sports & Physical Education"),
    ("How can I join cultural activities?", "Student Life & Cultural Clubs"),
    ("Does the college have basketball and chess?", "Sports & Physical Education"),
    ("What happens on Traditional Day and Freshers' Welcome?", "Student Life & Cultural Clubs"),
    ("Who are you?", "campus life"),
    ("What technical workshops and events are conducted?", "Technical Activities & Learning Opportunities"),
    ("Where can students find hall-ticket notices?", "Official Announcements & Circulars"),
    ("Where can I find fee structure and scholarship information?", "scholarship eligibility details"),
]

for query, expected_text in response_checks:
    answer = generate_ai_response(query)["answer"]
    passed = expected_text in answer
    all_passed = all_passed and passed
    print(f"\n[{'PASS' if passed else 'FAIL'}] Response content: '{query}'")
    if not passed:
        print(f"       Expected answer to include: {expected_text}")

print("\n" + "=" * 70)
if all_passed:
    print("ALL TESTS PASSED SUCCESSFULLY! (100% compliance)")
else:
    print("SOME TESTS FAILED - REVIEW LOGS ABOVE")
    sys.exit(1)
print("=" * 70)
