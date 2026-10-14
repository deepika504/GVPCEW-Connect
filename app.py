import os
import joblib
import streamlit as st
from pdf_knowledge import search_pdfs, get_categorized_documents, extract_all_chunks
from website_ai import generate_ai_response, IntentType

MODEL_PATH = "models/question_classifier.joblib"

st.set_page_config(
    page_title="GVPCEW Connect - Smart College Portal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CURATED KNOWLEDGE BASE ----------------
CATEGORY_KNOWLEDGE = {
    "exams": {
        "title": "Examinations & Timetables",
        "icon": "📝",
        "summary": "GVPCEW conducts autonomous semester examinations under college regulations.",
        "details": (
            "• **Mid-Term Exams**: Two continuous internal mid-term examinations (Mid-I & Mid-II) conducted per semester.\n"
            "• **End Semester Exams**: Theory and Practical lab exams held at the end of each semester.\n"
            "• **Notifications & Timetables**: Detailed branch-wise timetables (CSE, CSM, ECE, EEE, IT) are published under official notifications.\n"
            "• **Evaluation**: Continuous Internal Evaluation (CIE) + Semester End Examination (SEE) as per R24/R20 regulations."
        ),
        "docs": ["ExaminationNotification-IB.Tech-IISemester-June2026.pdf", "TimeTable-II B.Tech_II_Semester_CSE_Regular_Examinations_April_2026.pdf"]
    },
    "syllabus": {
        "title": "Syllabus & Course Structure",
        "icon": "📚",
        "summary": "Complete autonomous curriculum outlines for all engineering departments.",
        "details": (
            "• **Regulations**: R24 (Latest Autonomous Regulation) & R20 for B.Tech programmes.\n"
            "• **Branches Covered**: CSE, CSE-AIML (CSM), CSE-Cybersecurity, IT, ECE, and EEE.\n"
            "• **Components**: Theory courses, integrated laboratory sessions, skill-oriented courses, mandatory internships, and honors/minors degrees."
        ),
        "docs": ["BTECH ACADEMIC RULES AND REGULATIONS GVPCEW(A)-R24.pdf", "CSE AUTONOMOUS FOUR YEAR SYLLABUS.pdf", "CSM AUTONOMOUS FOUR YEAR SYLLABUS.pdf"]
    },
    "attendance": {
        "title": "Attendance Policy & Regulations",
        "icon": "🎯",
        "summary": "Mandatory academic attendance guidelines under Autonomous Regulations.",
        "details": (
            "• **Minimum Requirement**: A candidate must acquire a minimum of **75% aggregate attendance** in all subjects.\n"
            "• **Condonation of Shortage**: Shortage between **65% and 75%** may be condoned by the Academic Committee on genuine medical grounds upon submission of valid medical certificate and condonation fee.\n"
            "• **Detention**: Students with less than **65% aggregate attendance** are NOT eligible to appear for semester-end examinations and will be detained for that academic year.\n"
            "• **ERP Tracking**: Attendance is updated daily on the College ERP portal."
        ),
        "docs": ["BTECH ACADEMIC RULES AND REGULATIONS GVPCEW(A)-R24.pdf", "STUDENTS HAND BOOK 2021-2022.pdf"]
    },
    "academic_calendar": {
        "title": "Academic Calendar & Schedules",
        "icon": "📅",
        "summary": "Official academic dates, commencement of classes, and semester timelines.",
        "details": (
            "• **Classwork Commencement**: Separate schedules for I Year, II Year, III Year, and IV Year B.Tech.\n"
            "• **Instruction Period**: Typically 16 weeks of continuous instruction per semester divided into two spells.\n"
            "• **Preparation & Practical Exams**: Scheduled immediately after second spell of instruction.\n"
            "• **Vacation Periods**: Dussehra break, Sankranti vacation, and Summer break as per academic council notifications."
        ),
        "docs": ["2026-27-II_B.Tech-AcedamicCalendar-2025AdmittedBatch.pdf", "2026-27-III_B.Tech-AcedamicCalendar-2024AdmittedBatch.pdf"]
    },
    "placements": {
        "title": "Placements & Career Training",
        "icon": "💼",
        "summary": "Outstanding campus recruitment track record with top multinational corporations.",
        "details": (
            "• **Training & Placement Cell**: Provides pre-placement soft skills, coding bootcamps, and aptitude training.\n"
            "• **Top Recruiters**: Amazon, TCS, Infosys, Cognizant, Wipro, Accenture, Virtusa, Capgemini, Tech Mahindra, and more.\n"
            "• **Placement Packages**: Highest packages exceeding **20+ LPA** with exceptional branch-wise placement percentages.\n"
            "• **Internships**: Mandatory summer internships in industry and research institutions."
        ),
        "docs": ["Final Overall Placement Data.pdf", "Final Overall Placement Data2023.pdf", "ANNUAL REPORT 2023-24.pdf"]
    },
    "departments": {
        "title": "Academic Departments & Programs",
        "icon": "🏫",
        "summary": "NBA accredited and high-standard departments with state-of-the-art laboratory infrastructure.",
        "details": (
            "• **Computer Science & Engineering (CSE)**\n"
            "• **Computer Science & Machine Learning (CSM / AIML)**\n"
            "• **Information Technology (IT)**\n"
            "• **Electronics & Communication Engineering (ECE)**\n"
            "• **Electrical & Electronics Engineering (EEE)**\n"
            "• **Basic Sciences & Humanities (BS&H)**\n"
            "All departments are equipped with modern research labs, high-speed campus internet, and digital smart classrooms."
        ),
        "docs": ["GVPW_BROCHURE_2024.pdf"]
    },
    "cultural_activities": {
        "title": "Cultural Activities & Student Clubs",
        "icon": "🎭",
        "summary": "Vibrant campus life with arts, music, dance, and cultural celebrations.",
        "details": (
            "• **Annual Cultural Fest & Festivities**: Traditional Day, Sankranti Celebrations, Freshers' Welcome, and Farewell events.\n"
            "• **Student Clubs**: Literary club, Music & Dance club, Fine Arts, and Social Service clubs.\n"
            "• **Competitions**: Inter-departmental dance, music, drama, rangoli, and debate competitions throughout the academic year."
        ),
        "docs": ["AnnualReport-2022-23.pdf", "ANNUAL REPORT 2023-24.pdf"]
    },
    "sports": {
        "title": "Sports & Campus Facilities",
        "icon": "🏅",
        "summary": "Physical education, indoor sports, and outdoor athletic championships.",
        "details": (
            "• **Facilities**: Basketball courts, Volleyball courts, Throwball, Badminton courts, Table Tennis, Chess, and Carroms.\n"
            "• **Annual Sports Meet**: Inter-branch tournaments with medals and awards.\n"
            "• **Competition Opportunities**: Students can participate in inter-college and wider-level sports tournaments."
        ),
        "docs": ["STUDENTS HAND BOOK 2021-2022.pdf"]
    },
    "notices": {
        "title": "Official Notices & Circulars",
        "icon": "📢",
        "summary": "Institutional circulars, administrative orders, and academic circulars.",
        "details": (
            "• Official circulars are posted on the college ERP, website notices section, and departmental boards.\n"
            "• Students should regularly monitor examination notifications, fee deadlines, and scholarship notices."
        ),
        "docs": ["6.2.3_ERP DOCUMENT.pdf", "ExaminationNotification-IB.Tech-IISemester-June2026.pdf"]
    },
    "holidays": {
        "title": "College Holidays & Breaks",
        "icon": "🗓️",
        "summary": "Government and institutional approved holidays.",
        "details": (
            "• Follows Andhra Pradesh government holidays and official college academic notifications.\n"
            "• Key breaks: Sankranti vacation, Dasara holidays, and Summer vacation as per the Academic Calendar."
        ),
        "docs": ["2026-27-II_B.Tech-AcedamicCalendar-2025AdmittedBatch.pdf"]
    },
    "academic_activities": {
        "title": "Technical Activities & Symposia",
        "icon": "🔬",
        "summary": "Workshops, technical paper presentations, hackathons, and guest lectures.",
        "details": (
            "• Departmental student associations organize annual technical fests.\n"
            "• Professional chapters: IEEE Student Branch, CSI (Computer Society of India), IETE, and ISTE.\n"
            "• Regular guest lectures from industry professionals and premier institute professors."
        ),
        "docs": ["ANNUAL REPORT 2023-24.pdf"]
    }
}

# ---------------- THEME ----------------
if "app_theme" not in st.session_state:
    st.session_state.app_theme = "Light"

dark_mode = st.session_state.app_theme == "Dark"

if dark_mode:
    BG = "#0B1528"
    SURFACE = "#13223D"
    SURFACE_ALT = "#192D50"
    CARD = "#162847"
    TEXT = "#EEF4FF"
    MUTED = "#9FB7D8"
    BORDER = "#2C4673"
    ACCENT = "#3B82F6"
    ACCENT_LIGHT = "rgba(59, 130, 246, 0.15)"
else:
    BG = "#F5F8FC"
    SURFACE = "#FFFFFF"
    SURFACE_ALT = "#F0F5FD"
    CARD = "#FFFFFF"
    TEXT = "#102341"
    MUTED = "#556B8A"
    BORDER = "#D6E3F5"
    ACCENT = "#1A56DB"
    ACCENT_LIGHT = "rgba(26, 86, 219, 0.08)"

# ---------------- CUSTOM CSS ----------------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
}}

.stApp {{
    background: {BG};
    color: {TEXT};
}}

.block-container {{
    max-width: 1200px;
    padding-top: 1rem;
    padding-bottom: 3rem;
}}

/* Top Hero Banner */
.portal-hero {{
    background: linear-gradient(135deg, #0A2558 0%, #17428F 50%, #205BB5 100%);
    border-radius: 20px;
    padding: 30px 32px;
    color: #ffffff;
    box-shadow: 0 10px 30px rgba(10, 37, 88, 0.15);
    margin-bottom: 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 20px;
    border: 1px solid rgba(255, 255, 255, 0.12);
}}

.portal-title {{
    font-family: 'Outfit', sans-serif;
    font-size: 32px;
    font-weight: 800;
    margin: 0;
    color: #ffffff !important;
    letter-spacing: -0.5px;
}}

.portal-subtitle {{
    font-size: 15px;
    color: #CFE0FF !important;
    margin-top: 6px;
    margin-bottom: 0;
}}

.portal-badge {{
    display: inline-block;
    background: rgba(255, 255, 255, 0.18);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.3);
    padding: 6px 14px;
    border-radius: 25px;
    font-size: 13px;
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 10px;
}}

.stat-pill-container {{
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
}}

.stat-pill {{
    background: rgba(255, 255, 255, 0.12);
    border: 1px solid rgba(255, 255, 255, 0.2);
    padding: 10px 16px;
    border-radius: 12px;
    text-align: center;
}}

.stat-pill .num {{
    font-size: 20px;
    font-weight: 700;
    color: #FFE680;
}}

.stat-pill .label {{
    font-size: 11px;
    color: #E2ECFF;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

/* Quick Query Pill Buttons */
.chip-container {{
    display: flex;
    gap: 10px;
    overflow-x: auto;
    padding: 6px 2px 14px;
}}

/* Card container */
.info-card {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 18px;
    box-shadow: 0 4px 14px rgba(10, 37, 88, 0.04);
}}

/* Answers styling */
.answer-box {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-left: 5px solid {ACCENT};
    border-radius: 14px;
    padding: 20px 22px;
    margin-top: 14px;
    margin-bottom: 18px;
    box-shadow: 0 4px 16px rgba(10, 37, 88, 0.05);
}}

.source-badge {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: {SURFACE_ALT};
    border: 1px solid {BORDER};
    padding: 5px 12px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
    color: {TEXT};
    margin-top: 10px;
}}

/* Tabs styling */
.stTabs [data-baseweb="tab-list"] {{
    gap: 8px;
    border-bottom: 2px solid {BORDER};
    padding-bottom: 4px;
}}

.stTabs [data-baseweb="tab"] {{
    border-radius: 10px 10px 0 0;
    padding: 10px 20px;
    font-weight: 600;
    color: {MUTED};
    background-color: transparent;
}}

.stTabs [aria-selected="true"] {{
    color: {ACCENT} !important;
    border-bottom: 3px solid {ACCENT} !important;
}}

/* Button styling */
.stButton > button {{
    border: 1px solid {BORDER} !important;
    border-radius: 10px !important;
    background: {SURFACE} !important;
    color: {TEXT} !important;
    font-weight: 600 !important;
    transition: all 0.2s ease;
}}

.stButton > button:hover {{
    border-color: {ACCENT} !important;
    color: {ACCENT} !important;
    box-shadow: 0 4px 12px rgba(26, 86, 219, 0.12);
}}

/* Chat message */
div[data-testid="stChatMessage"] {{
    background: {SURFACE} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 14px !important;
    padding: 14px 18px !important;
    margin-bottom: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
}}

/* Chat input */
div[data-testid="stChatInput"] {{
    background: {SURFACE} !important;
    border: 1.5px solid {BORDER} !important;
    border-radius: 14px !important;
}}

div[data-testid="stChatInput"]:focus-within {{
    border-color: {ACCENT} !important;
    box-shadow: 0 0 0 3px {ACCENT_LIGHT} !important;
}}

/* Document pill in library */
.doc-card {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    transition: transform 0.15s ease, border-color 0.15s ease;
}}

.doc-card:hover {{
    border-color: {ACCENT};
    transform: translateY(-2px);
}}

.footer {{
    text-align: center;
    color: {MUTED};
    font-size: 13px;
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px solid {BORDER};
}}
</style>
""", unsafe_allow_html=True)

# ---------------- MODEL LOADER ----------------
@st.cache_resource
def load_ml_classifier():
    if os.path.exists(MODEL_PATH):
        try:
            return joblib.load(MODEL_PATH)
        except Exception:
            return None
    return None

model = load_ml_classifier()

# Warm up PDF cache
@st.cache_resource
def get_pdf_engine():
    return extract_all_chunks(force_refresh=False)

# Trigger background engine initialization
get_pdf_engine()

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Graduation_hat.svg/300px-Graduation_hat.svg.png",
        width=60,
    )
    st.markdown("### **GVPCEW Connect**")
    st.caption("Gayatri Vidya Parishad College of Engineering for Women (Autonomous)")
    st.caption("Kommadi, Madhurawada, Visakhapatnam - 530048")
    st.markdown("---")

    # Theme Toggle
    st.markdown("**🌓 Theme Mode**")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        if st.button("☀️ Light", use_container_width=True):
            st.session_state.app_theme = "Light"
            st.rerun()
    with col_t2:
        if st.button("🌙 Dark", use_container_width=True):
            st.session_state.app_theme = "Dark"
            st.rerun()

    st.markdown("---")
    st.markdown("### 📌 **Quick Information**")
    st.info(
        "**Autonomous Status**: UGC autonomous institution\n\n"
        "**Accreditation**: NAAC 'A' Grade, NBA\n\n"
        "**College Code**: GVPW\n\n"
        "**Website**: [gvpcew.ac.in](https://gvpcew.ac.in)"
    )

    st.markdown("---")
    if st.button("🔄 Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ---------------- HERO HEADER ----------------
st.markdown("""
<div class="portal-hero">
    <div>
        <div class="portal-badge">🏛️ Autonomous Institution · NAAC 'A' Grade</div>
        <h1 class="portal-title">GVPCEW Connect</h1>
        <p class="portal-subtitle">Official Smart Academic Portal & AI Knowledge Assistant</p>
    </div>
    <div class="stat-pill-container">
        <div class="stat-pill">
            <div class="num">33+</div>
            <div class="label">Official Documents</div>
        </div>
        <div class="stat-pill">
            <div class="num">2,650+</div>
            <div class="label">Knowledge Chunks</div>
        </div>
        <div class="stat-pill">
            <div class="num">100%</div>
            <div class="label">Instant Search</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------- NAVIGATION TABS ----------------
tab_chat, tab_docs, tab_topics, tab_about = st.tabs([
    "💬 Smart AI Assistant",
    "📑 College Document Library (33 PDFs)",
    "🏛️ Academic Topics & FAQs",
    "ℹ️ About GVPCEW & Portal"
])

# ================= TAB 1: SMART AI ASSISTANT =================
with tab_chat:
    st.markdown("##### ⚡ **Quick Questions (Click to Ask)**")
    
    # Quick prompt pills
    chips = [
        "What is the minimum attendance requirement?",
        "When are the II B.Tech II Sem exams?",
        "Show CSE syllabus and course structure",
        "Tell me about campus placements and companies",
        "Show Academic Calendar for 2026",
        "What are the autonomous B.Tech R24 rules?"
    ]
    
    selected_chip = None
    c_cols = st.columns(3)
    for i, chip_text in enumerate(chips):
        with c_cols[i % 3]:
            if st.button(f"🔍 {chip_text}", key=f"chip_{i}", use_container_width=True):
                selected_chip = chip_text

    st.markdown("---")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "**Welcome to GVPCEW Connect!** 👋\n\n"
                    "I have indexed all 33 official college documents including semester exam timetables, "
                    "autonomous syllabuses (R24/R20), academic calendars, placement records, and handbooks.\n\n"
                    "How can I help you today? Ask any question or click one of the quick suggestions above!"
                )
            }
        ]

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"], unsafe_allow_html=True)

    # Question Input
    user_input = st.chat_input("Ask a question about exams, syllabus, attendance, calendar, placements...")

    active_query = user_input or selected_chip

    if active_query and active_query.strip():
        query_text = active_query.strip()
        st.session_state.messages.append({"role": "user", "content": query_text})

        with st.spinner("Processing official website query..."):
            ai_res = generate_ai_response(query_text)
            
            source_info = ai_res.get("source", "Verified College Academic Record")
            response_markdown = f"{ai_res['answer']}\n\n---\n📌 **Source**: `{source_info}`"

        st.session_state.messages.append({"role": "assistant", "content": response_markdown})
        st.rerun()

# ================= TAB 2: DOCUMENT LIBRARY =================
with tab_docs:
    st.markdown("### 📑 **GVPCEW Official Document Library**")
    st.caption("Browse, inspect, and access all 33 verified college PDF documents.")

    doc_categories = get_categorized_documents()
    pdf_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "college_pdfs")

    search_doc = st.text_input("🔍 Filter documents by name...", placeholder="e.g. syllabus, timetable, calendar, placement")

    for cat_name, file_list in doc_categories.items():
        filtered_files = [f for f in file_list if search_doc.lower() in f.lower()] if search_doc else file_list
        
        if filtered_files:
            with st.expander(f"📁 {cat_name} ({len(filtered_files)} Documents)", expanded=True):
                for fname in filtered_files:
                    fpath = os.path.join(pdf_dir, fname)
                    fsize_kb = os.path.getsize(fpath) // 1024 if os.path.exists(fpath) else 0

                    col_name, col_size, col_btn = st.columns([6, 2, 2])
                    with col_name:
                        st.markdown(f"📄 **{fname}**")
                    with col_size:
                        st.caption(f"{fsize_kb:,} KB")
                    with col_btn:
                        if os.path.exists(fpath):
                            with open(fpath, "rb") as f_data:
                                st.download_button(
                                    label="📥 Download",
                                    data=f_data.read(),
                                    file_name=fname,
                                    mime="application/pdf",
                                    key=f"dl_{fname}"
                                )

# ================= TAB 3: ACADEMIC TOPICS & FAQS =================
with tab_topics:
    st.markdown("### 🏛️ **College Guidelines & Quick FAQs**")
    st.caption("Verified institutional policies and autonomous academic standards at GVPCEW.")

    t_cols = st.columns(2)
    cat_items = list(CATEGORY_KNOWLEDGE.items())

    for idx, (cat_key, cat_data) in enumerate(cat_items):
        target_col = t_cols[idx % 2]
        with target_col:
            st.markdown(f"""
            <div class="info-card">
                <h4>{cat_data['icon']} {cat_data['title']}</h4>
                <p style="color:{MUTED}; font-size:14px; margin-bottom:12px;">{cat_data['summary']}</p>
                <div style="font-size:13.5px; line-height:1.7;">
                    {cat_data['details'].replace(chr(10), '<br>')}
                </div>
            </div>
            """, unsafe_allow_html=True)

# ================= TAB 4: ABOUT GVPCEW =================
with tab_about:
    st.markdown("### 🎓 **About GVPCEW Connect**")
    
    st.markdown("""
    **Gayatri Vidya Parishad College of Engineering for Women (GVPCEW)** was established in 2008 by Gayatri Vidya Parishad, a premier educational society in Visakhapatnam, Andhra Pradesh.

    #### Key Highlights:
    - **Status**: Autonomous Institution approved by AICTE.
    - **Accreditation**: Accredited by **NAAC with 'A' Grade** and programs accredited by the **National Board of Accreditation (NBA)**.
    - **Branches Offered**:
      - Computer Science and Engineering (CSE)
      - Computer Science and Engineering - AI & Machine Learning (CSM)
      - Computer Science and Engineering - Data Science (CSD)
      - Information Technology (IT)
      - Electronics and Communication Engineering (ECE)
      - Electrical and Electronics Engineering (EEE)
    - **State-of-the-Art Facilities**: High-performance computing labs, advanced AI/ML workstations, digital central library with IEEE & Springer access, Wi-Fi campus, seminar halls, sports arena, and transportation covering entire Visakhapatnam.

    #### About this Portal:
    **GVPCEW Connect** brings all college resources, timetables, regulations, and official circulars into an intelligent search portal.
    """)

# ---------------- FOOTER ----------------
st.markdown("""
<div class="footer">
    © 2026 Gayatri Vidya Parishad College of Engineering for Women · Kommadi, Visakhapatnam · GVPCEW Connect
</div>
""", unsafe_allow_html=True)