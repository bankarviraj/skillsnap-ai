from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
import fitz  # PyMuPDF
import re
from datetime import datetime

# ---------------- Flask Setup ----------------
app = Flask(__name__)
CORS(app, origins="http://localhost:4200")

# Uploads folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- Database Setup ----------------
DB_USER = "postgres"
DB_PASSWORD = "Viraj123"
DB_HOST = "localhost"
DB_PORT = "7070"  # ✅ Correct port
DB_NAME = "resume_db"

app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ---------------- Resume Model ----------------
class Resume(db.Model):
    __tablename__ = "resumes"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(50))
    job_title = db.Column(db.String(120))
    match_score = db.Column(db.Float)
    matched_skills = db.Column(db.Text)
    missing_skills = db.Column(db.Text)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, name, email, phone, job_title, match_score, matched_skills, missing_skills):
        self.name = name
        self.email = email
        self.phone = phone
        self.job_title = job_title
        self.match_score = match_score
        self.matched_skills = ",".join(matched_skills) if matched_skills else ""
        self.missing_skills = ",".join(missing_skills) if missing_skills else ""

# ---------------- PDF Handling ----------------
def extract_text_from_pdf(pdf_path):
    text = ''
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text.lower()

def match_skills(resume_text, skill_set):
    matched = []
    for skill in skill_set:
        if re.search(r'\b' + re.escape(skill.lower()) + r'\b', resume_text):
            matched.append(skill)
    return matched

# ---------------- Job Profiles ----------------
job_profiles = {
    "AI/ML Engineer": ["machine learning", "deep learning", "tensorflow", "pytorch", "python", "data science"],
    "Web Developer": ["html", "css", "javascript", "react", "angular", "node.js"],
    "Cybersecurity Analyst": ["nmap", "wireshark", "vulnerability", "firewalls", "malware", "encryption"],
    "Data Analyst": ["sql", "excel", "tableau", "power bi", "statistics", "data cleaning"],
    "Android Developer": ["android", "kotlin", "java", "android studio", "xml"]
}

# ---------------- Routes ----------------
@app.route('/upload', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    resume = request.files['resume']
    if resume.filename == '' or not resume.filename.endswith('.pdf'):
        return jsonify({'error': 'Invalid or missing PDF file'}), 400

    # Form fields
    name = request.form.get('name', 'user')
    email = request.form.get('email', '')
    phone = request.form.get('phone', '')

    # Save PDF
    filename = f"{name.replace(' ', '_')}_Resume.pdf"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    resume.save(filepath)
    print(f"✅ Saved PDF to {filepath}")

    # Extract text
    resume_text = extract_text_from_pdf(filepath)

    # Role matching logic
    best_match = None
    best_score = 0
    matched_skills = []

    for role, skills in job_profiles.items():
        found = match_skills(resume_text, skills)
        score = round((len(found) / len(skills)) * 100, 2) if skills else 0
        if score > best_score:
            best_match = role
            best_score = score
            matched_skills = found

    all_skills = job_profiles.get(best_match, [])
    missing_skills = [s for s in all_skills if s not in matched_skills]

    suggestions = [f"Consider learning '{skill}' to strengthen your profile." for skill in missing_skills]

    # ✅ Save into PostgreSQL
    try:
        new_resume = Resume(
            name=name,
            email=email,
            phone=phone,
            job_title=best_match or "No Match Found",
            match_score=best_score,
            matched_skills=matched_skills,
            missing_skills=missing_skills
        )
        db.session.add(new_resume)
        db.session.commit()
        print(f"📌 Saved resume data for {name} into DB")
    except Exception as e:
        print(f"❌ Error saving to DB: {e}")

    return jsonify({
        "name": name,
        "email": email,
        "phone": phone,
        "job_title": best_match or "No Match Found",
        "match_score": best_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "suggestions": suggestions,
        "job_links": {
            "linkedin": [f"https://www.linkedin.com/jobs/search/?keywords={best_match.replace(' ', '%20')}"],
            "naukri": [f"https://www.naukri.com/{best_match.replace(' ', '-').lower()}-jobs"]
        }
    }), 200

# ---------------- Run App ----------------
if __name__ == '__main__':
    # ✅ Try creating tables, handle connection errors
    try:
        with app.app_context():
            db.create_all()
            print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")

    app.run(debug=True)
