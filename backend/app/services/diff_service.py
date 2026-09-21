"""Master vs. tailored-version comparison (spec §31): added / removed /
modified / reordered, at section granularity, with line-level diff text for
modified sections.
"""

import difflib
import json

from app.schemas.resume import ResumeData, ResumeSectionDTO


def _section_text_lines(section: ResumeSectionDTO) -> list[str]:
    return json.dumps(section.content, indent=2, sort_keys=True).splitlines()


def diff_resumes(a: ResumeData, b: ResumeData) -> dict:
    a_by_id = {s.id: s for s in a.sections}
    b_by_id = {s.id: s for s in b.sections}

    added = [s.title for sid, s in b_by_id.items() if sid not in a_by_id]
    removed = [s.title for sid, s in a_by_id.items() if sid not in b_by_id]

    modified: list[dict] = []
    unchanged: list[str] = []
    for sid, a_section in a_by_id.items():
        b_section = b_by_id.get(sid)
        if b_section is None:
            continue
        a_lines = _section_text_lines(a_section)
        b_lines = _section_text_lines(b_section)
        if a_lines == b_lines and a_section.title == b_section.title:
            unchanged.append(a_section.title)
            continue
        diff_lines = list(
            difflib.unified_diff(a_lines, b_lines, fromfile="master", tofile="tailored", lineterm="")
        )
        modified.append({"section": b_section.title, "diffLines": diff_lines})

    a_order = [s.id for s in sorted(a.sections, key=lambda s: s.order)]
    b_order = [s.id for s in sorted(b.sections, key=lambda s: s.order)]
    common = [sid for sid in a_order if sid in b_by_id]
    common_in_b_order = [sid for sid in b_order if sid in a_by_id]
    reordered = common != common_in_b_order

    return {
        "added": added,
        "removed": removed,
        "modified": modified,
        "unchanged": unchanged,
        "reordered": reordered,
    }
