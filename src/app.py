import json
import tempfile
import streamlit as st

from parser import load_resume, extract_skills
from matcher import calculate_rule_based_score, generate_recommendation
from semantic_matcher import compute_semantic_score


def build_job_text(job):
    required = ", ".join(job.get("required_skills", []))
    nice = ", ".join(job.get("nice_to_have", []))
    return (
        f"Title: {job['title']}\n"
        f"Company: {job['company']}\n"
        f"Description: {job['description']}\n"
        f"Required skills: {required}\n"
        f"Nice to have: {nice}"
    )


st.set_page_config(page_title="Career Match Analyzer", layout="wide")
st.title("Career Match Analyzer")

resume_file = st.file_uploader("Upload resume (.txt or .pdf)", type=["txt", "pdf"])
jobs_file = st.file_uploader("Upload jobs.json", type=["json"])

if resume_file and jobs_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{resume_file.name.split('.')[-1]}") as tmp_resume:
        tmp_resume.write(resume_file.getvalue())
        resume_path = tmp_resume.name

    jobs = json.loads(jobs_file.getvalue().decode("utf-8"))
    resume_text = load_resume(resume_path)
    resume_skills = extract_skills(resume_text)

    st.subheader("Detected skills")
    st.write(resume_skills)

    results = []
    for job in jobs:
        rule_result = calculate_rule_based_score(resume_skills, job)
        semantic_score = compute_semantic_score(resume_text, build_job_text(job))
        final_score = round((0.65 * rule_result["rule_score"]) + (0.35 * semantic_score), 2)

        results.append({
            "title": job["title"],
            "company": job["company"],
            "final_score": final_score,
            "rule_score": rule_result["rule_score"],
            "semantic_score": semantic_score,
            "recommendation": generate_recommendation(final_score),
            "matched_required": rule_result["matched_required"],
            "missing_required": rule_result["missing_required"],
            "matched_nice": rule_result["matched_nice"],
            "missing_nice": rule_result["missing_nice"],
        })

    results.sort(key=lambda x: x["final_score"], reverse=True)

    st.subheader("Ranked jobs")
    for result in results:
        with st.container():
            st.markdown(f"### {result['title']} — {result['company']}")
            st.write(f"**Final Score:** {result['final_score']}")
            st.write(f"**Recommendation:** {result['recommendation']}")
            st.write(f"**Rule Score:** {result['rule_score']}")
            st.write(f"**Semantic Score:** {result['semantic_score']}")
            st.write(f"**Matched Required:** {result['matched_required']}")
            st.write(f"**Missing Required:** {result['missing_required']}")
            st.write(f"**Matched Nice:** {result['matched_nice']}")
            st.write(f"**Missing Nice:** {result['missing_nice']}")
            st.divider()