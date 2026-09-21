"""Deterministic regex/heuristic extraction of contact fields, links and
dates from raw resume text. No AI involved — spec §47 requires the parser
to be PDF -> structured data, never a rewrite.
"""

import re

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3,5}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}")
LINKEDIN_RE = re.compile(r"(https?://)?(www\.)?linkedin\.com/in/[A-Za-z0-9\-_/%]+", re.I)
GITHUB_RE = re.compile(r"(https?://)?(www\.)?github\.com/[A-Za-z0-9\-_]+", re.I)
LEETCODE_RE = re.compile(r"(https?://)?(www\.)?leetcode\.com/[A-Za-z0-9\-_/]+", re.I)
HACKERRANK_RE = re.compile(r"(https?://)?(www\.)?hackerrank\.com/[A-Za-z0-9\-_/]+", re.I)
GENERIC_URL_RE = re.compile(r"(https?://)?(www\.)?[A-Za-z0-9\-]+\.[A-Za-z]{2,}(/[A-Za-z0-9\-_/%.]*)?")

DATE_RANGE_RE = re.compile(
    r"(?P<start>[A-Za-z]{3,9}\.?\s+\d{4}|\d{4})\s*[-–—to]{1,3}\s*(?P<end>[A-Za-z]{3,9}\.?\s+\d{4}|\d{4}|[Pp]resent)"
)


def extract_email(text: str) -> str | None:
    m = EMAIL_RE.search(text)
    return m.group(0) if m else None


def extract_phone(text: str) -> str | None:
    for m in PHONE_RE.finditer(text):
        digits = re.sub(r"\D", "", m.group(0))
        if 9 <= len(digits) <= 13:
            return m.group(0).strip()
    return None


def extract_linkedin(text: str) -> str | None:
    m = LINKEDIN_RE.search(text)
    return _normalize_url(m.group(0)) if m else None


def extract_github(text: str) -> str | None:
    m = GITHUB_RE.search(text)
    return _normalize_url(m.group(0)) if m else None


def extract_leetcode_handle(text: str) -> str | None:
    m = LEETCODE_RE.search(text)
    if m:
        return _normalize_url(m.group(0))
    m2 = re.search(r"LeetCode\s*:?\s*([A-Za-z0-9_\-]+)", text, re.I)
    return m2.group(1) if m2 else None


def extract_hackerrank_handle(text: str) -> str | None:
    m = HACKERRANK_RE.search(text)
    if m:
        return _normalize_url(m.group(0))
    m2 = re.search(r"HackerRank\s*:?\s*([A-Za-z0-9_\-]+)", text, re.I)
    return m2.group(1) if m2 else None


def extract_portfolio(text: str, known_urls_to_exclude: set[str]) -> str | None:
    m2 = re.search(r"Portfolio\s*:?\s*([A-Za-z0-9\-.]+\.[A-Za-z]{2,}[^\s|,;]*)", text, re.I)
    if m2:
        return m2.group(1)
    return None


def extract_date_ranges(text: str) -> list[tuple[str, str]]:
    return [(m.group("start"), m.group("end")) for m in DATE_RANGE_RE.finditer(text)]


def _normalize_url(url: str) -> str:
    return url.strip().rstrip(").,;")
