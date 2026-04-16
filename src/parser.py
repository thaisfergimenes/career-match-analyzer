import re
from pathlib import Path
from pypdf import PdfReader
from skill_config import SKILL_PATTERNS


def load_text_file(path: str) -> str:
    encodings = ["utf-8", "latin-1", "cp1252", "iso-8859-1"]
    
    for encoding in encodings:
        try:
            return Path(path).read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    
    raise ValueError(f"Could not decode file {path} with any known encoding")


def load_pdf_file(path: str) -> str:
    reader = PdfReader(path)
    pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)
    return "\n".join(pages)


def load_resume(path: str) -> str:
    path_obj = Path(path)
    suffix = path_obj.suffix.lower()

    if suffix == ".txt":
        return load_text_file(path)
    if suffix == ".pdf":
        return load_pdf_file(path)

    raise ValueError(f"Unsupported file type: {suffix}")


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def extract_skills(text: str) -> list[str]:
    normalized = normalize_text(text)
    found = []

    for canonical_skill, patterns in SKILL_PATTERNS.items():
        if any(re.search(pattern, normalized) for pattern in patterns):
            found.append(canonical_skill)

    return sorted(found)


def parse_pasted_jobs(raw_text: str) -> list[dict]:
    """Parse multiple jobs from pasted text separated by ===JOB=== markers."""
    jobs = []
    blocks = [block.strip() for block in raw_text.split("===JOB===") if block.strip()]

    for idx, block in enumerate(blocks, start=1):
        lines = block.splitlines()

        job = {
            "id": idx,
            "title": "",
            "company": "",
            "description": "",
            "required_skills": [],
            "nice_to_have": []
        }

        description_lines = []
        in_description = False

        for line in lines:
            stripped = line.strip()

            if stripped.startswith("Title:"):
                job["title"] = stripped.replace("Title:", "", 1).strip()
                in_description = False

            elif stripped.startswith("Company:"):
                job["company"] = stripped.replace("Company:", "", 1).strip()
                in_description = False

            elif stripped.startswith("Description:"):
                desc_start = stripped.replace("Description:", "", 1).strip()
                if desc_start:
                    description_lines.append(desc_start)
                in_description = True

            elif stripped.startswith("Required skills:"):
                skills = stripped.replace("Required skills:", "", 1).strip()
                job["required_skills"] = [s.strip() for s in skills.split(",") if s.strip()]
                in_description = False

            elif stripped.startswith("Nice to have:"):
                skills = stripped.replace("Nice to have:", "", 1).strip()
                job["nice_to_have"] = [s.strip() for s in skills.split(",") if s.strip()]
                in_description = False

            elif in_description:
                description_lines.append(stripped)

        job["description"] = " ".join(description_lines).strip()
        jobs.append(job)

    return jobs