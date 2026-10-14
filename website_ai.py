"""
GVPCEW Connect - Website AI Core Engine
Strictly website-focused AI response logic with 5-intent classification:
1. Greeting or common conversation
2. Question about the website (features, services, verified content)
3. Website-related question whose answer is unavailable (e.g. contact numbers)
4. Out-of-scope / unrelated question (politely redirected)
5. Unclear or meaningless message (asks for clarification)
"""

import re
import string
from enum import Enum
from typing import Dict, Any, Tuple, Optional
from pdf_knowledge import search_pdfs

class IntentType(str, Enum):
    GREETING = "greeting"
    WEBSITE_QUESTION = "website_question"
    WEBSITE_UNAVAILABLE = "website_unavailable"
    OUT_OF_SCOPE = "out_of_scope"
    UNCLEAR = "unclear"


# ---------------- VERIFIED WEBSITE CONTENT REPOSITORY ----------------
WEBSITE_INFO = {
    "website_overview": {
        "title": "About GVPCEW Connect Portal",
        "answer": (
            "**Welcome to GVPCEW Connect** — the official smart academic portal for "
            "**Gayatri Vidya Parishad College of Engineering for Women (Autonomous)**, Visakhapatnam.\n\n"
            "• **Institution Status**: UGC Autonomous Institution, accredited with NAAC 'A' Grade, and NBA-accredited programs.\n"
            "• **Campus Location**: Kommadi, Madhurawada, Visakhapatnam, Andhra Pradesh – 530048 (College Code: GVPW).\n"
            "• **Website Purpose**: GVPCEW Connect provides students and visitors with instant, verified academic guidance based on official college records and autonomous regulations (R24/R20).\n"
            "• **Official College URL**: [gvpcew.ac.in](https://gvpcew.ac.in)"
        ),
        "source": "GVPCEW Institutional Overview"
    },
    "website_capabilities": {
        "title": "What You Can Do on GVPCEW Connect",
        "answer": (
            "On the **GVPCEW Connect** website, you can:\n\n"
            "• **Ask Student Questions**: Get guidance on academics, campus life, sports, cultural and technical activities, facilities, placements, and student services using available college records.\n"
            "• **Check 75% Attendance & Detention Rules**: Learn about mandatory attendance percentages, 65%–75% medical condonation, and semester detention criteria.\n"
            "• **Explore Course Syllabuses**: View 160-credit B.Tech curriculum details for CSE, CSM (AIML), CSD, IT, ECE, and EEE under autonomous R24/R20 regulations.\n"
            "• **Review Semester Exam Patterns**: Check Continuous Internal Evaluation (Mid-I & Mid-II), Semester-End Exam (SEE) timings, passing marks, and evaluation norms.\n"
            "• **Inspect Campus Placements**: Access recruitment statistics, top packages (exceeding 20+ LPA), and recruiting companies like Amazon, TCS, Infosys, and Cognizant.\n"
            "• **Explore Campus Life**: Ask about cultural events, student clubs, sports, technical activities, internships, facilities, and college notices.\n"
            "• **Track Academic Calendars**: View instructional timelines, mid-term exam schedules, and holiday vacation periods.\n"
            "• **Search Official Documents**: Access verified information extracted from 33 official college PDFs in the document repository.\n"
            "• **Use Interactive Tools**: Use quick suggestion cards, topic chips, Dark/Light theme switching, and 1-click clipboard answer copying."
        ),
        "source": "GVPCEW Connect Capabilities"
    },
    "website_features": {
        "title": "Verified Features of GVPCEW Connect",
        "answer": (
            "The **GVPCEW Connect** website provides the following verified features:\n\n"
            "• **AI Student Assistant**: Responds to questions about academics, campus life, student activities, facilities, and services using available college information.\n"
            "• **Student FAQ Cards**: One-click questions for attendance, exams, syllabus, placements, campus life, sports, technical events, facilities, notices, results, and fees.\n"
            "• **Interactive Quick Topic Chips**: A carousel of clickable filter buttons for rapid navigation across popular academic categories.\n"
            "• **33 Official College Documents**: Integrated access to 33 verified college PDF documents including timetables, calendars, R24 syllabuses, and annual reports.\n"
            "• **Dark & Light Mode Switcher**: Seamless theme toggle in the navigation bar with preference saved in browser local storage.\n"
            "• **1-Click Copy Answer**: Copy any response text directly to your clipboard with toast notification feedback.\n"
            "• **New Chat Reset**: Instant conversation reset button to clear history and start a fresh inquiry.\n"
            "• **Live Backend Health Monitor**: Real-time status indicator displaying server connection status (`/api/health`)."
        ),
        "source": "GVPCEW Connect Features & Services"
    },
    "theme_feature": {
        "title": "Dark & Light Theme Mode",
        "answer": (
            "**Theme Customization on GVPCEW Connect:**\n\n"
            "• You can toggle between **Dark Mode** and **Light Mode** at any time by clicking the theme button (🌙 / ☀️) in the top-right navbar.\n"
            "• Your selected theme preference is automatically saved in your browser's local storage (`localStorage`) and remembered across visits."
        ),
        "source": "GVPCEW Connect UI Features"
    },
    "copy_feature": {
        "title": "Copy Answer Feature",
        "answer": (
            "**Copying Answers on GVPCEW Connect:**\n\n"
            "• Every response generated by the assistant features a **📋 Copy Answer** button at the bottom of the message card.\n"
            "• Clicking it copies the complete answer text directly to your clipboard, accompanied by a confirmation popup toast."
        ),
        "source": "GVPCEW Connect UI Features"
    },
    "document_library_feature": {
        "title": "Official Document Repository (33 PDFs)",
        "answer": (
            "**College Document Library on GVPCEW Connect:**\n\n"
            "• The system indexes **33 official college PDF documents** in the knowledge repository.\n"
            "• Documents include Autonomous Academic Regulations (R24), Four-Year Syllabuses for CSE, CSM, ECE, EEE, and IT, Mid & Semester Exam Timetables, Academic Calendars, Placement Reports, and Student Handbooks.\n"
            "• When you ask specific questions, the assistant retrieves exact citations (document name and page number) directly from these records."
        ),
        "source": "GVPCEW Connect Document Repository"
    },
    "attendance": {
        "title": "Attendance & Detention Regulations (R24/R20)",
        "answer": (
            "**GVPCEW Mandatory Attendance Policy (Autonomous Regulations):**\n\n"
            "• **Minimum Requirement**: Every student must maintain a minimum of **75% aggregate attendance** across all registered theory and lab courses in each semester.\n"
            "• **Condonation of Shortage**: Attendance shortage between **65% and 75%** may be condoned by the Academic Committee on genuine medical grounds upon submission of valid medical proof and payment of the prescribed condonation fee.\n"
            "• **Detention Rule**: Students securing **less than 65% aggregate attendance** are **NOT permitted** to appear for Semester-End Examinations (theory or practical) under any circumstances and will be **detained** for that semester.\n"
            "• **Progression**: Detained students must repeat that entire semester in the subsequent academic year when offered.\n"
            "• **ERP Tracking**: Attendance is updated daily on the College ERP portal so students can monitor their percentage in real-time."
        ),
        "source": "Autonomous Academic Regulations (R24) - Attendance Criteria"
    },
    "exams": {
        "title": "Examinations & Evaluation Guidelines",
        "answer": (
            "**GVPCEW Autonomous Examination Guidelines:**\n\n"
            "• **Continuous Internal Evaluation (CIE)**: Consists of two Mid-Term Examinations (Mid-I and Mid-II) per semester. Mid-I covers the first 50% syllabus; Mid-II covers the remaining 50%.\n"
            "• **Semester End Examinations (SEE)**: Comprehensive external theory and practical lab examinations conducted at the conclusion of 16 weeks of instruction.\n"
            "• **Exam Timings**: Standard exam sessions are conducted in Forenoon (FN: 10:00 AM – 1:00 PM) and Afternoon (AN: 2:00 PM – 5:00 PM).\n"
            "• **Passing Criteria**: A student must secure a minimum of **35% in SEE** and an aggregate of **40% (CIE + SEE combined)** to pass each course and earn credits.\n"
            "• **Supply & Revaluation**: Regular and supplementary exams run simultaneously. Provision for challenge evaluation and revaluation is available as per college autonomous norms."
        ),
        "source": "Autonomous Examination Guidelines & Evaluation Norms"
    },
    "syllabus_csm": {
        "title": "CSM (AI & ML) Autonomous Syllabus",
        "answer": (
            "**CSE - Artificial Intelligence & Machine Learning (CSM) — 160 Credits:**\n\n"
            "• **Core AI/ML Subjects**: Mathematical Foundations for AI, Machine Learning, Deep Learning, Natural Language Processing (NLP), Computer Vision, and Neural Networks.\n"
            "• **Programming**: Python for AI, Data Structures & Algorithms, OOP, and Software Engineering.\n"
            "• **Advanced Electives**: Reinforcement Learning, Robotics, Generative AI, Large Language Models (LLMs), and AI Ethics.\n"
            "• **Lab Courses**: ML Lab (Scikit-learn & TensorFlow), Deep Learning Lab (Keras & PyTorch), NLP Lab, and Computer Vision Lab.\n"
            "• **Skill Courses**: MLOps with Cloud Platforms, Data Analytics, and Full Stack AI Application Development.\n"
            "• **Mandatory Internship**: Industry/research internship after 2nd and 3rd year plus final year project.\n"
            "• **Honors & Minors**: CGPA >= 8.0 students can pursue 18–20 additional credits in Cybersecurity, Data Science, or IoT."
        ),
        "source": "CSM Autonomous Four-Year Syllabus - GVPCEW"
    },
    "syllabus_cse": {
        "title": "CSE Autonomous Syllabus",
        "answer": (
            "**Computer Science & Engineering (CSE) — 160 Credits:**\n\n"
            "• **Core Subjects**: Data Structures & Algorithms, OOP (Java & Python), Database Management Systems (DBMS), Operating Systems, Computer Networks, and Theory of Computation.\n"
            "• **Systems & Development**: Compiler Design, Software Engineering, Full Stack Web Development, and Cloud Computing.\n"
            "• **Advanced Electives**: Cybersecurity, Blockchain, DevOps, Distributed Systems, and Data Warehousing.\n"
            "• **Lab Courses**: Programming Lab (C/Java/Python), DBMS Lab, Networks Lab, OS Lab, and Web Development Lab.\n"
            "• **Mandatory Internship**: Industry internship after 2nd and 3rd year.\n"
            "• **Honors & Minors**: CGPA >= 8.0 students can pursue 18–20 additional credits in AI/ML, Data Science, or IoT."
        ),
        "source": "CSE Autonomous Four-Year Syllabus - GVPCEW"
    },
    "syllabus_it": {
        "title": "IT Autonomous Syllabus",
        "answer": (
            "**Information Technology (IT) — 160 Credits:**\n\n"
            "• **Core Subjects**: Software Engineering, Information Security & Cryptography, Distributed Computing, Mobile App Development, and Database Systems.\n"
            "• **Development & Cloud**: Full Stack Development, Cloud Architecture (AWS/Azure/GCP), Microservices, and DevOps.\n"
            "• **Advanced Electives**: Cyber Forensics, IoT & Embedded Systems, Blockchain Technology, and Big Data Analytics.\n"
            "• **Lab Courses**: Software Development Lab, Security Lab, Cloud & DevOps Lab, and Web Technologies Lab.\n"
            "• **Mandatory Internship**: Industry internship after 2nd and 3rd year.\n"
            "• **Honors & Minors**: CGPA >= 8.0 students can pursue 18–20 additional credits in AI/ML or Cybersecurity."
        ),
        "source": "IT Autonomous Four-Year Syllabus - GVPCEW"
    },
    "syllabus_ece": {
        "title": "ECE Autonomous Syllabus",
        "answer": (
            "**Electronics & Communication Engineering (ECE) — 160 Credits:**\n\n"
            "• **Core Subjects**: Electronic Devices & Circuits, Signals & Systems, Analog & Digital Communication, Electromagnetic Theory, and VLSI System Design.\n"
            "• **Systems & Embedded**: Embedded Systems, Microprocessors & Microcontrollers, Real-Time Operating Systems, and IoT Communication Protocols.\n"
            "• **Advanced Electives**: Digital Signal Processing (DSP), Antenna & Wave Propagation, Satellite Communications, and RF Engineering.\n"
            "• **Lab Courses**: Electronics Lab, Communication Lab, Microprocessor Lab, VLSI Lab, and Embedded Systems Lab.\n"
            "• **Mandatory Internship**: Industry/research internship after 2nd and 3rd year.\n"
            "• **Honors & Minors**: CGPA >= 8.0 students can pursue 18–20 additional credits in AI/ML or IoT."
        ),
        "source": "ECE Autonomous Four-Year Syllabus - GVPCEW"
    },
    "syllabus_eee": {
        "title": "EEE Autonomous Syllabus",
        "answer": (
            "**Electrical & Electronics Engineering (EEE) — 160 Credits:**\n\n"
            "• **Core Subjects**: Circuit Theory, Electrical Machines, Power Systems, Control Systems, and Power Electronics.\n"
            "• **Modern & Emerging**: Renewable Energy Sources (Solar, Wind), Electric Vehicle (EV) Technology, Smart Grid, and Energy Auditing.\n"
            "• **Advanced Electives**: FACTS Technology, High Voltage Engineering, Industrial Drives, and PLC & SCADA Systems.\n"
            "• **Lab Courses**: Electrical Machines Lab, Power Electronics Lab, Control Systems Lab, and Simulation Lab (MATLAB/Simulink).\n"
            "• **Mandatory Internship**: Industry internship after 2nd and 3rd year.\n"
            "• **Honors & Minors**: CGPA >= 8.0 students can pursue 18–20 additional credits in Renewable Energy or Power Systems."
        ),
        "source": "EEE Autonomous Four-Year Syllabus - GVPCEW"
    },
    "syllabus": {
        "title": "Autonomous Curriculum & Syllabus — All Branches",
        "answer": (
            "**GVPCEW B.Tech Autonomous Curriculum (160 Total Credits) — All Branches:**\n\n"
            "• **CSE (Computer Science & Engineering)**: Data Structures, Algorithms, OOP, DBMS, OS, Computer Networks, Full Stack Development, and Cloud Computing.\n"
            "• **CSM (AI & Machine Learning)**: Mathematical Foundations for AI, Deep Learning, NLP, Computer Vision, Neural Networks, and Robotics.\n"
            "• **IT (Information Technology)**: Software Engineering, Information Security, Cryptography, Distributed Systems, Cloud Architecture, and DevOps.\n"
            "• **ECE (Electronics & Communication)**: VLSI Design, Embedded Systems, Microprocessors, Digital Signal Processing, and IoT Communication.\n"
            "• **EEE (Electrical & Electronics)**: Power Systems, Control Systems, Power Electronics, Renewable Energy, and Electric Vehicle Technology.\n"
            "• **Honors & Minors**: CGPA >= 8.0 students can register for 18–20 additional credits in specialized emerging fields.\n\n"
            "👉 Ask specifically — e.g. *CSM syllabus*, *CSE syllabus*, *ECE syllabus* — for detailed branch info!"
        ),
        "source": "GVPCEW Autonomous Four-Year B.Tech Curriculum"
    },
    "placements": {
        "title": "Campus Placements & Training Highlights",
        "answer": (
            "**GVPCEW Campus Recruitment Highlights:**\n\n"
            "• **Highest Salary Package**: Exceeds **20+ LPA** with top multinational product firms.\n"
            "• **Average Salary Package**: Ranges between **4.5 LPA – 6.5 LPA** across branches.\n"
            "• **Top Multinational Recruiters**: Amazon, TCS, Infosys, Cognizant, Wipro, Accenture, Virtusa, Capgemini, Tech Mahindra, Hexaware, Cisco, and ServiceNow.\n"
            "• **Training & Placement Cell**: Year-round aptitude training, competitive coding bootcamps (LeetCode, HackerRank), mock technical interviews, and soft skill workshops.\n"
            "• **Internships**: Mandatory summer internships in core industries and research organizations after 2nd and 3rd year."
        ),
        "source": "Training & Placement Cell Official Statistics"
    },
    "academic_calendar": {
        "title": "Academic Calendar & Semester Timelines",
        "answer": (
            "**Semester Schedule & Academic Timeline:**\n\n"
            "• **Instruction Structure**: Each semester comprises **16 weeks of continuous instruction** divided into Spell-I (weeks 1–8) and Spell-II (weeks 9–16).\n"
            "• **Mid-I Examinations**: Held immediately after completion of the 8th week of Spell-I instruction.\n"
            "• **Mid-II Examinations**: Held after the 16th week of Spell-II instruction.\n"
            "• **Preparation & Practical Exams**: 1 week scheduled right after Spell-II prior to semester-end theory exams.\n"
            "• **Vacation Breaks**: Sankranti holidays (mid-January, ~1 week), Dasara break (October, ~1 week), and Summer vacation as notified by the Academic Council."
        ),
        "source": "Institutional Academic Calendar Guidelines"
    },
    "holidays": {
        "title": "College Holidays & Vacation Schedules",
        "answer": (
            "**Official College Holidays & Festive Breaks:**\n\n"
            "• **Sankranti Holidays**: Typically a 1-week break in mid-January.\n"
            "• **Dasara / Vijayadashami Break**: 1-week festive recess in October.\n"
            "• **Summer Vacation**: Provided at the conclusion of even-semester examinations for students not undertaking mandatory summer internships.\n"
            "• **National Holidays**: Republic Day, Independence Day, Gandhi Jayanti, and Andhra Pradesh state government gazetted holidays are strictly observed."
        ),
        "source": "Institutional Holiday Schedule"
    },
    "departments": {
        "title": "Academic Departments & Infrastructure",
        "answer": (
            "**Academic Departments at GVPCEW (NBA-Accredited):**\n\n"
            "• **Computer Science & Engineering (CSE)**\n"
            "• **CSE - Artificial Intelligence & Machine Learning (CSM)**\n"
            "• **CSE - Data Science (CSD)**\n"
            "• **Information Technology (IT)**\n"
            "• **Electronics & Communication Engineering (ECE)**\n"
            "• **Electrical & Electronics Engineering (EEE)**\n"
            "• **Basic Sciences & Humanities (BS&H)**\n\n"
            "**Campus Facilities**: State-of-the-art computer labs with high-speed internet, central digital library, secure on-campus women's hostel, gymnasium, seminar halls, and extensive bus transport covering Visakhapatnam city."
        ),
        "source": "College Profile & Departmental Overview"
    },
    "cultural_activities": {
        "title": "Campus Life, Cultural Activities & Clubs",
        "answer": (
            "**Student Life & Cultural Clubs at GVPCEW:**\n\n"
            "• **Annual Cultural Fest**: Inter-collegiate youth festival with dance, music, dramatic arts, fashion, and talent competitions.\n"
            "• **Student Professional Chapters**: IEEE Women in Engineering (WIE), Computer Society of India (CSI), and ISTE chapters.\n"
            "• **Campus Clubs**: Literary & Debating Club, Fine Arts & Photography Club, Music & Dance Club, and NSS (National Service Scheme) social outreach cell.\n"
            "• **Celebrations**: Traditional Day, Engineers' Day, Freshers' Welcome, and Farewell celebrations."
        ),
        "source": "Student Affairs & Campus Life Records"
    },
    "sports": {
        "title": "Sports & Athletic Facilities",
        "answer": (
            "**Sports & Physical Education at GVPCEW:**\n\n"
            "• **Indoor Facilities**: Table Tennis, Chess, Carrom, and Gymnasium facilities on campus.\n"
            "• **Outdoor Sports**: Dedicated courts for Volleyball, Throwball, Badminton, and Basketball.\n"
            "• **Annual Sports Meet**: Inter-departmental competitions and athletics meets organized on National Sports Day and College Day.\n"
            "• **Competition Opportunities**: Students can participate in inter-college, state, and national sports meets."
        ),
        "source": "Sports & Physical Education Records"
    },
    "technical_activities": {
        "title": "Technical Activities & Student Events",
        "answer": (
            "**Technical Activities & Learning Opportunities at GVPCEW:**\n\n"
            "• **Department Events**: Student associations organize technical fests and academic activities.\n"
            "• **Workshops & Talks**: Workshops, symposia, paper presentations, hackathons, and guest lectures provide opportunities to learn and share work.\n"
            "• **Professional Chapters**: IEEE, CSI, IETE, and ISTE student chapters support technical learning and peer participation.\n"
            "• Check department notices and official college announcements for current dates and registration details."
        ),
        "source": "Technical Activities & Annual Reports"
    },
    "notices": {
        "title": "Official Notices & Circulars",
        "answer": (
            "**Official Announcements & Circulars:**\n\n"
            "• All examination circulars, timetable updates, fee deadlines, and placement drives are posted on the college ERP portal and digital noticeboards.\n"
            "• Students receive real-time notifications for mid-term dates, hall-ticket generation, and campus recruitment drives."
        ),
        "source": "Academic Notices & Circulars"
    }
}


# ---------------- INTENT CLASSIFICATION HELPERS ----------------

def _clean_query(text: str) -> str:
    """Normalize query text for classification."""
    return re.sub(r'\s+', ' ', text.strip().lower())

def is_meaningless_or_unclear(query: str) -> bool:
    """
    Detect if the user message is unclear, gibberish, keyboard mash,
    empty, or pure punctuation/symbols.
    """
    cleaned = query.strip()
    if not cleaned:
        return True

    # Punctuation/symbols only (e.g., "???", "...", "!", "!@#$%")
    no_punct = cleaned.translate(str.maketrans('', '', string.punctuation + string.whitespace))
    if not no_punct:
        return True

    # Numbers only with no query context (e.g. "12345", "999")
    if no_punct.isdigit() and len(no_punct) < 6:
        return True

    q_lower = cleaned.lower()

    # Repetitive single character (e.g. "aaaaaa", "zzzz", ".....")
    if len(q_lower) >= 3 and len(set(q_lower.replace(" ", ""))) == 1:
        return True

    # Check words for keyboard smashing / non-words
    words = re.findall(r'[a-zA-Z]+', q_lower)
    if not words:
        return True

    # Common short valid words/acronyms to whitelist
    valid_tokens = {
        "hi", "hey", "hello", "bye", "ok", "okay", "yo", "sup", "yes", "no",
        "cse", "csm", "csd", "ece", "eee", "it", "r24", "r20", "cie", "see",
        "lpa", "gvp", "gvpw", "jntu", "nba", "naac", "erp", "fn", "an", "ctc",
        "fee", "mid", "lab", "gym", "bus", "who", "what", "when", "why", "how",
        "can", "you", "tell", "show", "help", "give", "is", "are", "am", "do",
        "does", "the", "a", "an", "in", "on", "at", "to", "for", "of", "with",
        "about", "my", "our", "this", "site", "web"
    }

    vowels = set("aeiouy")
    meaningless_word_count = 0

    for w in words:
        if w in valid_tokens:
            continue
        # Length > 4 and has no vowels at all (e.g. "sdfgh", "asdfghjkl")
        if len(w) >= 4 and not any(ch in vowels for ch in w):
            meaningless_word_count += 1
            continue
        # 5 or more consecutive consonants (e.g. "asdfghjkl", "hksdjfhskdf")
        if re.search(r'[^aeiouy\s]{5,}', w):
            meaningless_word_count += 1
            continue
        # Repetitive 3+ same char (e.g. "soooo", "heyyyy" is fine, but "asdasdasd", "qwertyqwerty")
        if re.search(r'(.)\1{3,}', w):
            meaningless_word_count += 1
            continue
        # Keyboard smash patterns (e.g. "asdf", "qwerty", "zxcv")
        if w in {"asdf", "asdfg", "asdfgh", "asdfghjkl", "qwerty", "qwertyuiop", "zxcv", "zxcvbnm", "qweasd", "hjkhjk", "jklsem"}:
            meaningless_word_count += 1
            continue

    # If all alphabetic words look like gibberish
    if meaningless_word_count > 0 and meaningless_word_count == len(words):
        return True

    return False


def is_greeting_or_conversation(query: str) -> Tuple[bool, Optional[str]]:
    """
    Detect if query is a greeting, pleasantry, gratitude, farewell, or acknowledgment.
    Returns (True, sub_type) or (False, None).
    """
    q = _clean_query(query)
    q_no_punct = q.translate(str.maketrans('', '', string.punctuation)).strip()

    # Exact single/two word greetings
    greeting_map = {
        "hi": "hi",
        "hello": "hello",
        "hey": "hey",
        "hiya": "hey",
        "howdy": "hey",
        "yo": "hey",
        "sup": "hey",
        "hi there": "hi",
        "hello there": "hello",
        "hey there": "hey",
        "greetings": "hello",
        "good morning": "hello",
        "good afternoon": "hello",
        "good evening": "hello",
        "good day": "hello"
    }

    if q_no_punct in greeting_map:
        return True, greeting_map[q_no_punct]

    # "How are you" variations
    if any(q_no_punct.startswith(k) or q_no_punct == k for k in [
        "how are you", "how are u", "how are you doing", "how are u doing",
        "how is it going", "hows it going", "how do you do", "hope you are well",
        "whats up", "what is up"
    ]):
        return True, "how_are_you"

    # Gratitude / Thank you variations
    if any(q_no_punct.startswith(k) or q_no_punct == k for k in [
        "thank you", "thanks", "thank u", "thanks a lot", "thank you so much",
        "thx", "appreciate it", "many thanks", "great thanks", "thanks for help"
    ]):
        return True, "thank_you"

    # Farewells
    if any(q_no_punct.startswith(k) or q_no_punct == k for k in [
        "bye", "goodbye", "good bye", "bye bye", "see you", "see ya", "cya",
        "talk to you later", "have a nice day", "have a great day", "farewell",
        "take care", "good night"
    ]):
        return True, "bye"

    # Polite acknowledgments
    if q_no_punct in ["ok", "okay", "alright", "cool", "got it", "noted", "understood", "nice", "great", "sure", "k"]:
        return True, "acknowledgment"

    # Conversational questions about bot identity/feelings
    if q_no_punct in ["who are you", "what is your name", "who made you", "what can you do"]:
        # "what can you do" can lead to website overview
        if "what can you do" in q_no_punct:
            return False, None
        return True, "who_are_you"

    return False, None


def is_out_of_scope(query: str) -> Tuple[bool, Optional[str]]:
    """
    Detect if the user message is about an unrelated topic:
    - Programming/coding questions (not college syllabus)
    - General knowledge, external celebrities, cricket/sports stars, politicians
    - Jokes, songs, stories, entertainment
    - Weather, news, stocks
    - General geography, history, science, math
    - Personal/medical/financial advice
    """
    q = _clean_query(query)

    # 1. Jokes / Entertainment requests
    if any(k in q for k in ["tell me a joke", "tell a joke", "say a joke", "make me laugh", "tell me a story", "sing a song", "tell a riddle"]):
        return True, "joke"

    # 2. Weather & Climate
    if any(k in q for k in ["weather", "temperature today", "will it rain", "weather forecast", "weather today"]):
        return True, "weather"

    # 3. External Sports Celebrities & External Matches (Virat Kohli, Dhoni, IPL, etc.)
    celebrities = [
        "virat kohli", "kohli", "ms dhoni", "dhoni", "rohit sharma", "sachin tendulkar",
        "sachin", "ronaldo", "messi", "shah rukh", "shahrukh", "salman khan",
        "narendra modi", "modi", "donald trump", "trump", "biden", "elon musk",
        "ipl", "fifa", "world cup winner"
    ]
    if any(celeb in q for celeb in celebrities):
        return True, "celebrity"

    # 4. Programming / Coding tutorials (unrelated to college syllabus request)
    # Note: If query asks "syllabus for python" or "cse syllabus", that's website-related!
    # But "what is python", "write code in python", "how to write a loop" is programming out-of-scope.
    programming_topics = [
        "what is python", "what is java", "what is c++", "what is javascript",
        "what is react", "what is html", "what is css", "what is binary search",
        "how to code", "write a code", "write code", "how to reverse a linked list",
        "solve this code", "debug this", "how to print in python", "learn python",
        "explain recursion", "write a python script", "what is an array",
        "what is machine learning in general", "explain binary tree"
    ]
    if any(pt in q for pt in programming_topics):
        return True, "programming"

    # If query starts with "what is <programming language>" with no college context
    if re.match(r'^what is (python|java|c\+\+|javascript|react|angular|vue|c language|rust|golang|php|ruby)\b', q):
        return True, "programming"

    # 5. General Knowledge / Trivia / History / Geography / Math
    general_knowledge_patterns = [
        "capital of france", "capital of india", "capital of germany", "capital of usa",
        "who discovered gravity", "distance to moon", "distance to sun", "speed of light",
        "who was the first president", "who won world war", "how many countries in the world",
        "solve 2+2", "what is 2+2", "who is the prime minister", "who is the president",
        "what is quantum physics", "formula for relativity", "photosynthesis"
    ]
    if any(gk in q for gk in general_knowledge_patterns):
        return True, "general_knowledge"

    # 6. Personal advice / Medical / Finance
    advice_patterns = [
        "how to lose weight", "i have a headache", "medical advice", "cure for fever",
        "relationship advice", "should i buy bitcoin", "stock market tips", "investment advice"
    ]
    if any(ap in q for ap in advice_patterns):
        return True, "advice"

    return False, None


def is_website_unavailable(query: str) -> Tuple[bool, Optional[str]]:
    """
    Detect if the user is asking about something related to the website/college,
    but the information is NOT available on the website (e.g., contact phone numbers,
    bank accounts, canteen menu prices, bus stop times, student marks).
    """
    q = _clean_query(query)

    # 1. Contact / Phone / Mobile / Telephone / Helpline numbers
    contact_keywords = [
        "contact number", "contact no", "phone number", "phone no",
        "mobile number", "mobile no", "telephone number", "telephone no",
        "helpline number", "helpline no", "toll free", "call number",
        "contact phone", "principal phone", "principal's phone", "principal mobile",
        "admission phone", "office phone", "college phone", "what is the contact number",
        "what is the phone number", "give me contact number", "share phone number"
    ]
    if any(k in q for k in contact_keywords):
        return True, "contact_number"

    # Also check "contact" with "number" or "phone" or "call"
    if "contact" in q and any(w in q for w in ["number", "no", "phone", "call", "mobile"]):
        return True, "contact_number"

    # 2. Bank account / Fee payment account / IFSC code
    bank_keywords = ["bank account", "ifsc code", "account number", "account details for fee", "bank details"]
    if any(k in q for k in bank_keywords):
        return True, "bank_details"

    fee_keywords = ["fee structure", "tuition fee", "college fees", "scholarship", "financial aid"]
    if any(k in q for k in fee_keywords):
        return True, "fees_scholarships"

    # 3. Canteen daily food menu / Prices
    canteen_keywords = ["canteen menu", "canteen food price", "mess food menu", "canteen rate list"]
    if any(k in q for k in canteen_keywords):
        return True, "canteen_menu"

    # 4. Bus stop timings / Driver numbers
    bus_timing_keywords = ["bus timing", "bus stop time", "bus arrival time", "bus route timetable", "bus driver phone"]
    if any(k in q for k in bus_timing_keywords):
        return True, "bus_timings"

    # 5. Personal student grades / marks / roll number results
    result_keywords = ["my marks", "my result", "my results", "check my results", "where can i check my results", "my sgpa", "my cgpa", "roll number 2", "check my grade"]
    if any(k in q for k in result_keywords):
        return True, "student_results"

    # 6. Faculty personal mobile numbers
    faculty_contact_keywords = ["faculty phone", "faculty mobile", "teacher phone", "hod phone", "professor mobile"]
    if any(k in q for k in faculty_contact_keywords):
        return True, "faculty_contact"

    return False, None


def classify_user_intent(query: str) -> Tuple[IntentType, Dict[str, Any]]:
    """
    Classify user message into one of 5 distinct categories:
    1. GREETING (greeting or common conversation)
    2. WEBSITE_QUESTION (question about website features, capabilities, or verified content)
    3. WEBSITE_UNAVAILABLE (website-related question whose answer is unavailable)
    4. OUT_OF_SCOPE (unrelated questions like Python programming, Virat Kohli, joke, weather)
    5. UNCLEAR (meaningless text, gibberish, empty)
    """
    # Step 1: Meaningless or unclear check
    if is_meaningless_or_unclear(query):
        return IntentType.UNCLEAR, {"reason": "meaningless_or_unclear"}

    # Step 2: Greeting or common conversation check
    is_greet, greet_type = is_greeting_or_conversation(query)
    if is_greet:
        return IntentType.GREETING, {"sub_type": greet_type}

    # Step 3: Out-of-scope check (programming, jokes, celebrities, weather, general trivia)
    is_out, out_type = is_out_of_scope(query)
    if is_out:
        return IntentType.OUT_OF_SCOPE, {"sub_type": out_type}

    # Step 4: Website-related unavailable information check (contact numbers, etc.)
    is_unavail, unavail_type = is_website_unavailable(query)
    if is_unavail:
        return IntentType.WEBSITE_UNAVAILABLE, {"sub_type": unavail_type}

    # Step 5: Website-related questions
    return IntentType.WEBSITE_QUESTION, {}


# ---------------- RESPONSE GENERATION ENGINE ----------------

def generate_ai_response(query: str) -> Dict[str, Any]:
    """
    Primary AI response logic enforcing strict website-only boundaries.
    """
    intent, meta = classify_user_intent(query)
    q_lower = _clean_query(query)

    # ---------------- 1. GREETING OR COMMON CONVERSATION ----------------
    if intent == IntentType.GREETING:
        sub_type = meta.get("sub_type", "hello")
        if sub_type == "hi":
            answer = "Hi! How can I help you with this website?"
        elif sub_type == "hello":
            answer = "Hello! What would you like to know about our website?"
        elif sub_type == "hey":
            answer = "Hey! How can I assist you?"
        elif sub_type == "how_are_you":
            answer = "I'm doing well, thanks! How can I help you with the website?"
        elif sub_type == "thank_you":
            answer = "You're welcome! Let me know if you have any other questions about the website."
        elif sub_type == "bye":
            answer = "Goodbye! Have a great day."
        elif sub_type == "acknowledgment":
            answer = "Glad to help! Let me know if you have any other questions about the website."
        elif sub_type == "who_are_you":
            answer = (
                "I am the **GVPCEW Connect AI Assistant**! I am here to help you with information "
                "about academics, campus life, cultural and technical activities, sports, facilities, placements, and student services, based on available college records. "
                "If a detail is not in the records, I will let you know."
            )
        else:
            answer = "Hello! What would you like to know about our website?"

        return {
            "answer": answer,
            "source": "GVPCEW Assistant",
            "page": 1,
            "intent": IntentType.GREETING.value,
            "score": 1.0,
            "detected_category": "greeting"
        }

    # ---------------- 5. UNCLEAR OR MEANINGLESS MESSAGE ----------------
    if intent == IntentType.UNCLEAR:
        return {
            "answer": "I couldn't understand your message. Could you please clarify or rephrase what you'd like to know about the website?",
            "source": "GVPCEW Assistant",
            "page": 1,
            "intent": IntentType.UNCLEAR.value,
            "score": 0.0,
            "detected_category": "unclear"
        }

    # ---------------- 4. OUT-OF-SCOPE QUESTIONS ----------------
    if intent == IntentType.OUT_OF_SCOPE:
        sub_type = meta.get("sub_type", "general")
        if sub_type == "programming":
            answer = "I'm here to answer questions about this website. Is there anything about the website I can help you with?"
        elif sub_type == "celebrity":
            answer = "I can help with information about this website. What would you like to know about it?"
        elif sub_type == "joke":
            answer = "I'm designed to assist with questions about this website. Feel free to ask me about its features or content."
        elif sub_type == "weather":
            answer = "I can help with information available on this website, but I can't answer unrelated questions."
        else:
            answer = "I'm here to help with GVPCEW information, campus life, and student-related questions. Ask me about the website or college topics."

        return {
            "answer": answer,
            "source": "Website Scope Policy",
            "page": 1,
            "intent": IntentType.OUT_OF_SCOPE.value,
            "score": 0.0,
            "detected_category": "out_of_scope"
        }

    # ---------------- 3. UNKNOWN / UNAVAILABLE WEBSITE INFORMATION ----------------
    if intent == IntentType.WEBSITE_UNAVAILABLE:
        sub_type = meta.get("sub_type", "general")
        if sub_type == "contact_number":
            answer = "I couldn't find a contact number in the available website information."
        elif sub_type == "bank_details":
            answer = "Bank account numbers and IFSC code details for fee payments are not available on this website. Please consult the college administration office directly."
        elif sub_type == "canteen_menu":
            answer = "The canteen menu and daily food pricing details are not available on this website."
        elif sub_type == "bus_timings":
            answer = "Detailed bus route stop timings are not available in the website records."
        elif sub_type == "student_results":
            answer = "Individual student marks and examination grades are not accessible on this website. Please log into the official college ERP portal."
        elif sub_type == "fees_scholarships":
            answer = "Current fee amounts and scholarship eligibility details aren't included in the available website records. Please check the latest official college notices or contact the college administration for verified information."
        elif sub_type == "faculty_contact":
            answer = "Personal phone numbers of individual faculty members are not available in the website information."
        else:
            answer = "I couldn't find that specific information in the available website records."

        return {
            "answer": answer,
            "source": "Website Information Status",
            "page": 1,
            "intent": IntentType.WEBSITE_UNAVAILABLE.value,
            "score": 0.0,
            "detected_category": "unavailable"
        }

    # ---------------- 2. QUESTION ABOUT THE WEBSITE ----------------
    # A. Inquiries about the website itself, what can be done, features, and UI
    if any(k in q_lower for k in [
        "what can i do on this website", "what can i do on this site", "what can you do",
        "how to use this website", "how do i use this website", "what does this website do",
        "what is this website for", "help me with this website"
    ]):
        info = WEBSITE_INFO["website_capabilities"]
        return {
            "answer": info["answer"],
            "source": info["source"],
            "page": 1,
            "intent": IntentType.WEBSITE_QUESTION.value,
            "score": 1.0,
            "detected_category": "website_capabilities"
        }

    if any(k in q_lower for k in [
        "what features does this website provide", "what features are available",
        "what features does this site have", "features of this website", "website features",
        "what functionality", "features provided", "what services does this website provide"
    ]):
        info = WEBSITE_INFO["website_features"]
        return {
            "answer": info["answer"],
            "source": info["source"],
            "page": 1,
            "intent": IntentType.WEBSITE_QUESTION.value,
            "score": 1.0,
            "detected_category": "website_features"
        }

    if any(k in q_lower for k in ["about this website", "what is gvpcew connect", "about gvpcew connect", "tell me about this portal", "college portal"]):
        info = WEBSITE_INFO["website_overview"]
        return {
            "answer": info["answer"],
            "source": info["source"],
            "page": 1,
            "intent": IntentType.WEBSITE_QUESTION.value,
            "score": 1.0,
            "detected_category": "website_overview"
        }

    if any(k in q_lower for k in ["theme", "dark mode", "light mode", "change theme"]):
        info = WEBSITE_INFO["theme_feature"]
        return {
            "answer": info["answer"],
            "source": info["source"],
            "page": 1,
            "intent": IntentType.WEBSITE_QUESTION.value,
            "score": 1.0,
            "detected_category": "theme_feature"
        }

    if any(k in q_lower for k in ["copy answer", "copy message", "clipboard"]):
        info = WEBSITE_INFO["copy_feature"]
        return {
            "answer": info["answer"],
            "source": info["source"],
            "page": 1,
            "intent": IntentType.WEBSITE_QUESTION.value,
            "score": 1.0,
            "detected_category": "copy_feature"
        }

    if any(k in q_lower for k in ["33 pdf", "document library", "pdf documents", "download pdf", "what documents"]):
        info = WEBSITE_INFO["document_library_feature"]
        return {
            "answer": info["answer"],
            "source": info["source"],
            "page": 1,
            "intent": IntentType.WEBSITE_QUESTION.value,
            "score": 1.0,
            "detected_category": "document_library"
        }

    # B. Specific Academic Topics Available on the Website
    if any(k in q_lower for k in ["attendance", "present", "absent", "detention", "condonation", "medical shortage", "75%"]):
        info = WEBSITE_INFO["attendance"]
        return {
            "answer": info["answer"],
            "source": info["source"],
            "page": 1,
            "intent": IntentType.WEBSITE_QUESTION.value,
            "score": 1.0,
            "detected_category": "attendance"
        }

    if any(k in q_lower for k in ["exam", "timetable", "mid exam", "mid-term", "internal exam", "semester end", "marks evaluation", "cie", "see"]):
        info = WEBSITE_INFO["exams"]
        return {
            "answer": info["answer"],
            "source": info["source"],
            "page": 1,
            "intent": IntentType.WEBSITE_QUESTION.value,
            "score": 1.0,
            "detected_category": "exams"
        }

    if any(k in q_lower for k in ["syllabus", "curriculum", "course structure", "credit", "r24", "r20", "subject"]):
        # Detect specific branch
        if any(k in q_lower for k in ["csm", "ai ml", "aiml", "ai and ml", "artificial intelligence", "machine learning branch", "cse aiml", "cse ai"]):
            info = WEBSITE_INFO["syllabus_csm"]
        elif any(k in q_lower for k in ["cse", "computer science", "cs syllabus"]):
            info = WEBSITE_INFO["syllabus_cse"]
        elif any(k in q_lower for k in ["it syllabus", "information technology syllabus", " it ", "it branch", "it department"]):
            info = WEBSITE_INFO["syllabus_it"]
        elif any(k in q_lower for k in ["ece", "electronics and communication", "electronics communication"]):
            info = WEBSITE_INFO["syllabus_ece"]
        elif any(k in q_lower for k in ["eee", "electrical", "electrical and electronics"]):
            info = WEBSITE_INFO["syllabus_eee"]
        else:
            info = WEBSITE_INFO["syllabus"]
        return {
            "answer": info["answer"],
            "source": info["source"],
            "page": 1,
            "intent": IntentType.WEBSITE_QUESTION.value,
            "score": 1.0,
            "detected_category": "syllabus"
        }

    if any(k in q_lower for k in ["placement", "company", "companies", "package", "salary", "lpa", "recruiter", "ctc"]):
        info = WEBSITE_INFO["placements"]
        return {
            "answer": info["answer"],
            "source": info["source"],
            "page": 1,
            "intent": IntentType.WEBSITE_QUESTION.value,
            "score": 1.0,
            "detected_category": "placements"
        }

    if any(k in q_lower for k in ["internship", "internships", "career training", "placement training", "coding bootcamp", "mock interview"]):
        info = WEBSITE_INFO["placements"]
        return {
            "answer": info["answer"],
            "source": info["source"],
            "page": 1,
            "intent": IntentType.WEBSITE_QUESTION.value,
            "score": 1.0,
            "detected_category": "placements"
        }

    if any(k in q_lower for k in ["notice", "circular", "hall ticket", "erp notification", "fee deadline"]):
        info = WEBSITE_INFO["notices"]
        return {
            "answer": info["answer"],
            "source": info["source"],
            "page": 1,
            "intent": IntentType.WEBSITE_QUESTION.value,
            "score": 1.0,
            "detected_category": "notices"
        }

    if any(k in q_lower for k in ["calendar", "spell", "reopen", "instruction period", "commencement", "academic calendar"]):
        info = WEBSITE_INFO["academic_calendar"]
        return {
            "answer": info["answer"],
            "source": info["source"],
            "page": 1,
            "intent": IntentType.WEBSITE_QUESTION.value,
            "score": 1.0,
            "detected_category": "academic_calendar"
        }

    if any(k in q_lower for k in ["holiday", "vacation", "sankranti", "dasara", "summer break"]):
        info = WEBSITE_INFO["holidays"]
        return {
            "answer": info["answer"],
            "source": info["source"],
            "page": 1,
            "intent": IntentType.WEBSITE_QUESTION.value,
            "score": 1.0,
            "detected_category": "holidays"
        }

    if any(k in q_lower for k in ["branch", "department", "cse", "csm", "csd", "ece", "eee", "facility", "hostel", "labs", "library", "transport", "gymnasium", "seminar hall"]) or re.search(r"\bit\b", q_lower):
        info = WEBSITE_INFO["departments"]
        return {
            "answer": info["answer"],
            "source": info["source"],
            "page": 1,
            "intent": IntentType.WEBSITE_QUESTION.value,
            "score": 1.0,
            "detected_category": "departments"
        }

    if any(k in q_lower for k in ["technical activity", "technical activities", "technical fest", "workshop", "hackathon", "symposium", "paper presentation", "guest lecture", "professional chapter"]):
        info = WEBSITE_INFO["technical_activities"]
        return {
            "answer": info["answer"],
            "source": info["source"],
            "page": 1,
            "intent": IntentType.WEBSITE_QUESTION.value,
            "score": 1.0,
            "detected_category": "technical_activities"
        }

    if any(k in q_lower for k in ["club", "cultural", "fest", "dance", "music", "drama", "theater", "theatre", "rangoli", "traditional day", "freshers", "farewell", "annual day", "arts", "activity", "activities", "event", "competition", "celebration"]):
        info = WEBSITE_INFO["cultural_activities"]
        return {
            "answer": info["answer"],
            "source": info["source"],
            "page": 1,
            "intent": IntentType.WEBSITE_QUESTION.value,
            "score": 1.0,
            "detected_category": "cultural_activities"
        }

    if any(k in q_lower for k in ["sport", "athletic", "game", "volleyball", "badminton", "throwball", "basketball", "table tennis", "chess", "carrom"]):
        info = WEBSITE_INFO["sports"]
        return {
            "answer": info["answer"],
            "source": info["source"],
            "page": 1,
            "intent": IntentType.WEBSITE_QUESTION.value,
            "score": 1.0,
            "detected_category": "sports"
        }

    # C. Search 33 College PDF index for specific technical or document queries
    results = search_pdfs(query, top_k=2)
    if results and results[0]["score"] >= 0.14:
        top_res = results[0]
        text = top_res["text"].strip()
        words = text.split()
        if len(words) > 130:
            text = " ".join(words[:130]) + "..."

        return {
            "answer": (
                f"**Information from College Records:**\n\n"
                f"{text}\n\n"
                f"• **Source Document**: `{top_res['source']}` (Page {top_res['page']})"
            ),
            "source": top_res["source"],
            "page": top_res["page"],
            "intent": IntentType.WEBSITE_QUESTION.value,
            "score": round(top_res["score"], 3),
            "detected_category": "document_search"
        }

    # D. If it's a website-related inquiry but specific details are not available in our records
    # Instead of generating unrelated assumptions or the old repetitive generic response:
    return {
        "answer": (
            "I couldn't find that specific information in the available website records. "
            "You can ask about attendance regulations, semester examinations, autonomous syllabus (R24), "
            "campus placements, or academic calendars!"
        ),
        "source": "Website Information Status",
        "page": 1,
        "intent": IntentType.WEBSITE_UNAVAILABLE.value,
        "score": 0.0,
        "detected_category": "unavailable"
    }
