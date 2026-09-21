import re

# heading text -> canonical section type
HEADING_SYNONYMS: dict[str, str] = {
    "professional summary": "summary",
    "summary": "summary",
    "career summary": "summary",
    "technical skills": "skills",
    "skills": "skills",
    "core competencies": "skills",
    "professional experience": "experience",
    "work experience": "experience",
    "experience": "experience",
    "employment history": "experience",
    "key projects": "projects",
    "projects": "projects",
    "personal projects": "projects",
    "education": "education",
    "academic background": "education",
    "certifications": "certifications",
    "certificates": "certifications",
    "licenses & certifications": "certifications",
    "achievements": "achievements",
    "accomplishments": "achievements",
    "publications": "publications",
    "awards": "awards",
    "awards & honors": "awards",
    "open source": "open_source",
    "open source contributions": "open_source",
    "volunteer experience": "volunteer",
    "volunteering": "volunteer",
    "languages": "languages",
    "interests": "interests",
    "hobbies": "interests",
}


def is_heading_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped or len(stripped) > 50:
        return False
    if stripped.startswith(("•", "-", "*", "o ")):
        return False
    letters = [c for c in stripped if c.isalpha()]
    if not letters:
        return False
    upper_ratio = sum(1 for c in letters if c.isupper()) / len(letters)
    if upper_ratio >= 0.85:
        return True
    return stripped.lower() in HEADING_SYNONYMS


def classify_heading(line: str) -> str:
    key = re.sub(r"[^a-z& ]", "", line.strip().lower()).strip()
    return HEADING_SYNONYMS.get(key, "custom")
