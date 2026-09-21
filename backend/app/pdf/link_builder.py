"""Builds real, clickable hyperlink targets from the stored personal-info
values for PDF/DOCX export. Some fields (LeetCode/HackerRank) are stored as
bare handles rather than full URLs — see field_extractor.py — so this
reconstructs a canonical profile URL for those.
"""

import re

_URL_LIKE_RE = re.compile(r"^https?://", re.I)


def build_href(kind: str, value: str) -> str:
    value = value.strip()
    if not value:
        return ""
    if kind == "email":
        return f"mailto:{value}"
    if _URL_LIKE_RE.match(value):
        return value
    if "." in value:  # already domain-shaped, e.g. "linkedin.com/in/x" or "midnightsun.in"
        return f"https://{value}"
    if kind == "leetcode":
        return f"https://leetcode.com/{value}"
    if kind == "hackerrank":
        return f"https://www.hackerrank.com/profile/{value}"
    return f"https://{value}"


def build_personal_links(personal_info: dict) -> dict[str, str]:
    fields = ("email", "linkedin", "github", "portfolio", "leetcode", "hackerrank")
    return {f: build_href(f, personal_info.get(f, "") or "") for f in fields}
