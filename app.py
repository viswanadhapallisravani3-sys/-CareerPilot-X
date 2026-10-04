import re
from datetime import date
from urllib.parse import quote_plus

import pandas as pd
import streamlit as st

st.set_page_config(page_title="CareerPilot-X", page_icon="🚀", layout="wide")

CAREERS = {
    "AI/ML Engineer": {
        "skills": ["python", "machine learning", "numpy", "pandas", "tensorflow", "nlp", "statistics"],
        "roadmap": ["Python foundations", "NumPy and Pandas", "Statistics and probability", "Machine learning", "Deep learning", "NLP or computer vision", "Portfolio project"],
        "description": "Build intelligent systems that learn from data.",
    },
    "Data Scientist": {
        "skills": ["python", "pandas", "numpy", "statistics", "sql", "machine learning", "visualization"],
        "roadmap": ["Python", "SQL", "Statistics", "Pandas and NumPy", "Data visualization", "Machine learning", "End-to-end project"],
        "description": "Turn data into insights, predictions and decisions.",
    },
    "Data Analyst": {
        "skills": ["excel", "sql", "python", "pandas", "statistics", "power bi", "visualization"],
        "roadmap": ["Excel", "SQL", "Statistics", "Power BI or Tableau", "Python basics", "Dashboard project", "Business storytelling"],
        "description": "Analyze information and communicate useful business insights.",
    },
    "Software Developer": {
        "skills": ["python", "java", "dsa", "oops", "git", "testing", "sql"],
        "roadmap": ["Choose Python or Java", "Object-oriented programming", "Data structures and algorithms", "Git and GitHub", "Databases", "Testing", "Build and deploy projects"],
        "description": "Design, build, test and maintain software.",
    },
    "Web Developer": {
        "skills": ["html", "css", "javascript", "react", "git", "api", "responsive design"],
        "roadmap": ["HTML", "CSS and responsive design", "JavaScript", "Git and GitHub", "React", "APIs", "Deploy a portfolio website"],
        "description": "Create interactive websites and web applications.",
    },
    "Cybersecurity Analyst": {
        "skills": ["networking", "linux", "python", "security", "siem", "incident response", "ethical hacking"],
        "roadmap": ["Networking basics", "Linux", "Security fundamentals", "Python scripting", "SIEM tools", "Incident response", "Practice in legal labs"],
        "description": "Help protect systems, networks and information.",
    },
    "Cloud Engineer": {
        "skills": ["linux", "aws", "docker", "networking", "python", "iam", "monitoring"],
        "roadmap": ["Linux", "Networking", "Cloud fundamentals", "AWS or Azure", "IAM and security", "Docker", "Deploy and monitor a project"],
        "description": "Build and operate reliable cloud infrastructure.",
    },
    "DevOps Engineer": {
        "skills": ["linux", "docker", "git", "kubernetes", "aws", "ci/cd", "monitoring"],
        "roadmap": ["Linux and scripting", "Git", "CI/CD", "Docker", "Cloud basics", "Kubernetes", "Monitoring and deployment project"],
        "description": "Automate software delivery and infrastructure operations.",
    },
    "Business Analyst": {
        "skills": ["excel", "sql", "statistics", "communication", "requirements", "visualization", "problem solving"],
        "roadmap": ["Business communication", "Excel", "Requirements gathering", "SQL", "Process mapping", "Dashboards", "Case-study portfolio"],
        "description": "Connect business needs with data, processes and solutions.",
    },
    "UI/UX Designer": {
        "skills": ["figma", "wireframing", "prototyping", "user research", "visual design", "accessibility", "communication"],
        "roadmap": ["Design principles", "Figma", "User research", "Wireframes", "Prototyping", "Accessibility", "Case-study portfolio"],
        "description": "Design useful, accessible and intuitive digital experiences.",
    },
}

INTERVIEW_QUESTIONS = {
    "General": [
        ("Tell me about yourself.", ["introduction", "education", "skills", "project", "goal"]),
        ("Describe a challenge you faced and how you handled it.", ["challenge", "action", "result", "learned"]),
        ("Why are you interested in this role?", ["role", "skills", "interest", "contribute", "learn"]),
        ("Tell me about a project you are proud of.", ["project", "problem", "approach", "tools", "result"]),
    ],
    "Technical": [
        ("Explain a technical concept you know well.", ["concept", "how", "example", "use", "tradeoff"]),
        ("How do you debug a problem in your code?", ["reproduce", "isolate", "logs", "test", "fix"]),
        ("How do you make sure your work is reliable?", ["test", "review", "edge", "document", "monitor"]),
        ("Describe a technical decision you made on a project.", ["requirement", "options", "choose", "reason", "result"]),
    ],
}

def normalize_skills(raw):
    return sorted(set(s.strip().lower() for s in re.split(r"[,;\n]", raw or "") if s.strip()))

def skill_score(user_skills, required):
    user = set(user_skills)
    return round(100 * sum(skill.lower() in user for skill in required) / len(required)) if required else 0

def missing_skills(user_skills, required):
    user = set(user_skills)
    return [skill for skill in required if skill.lower() not in user]

def career_results(user_skills):
    rows = []
    user = set(user_skills)
    for name, data in CAREERS.items():
        req = data["skills"]
        matched = [skill for skill in req if skill.lower() in user]
        rows.append({
            "Career": name,
            "Match (%)": skill_score(user_skills, req),
            "Matched skills": ", ".join(matched) if matched else "—",
            "Skills to build": ", ".join(missing_skills(user_skills, req)) or "None",
        })
    return pd.DataFrame(rows).sort_values("Match (%)", ascending=False).reset_index(drop=True)

def feedback_for_answer(answer, keywords):
    words = re.findall(r"\b[\w+#.-]+\b", (answer or "").lower())
    found = [k for k in keywords if k.lower() in (answer or "").lower()]
    missing = [k for k in keywords if k not in found]
    length_score = min(40, round(len(words) / 2))
    coverage_score = round(60 * len(found) / len(keywords)) if keywords else 0
    score = min(100, length_score + coverage_score)
    if len(words) < 25:
        note = "Try adding more context, specific actions and a clear outcome."
    elif missing:
        note = "Good start. Add a concrete example and address the missing prompts where relevant."
    else:
        note = "Your answer covers the suggested prompts. Practice making it concise and specific."
    return score, found, missing, note

def safe_text_extract(upload):
    if upload is None:
        return ""
    name = upload.name.lower()
    try:
        if name.endswith((".txt", ".md")):
            return upload.getvalue().decode("utf-8", errors="ignore")
        if name.endswith(".pdf"):
            from pypdf import PdfReader
            reader = PdfReader(upload)
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        if name.endswith(".docx"):
            from docx import Document
            doc = Document(upload)
            return "\n".join(p.text for p in doc.paragraphs)
    except Exception as exc:
        st.error(f"Could not read the file: {exc}")
    return ""

# Session state
defaults = {
    "skills_text": "",
    "interview_answers": {},
    "applications": [],
    "roadmap_done": {},
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

PAGES = [
    "🏠 Dashboard", "🎯 Career Match", "🧩 Skill Gap Analysis",
    "🧪 What-If Career Lab", "📄 Resume Analyzer", "🔎 Live Job Search",
    "🪞 Career Digital Twin", "🎤 Interview Simulator",
    "⚖️ Compare Opportunities", "📋 Application Tracker", "🗺️ Learning Roadmap",
]
st.sidebar.title("🚀 CareerPilot-X")
page = st.sidebar.radio("Navigate", PAGES)
st.sidebar.markdown("---")
st.sidebar.caption("Build skills. Explore paths. Move forward.")

def skill_input():
    st.text_area(
        "Enter your skills (separate with commas)",
        key="skills_text",
        placeholder="Python, SQL, Excel, communication",
        height=100,
    )
    return normalize_skills(st.session_state.skills_text)

user_skills = normalize_skills(st.session_state.skills_text)

if page == "🏠 Dashboard":
    st.title("🚀 CareerPilot-X")
    st.subheader("Your practical career exploration workspace")
    st.write("Explore career paths, identify skill gaps, practice interviews and organize applications.")
    c1, c2, c3 = st.columns(3)
    c1.metric("Career paths", len(CAREERS))
    c2.metric("Skills entered", len(user_skills))
    c3.metric("Tools", len(PAGES))
    st.markdown("### Get started")
    st.write("1. Add your skills in Career Match.  2. Review your skill gaps.  3. Choose a learning roadmap and track applications.")
    st.info("Career matches and feedback are simple keyword-based indicators, not professional hiring assessments.")

elif page == "🎯 Career Match":
    st.title("🎯 Career Match")
    st.write("Enter skills you already know to see which career profiles overlap.")
    user_skills = skill_input()
    if user_skills:
        results = career_results(user_skills)
        st.dataframe(results, hide_index=True, use_container_width=True)
        best = results.iloc[0]
        st.success(f"Top keyword match: {best['Career']} ({best['Match (%)']}%).")
    else:
        st.info("Add a few skills to calculate your career matches.")

elif page == "🧩 Skill Gap Analysis":
    st.title("🧩 Skill Gap Analysis")
    career = st.selectbox("Choose a target career", list(CAREERS.keys()))
    user_skills = skill_input()
    required = CAREERS[career]["skills"]
    score = skill_score(user_skills, required)
    st.progress(score / 100, text=f"Current skill coverage: {score}%")
    missing = missing_skills(user_skills, required)
    st.markdown("**Skills already covered:** " + (", ".join(s for s in required if s in set(user_skills)) or "None entered"))
    st.markdown("**Skills to develop:** " + (", ".join(missing) or "No gaps detected in this starter profile"))
    st.caption("This is a starter skill profile. Actual job requirements vary by employer.")

elif page == "🧪 What-If Career Lab":
    st.title("🧪 What-If Career Lab")
    st.write("Add skills you plan to learn and see how the keyword match changes.")
    career = st.selectbox("Target career", list(CAREERS.keys()))
    user_skills = skill_input()
    planned_text = st.text_input("Skills you may learn", placeholder="TensorFlow, NLP")
    planned = normalize_skills(planned_text)
    before = skill_score(user_skills, CAREERS[career]["skills"])
    after = skill_score(user_skills + planned, CAREERS[career]["skills"])
    a, b, c = st.columns(3)
    a.metric("Current match", f"{before}%")
    b.metric("With planned skills", f"{after}%")
    c.metric("Potential change", f"+{after-before}%")
    st.write("Still to learn:", ", ".join(missing_skills(user_skills + planned, CAREERS[career]["skills"])) or "No listed gaps")

elif page == "📄 Resume Analyzer":
    st.title("📄 Resume Analyzer")
    st.write("Upload a resume to compare extracted text with a selected career's starter skills.")
    career = st.selectbox("Target career", list(CAREERS.keys()))
    upload = st.file_uploader("Upload TXT, Markdown, PDF or DOCX", type=["txt", "md", "pdf", "docx"])
    pasted = st.text_area("Or paste resume text here", height=180)
    resume_text = safe_text_extract(upload) if upload else pasted
    if st.button("Analyze resume", type="primary"):
        if not resume_text.strip():
            st.warning("Upload a supported file or paste resume text first.")
        else:
            lower = resume_text.lower()
            required = CAREERS[career]["skills"]
            found = [s for s in required if s.lower() in lower]
            missing = [s for s in required if s.lower() not in lower]
            st.metric("Keyword coverage", f"{skill_score(found, required)}%")
            st.write("**Detected skills:**", ", ".join(found) or "No listed skills detected")
            st.write("**Potential skills to highlight or develop:**", ", ".join(missing) or "None")
            st.caption("This checks keyword presence only; it does not judge resume quality or verify experience.")

elif page == "🔎 Live Job Search":
    st.title("🔎 Live Job Search")
    st.write("Open external job-search results for a role and location.")
    role = st.text_input("Job title", value="Data Analyst")
    location = st.text_input("Location", value="India")
    if role.strip() and location.strip():
        query = quote_plus(f"{role.strip()} jobs in {location.strip()}")
        st.markdown(f"- [Search Google Jobs](https://www.google.com/search?ibp=htl;jobs&q={query})")
        st.markdown(f"- [Search LinkedIn Jobs](https://www.linkedin.com/jobs/search/?keywords={quote_plus(role.strip())}&location={quote_plus(location.strip())})")
    st.caption("These links open external search pages. Job listings are not fetched or verified inside this app.")

elif page == "🪞 Career Digital Twin":
    st.title("🪞 Career Digital Twin")
    st.write("Create a simple profile snapshot from your skills and target role.")
    user_skills = skill_input()
    target = st.selectbox("Target career", list(CAREERS.keys()))
    st.markdown("### Your profile")
    st.write("**Target:**", target)
    st.write("**Current skills:**", ", ".join(user_skills) or "Not entered")
    st.metric("Keyword match", f"{skill_score(user_skills, CAREERS[target]['skills'])}%")
    st.write("**Career overview:**", CAREERS[target]["description"])
    st.caption("This is a rule-based profile snapshot, not a predictive AI model.")

elif page == "🎤 Interview Simulator":
    st.title("🎤 Interview Simulator")
    st.write("Practice answering questions and get structured, keyword-based feedback.")
    kind = st.radio("Interview type", ["General", "Technical"], horizontal=True)
    questions = INTERVIEW_QUESTIONS[kind]
    idx = st.selectbox("Question", list(range(len(questions))), format_func=lambda i: f"Question {i+1}")
    question, keywords = questions[idx]
    st.markdown(f"### {question}")
    answer_key = f"{kind}_{idx}"
    answer = st.text_area("Your answer", value=st.session_state.interview_answers.get(answer_key, ""), height=180)
    if st.button("Evaluate answer", type="primary"):
        st.session_state.interview_answers[answer_key] = answer
        score, found, missing, note = feedback_for_answer(answer, keywords)
        st.subheader("Practice feedback")
        st.metric("Answer structure indicator", f"{score}/100")
        st.write("**Relevant points detected:**", ", ".join(found) if found else "Add details directly related to the question.")
        st.write("**Consider covering:**", ", ".join(missing) if missing else "You touched on the key prompts.")
        st.write(note)
        st.caption("Feedback is based on keyword coverage and answer length; it does not assess factual correctness.")
    st.caption("Tip: Use Situation–Task–Action–Result for behavioral examples.")

elif page == "⚖️ Compare Opportunities":
    st.title("⚖️ Compare Opportunities")
    st.write("Compare up to three career paths using their starter skill profiles.")
    choices = st.multiselect("Select careers", list(CAREERS.keys()), default=["AI/ML Engineer", "Data Scientist"], max_selections=3)
    if choices:
        compare = []
        for career in choices:
            req = CAREERS[career]["skills"]
            compare.append({
                "Career": career,
                "Your match": f"{skill_score(user_skills, req)}%",
                "Skills required": len(req),
                "Skills you cover": len([s for s in req if s in set(user_skills)]),
                "Description": CAREERS[career]["description"],
            })
        st.dataframe(pd.DataFrame(compare), hide_index=True, use_container_width=True)
        st.bar_chart(pd.DataFrame({c: [skill_score(user_skills, CAREERS[c]["skills"])] for c in choices}, index=["Match (%)"]))
    else:
        st.info("Choose one or more careers to compare.")
    st.caption("Consider your interests, work environment and real job requirements alongside this comparison.")

elif page == "📋 Application Tracker":
    st.title("📋 Application Tracker")
    st.write("Track applications during this session. Entries may reset when the app restarts.")
    with st.form("application_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        company = col1.text_input("Company")
        role = col2.text_input("Role")
        col3, col4 = st.columns(2)
        applied_on = col3.date_input("Application date", value=date.today())
        status = col4.selectbox("Status", ["Interested", "Applied", "Assessment", "Interview", "Offer", "Rejected"])
        link = st.text_input("Job URL (optional)")
        notes = st.text_area("Notes (optional)")
        submitted = st.form_submit_button("Add application", type="primary")
        if submitted:
            if not company.strip() or not role.strip():
                st.error("Please enter both company and role.")
            else:
                st.session_state.applications.append({
                    "Company": company.strip(), "Role": role.strip(),
                    "Date": applied_on.isoformat(), "Status": status,
                    "URL": link.strip(), "Notes": notes.strip(),
                })
                st.success("Application added.")
    if st.session_state.applications:
        app_df = pd.DataFrame(st.session_state.applications)
        st.dataframe(app_df, hide_index=True, use_container_width=True)
        st.download_button("Download tracker CSV", app_df.to_csv(index=False).encode("utf-8"), "careerpilot_applications.csv", "text/csv")
        if st.button("Clear all applications"):
            st.session_state.applications = []
            st.rerun()
    else:
        st.info("No applications yet. Add one using the form above.")

elif page == "🗺️ Learning Roadmap":
    st.title("🗺️ Learning Roadmap")
    st.write("Choose a target career and track the learning milestones you complete.")
    career = st.selectbox("Target career", list(CAREERS.keys()))
    steps = CAREERS[career]["roadmap"]
    key = f"roadmap_{career}"
    if key not in st.session_state.roadmap_done:
        st.session_state.roadmap_done[key] = []
    done = st.session_state.roadmap_done[key]
    st.progress(len(done) / len(steps), text=f"{len(done)} of {len(steps)} milestones completed")
    updated = []
    for i, step in enumerate(steps):
        if st.checkbox(step, value=i in done, key=f"{key}_{i}"):
            updated.append(i)
    st.session_state.roadmap_done[key] = updated
    st.markdown("#### Suggested sequence")
    for i, step in enumerate(steps, start=1):
        st.write(f"{i}. {step}")
    st.caption("Progress is stored for the active session. Save or export it externally for a durable record.")
