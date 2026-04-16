import json
import tempfile
import streamlit as st

from parser import load_resume, extract_skills
from matcher import calculate_rule_based_score, generate_recommendation
from semantic_matcher import compute_semantic_score
from llm_explainer import generate_llm_explanation
from parser import load_resume, extract_skills, parse_pasted_jobs


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


def get_recommendation_color(recommendation):
    if recommendation == "High match":
        return "🟢"
    if recommendation == "Medium match":
        return "🟡"
    return "🔴"


st.set_page_config(page_title="Career Match Analyzer", layout="wide")
st.title("Career Match Analyzer")
st.caption("Analyze how well a resume matches job postings using rule-based scoring, semantic similarity, and AI explanations.")

resume_file = st.file_uploader("Upload resume (.txt or .pdf)", type=["txt", "pdf"])

input_mode = st.radio(
    "Choose job input method",
    ["Upload jobs.json", "Paste job text"]
)

jobs = []

if input_mode == "Upload jobs.json":
    jobs_file = st.file_uploader("Upload jobs.json", type=["json"])
    if jobs_file:
        jobs = json.loads(jobs_file.getvalue().decode("utf-8"))
else:
    job_text = st.text_area("Paste job posting text (use ===JOB=== to separate multiple jobs)", height=200)
    if job_text:
        jobs = parse_pasted_jobs(job_text)

if resume_file and jobs:
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{resume_file.name.split('.')[-1]}") as tmp_resume:
        tmp_resume.write(resume_file.getvalue())
        resume_path = tmp_resume.name

    resume_text = load_resume(resume_path)
    resume_skills = extract_skills(resume_text)

    st.subheader("Detected skills")
    st.write(resume_skills)

    results = []

    for job in jobs:
        rule_result = calculate_rule_based_score(resume_skills, job)
        semantic_score = compute_semantic_score(resume_text, build_job_text(job))
        final_score = round((0.65 * rule_result["rule_score"]) + (0.35 * semantic_score), 2)

        result = {
            "job_id": job.get("id"),
            "title": job["title"],
            "company": job["company"],
            "rule_score": rule_result["rule_score"],
            "semantic_score": semantic_score,
            "final_score": final_score,
            "recommendation": generate_recommendation(final_score),
            "matched_required": rule_result["matched_required"],
            "matched_nice": rule_result["matched_nice"],
            "missing_required": rule_result["missing_required"],
            "missing_nice": rule_result["missing_nice"],
        }

        results.append((job, result))

    results.sort(key=lambda x: x[1]["final_score"], reverse=True)

    st.subheader("Ranked jobs")

    for job, result in results:
        icon = get_recommendation_color(result["recommendation"])

        with st.container():
            st.markdown(f"## {icon} {result['title']} — {result['company']}")
            st.progress(min(result["final_score"] / 100, 1.0))
            st.write(f"**Final Score:** {result['final_score']}")
            st.write(f"**Recommendation:** {result['recommendation']}")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Rule Score", result["rule_score"])

            with col2:
                st.metric("Semantic Score", result["semantic_score"])

            with col3:
                st.metric("Final Score", result["final_score"])

            st.markdown("### Match details")
            detail_col1, detail_col2 = st.columns(2)

            with detail_col1:
                st.write("**Matched required skills**")
                st.write(result["matched_required"] if result["matched_required"] else ["None"])

                st.write("**Matched nice-to-have skills**")
                st.write(result["matched_nice"] if result["matched_nice"] else ["None"])

            with detail_col2:
                st.write("**Missing required skills**")
                st.write(result["missing_required"] if result["missing_required"] else ["None"])

                st.write("**Missing nice-to-have skills**")
                st.write(result["missing_nice"] if result["missing_nice"] else ["None"])

            with st.expander("AI explanation"):
                explanation = generate_llm_explanation(job, result)
                st.write(explanation)

            st.divider()