"""Deterministic ATS Compatibility Score (spec §14). Every sub-score is a
plain computable percentage — nothing here is an AI-generated number.

  Keyword Match:              30%
  Skill Match:                20%
  Job Title Match:             10%
  Experience Relevance:       10%
  Section Completeness:       10%
  Parsing Accuracy:           10%
  Formatting Compatibility:    5%
  Readability:                 5%
"""

import difflib
import re

from app.ats.experience_utils import parse_required_years, total_experience_years
from app.ats.keyword_matcher import match_keywords, matched_keywords_in_resume
from app.ats.keyword_normalizer import canonicalize_all
from app.ats.readability import readability_pct
from app.ats.section_validator import (
    formatting_warnings,
    section_completeness_pct,
    validate_section_titles,
)
from app.schemas.ats import AtsScoreBreakdown, ParsingChecklistItem
from app.schemas.job_description import ParsedJobDescription
from app.schemas.resume import ResumeData

WEIGHTS = {
    "keyword": 0.30,
    "skills": 0.20,
    "title": 0.10,
    "experience": 0.10,
    "sections": 0.10,
    "parsing": 0.10,
    "formatting": 0.05,
    "readability": 0.05,
}


def _title_match_pct(resume: ResumeData, jd: ParsedJobDescription) -> float:
    if not jd.job_title:
        return 100.0
    resume_title = (resume.personal_info.title or "").lower()
    jd_title = jd.job_title.lower()
    resume_tokens = set(re.findall(r"[a-z0-9.+#]+", resume_title))
    jd_tokens = set(re.findall(r"[a-z0-9.+#]+", jd_title))
    if not jd_tokens:
        return 100.0
    overlap = len(resume_tokens & jd_tokens)
    token_score = 100 * overlap / len(jd_tokens)
    fuzzy = difflib.SequenceMatcher(None, resume_title, jd_title).ratio() * 100
    return round(max(token_score, fuzzy), 1)


def _skills_match_pct(resume: ResumeData, jd: ParsedJobDescription) -> float:
    if not jd.required_skills:
        return 100.0
    required = canonicalize_all(jd.required_skills)
    matched = matched_keywords_in_resume(resume, required)
    return round(100 * len(matched) / len(required), 1) if required else 100.0


def _experience_relevance_pct(resume: ResumeData, jd: ParsedJobDescription) -> float:
    required_years = parse_required_years(jd.years_of_experience)
    if required_years is None or required_years == 0:
        return 100.0
    exp_section = next((s for s in resume.sections if s.type == "experience"), None)
    items = exp_section.content.get("items", []) if exp_section else []
    actual_years = total_experience_years(items)
    if actual_years >= required_years:
        return 100.0
    return round(100 * actual_years / required_years, 1)


def compute_ats_score(
    resume: ResumeData,
    jd: ParsedJobDescription | None,
    parsing_checklist: dict[str, ParsingChecklistItem],
    page_count: int | None,
) -> AtsScoreBreakdown:
    section_titles_warnings = validate_section_titles(resume)
    fmt_warnings = formatting_warnings()

    if jd is not None:
        matched, missing, related = match_keywords(resume, jd)
        total_jd_kw = len(matched) + len(missing)
        keyword_pct = round(100 * len(matched) / total_jd_kw, 1) if total_jd_kw else 100.0
        skills_pct = _skills_match_pct(resume, jd)
        title_pct = _title_match_pct(resume, jd)
        experience_pct = _experience_relevance_pct(resume, jd)
    else:
        matched, missing, related = [], [], []
        keyword_pct = 0.0
        skills_pct = 0.0
        title_pct = 0.0
        experience_pct = 0.0

    sections_pct = section_completeness_pct(resume)

    detected_count = sum(1 for v in parsing_checklist.values() if v.detected)
    parsing_pct = round(100 * detected_count / len(parsing_checklist), 1) if parsing_checklist else 0.0

    formatting_pct = max(0.0, 100.0 - 10 * len(fmt_warnings))
    read_pct, stuffing_warnings = readability_pct(resume)

    overall = (
        keyword_pct * WEIGHTS["keyword"]
        + skills_pct * WEIGHTS["skills"]
        + title_pct * WEIGHTS["title"]
        + experience_pct * WEIGHTS["experience"]
        + sections_pct * WEIGHTS["sections"]
        + parsing_pct * WEIGHTS["parsing"]
        + formatting_pct * WEIGHTS["formatting"]
        + read_pct * WEIGHTS["readability"]
    )

    suggestions: list[str] = []
    for m in missing[:5]:
        suggestions.append(f"{m} — not found in current resume. Add it only if genuinely supported by your experience.")
    if page_count and page_count > 1:
        suggestions.append("Resume exceeds one page — run Auto Optimize before exporting.")

    return AtsScoreBreakdown(
        overall_score=round(overall, 1),
        keyword_match_pct=keyword_pct,
        skills_match_pct=skills_pct,
        title_match_pct=title_pct,
        experience_relevance_pct=experience_pct,
        section_completeness_pct=sections_pct,
        parsing_accuracy_pct=parsing_pct,
        formatting_compatibility_pct=formatting_pct,
        readability_pct=read_pct,
        matched_keywords=matched,
        missing_keywords=missing,
        related_keywords=related,
        formatting_warnings=fmt_warnings,
        section_warnings=section_titles_warnings + stuffing_warnings,
        suggestions=suggestions,
        parsing_checklist=parsing_checklist,
        page_count=page_count,
        one_page_ok=(page_count == 1) if page_count is not None else False,
    )
