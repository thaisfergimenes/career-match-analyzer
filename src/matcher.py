def calculate_match_score(resume_skills, job):
    required = job["required_skills"]
    nice_to_have = job.get("nice_to_have", [])

    # Contagem de matches
    matched_required = [skill for skill in required if skill in resume_skills]
    matched_nice = [skill for skill in nice_to_have if skill in resume_skills]

    missing_required = [skill for skill in required if skill not in resume_skills]
    missing_nice = [skill for skill in nice_to_have if skill not in resume_skills]

    # Cálculo de score
    required_score = len(matched_required) / len(required) if required else 0
    nice_score = len(matched_nice) / len(nice_to_have) if nice_to_have else 0

    final_score = (0.7 * required_score + 0.3 * nice_score) * 100

    return {
        "job_id": job["id"],
        "title": job["title"],
        "company": job["company"],
        "match_score": round(final_score, 2),
        "matched_skills": matched_required + matched_nice,
        "missing_skills": missing_required + missing_nice
    }


def generate_recommendation(score):
    if score >= 80:
        return "High match"
    elif score >= 60:
        return "Medium match"
    else:
        return "Low match"