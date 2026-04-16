import json
from matcher import calculate_match_score, generate_recommendation

# Lista de skills conhecidas
SKILL_LIBRARY = [
    "Python", "SQL", "AWS", "ETL", "PostgreSQL", "MySQL",
    "Docker", "Java", "Pandas", "Airflow", "Spark",
    "REST API", "Machine Learning", "TensorFlow"
]


def load_resume(path):
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


def load_jobs(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def extract_skills(resume_text, skill_library):
    resume_text_lower = resume_text.lower()
    found_skills = []

    for skill in skill_library:
        if skill.lower() in resume_text_lower:
            found_skills.append(skill)

    return found_skills


def main():
    resume_path = "data/sample_resume.txt"
    jobs_path = "data/jobs.json"

    resume_text = load_resume(resume_path)
    jobs = load_jobs(jobs_path)

    resume_skills = extract_skills(resume_text, SKILL_LIBRARY)

    results = []

    for job in jobs:
        match = calculate_match_score(resume_skills, job)
        match["recommendation"] = generate_recommendation(match["match_score"])
        results.append(match)

    # Ordenar por score
    results = sorted(results, key=lambda x: x["match_score"], reverse=True)

    # Print bonito
    for result in results:
        print("=" * 50)
        print(f"Job: {result['title']} - {result['company']}")
        print(f"Score: {result['match_score']}")
        print(f"Recommendation: {result['recommendation']}")
        print(f"Matched Skills: {result['matched_skills']}")
        print(f"Missing Skills: {result['missing_skills']}")

    # Salvar resultado
    with open("results/matches.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)


if __name__ == "__main__":
    main()