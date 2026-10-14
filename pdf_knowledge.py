import os
import joblib
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

PDF_FOLDER = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "data",
    "college_pdfs"
)

CACHE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "data",
    "pdf_index_cache.joblib"
)

# In-memory global cache
_INDEX_CACHE = None


def extract_all_chunks(force_refresh=False):
    """Extract chunks from all PDFs in PDF_FOLDER with disk caching."""
    global _INDEX_CACHE

    if not force_refresh and _INDEX_CACHE is not None:
        return _INDEX_CACHE

    if not force_refresh and os.path.exists(CACHE_FILE):
        try:
            _INDEX_CACHE = joblib.load(CACHE_FILE)
            if isinstance(_INDEX_CACHE, dict) and "chunks" in _INDEX_CACHE and "vectorizer" in _INDEX_CACHE:
                return _INDEX_CACHE
        except Exception as e:
            print(f"Cache load warning: {e}. Rebuilding index...")

    chunks = []
    if not os.path.exists(PDF_FOLDER):
        print(f"PDF folder not found: {PDF_FOLDER}")
        return {"chunks": [], "vectorizer": None, "document_matrix": None}

    pdf_files = [f for f in os.listdir(PDF_FOLDER) if f.lower().endswith(".pdf")]

    for filename in sorted(pdf_files):
        filepath = os.path.join(PDF_FOLDER, filename)
        try:
            reader = PdfReader(filepath)
            for page_number, page in enumerate(reader.pages, start=1):
                try:
                    text = page.extract_text() or ""
                except Exception:
                    continue
                text = " ".join(text.split())
                if not text:
                    continue

                words = text.split()
                chunk_size = 180
                overlap = 30
                step = max(chunk_size - overlap, 50)

                for start in range(0, len(words), step):
                    chunk_text = " ".join(words[start:start + chunk_size])
                    if chunk_text.strip():
                        chunks.append({
                            "text": chunk_text,
                            "source": filename,
                            "page": page_number
                        })
        except Exception as error:
            print(f"Could not read {filename}: {error}")

    if not chunks:
        _INDEX_CACHE = {"chunks": [], "vectorizer": None, "document_matrix": None}
        return _INDEX_CACHE

    documents = [c["text"] for c in chunks]
    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),
        max_features=25000
    )
    document_matrix = vectorizer.fit_transform(documents)

    _INDEX_CACHE = {
        "chunks": chunks,
        "vectorizer": vectorizer,
        "document_matrix": document_matrix
    }

    try:
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        joblib.dump(_INDEX_CACHE, CACHE_FILE)
        print(f"Successfully cached {len(chunks)} chunks to {CACHE_FILE}")
    except Exception as e:
        print(f"Could not save cache to disk: {e}")

    return _INDEX_CACHE


def load_pdf_chunks():
    """Compatibility helper: returns list of chunks."""
    cache = extract_all_chunks()
    return cache.get("chunks", [])


def search_pdfs(question, top_k=3):
    """Fast search using precomputed TF-IDF index and keyword awareness."""
    cache = extract_all_chunks()
    chunks = cache.get("chunks", [])
    vectorizer = cache.get("vectorizer")
    document_matrix = cache.get("document_matrix")

    if not chunks or vectorizer is None or document_matrix is None:
        return []

    try:
        question_vector = vectorizer.transform([question])
        raw_scores = cosine_similarity(question_vector, document_matrix).flatten()
    except Exception:
        return []

    # Apply intelligent keyword boosting for high precision
    query_lower = question.lower()
    query_tokens = [w for w in query_lower.split() if len(w) > 2]
    
    adjusted_scores = raw_scores.copy()
    for idx, chunk in enumerate(chunks):
        bonus = 0.0
        source_lower = chunk["source"].lower()
        chunk_lower = chunk["text"].lower()

        for token in query_tokens:
            if token in source_lower:
                bonus += 0.08
            if token in chunk_lower:
                bonus += 0.02
        adjusted_scores[idx] += bonus

    best_indices = adjusted_scores.argsort()[::-1][:top_k * 2]
    results = []

    for index in best_indices:
        score = adjusted_scores[index]
        if score < 0.09:
            continue

        result = chunks[index].copy()
        result["score"] = float(score)
        result["raw_score"] = float(raw_scores[index])
        results.append(result)

        if len(results) >= top_k:
            break

    return results


def get_categorized_documents():
    """Returns all available college PDFs organized by category."""
    if not os.path.exists(PDF_FOLDER):
        return {}

    categories = {
        "Timetables & Exams": [],
        "Syllabus & Curriculum": [],
        "Academic Calendars": [],
        "Placements & Reports": [],
        "Regulations & Handbooks": []
    }

    for f in sorted(os.listdir(PDF_FOLDER)):
        if not f.lower().endswith(".pdf"):
            continue
        fl = f.lower()
        if "timetable" in fl or "exam" in fl or "notification" in fl:
            categories["Timetables & Exams"].append(f)
        elif "syllabus" in fl or "course structure" in fl:
            categories["Syllabus & Curriculum"].append(f)
        elif "calander" in fl or "calendar" in fl:
            categories["Academic Calendars"].append(f)
        elif "placement" in fl or "annual report" in fl:
            categories["Placements & Reports"].append(f)
        else:
            categories["Regulations & Handbooks"].append(f)

    return categories