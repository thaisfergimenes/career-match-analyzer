import os
from openai import OpenAI


def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


def build_explanation_prompt(job, result):
    return f"""
You are a career assistant helping a candidate understand job fit.

Analyze the match result and write:
1. A short summary of why this job matches or does not match
2. Main strengths
3. Main gaps
4. A final recommendation using one of these labels:
   - Apply now
   - Apply with caution
   - Low priority

Job title: {job['title']}
Company: {job['company']}
Job description: {job['description']}
Required skills: {job.get('required_skills', [])}
Nice to have skills: {job.get('nice_to_have', [])}

Rule score: {result['rule_score']}
Semantic score: {result['semantic_score']}
Final score: {result['final_score']}
Matched required skills: {result['matched_required']}
Missing required skills: {result['missing_required']}
Matched nice skills: {result['matched_nice']}
Missing nice skills: {result['missing_nice']}

Keep the answer concise, professional, and easy to read.
Return plain text only.
""".strip()


def generate_llm_explanation(job, result):
    client = get_openai_client()
    if client is None:
        return (
            "LLM explanation unavailable. Set the OPENAI_API_KEY environment variable "
            "to enable AI-generated match explanations."
        )

    prompt = build_explanation_prompt(job, result)

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )
        return response.output_text.strip()
    except Exception as e:
        return f"Failed to generate explanation: {str(e)}"