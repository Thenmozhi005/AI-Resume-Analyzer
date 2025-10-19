import re
import spacy
from PyPDF2 import PdfReader

# Load English NLP model (for text understanding)
nlp = spacy.load("en_core_web_sm")

# Function to extract text from uploaded PDF
def extract_text_from_pdf(uploaded_file):
    pdf_reader = PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Function to extract skills from text
def extract_skills(text):
    # Basic skill list (we’ll expand later)
    skills = ["python", "java", "c++", "sql", "html", "css", "javascript", 
              "machine learning", "deep learning", "data analysis", 
              "excel", "communication", "leadership", "teamwork"]
    
    text = text.lower()
    found_skills = [skill for skill in skills if skill in text]
    return found_skills

# Function to calculate match percentage
def calculate_match(resume_text, job_desc):
    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_desc)

    matched = [skill for skill in resume_skills if skill in job_skills]
    score = len(matched) / len(job_skills) * 100 if job_skills else 0

    return round(score, 2), matched
