"""Deterministic keyword matching between a resume and a job description.
Never AI-driven — spec §17 forbids fabricating matches or inserting
keywords the resume doesn't actually support.

Matching is done as a word-boundary-safe substring search across the
resume's full text (skills + bullets + project tech), not exact equality
against discrete skill-list items. Real ATS keyword scanners work this
way — they full-text search the document, they don't require a skill to
be its own standalone list entry. Without this, a resume that writes
"AWS (S3, EC2, IAM, CloudWatch)" as one skills-category entry would
incorrectly show "AWS"/"EC2"/"S3" as missing even though they're right
there in the text.
"""

import re

from app.ats.keyword_normalizer import canonicalize_all
from app.schemas.job_description import ParsedJobDescription
from app.schemas.resume import ResumeData

# concept -> resume keywords that are "related but not equivalent" to it.
# Mirrors spec §17's own example (Kafka/Redis/Kubernetes missing ->
# Microservices/Docker/CI-CD related).
RELATED_CONCEPTS: dict[str, list[str]] = {
    "Kafka": ["Microservices", "Event-Driven Architecture", "RabbitMQ"],
    "Redis": ["Caching", "MySQL", "PostgreSQL"],
    "Kubernetes": ["Docker", "Containerization", "CI/CD"],
    "GraphQL": ["RESTful APIs"],
    "Terraform": ["AWS", "CI/CD", "Docker"],
    "Elasticsearch": ["MySQL", "PostgreSQL"],
    "RabbitMQ": ["Microservices", "Kafka"],
}


def extract_jd_keywords(jd: ParsedJobDescription) -> list[str]:
    raw = (
        jd.required_skills
        + jd.preferred_skills
        + jd.technologies
        + jd.tools
        + jd.frameworks
        + jd.databases
        + jd.cloud_technologies
    )
    return canonicalize_all(raw)


def build_resume_search_text(resume: ResumeData) -> str:
    parts: list[str] = []
    for section in resume.sections:
        content = section.content
        if content.get("text"):
            parts.append(content["text"])
        for cat in content.get("categories", []) or []:
            parts.append(cat.get("name", ""))
            parts.extend(cat.get("items", []))
        for item in content.get("items", []) or []:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                parts.append(item.get("title", "") or item.get("name", ""))
                parts.append(item.get("company", ""))
                parts.extend(item.get("bullets", []) or [])
                parts.extend(item.get("technologies", []) or [])
    return "\n".join(p for p in parts if p)


_TOKEN_RE = re.compile(r"[A-Za-z0-9]+(?:[./#+\-][A-Za-z0-9]+)*")


def _tokenize(text: str) -> list[str]:
    """Splits text into words, keeping internal punctuation that's part of
    a real token ("React.js", "CI/CD", "Role-Based") but treating commas,
    parentheses, and whitespace as real separators — so "AWS (S3, EC2,
    IAM, CloudWatch)" tokenizes to ["AWS", "S3", "EC2", "IAM", "CloudWatch"]
    instead of one opaque blob.
    """
    return _TOKEN_RE.findall(text)


def _collapse(s: str) -> str:
    """Strips punctuation that commonly varies between how a term is
    written (dots, hyphens, slashes, spaces) so "React.js" and "ReactJS"
    compare equal — a generic algorithm, not a hardcoded word list. Only
    ever used for exact token-to-token comparison — never as a substring
    search over a whole blob, which would false-positive on short keywords
    hiding inside unrelated words (e.g. "RDS" inside "standards").
    """
    return re.sub(r"[.\-\s/]", "", s.lower())


def keyword_in_text(keyword: str, text_lower: str, tokens_collapsed: set[str]) -> bool:
    kw_lower = keyword.lower()
    # exact phrase, word-boundary safe — catches both single tokens ("AWS")
    # and true multi-word phrases ("RESTful APIs") appearing verbatim.
    if re.search(r"(?<![a-z0-9])" + re.escape(kw_lower) + r"(?![a-z0-9])", text_lower):
        return True
    # punctuation-variant spelling of a single token ("ReactJS" vs "React.js")
    kw_collapsed = _collapse(keyword)
    return bool(kw_collapsed) and kw_collapsed in tokens_collapsed


def _prepare(resume: ResumeData) -> tuple[str, set[str]]:
    text_lower = build_resume_search_text(resume).lower()
    tokens_collapsed = {_collapse(t) for t in _tokenize(text_lower)}
    return text_lower, tokens_collapsed


def matched_keywords_in_resume(resume: ResumeData, keywords: list[str]) -> list[str]:
    """Public entry point for "does the resume's full text support these
    keywords" — used both for JD keyword matching and the ATS scorer's
    required-skills check, so both apply the exact same matching rules.
    """
    text_lower, tokens_collapsed = _prepare(resume)
    return [k for k in keywords if keyword_in_text(k, text_lower, tokens_collapsed)]


def match_keywords(resume: ResumeData, jd: ParsedJobDescription) -> tuple[list[str], list[str], list[str]]:
    text_lower, tokens_collapsed = _prepare(resume)
    jd_keywords = extract_jd_keywords(jd)

    matched = [k for k in jd_keywords if keyword_in_text(k, text_lower, tokens_collapsed)]
    missing = [k for k in jd_keywords if k not in matched]

    related: list[str] = []
    for miss in missing:
        for related_term in RELATED_CONCEPTS.get(miss, []):
            if keyword_in_text(related_term, text_lower, tokens_collapsed) and related_term not in related:
                related.append(related_term)

    return matched, missing, related
