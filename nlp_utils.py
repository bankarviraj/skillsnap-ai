import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction import text

stop_words = set(text.ENGLISH_STOP_WORDS)

# Pre-defined skill sets for each IT role
ROLE_SKILL_MAP = {
    "AI/ML Engineer": {"python", "tensorflow", "keras", "pytorch", "scikit-learn", "huggingface", "transformers", "opencv", "xgboost", "fastai", "flask", "pandas", "numpy"},
    "Data Scientist": {"python", "r", "pandas", "numpy", "statistics", "tableau", "data analysis", "visualization", "sql", "matplotlib"},
    "Full Stack Developer": {"html", "css", "javascript", "react", "angular", "vue.js", "node.js", "java", "spring boot", "mongodb", "postgresql", "rest api", "graphql", "flask", "django"},
    "Frontend Developer": {"html", "css", "javascript", "react", "angular", "typescript", "tailwind", "bootstrap", "redux", "sass"},
    "Backend Developer": {"java", "spring boot", "node.js", "express", "flask", "django", "graphql", "mysql", "postgresql", "mongodb"},
    "DevOps Engineer": {"docker", "kubernetes", "ci/cd", "aws", "terraform", "ansible", "jenkins", "bash", "github actions"},
    "Cloud Engineer": {"aws", "azure", "gcp", "s3", "ec2", "lambda", "cloud functions", "firebase", "rds", "cloudwatch"},
    "QA/Test Engineer": {"selenium", "cypress", "postman", "junit", "testng", "jmeter", "pytest", "automation", "bug tracking", "jira"},
    "Cybersecurity Analyst": {"kali", "nmap", "burpsuite", "wireshark", "metasploit", "firewalls", "network security", "threat", "encryption"},
    "Mobile App Developer": {"flutter", "dart", "kotlin", "swift", "android", "ios", "react native", "firebase", "xcode"},
    "UI/UX Designer": {"figma", "xd", "sketch", "wireframes", "typography", "prototyping", "accessibility"},
    "Blockchain Developer": {"solidity", "web3", "ethereum", "nft", "smart contracts", "truffle", "metamask"},
    "Game Developer": {"unity", "c#", "unreal", "godot", "game physics", "multiplayer", "rendering", "level design"},
}


def clean_text(text_data):
    return re.sub(r'[^\w\s]', '', text_data.lower())

def extract_skills(text_data):
    words = set(clean_text(text_data).split()) - stop_words
    return words

def detect_role(resume_skills):
    best_role = "General IT Professional"
    max_matches = 0
    matched_role_skills = set()

    for role, skills in ROLE_SKILL_MAP.items():
        common_skills = resume_skills & skills
        if len(common_skills) > max_matches:
            max_matches = len(common_skills)
            best_role = role
            matched_role_skills = common_skills

    return best_role, matched_role_skills

def match_resume_to_job(resume_text, job_desc_text):
    resume_clean = clean_text(resume_text)
    job_clean = clean_text(job_desc_text)

    # Cosine Similarity Score
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform([resume_clean, job_clean])
    score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

    # Extract skills
    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_desc_text)

    matched_skills = sorted(list(resume_skills & job_skills))
    missing_skills = sorted(list(job_skills - resume_skills))

    # Predict best role based on skills
    predicted_role, role_matched_skills = detect_role(resume_skills)

    result = {
        "match_score": round(score * 100, 2),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "detected_role": predicted_role,
        "role_matched_skills": sorted(list(role_matched_skills)),
        "message": f"Resume best fits the role of {predicted_role}"
    }

    return result
