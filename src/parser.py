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