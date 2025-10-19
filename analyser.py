import spacy
import pdfplumber
import re

# Load spaCy model
import spacy
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")


# -------------------------------------------------
# Extract text from PDF
# -------------------------------------------------
def extract_text_from_pdf(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

# -------------------------------------------------
# Skill Normalization Mapping
# -------------------------------------------------
SKILL_NORMALIZATION = {
    "cpp": "c++",
    "c plus plus": "c++",
    "python3": "python",
    "py": "python",
    "js": "javascript",
    "nodejs": "node.js",
    "reactjs": "react",
    "react.js": "react",
    "html5": "html",
    "css3": "css",
    "sql database": "sql",
    "structured query language": "sql",
    "ml": "machine learning",
    "dl": "deep learning",
    "ai": "artificial intelligence",
    "team work": "teamwork",
    "comm": "communication",
    "lead": "leadership",
}

def normalize_skill(skill):
    """Normalize synonyms and variations."""
    skill = skill.lower().strip()
    return SKILL_NORMALIZATION.get(skill, skill)

# -------------------------------------------------
# Smart Keyword Extraction
# -------------------------------------------------
def extract_keywords(text):
    """
    Extracts clean skills from job description or resume.
    Handles phrases like 'looking for candidates skilled in C++ or Python'.
    """
    text = text.lower()
    doc = nlp(text)

    # Step 1: Collect potential keywords (nouns & proper nouns)
    keywords = [token.lemma_ for token in doc if token.pos_ in ["NOUN", "PROPN"] and len(token) > 2]

    # Step 2: Capture patterns like "skills in X", "experience with Y"
    pattern = r"(?:skills|skill|experience|proficient|knowledge|expertise|looking for|familiar|candidate|candidates|skilled).*?(?:in|with|:)?\s*([a-zA-Z0-9\+\#\-\s,]+)"
    found = re.findall(pattern, text)

    found_tokens = []
    for group in found:
        parts = re.split(r',|\band\b', group)
        for p in parts:
            cleaned = p.strip()
            cleaned = re.sub(r'\b(candidates?|skilled|looking|for|in|with)\b', '', cleaned).strip()
            if cleaned:
                found_tokens.append(cleaned)

    # Step 3: Normalize skills and clean up noise
    merged = set([normalize_skill(k) for k in keywords + found_tokens if len(k) > 1])
    noise = {"experience", "skills", "candidate", "candidates", "knowledge", "requirement"}
    merged = set([k for k in merged if k not in noise])

    return merged

# -------------------------------------------------
# Compare skills between resume and JD
# -------------------------------------------------
def compare_skills(resume_text, jd_text):
    resume_keywords = extract_keywords(resume_text)
    jd_keywords = extract_keywords(jd_text)

    matched_skills = list(resume_keywords.intersection(jd_keywords))
    missing_skills = list(jd_keywords - resume_keywords)

    if len(jd_keywords) == 0:
        match_score = 0
    else:
        match_score = round((len(matched_skills) / len(jd_keywords)) * 100, 2)

    return {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "match_score": match_score
    }

# -------------------------------------------------
# Career Suggestions
# -------------------------------------------------
def career_suggestions(missing_skills):
    suggestions = []
    for skill in missing_skills:
        if "python" in skill:
            suggestions.append("Take an advanced Python course on data analysis or web frameworks.")
        elif "java" in skill:
            suggestions.append("Enhance your Java OOP and Spring Boot development skills.")
        elif "sql" in skill:
            suggestions.append("Practice writing complex SQL joins and queries.")
        elif "machine learning" in skill:
            suggestions.append("Learn ML libraries like scikit-learn or TensorFlow.")
        elif "communication" in skill:
            suggestions.append("Join communication and soft skills workshops.")
        elif "c++" in skill:
            suggestions.append("Brush up on C++ data structures and STL concepts.")
    if not suggestions:
        suggestions.append("You're doing great! Keep updating your resume with new certifications.")
    return list(set(suggestions))

# -------------------------------------------------
# NEW FEATURE: Evaluate Resume Structure
# -------------------------------------------------
def evaluate_structure(resume_text):
    """
    Detects if major sections like Education, Experience, Projects, etc. exist.
    Returns structure score and dictionary of sections.
    """
    sections = {
        "summary": bool(re.search(r"summary|objective|profile", resume_text, re.I)),
        "education": bool(re.search(r"education|qualification|academics", resume_text, re.I)),
        "experience": bool(re.search(r"experience|work history|employment", resume_text, re.I)),
        "projects": bool(re.search(r"project|portfolio", resume_text, re.I)),
        "skills": bool(re.search(r"skills|technical skills|proficiency", resume_text, re.I)),
    }

    found_count = sum(sections.values())
    structure_score = round((found_count / len(sections)) * 100, 2)

    return structure_score, sections
