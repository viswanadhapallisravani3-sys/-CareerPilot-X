# --------------------------- INTERVIEW ---------------------------
elif page == "🎤 Interview Simulator":
    st.title("🎤 Interview Simulator")
    st.write("Practice answering questions and get structured, keyword-based feedback.")
    kind = st.radio("Interview type", ["General", "Technical"], horizontal=True)
    questions = INTERVIEW_QUESTIONS[kind]
    idx = st.selectbox("Question", list(range(len(questions))), format_func=lambda i: f"Question {i+1}")
    question, keywords = questions[idx]
    st.markdown(f"### {question}")
    answer = st.text_area("Your answer", value=st.session_state.interview_answers.get(f"{kind}_{idx}", ""), height=180)
    if st.button("Evaluate answer", type="primary"):
        st.session_state.interview_answers[f"{kind}_{idx}"] = answer
        score, found, missing = feedback_for_answer(answer, keywords)[:3]
        st.subheader("Practice feedback")
        st.metric("Answer structure indicator", f"{score}/100")
        st.write("**Relevant points detected:**", ", ".join(found) if found else "Add details directly related to the question.")
        st.write("**Consider covering:**", ", ".join(missing) if missing else "You touched on the key prompts.")
        st.write(feedback_for_answer(answer, keywords)[3])
        st.caption("Automated feedback is based on keyword coverage and answer length; it is not an assessment of factual correctness.")
    st.caption("Tip: Use a Situation–Task–Action–Result structure for behavioral examples.")

# --------------------------- COMPARE ---------------------------
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
                "Description": CAREERS[career]["description"]
            })
        st.dataframe(pd.DataFrame(compare), hide_index=True, use_container_width=True)
        st.bar_chart(pd.DataFrame({c: [skill_score(user_skills, CAREERS[c]["skills"])] for c in choices}, index=["Match (%)"]))
        st.caption("Consider interest, work environment and actual job requirements alongside this skills comparison.")
    else:
        st.info("Choose one or more careers to compare.")

# --------------------------- TRACKER ---------------------------
elif page == "📋 Application Tracker":
    st.title("📋 Application Tracker")
    st.write("Track applications during this session. Entries are stored in session memory and may reset when the app restarts.")
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
                    "URL": link.strip(), "Notes": notes.strip()
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

# --------------------------- ROADMAP ---------------------------
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
    st.caption("Milestone tracking is stored for this active session. Export or save progress externally if you need a durable record.")

st.sidebar.markdown("---")
st.sidebar.caption("CareerPilot-X • Build skills. Explore paths. Move forward.")
