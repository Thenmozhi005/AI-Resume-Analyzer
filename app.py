import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from analyser import extract_text_from_pdf, compare_skills, career_suggestions
from resume_parser import extract_skills
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import io
import language_tool_python
import textstat

# --------------------------------
# Streamlit Page Config
# --------------------------------
st.set_page_config(page_title="Smart Resume Analyzer — Final Edition", layout="wide")
st.title("📘 Smart Resume Analyzer — AI Resume Quality & PDF Report Generator")
st.markdown("### Analyze your resume like an ATS and get a downloadable AI-powered report!")

# --------------------------------
# Upload Resume
# --------------------------------
uploaded_file = st.file_uploader("📤 Upload Your Resume (PDF only)", type=["pdf"])

# --------------------------------
# Job Description Input
# --------------------------------
jd_text = st.text_area("📋 Paste the Job Description (Optional)")

# --------------------------------
# Helper: Structure Check
# --------------------------------
def analyze_structure(resume_text):
    sections = {
        "education": "education" in resume_text.lower(),
        "experience": "experience" in resume_text.lower(),
        "projects": "project" in resume_text.lower(),
        "skills": "skill" in resume_text.lower(),
        "summary": "summary" in resume_text.lower() or "objective" in resume_text.lower()
    }
    return sections

# --------------------------------
# Helper: Structure Tips
# --------------------------------
def structure_tips(structure):
    tips = []
    if not structure["summary"]:
        tips.append("Add a short professional summary at the beginning.")
    if not structure["skills"]:
        tips.append("Include a skills section with both technical and soft skills.")
    if not structure["projects"]:
        tips.append("Add academic or personal projects to showcase your work.")
    if not structure["experience"]:
        tips.append("Include work or internship experience with measurable results.")
    if not structure["education"]:
        tips.append("Make sure your education section has degrees and dates.")
    if not tips:
        tips.append("Your resume structure looks great!")
    return tips

# --------------------------------
# Helper: PDF Report Generator
# --------------------------------
def generate_resume_report(filename, total_score, structure, readability_score, grammar_score, skill_result, structure_tips_list, suggestions):
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("<b>📘 Smart Resume Analyzer Report</b>", styles["Title"]))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"<b>Overall Resume Quality Score:</b> {total_score}%", styles["Normal"]))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("<b>📑 Resume Structure:</b>", styles["Heading2"]))
    for section, present in structure.items():
        elements.append(Paragraph(f"- {section.capitalize()}: {'✅ Found' if present else '❌ Missing'}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("<b>🧩 Section Improvement Tips:</b>", styles["Heading2"]))
    for tip in structure_tips_list:
        elements.append(Paragraph(f"• {tip}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("<b>🗣 Grammar & Readability:</b>", styles["Heading2"]))
    elements.append(Paragraph(f"Readability Score: {readability_score:.2f}", styles["Normal"]))
    elements.append(Paragraph(f"Grammar Score: {grammar_score:.2f}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("<b>🎯 Skill Match Analysis:</b>", styles["Heading2"]))
    elements.append(Paragraph(f"Skill Match Score: {skill_result['match_score']}%", styles["Normal"]))
    elements.append(Paragraph(f"Matched Skills: {', '.join(skill_result['matched_skills']) or 'None'}", styles["Normal"]))
    elements.append(Paragraph(f"Missing Skills: {', '.join(skill_result['missing_skills']) or 'None'}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("<b>🚀 Career Suggestions:</b>", styles["Heading2"]))
    for s in suggestions:
        elements.append(Paragraph(f"• {s}", styles["Normal"]))

    doc.build(elements)

# --------------------------------
# Analyze Button
# --------------------------------
if st.button("🔍 Analyze Resume"):
    if uploaded_file:
        with st.spinner("Analyzing your resume... ⏳"):
            resume_text = extract_text_from_pdf(uploaded_file)

            # --- Grammar ---
            tool = language_tool_python.LanguageTool('en-US')
            matches = tool.check(resume_text)
            grammar_issues = len(matches)
            words = len(resume_text.split())
            grammar_score = max(0, 100 - (grammar_issues / words * 100)) if words > 0 else 100

            # --- Readability ---
            readability_score = textstat.flesch_reading_ease(resume_text)

            # --- Structure ---
            structure = analyze_structure(resume_text)
            structure_score = sum(structure.values()) / len(structure) * 100
            structure_tips_list = structure_tips(structure)

            # --- Skills (Job Description) ---
            if jd_text.strip():
                skill_result = compare_skills(resume_text, jd_text)
            else:
                skill_result = {"match_score": 0, "matched_skills": [], "missing_skills": []}

            # --- Overall Resume Quality ---
            total_score = round(
                (grammar_score * 0.3 + min(readability_score, 100) * 0.2 + structure_score * 0.3 + skill_result['match_score'] * 0.2),
                2
            )

        # --------------------------------
        # Display Results
        # --------------------------------
        st.subheader("📊 Analysis Results")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Grammar Score", value=f"{grammar_score:.1f}%")
        with col2:
            st.metric(label="Readability Score", value=f"{readability_score:.1f}")
        with col3:
            st.metric(label="Overall Resume Quality", value=f"{total_score}%")

        # Pie Chart (if JD provided)
        if jd_text.strip():
            matched = len(skill_result["matched_skills"])
            missing = len(skill_result["missing_skills"])
            if matched + missing > 0:
                labels = ['Matched Skills', 'Missing Skills']
                values = [matched, missing]
                colors = ['#00C49F', '#FF8042']
                fig, ax = plt.subplots()
                ax.pie(values, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
                ax.axis('equal')
                st.pyplot(fig)

        st.markdown("### ✅ **Resume Structure**")
        for sec, found in structure.items():
            st.write(f"- {sec.capitalize()}: {'✅ Found' if found else '❌ Missing'}")

        st.markdown("### 💡 **Section Improvement Tips**")
        for tip in structure_tips_list:
            st.info(f"- {tip}")

        st.markdown("### ✍️ **Grammar & Readability Insights**")
        st.warning(f"Grammar Issues Found: {grammar_issues}")
        st.info(f"Readability Score: {readability_score:.2f}")

        if jd_text.strip():
            st.markdown("### 🎯 **Skill Match Analysis**")
            st.success(", ".join(skill_result["matched_skills"]) or "None")
            st.error(", ".join(skill_result["missing_skills"]) or "None")

            st.markdown("### 🚀 **Career Suggestions**")
            for tip in career_suggestions(skill_result["missing_skills"]):
                st.markdown(f"- {tip}")

        # --------------------------------
        # PDF Report Download
        # --------------------------------
        st.subheader("📥 Download Full AI Report")
        pdf_buffer = io.BytesIO()
        generate_resume_report(
            pdf_buffer,
            total_score,
            structure,
            readability_score,
            grammar_score,
            skill_result,
            structure_tips_list,
            career_suggestions(skill_result["missing_skills"])
        )
        pdf_buffer.seek(0)
        st.download_button(
            label="⬇️ Download Resume Analysis Report (PDF)",
            data=pdf_buffer,
            file_name="Smart_Resume_Analyzer_Report.pdf",
            mime="application/pdf"
        )

    else:
        st.warning("⚠️ Please upload a PDF resume before analyzing.")
