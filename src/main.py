import json
from parser import load_resume, extract_skills
from matcher import calculate_rule_based_score, generate_recommendation
from semantic_matcher import compute_semantic_score


def load_jobs(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


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


def main():
    resume_path = "../data/sample_resume.txt"  # depois pode trocar para PDF
    jobs_path = "../data/jobs.json"

    resume_text = load_resume(resume_path)
    resume_skills = extract_skills(resume_text)
    jobs = load_jobs(jobs_path)

    results = []

    for job in jobs:
        rule_result = calculate_rule_based_score(resume_skills, job)
        semantic_score = compute_semantic_score(resume_text, build_job_text(job))
        final_score = round((0.65 * rule_result["rule_score"]) + (0.35 * semantic_score), 2)

        results.append({
            "job_id": job["id"],
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
        })

    results.sort(key=lambda x: x["final_score"], reverse=True)

    for result in results:
        print("=" * 60)
        print(f"Job: {result['title']} - {result['company']}")
        print(f"Rule Score: {result['rule_score']}")
        print(f"Semantic Score: {result['semantic_score']}")
        print(f"Final Score: {result['final_score']}")
        print(f"Recommendation: {result['recommendation']}")
        print(f"Matched Required: {result['matched_required']}")
        print(f"Matched Nice: {result['matched_nice']}")
        print(f"Missing Required: {result['missing_required']}")
        print(f"Missing Nice: {result['missing_nice']}")

    with open("../results/matches.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()