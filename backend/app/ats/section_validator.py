"""Standard-heading validation (spec §28) and formatting-safety checks
(spec §12). Since our own renderer never emits tables/images/columns, the
formatting checks here mostly guard against a user renaming a section into
something an ATS parser won't recognize.
"""

from app.schemas.resume import STANDARD_SECTION_TITLES, ResumeData

_STANDARD_TITLES_LOWER = {v.lower() for v in STANDARD_SECTION_TITLES.values()}

REQUIRED_SECTION_TYPES = ("summary", "skills", "experience", "education")


def validate_section_titles(resume: ResumeData) -> list[str]:
    warnings: list[str] = []
    for section in resume.sections:
        if not section.visible:
            continue
        if section.type == "custom":
            if section.title.strip().lower() not in _STANDARD_TITLES_LOWER:
                warnings.append(
                    f'Non-standard section heading "{section.title}" may not be recognized by all ATS parsers.'
                )
        else:
            expected = STANDARD_SECTION_TITLES.get(section.type)
            if expected and section.title.strip().lower() != expected.lower():
                warnings.append(
                    f'Section "{section.title}" uses a custom heading instead of the standard "{expected}".'
                )
    return warnings


def section_completeness_pct(resume: ResumeData) -> float:
    present_types = {s.type for s in resume.sections if s.visible}
    has_content = 0
    for t in REQUIRED_SECTION_TYPES:
        section = next((s for s in resume.sections if s.type == t and s.visible), None)
        if section and _section_has_content(section):
            has_content += 1
    return round(100 * has_content / len(REQUIRED_SECTION_TYPES), 1)


def _section_has_content(section) -> bool:
    content = section.content
    if "text" in content:
        return bool(content["text"].strip())
    if "items" in content:
        return len(content["items"]) > 0
    if "categories" in content:
        return any(c.get("items") for c in content["categories"])
    return False


# Formatting rules from spec §12 that our own generator guarantees by
# construction; still surfaced explicitly so the ATS panel is honest about
# what was checked rather than silently assuming.
def formatting_warnings() -> list[str]:
    return []  # the "professional_ats" template never uses tables/columns/images/icons
