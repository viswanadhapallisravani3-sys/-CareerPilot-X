
import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="CareerPilot-X",
    page_icon="🚀",
    layout="wide"
)

# Career skills database
careers = {
    "AI/ML Engineer": [
        "python", "machine learning", "numpy",
        "pandas", "tensorflow", "nlp"
    ],
    "Data Scientist": [
        "python", "pandas", "numpy",
        "statistics", "machine learning"
    ],
    "Data Analyst": [
        "python", "pandas", "excel",
        "sql", "statistics"
    ],
    "Software Developer": [
        "python", "java", "dsa", "oops", "git"
    ],
    "Web Developer": [
        "html", "css", "javascript", "react", "git"
    ],
    "Cybersecurity Analyst": [
        "networking", "linux", "python",
        "security", "ethical hacking"
    ],
    "Cloud Engineer": [
        "linux", "aws", "docker",
        "networking", "python"
    ],
    "DevOps Engineer": [
        "linux", "docker", "git",
        "kubernetes", "aws"
    ],
    "Business Analyst": [
        "excel", "sql", "statistics", "communication"
    ]
}

# Career learning roadmaps
roadmap = {
    "AI/ML Engineer":
        "Python → NumPy → Pandas → Machine Learning → NLP → Deep Learning",
    "Data Scientist":
        "Python → Pandas → Statistics → SQL → Machine Learning",
    "Data Analyst":
        "Excel → SQL → Python → Pandas → Power BI",
    "Software Developer":
        "Python/Java → OOP → DSA → Git → Projects",
    "Web Developer":
        "HTML → CSS → JavaScript → React → Projects",
    "Cybersecurity Analyst":
        "Networking → Linux → Python → Security → Ethical Hacking",
    "Cloud Engineer":
        "Linux → Networking → AWS → Docker → Projects",
    "DevOps Engineer":
        "Linux → Git → Docker → Kubernetes → AWS",
    "Business Analyst":
        "Excel → SQL → Statistics → Communication"
}

# Helper functions
def clean(text):
    return list(dict.fromkeys(
        item.strip().lower()
        for item in text.split(",")
        if item.strip()
    ))

def match(skills, required):
    if not required:
        return 0.0
    return round(
        len(set(skills) & set(required)) / len(required) * 100,
        1
    )

def gaps(skills, required):
    return [skill for skill in required if skill not in skills]

# Website header
st.title("🚀 CareerPilot-X")
st.subheader("AI-Powered Career Guidance Assistant")
st.write(
    "Discover suitable career paths, identify skill gaps, "
    "and plan your future career."
)

st.divider()

# Sidebar profile
st.sidebar.title("👤 Your Profile")
name = st.sidebar.text_input("Your Name", "Student")
education = st.sidebar.text_input("Education", "BTech CSE-AIML")
skills_text = st.sidebar.text_area(
    "Your Skills (comma-separated)",
    "python, java, pandas"
)
skills = clean(skills_text)

st.sidebar.caption(
    "Enter your current skills separated by commas."
)

# Career match
st.header("🎯 Career Match")
st.write("Explore how your current skills match different careers.")

results = []
for career, required in careers.items():
    results.append({
        "Career": career,
        "Match (%)": match(skills, required)
    })

df = pd.DataFrame(results)
df = df.sort_values("Match (%)", ascending=False).reset_index(drop=True)

st.dataframe(
    df,
    hide_index=True,
    use_container_width=True
)

best_career = df.iloc[0]["Career"]
best_score = df.iloc[0]["Match (%)"]

st.success(
    f"⭐ Best Match for {name}: {best_career} ({best_score}%)"
)

st.divider()

# Career selection
st.header("🧭 Explore a Career")
selected = st.selectbox(
    "Choose a career to explore",
    list(careers.keys())
)
required = careers[selected]
current_score = match(skills, required)

st.metric("Current Career Match", f"{current_score}%")

# Skill gap analysis
st.header("🧠 Skill Gap Analysis")
st.write(f"Skills required for **{selected}**:")

st.write(", ".join(required))

missing = gaps(skills, required)

if missing:
    st.warning("📌 Skills you need to learn:")
    for skill in missing:
        st.write(f"- {skill}")
else:
    st.success("🎉 You have all the listed skills for this career!")

st.divider()

# What-if career lab
st.header("🔮 What-If Career Lab")
st.write(
    "Add skills you plan to learn and see how your "
    "career match could improve."
)

new_skills_text = st.text_input(
    "Skills you plan to learn (comma-separated)",
    "machine learning, numpy, nlp",
    key="future_skills"
)

new_skills = clean(new_skills_text)
future_skills = list(set(skills + new_skills))
future_score = match(future_skills, required)
improvement = round(future_score - current_score, 1)

col1, col2, col3 = st.columns(3)
col1.metric("Current Match", f"{current_score}%")
col2.metric("Future Match", f"{future_score}%")
col3.metric("Improvement", f"{improvement:+.1f}%")

st.subheader("📈 Match Improvement")

chart = pd.DataFrame({
    "Stage": ["Current", "After Learning"],
    "Match": [current_score, future_score]
})
st.bar_chart(chart.set_index("Stage"))

remaining = gaps(future_skills, required)
st.subheader("🎯 Remaining Skill Gaps")

if remaining:
    st.write(", ".join(remaining))
else:
    st.success("🎉 You have covered all the required skills!")

st.divider()

# Learning roadmap
st.header("🗺️ Learning Roadmap")
st.write(f"Suggested learning path for **{selected}**:")

st.info(roadmap[selected])

st.caption(
    "CareerPilot-X | AI Career Guidance Assistant 🚀"
)
