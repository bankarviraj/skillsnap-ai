import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction import text

stop_words = set(text.ENGLISH_STOP_WORDS)

# ✅ Normalize all roles and skills to lowercase
ROLE_SKILL_MAP = {
    role: {skill.lower() for skill in skills}
    for role, skills in {
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
    }.items()
}


def clean_text(text_data):
    return re.sub(r'[^\w\s]', '', text_data.lower())


def extract_skills(text_data):
    return set(clean_text(text_data).split()) - stop_words


def match_resume_to_job(resume_text):
    print("📄 Matching started...")

    resume_text = resume_text.lower()
    resume_skills = extract_skills(resume_text)

    print("🔍 Extracted Skills from Resume:", resume_skills)

    if not resume_skills:
        return {
            "match_score": 0,
            "job_title": "No Skills Detected",
            "matched_skills": [],
            "missing_skills": [],
            "linkedin_jobs": [],
            "suggestions": ["Try uploading a better formatted resume."]
        }

    best_role = None
    best_score = 0
    matched_skills = set()
    missing_skills = set()

    for role, skills_required in ROLE_SKILL_MAP.items():
        common = resume_skills & skills_required
        if not common:
            continue

        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform([
            ' '.join(resume_skills),
            ' '.join(skills_required)
        ])
        score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

        print(f"🧠 Checking Role: {role} | Matched: {common} | Score: {round(score * 100, 2)}%")

        if score > best_score:
            best_score = score
            best_role = role
            matched_skills = common
            missing_skills = skills_required - resume_skills

    if best_score < 0.25 or not best_role:
        return {
            "match_score": 0,
            "job_title": "No Strong IT Role Match",
            "matched_skills": [],
            "missing_skills": [],
            "linkedin_jobs": [],
            "suggestions": ["Your resume doesn't strongly match any IT job role."]
        }

    return {
        "match_score": round(best_score * 100, 2),
        "job_title": best_role,
        "matched_skills": sorted(matched_skills),
        "missing_skills": sorted(missing_skills),
        "linkedin_jobs": [
            f"https://www.linkedin.com/jobs/search/?keywords={best_role.replace(' ', '%20')}",
            f"https://www.naukri.com/{best_role.replace(' ', '-').lower()}-jobs"
        ],
        "suggestions": [f"Learn: {', '.join(sorted(missing_skills)[:5])}"] if missing_skills else []
    }
