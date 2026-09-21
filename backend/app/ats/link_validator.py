"""Link structure validation (spec §29). Checks shape only — no live
network requests — since reachability checks would be slow and are outside
what a deterministic export-time gate should depend on.
"""

import re

from app.schemas.resume import ResumeData

_URL_LIKE_RE = re.compile(r"^[A-Za-z0-9.\-]+\.[A-Za-z]{2,}(/[^\s]*)?$")


def _looks_like_url(value: str) -> bool:
    value = value.strip()
    if not value:
        return True  # absent is fine; presence is validated elsewhere
    stripped = re.sub(r"^https?://", "", value, flags=re.I)
    stripped = re.sub(r"^www\.", "", stripped, flags=re.I)
    return bool(_URL_LIKE_RE.match(stripped))


def validate_links(resume: ResumeData) -> list[str]:
    problems: list[str] = []
    info = resume.personal_info

    if info.email and "@" not in info.email:
        problems.append("Email address does not look valid.")
    if info.linkedin and "linkedin.com" not in info.linkedin.lower():
        problems.append("LinkedIn field does not look like a linkedin.com URL.")
    if info.github and "github.com" not in info.github.lower():
        problems.append("GitHub field does not look like a github.com URL.")
    if info.portfolio and not _looks_like_url(info.portfolio):
        problems.append("Portfolio URL does not look valid.")

    for section in resume.sections:
        if section.type == "certifications":
            for item in section.content.get("items", []):
                url = item.get("credentialUrl", "")
                if url and not _looks_like_url(url):
                    problems.append(f'Credential URL for "{item.get("name", "certification")}" does not look valid.')

    return problems
