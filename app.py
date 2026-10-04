import streamlit as st
import pandas as pd
import re
from datetime import date
from urllib.parse import quote_plus

st.set_page_config(
    page_title="CareerPilot-X",
    page_icon="🚀",
    layout="wide"
)

# --------------------------- CAREER DATA ---------------------------

CAREERS = {
    "AI/ML Engineer": {
        "skills": [
            "python", "machine learning", "numpy", "pandas",
            "tensorflow", "nlp", "statistics"
        ],
        "roadmap": [
            "Python foundations", "NumPy and Pandas",
            "Statistics and probability", "Machine learning",
            "Deep learning", "NLP or computer vision",
            "Portfolio project"
        ],
        "description": "Build intelligent systems that learn from data."
    },
    "Data Scientist": {
        "skills": [
            "python", "pandas", "numpy", "statistics",
            "sql", "machine learning", "visualization"
        ],
        "roadmap": [
            "Python", "SQL", "Statistics", "Pandas and NumPy",
            "Data visualization", "Machine learning",
            "End-to-end project"
        ],
        "description": "Turn data into insights, predictions and decisions."
    },
    "Data Analyst": {
        "skills": [
            "excel", "sql", "python", "pandas",
            "statistics", "power bi", "visualization"
        ],
        "roadmap": [
            "Excel", "SQL", "Statistics", "Power BI or Tableau",
            "Python basics", "Dashboard project",
            "Business storytelling"
        ],
        "description": "Analyze information and communicate useful business insights."
    },
    "Software Developer": {
        "skills": [
            "python", "java", "dsa", "oops",
            "git", "testing", "sql"
        ],
        "roadmap": [
            "Choose Python or Java", "Object-oriented programming",
            "Data structures and algorithms", "Git and GitHub",
            "Databases", "Testing", "Build and deploy projects"
        ],
        "description": "Design, build, test and maintain software."
    },
    "Web Developer": {
        "skills": [
            "html", "css", "javascript", "react",
            "git", "api", "responsive design"
        ],
        "roadmap": [
            "HTML", "CSS and responsive design", "JavaScript",
            "Git and GitHub", "React", "APIs",
            "Deploy a portfolio website"
        ],
        "description": "Create interactive websites and web applications."
    },
    "Cybersecurity Analyst": {
        "skills": [
            "networking", "linux", "python", "security",
            "siem", "incident response", "ethical hacking"
        ],
        "roadmap": [
            "Networking basics", "Linux", "Security fundamentals",
            "Python scripting", "SIEM tools", "Incident response",
            "Practice in legal labs"
        ],
        "description": "Help protect systems, networks and information."
    },
    "Cloud Engineer": {
        "skills": [
            "linux", "aws", "docker", "networking",
            "python", "iam", "monitoring"
        ],
        "roadmap": [
            "Linux", "Networking", "Cloud fundamentals",
            "AWS or Azure", "IAM and security", "Docker",
            "Deploy and monitor a project"
        ],
        "description": "Build and operate reliable cloud infrastructure."
    },
    "DevOps Engineer": {
        "skills": [
            "linux", "docker", "git", "kubernetes",
            "aws", "ci/cd", "monitoring"
        ],
        "roadmap": [
            "Linux and scripting", "Git", "CI/CD",
            "Docker", "Cloud basics", "Kubernetes",
            "Monitoring and deployment project"
        ],
        "description": "Automate software delivery and infrastructure operations."
    },
    "Business Analyst": {
        "skills": [
            "excel", "sql", "statistics", "communication",
            "requirements", "visualization", "problem solving"
        ],
        "roadmap": [
            "Business communication", "Excel",
            "Requirements gathering", "SQL", "Process mapping",
            "Dashboards", "Case-study portfolio"
        ],
        "description": "Connect business needs with data, processes and solutions."
    },
    "UI/UX Designer": {
        "skills": [
            "figma", "wireframing", "prototyping",
            "user research", "visual design",
            "accessibility", "communication"
        ],
        "roadmap": [
            "Design principles", "Figma", "User research",
            "Wireframes", "Prototyping", "Accessibility",
            "Case-study portfolio"
        ],
        "description": "Design useful, accessible and intuitive digital experiences."
    }
}

INTERVIEW_QUESTIONS = {
    "General": [
        (
            "Tell me about yourself.",
            ["introduction", "education", "skills", "project", "goal"]
        ),
        (
            "Describe a challenge you faced and how you handled it.",
            ["challenge", "action", "result", "learned"]
        ),
        (
            "Why are you interested in this role?",
            ["role", "skills", "interest", "contribute", "learn"]
        ),
        (
            "Tell me about a project you are proud of.",
            ["project", "problem", "approach", "tools", "result"]
        )
    ],
    "Technical": [
        (
            "Explain a technical concept you know well.",
            ["concept", "how", "example", "use", "tradeoff"]
        ),
        (
            "How do you debug a problem in your code?",
            ["reproduce", "isolate", "logs", "test", "fix"]
        ),
        (
            "How do you make sure your work is reliable?",
            ["test", "review", "edge", "document", "monitor"]
        ),
        (
            "Describe a technical decision you made on a project.",
            ["requirement", "options", "choose", "reason", "result"]
        )
    ]
}

# --------------------------- HELPER FUNCTIONS ---------------------------

def normalize_skills(raw):
    """Convert comma, semicolon or newline separated skills to lowercase."""
    return sorted(set(
        skill.strip().lower()
        for skill in re.split(r"[,;\n]", raw or "")
        if skill.strip()
    ))


def skill_score(user_skills, required):
    """Calculate the percentage of required skills already known."""
    if not required:
        return 0

    user = set(user_skills)
    matched = sum(1 for skill in required if skill.lower() in user)

    return round(100 * matched / len(required))


def missing_skills(user_skills, required):
    """Return required skills not present in the user's profile."""
    user = set(user_skills)
    return [skill for skill in required if skill.lower() not in user]


def career_results(user_skills):
    """Create a career-match table for all listed careers."""
    rows = []

    for name, data in CAREERS.items():
        required = data["skills"]
        matched = [
            skill for skill in required
            if skill.lower() in set(user_skills)
        ]

        rows.append({
            "Career": name,
            "Match": skill_score(user_skills, required),
            "Matched skills": ", ".join(matched) if matched else "—",
            "Skills to build": ", ".join(
                missing_skills(user_skills, required)
            )
        })

    return (
        pd.DataFrame(rows)
        .sort_values("Match", ascending=False)
        .reset_index(drop=True)
    )


def safe_text_extract(upload):
    """Extract text from TXT, Markdown, PDF or DOCX resume files."""
    if upload is None:
        return ""

    name = upload.name.lower()

    if
