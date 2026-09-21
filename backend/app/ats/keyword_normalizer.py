"""Keyword de-duplication for JD/resume matching.

No hardcoded technology synonym table here — vendor-prefix and spelling
variants ("Apache Kafka" vs "Kafka", "Amazon RDS" vs "RDS", "ReactJS" vs
"React.js") are normalized dynamically per request by the AI at JD
extraction time (see app/ai/prompts/job_description_prompt.py), since that
requires semantic/domain knowledge no fixed word list can keep up with.
This module only does mechanical, case-insensitive de-duplication of
whatever terms the AI already returned.
"""


def canonicalize_all(terms: list[str]) -> list[str]:
    """Case-insensitive de-duplication, preserving first-seen casing."""
    seen: dict[str, str] = {}
    for t in terms:
        t = t.strip()
        if not t:
            continue
        seen.setdefault(t.lower(), t)
    return list(seen.values())
