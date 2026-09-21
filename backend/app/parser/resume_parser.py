"""Turns raw resume lines (from PDF/DOCX/TXT) into a structured ResumeData
object. Deterministic only — no AI, no rewriting (spec §47).
"""

import re
import uuid

from app.parser import field_extractor as fx
from app.parser.section_detector import classify_heading, is_heading_line
from app.schemas.resume import (
    STANDARD_SECTION_TITLES,
    CertificationItem,
    EducationItem,
    ExperienceItem,
    PersonalInfo,
    ProjectItem,
    ResumeData,
    ResumeSectionDTO,
    SkillCategory,
)

BULLET_PREFIX_RE = re.compile(r"^[•\-\*▪●]\s+")
# Title/Company and Degree/Institution splits use an em dash, en dash, or
# pipe with mandatory surrounding whitespace, as authored ("Engineer —
# Techbird" or, in this app's own generated exports, "Engineer | Techbird").
# A plain ASCII hyphen (no required spaces) is deliberately excluded so
# mid-word hyphens in wrapped bullet text ("full-stack", "post-release",
# "JWT-based") never get misread as a new entry boundary.
TITLE_COMPANY_RE = re.compile(r"^(?P<title>.+?)\s[—–|]\s(?P<company>.+)$")
DATE_LINE_RE = re.compile(
    r"^(?P<start>[A-Za-z]{3,9}\.?\s+\d{4}|\d{4})\s*[-–—]\s*(?P<end>[A-Za-z]{3,9}\.?\s+\d{4}|\d{4}|[Pp]resent)\s*$"
)


def _split_items(text: str) -> list[str]:
    """Comma-split while treating parenthesized content as atomic, so
    "AWS (S3, EC2, IAM, CloudWatch)" stays one item instead of shattering
    into "AWS (S3", "EC2", "IAM", "CloudWatch)".
    """
    items: list[str] = []
    depth = 0
    current: list[str] = []
    for ch in text:
        if ch == "(":
            depth += 1
            current.append(ch)
        elif ch == ")":
            depth = max(0, depth - 1)
            current.append(ch)
        elif ch == "," and depth == 0:
            items.append("".join(current).strip())
            current = []
        else:
            current.append(ch)
    if current:
        items.append("".join(current).strip())
    return [i for i in items if i]


def _new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def _is_bullet(line: str) -> bool:
    return bool(BULLET_PREFIX_RE.match(line))


def _strip_bullet(line: str) -> str:
    return BULLET_PREFIX_RE.sub("", line).strip()


def _is_date_line(line: str) -> bool:
    return bool(DATE_LINE_RE.search(line))


def _split_contact_block(lines: list[str]) -> tuple[str, str, list[str], int]:
    """Returns (name, title, contact_lines, index_after_contact_block)."""
    if not lines:
        return "", "", [], 0
    name = lines[0]
    idx = 1
    title = ""
    if idx < len(lines) and not fx.EMAIL_RE.search(lines[idx]) and not is_heading_line(lines[idx]):
        title = lines[idx]
        idx += 1
    contact_lines: list[str] = []
    while idx < len(lines) and not is_heading_line(lines[idx]) and idx < 6:
        contact_lines.append(lines[idx])
        idx += 1
    return name, title, contact_lines, idx


def _parse_personal_info(lines: list[str]) -> tuple[PersonalInfo, int]:
    name, title, contact_lines, next_idx = _split_contact_block(lines)
    contact_text = "\n".join(contact_lines)

    location = ""
    if contact_lines:
        first = contact_lines[0]
        parts = [p.strip() for p in re.split(r"\||,(?=\s*[A-Za-z]+\s*\|)", first)]
        loc_candidate = first.split("|")[0].strip()
        if "@" not in loc_candidate and not re.search(r"\d{3,}", loc_candidate):
            location = loc_candidate

    info = PersonalInfo(
        name=name,
        title=title,
        location=location,
        email=fx.extract_email(contact_text) or "",
        phone=fx.extract_phone(contact_text) or "",
        linkedin=fx.extract_linkedin(contact_text) or "",
        github=fx.extract_github(contact_text) or "",
        leetcode=fx.extract_leetcode_handle(contact_text) or "",
        hackerrank=fx.extract_hackerrank_handle(contact_text) or "",
        portfolio=fx.extract_portfolio(contact_text, set()) or "",
    )
    return info, next_idx


def _group_into_sections(lines: list[str], start_idx: int) -> list[tuple[str, list[str]]]:
    """Returns [(heading_line, [content_lines...]), ...]."""
    groups: list[tuple[str, list[str]]] = []
    current_heading: str | None = None
    current_lines: list[str] = []
    for line in lines[start_idx:]:
        if is_heading_line(line):
            if current_heading is not None:
                groups.append((current_heading, current_lines))
            current_heading = line
            current_lines = []
        else:
            current_lines.append(line)
    if current_heading is not None:
        groups.append((current_heading, current_lines))
    return groups


def _parse_skills(lines: list[str]) -> dict:
    categories: list[SkillCategory] = []
    for line in lines:
        if ":" in line:
            label, _, rest = line.partition(":")
            categories.append(SkillCategory(name=label.strip(), items=_split_items(rest)))
        elif line.strip() and categories:
            # wrapped continuation of the previous category's item list
            categories[-1].items.extend(_split_items(line))
        elif line.strip():
            categories.append(SkillCategory(name="Skills", items=_split_items(line)))
    return {"categories": [c.model_dump(by_alias=True) for c in categories]}


def _parse_experience(lines: list[str]) -> dict:
    items: list[ExperienceItem] = []
    current: ExperienceItem | None = None
    for line in lines:
        if _is_date_line(line):
            if current is not None:
                m = DATE_LINE_RE.search(line)
                if m:
                    current.start_date = m.group("start")
                    current.end_date = m.group("end")
                    current.current = m.group("end").strip().lower() == "present"
            continue
        if _is_bullet(line):
            if current is not None:
                current.bullets.append(_strip_bullet(line))
            continue
        m = TITLE_COMPANY_RE.match(line)
        if m:
            if current is not None:
                items.append(current)
            current = ExperienceItem(
                id=_new_id("exp"), title=m.group("title").strip(), company=m.group("company").strip()
            )
        elif (
            current is not None
            and current.bullets
            and not current.bullets[-1].rstrip().endswith((".", "!", "?"))
        ):
            # wrapped continuation of the last bullet's text
            current.bullets[-1] = f"{current.bullets[-1]} {line}".strip()
        elif current is not None:
            current.bullets.append(line)
    if current is not None:
        items.append(current)
    return {"items": [i.model_dump(by_alias=True) for i in items]}


def _parse_projects(lines: list[str]) -> dict:
    items: list[ProjectItem] = []
    current: ProjectItem | None = None
    expecting_tech_line = False
    for line in lines:
        if _is_bullet(line):
            if current is not None:
                current.bullets.append(_strip_bullet(line))
            expecting_tech_line = False
            continue
        if expecting_tech_line and current is not None and not current.technologies:
            current.technologies = _split_items(line)
            expecting_tech_line = False
            continue
        if (
            current is not None
            and current.bullets
            and not current.bullets[-1].rstrip().endswith((".", "!", "?"))
        ):
            # wrapped continuation of the last bullet's text (bullet doesn't
            # yet end a sentence, so this line can't be a new project name)
            current.bullets[-1] = f"{current.bullets[-1]} {line}".strip()
            continue
        if current is not None:
            items.append(current)
        current = ProjectItem(id=_new_id("proj"), name=line.strip())
        expecting_tech_line = True
    if current is not None:
        items.append(current)
    return {"items": [i.model_dump(by_alias=True) for i in items]}


def _parse_education(lines: list[str]) -> dict:
    items: list[EducationItem] = []
    for line in lines:
        parts = [p.strip() for p in line.split("|")]
        head = parts[0]
        m = TITLE_COMPANY_RE.match(head)
        degree = m.group("title").strip() if m else head
        institution = m.group("company").strip() if m else ""
        gpa = ""
        year = ""
        for p in parts[1:]:
            if re.search(r"\d{4}", p) and "cgpa" not in p.lower() and "gpa" not in p.lower():
                year = p
            else:
                gpa = p
        items.append(EducationItem(id=_new_id("edu"), degree=degree, institution=institution, gpa=gpa, year=year))
    return {"items": [i.model_dump(by_alias=True) for i in items]}


def _parse_certifications(lines: list[str]) -> dict:
    items: list[CertificationItem] = []
    for line in lines:
        parts = [p.strip() for p in line.split("|")]
        head = parts[0]
        m = TITLE_COMPANY_RE.match(head)
        name = m.group("title").strip() if m else head
        issuer = m.group("company").strip() if m else ""
        year = ""
        credential_url = ""
        for p in parts[1:]:
            if "credential" in p.lower() or fx.GENERIC_URL_RE.search(p):
                credential_url = p.split(":", 1)[-1].strip()
            elif re.search(r"\d{4}", p):
                year = p
        items.append(
            CertificationItem(id=_new_id("cert"), name=name, issuer=issuer, year=year, credential_url=credential_url)
        )
    return {"items": [i.model_dump(by_alias=True) for i in items]}


SECTION_PARSERS = {
    "skills": _parse_skills,
    "experience": _parse_experience,
    "projects": _parse_projects,
    "education": _parse_education,
    "certifications": _parse_certifications,
}


def parse_lines_to_resume(lines: list[str]) -> ResumeData:
    personal_info, start_idx = _parse_personal_info(lines)
    groups = _group_into_sections(lines, start_idx)

    sections: list[ResumeSectionDTO] = []
    for order, (heading_line, content_lines) in enumerate(groups, start=1):
        section_type = classify_heading(heading_line)
        parser = SECTION_PARSERS.get(section_type)
        if parser:
            content = parser(content_lines)
        else:
            content = {"text": "\n".join(content_lines)}

        title = STANDARD_SECTION_TITLES.get(section_type, heading_line.strip())
        key = section_type if section_type in STANDARD_SECTION_TITLES and section_type != "custom" else _new_id(
            "section"
        )
        sections.append(
            ResumeSectionDTO(
                id=key,
                type=section_type,  # type: ignore[arg-type]
                title=title if section_type != "custom" else heading_line.strip().upper(),
                order=order,
                visible=True,
                content=content,
            )
        )

    return ResumeData(personal_info=personal_info, sections=sections)
