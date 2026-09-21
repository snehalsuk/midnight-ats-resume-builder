import re
from collections import Counter

from app.schemas.resume import ResumeData

IDEAL_BULLET_WORDS = (8, 30)


def _all_bullets(resume: ResumeData) -> list[str]:
    bullets: list[str] = []
    for section in resume.sections:
        if section.type in ("experience", "projects"):
            for item in section.content.get("items", []):
                bullets.extend(item.get("bullets", []))
    return bullets


def readability_pct(resume: ResumeData) -> tuple[float, list[str]]:
    bullets = _all_bullets(resume)
    if not bullets:
        return 100.0, []

    warnings: list[str] = []
    good = 0
    for b in bullets:
        word_count = len(b.split())
        if IDEAL_BULLET_WORDS[0] <= word_count <= IDEAL_BULLET_WORDS[1]:
            good += 1
    length_score = 100 * good / len(bullets)

    # keyword stuffing detection (spec §27)
    all_text = " ".join(bullets).lower()
    words = re.findall(r"[a-z][a-z0-9.+#]{2,}", all_text)
    counts = Counter(words)
    stuffing_penalty = 0
    for term, count in counts.items():
        if count >= 6 and term not in ("the", "and", "with", "for", "using"):
            warnings.append(f'"{term}" appears {count} times. Consider reducing repetition.')
            stuffing_penalty += 5

    score = max(0.0, min(100.0, length_score - stuffing_penalty))
    return round(score, 1), warnings
