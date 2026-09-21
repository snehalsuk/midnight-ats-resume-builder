"""Deterministic backstop over the AI's JD extraction (spec §52: never fully
trust free-form AI output). Even with explicit prompt instructions, an LLM
can still emit a full requirement sentence instead of an atomic skill name
(e.g. "Strong hands-on experience with TypeScript" instead of
"TypeScript") — this filters those out before they pollute keyword
matching and scoring.
"""

import re

_SENTENCE_LEAD_WORDS = (
    "strong", "good", "hands-on", "hands on", "experience", "knowledge",
    "working", "understanding", "ability", "familiarity", "proven",
    "solid", "years", "excellent", "basic",
)

_MAX_ATOMIC_WORDS = 4
_MAX_ATOMIC_CHARS = 40


def _looks_like_sentence(term: str) -> bool:
    stripped = term.strip()
    if not stripped:
        return True
    if stripped.endswith("."):
        return True
    if len(stripped) > _MAX_ATOMIC_CHARS:
        return True
    word_count = len(stripped.split())
    if word_count > _MAX_ATOMIC_WORDS:
        return True
    first_word = re.sub(r"[^a-z-]", "", stripped.split()[0].lower())
    if first_word in _SENTENCE_LEAD_WORDS:
        return True
    return False


def sanitize_atomic_terms(terms: list[str]) -> list[str]:
    return [t.strip() for t in terms if not _looks_like_sentence(t)]
