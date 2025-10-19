from analyser import extract_text_from_pdf, compare_skills, career_suggestions
from analyser import evaluate_structure  # newly added import
import language_tool_python
import textstat

# Path to your resume PDF
pdf_path = "sample_resume.pdf"

# Load and analyze resume
with open(pdf_path, "rb") as f:
    resume_text = extract_text_from_pdf(f)

# Sample job description (you can replace this text anytime)
job_description = """
We are seeking a Software Engineer skilled in Python, SQL, teamwork, and Java.
Experience in web development and strong communication skills preferred.
"""

# -----------------------------
# 1️⃣ Skill Matching
# -----------------------------
result = compare_skills(resume_text, job_description)
suggestions = career_suggestions(result["missing_skills"])

# -----------------------------
# 2️⃣ Structure Evaluation
# -----------------------------
structure_score, sections = evaluate_structure(resume_text)

# -----------------------------
# 3️⃣ Grammar Check
# -----------------------------
tool = language_tool_python.LanguageTool('en-US')
matches = tool.check(resume_text)
grammar_issues = len(matches)
words = len(resume_text.split())
grammar_score = max(0, 100 - (grammar_issues / words * 100)) if words > 0 else 100

# -----------------------------
# 4️⃣ Readability Score
# -----------------------------
readability_score = textstat.flesch_reading_ease(resume_text)

# -----------------------------
# 5️⃣ ATS Total Score
# -----------------------------
total_score = round((result['match_score'] * 0.4 + grammar_score * 0.2 + readability_score * 0.2 + structure_score * 0.2), 2)

# -----------------------------
# 📊 Display Results
# -----------------------------
print("\n===== ATS SCORE RESULT =====")
print(f"Total Score: {total_score}\n")

print("--- Feedback ---")
print(f"Skills: Matched skills: {', '.join(result['matched_skills']) or 'None'}")
print(f"Structure: {structure_score}% of key sections found.")
print(f"Readability: Readability Score: {readability_score:.0f} (aim for 60–80).")
print(f"Grammar: Grammar Score: {grammar_score:.0f} (higher is better).")

print("\n--- Sections Detected ---")
for section, found in sections.items():
    print(f"{section.capitalize()}: {'✅ Found' if found else '❌ Missing'}")

print("\n--- Career Suggestions ---")
for tip in suggestions:
    print(f"- {tip}")
