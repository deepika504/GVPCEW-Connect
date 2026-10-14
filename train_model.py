"""
GVPCEW Connect - Machine Learning Intent & Topic Classifier Trainer
Trains a TF-IDF Logistic Regression pipeline on institutional categories,
common greetings, website features, out-of-scope queries, and unavailable information.
"""

import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

training_data = {
    "greeting": [
        "Hi",
        "Hello",
        "Hey",
        "Hi there",
        "Hello there",
        "Good morning",
        "Good afternoon",
        "Good evening",
        "How are you?",
        "How are you doing?",
        "How is it going?",
        "Thank you",
        "Thanks",
        "Thank you very much",
        "Thanks a lot",
        "Bye",
        "Goodbye",
        "See you later",
        "Have a nice day"
    ],

    "website_features": [
        "What can I do on this website?",
        "What features does this website provide?",
        "What does this website do?",
        "How do I use this website?",
        "Tell me about GVPCEW Connect website",
        "What services are available on this portal?",
        "What functionality does this website have?",
        "How to toggle dark mode?",
        "How do I switch theme?",
        "How do I copy answers to clipboard?",
        "Show me website features",
        "What official documents are on this website?"
    ],

    "out_of_scope": [
        "What is Python?",
        "What is Java?",
        "What is C++?",
        "What is JavaScript?",
        "What is React?",
        "Write code to reverse a linked list",
        "Explain binary search algorithm",
        "Who is Virat Kohli?",
        "Who is MS Dhoni?",
        "Who is Sachin Tendulkar?",
        "Who is Cristiano Ronaldo?",
        "Who is Narendra Modi?",
        "Who is Donald Trump?",
        "Tell me a joke",
        "Make me laugh",
        "Tell me a story",
        "What is the weather today?",
        "Will it rain tomorrow?",
        "What is the capital of France?",
        "What is the capital of India?",
        "Who discovered gravity?",
        "What is the speed of light?",
        "Should I invest in crypto?",
        "Give me relationship advice"
    ],

    "website_unavailable": [
        "What is the contact number?",
        "What is the website's contact number?",
        "What is the college phone number?",
        "What is the principal's phone number?",
        "What is the admission helpline number?",
        "What is the mobile number for admissions?",
        "What is the bank account number for fee payment?",
        "What is the IFSC code of the college bank?",
        "What is today's canteen food menu?",
        "Show me canteen food prices",
        "What are the bus route stop timings?",
        "Check my roll number result"
    ],

    "exams": [
        "When are semester exams?",
        "When are first year semester exams?",
        "When are second year semester exams?",
        "When are third year semester exams?",
        "When are final year semester exams?",
        "When are first year exams for the 2026 batch?",
        "When are second year exams for the 2025 batch?",
        "When are third year exams for the 2024 batch?",
        "When are fourth year exams for the 2023 batch?",
        "Show the first year exam timetable",
        "Show the third year examination schedule",
        "When are internal examinations?",
        "When are practical exams?",
        "When will end semester exams start?",
        "Where can I find the examination notification?",
        "What is the passing mark in semester end exam?",
        "Tell me about continuous internal evaluation CIE"
    ],

    "syllabus": [
        "Where can I download the syllabus?",
        "Where can I download the first year syllabus?",
        "Where can I download the second year syllabus?",
        "Where can I download the third year syllabus?",
        "Where can I download the final year syllabus?",
        "Show the first year AIML syllabus",
        "Show the third year AIML syllabus",
        "What is the syllabus for my batch?",
        "What is the syllabus under the R24 regulation?",
        "Where can I find subject wise syllabus PDFs?",
        "Show me the course curriculum",
        "Where can I find laboratory syllabus details?",
        "I need the semester wise syllabus",
        "Show CSE syllabus and course structure",
        "Show CSM artificial intelligence syllabus"
    ],

    "attendance": [
        "What is the minimum attendance requirement?",
        "How can I check my attendance?",
        "What happens if my attendance is low?",
        "Where can I find attendance rules?",
        "How do I check my attendance percentage?",
        "What is the detention rule for attendance?",
        "Can attendance shortage be condoned on medical grounds?",
        "Is 75 percent attendance mandatory?"
    ],

    "holidays": [
        "When are college holidays?",
        "What are the official holidays this year?",
        "When are Sankranti holidays?",
        "When are Dussehra holidays?",
        "When does the summer vacation start?",
        "When will the college reopen after holidays?",
        "Show the holiday list for 2026",
        "Are there any holidays next month?",
        "Where can I download the official holiday calendar?"
    ],

    "cultural_activities": [
        "What cultural activities happen in college?",
        "Are there any dance competitions?",
        "Are music competitions conducted?",
        "When is the college cultural fest?",
        "What events happen during annual day?",
        "Are there science exhibitions?",
        "What student clubs are available?",
        "How can I participate in cultural events?",
        "Are there rangoli competitions?",
        "What extracurricular activities are available?",
        "Where can I find cultural event announcements?"
    ],

    "sports": [
        "What sports are available in college?",
        "Does the college conduct sports day?",
        "When is the annual sports meet?",
        "Are badminton competitions conducted?",
        "Can students participate in volleyball?",
        "Are there throwball tournaments?",
        "How do I register for sports competitions?",
        "When are intercollege sports events?",
        "Where can I find sports announcements?"
    ],

    "academic_activities": [
        "What technical events are conducted?",
        "Are coding competitions organized?",
        "Are science and technology exhibitions conducted?",
        "When are technical fests conducted?",
        "Are workshops organized by student clubs?",
        "How can I participate in paper presentations?",
        "Are quizzes conducted by departments?",
        "Where can I find seminar announcements?"
    ],

    "placements": [
        "When do campus placements start?",
        "Which companies visit the college?",
        "Where can I find placement notifications?",
        "How can I get placement updates?",
        "Where is the placement cell?",
        "What is the highest package in placements?",
        "What is the average salary package?",
        "What companies recruit from GVPCEW?"
    ],

    "notices": [
        "Show me the latest official notices",
        "Where can I find college circulars?",
        "Show official college announcements",
        "Where are event notifications published?",
        "Where can I find academic updates?",
        "Show the latest college news"
    ],

    "departments": [
        "What departments are available?",
        "Where can I find department information?",
        "What courses does the college offer?",
        "Where can I find faculty details?",
        "Tell me about the AIML department",
        "What branches are offered at GVPCEW?"
    ],

    "academic_calendar": [
        "Show the academic calendar",
        "Where can I download the first year academic calendar?",
        "Where can I download the second year academic calendar?",
        "Where can I download the third year academic calendar?",
        "Show the academic calendar for the 2025 batch",
        "Show the academic calendar for the 2024 batch",
        "When does the next semester begin?",
        "When does the semester end?",
        "Where can I find the classwork commencement date?"
    ]
}

def train_and_save():
    # Prepare questions and category labels
    X = []
    y = []

    for category, questions in training_data.items():
        for question in questions:
            X.append(question)
            y.append(category)

    # Create and train the ML model
    model = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), lowercase=True)),
        ("classifier", LogisticRegression(max_iter=1000, C=1.5)),
    ])

    model.fit(X, y)

    # Save the trained model
    os.makedirs("models", exist_ok=True)
    out_path = "models/question_classifier.joblib"
    joblib.dump(model, out_path)

    print("\nGVPCEW Connect ML model trained successfully!")
    print(f"Training examples: {len(X)}")
    print(f"Categories: {len(training_data)}")
    print(f"Saved to {out_path}")

if __name__ == "__main__":
    train_and_save()