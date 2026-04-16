def calculate_rule_based_score(resume_skills, job):
    required = job["required_skills"]
    nice_to_have = job.get("nice_to_have", [])

    matched_required = [skill for skill in required if skill in resume_skills]
    matched_nice = [skill for skill in nice_to_have if skill in resume_skills]

    missing_required = [skill for skill in required if skill not in resume_skills]
    missing_nice = [skill for skill in nice_to_have if skill not in resume_skills]

    required_score = len(matched_required) / len(required) if required else 0
    nice_score = len(matched_nice) / len(nice_to_have) if nice_to_have else 0

    final_score = (0.8 * required_score + 0.2 * nice_score) * 100

    return {
        "rule_score": round(final_score, 2),
        "matched_required": matched_required,
        "matched_nice": matched_nice,
        "missing_required": missing_required,
        "missing_nice": missing_nice,
    }


def generate_recommendation(score: float) -> str:
    if score >= 80:
        return "High match"
    if score >= 60:
        return "Medium match"
    return "Low match"