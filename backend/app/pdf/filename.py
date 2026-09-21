"""Company-specific export filenames (spec §22):
  FirstName_LastName_Company_Role.pdf  (or .docx)
  FirstName_LastName_Company.pdf       when role is not available
"""

import re

_ILLEGAL_CHARS_RE = re.compile(r'[<>:"/\\|?*]')


def _sanitize_segment(value: str) -> str:
    value = _ILLEGAL_CHARS_RE.sub("", value)
    value = re.sub(r"\s+", "_", value.strip())
    return value


def generate_export_filename(full_name: str, company: str | None, role: str | None, extension: str) -> str:
    name_parts = full_name.strip().split()
    first = name_parts[0] if name_parts else "Resume"
    last = name_parts[-1] if len(name_parts) > 1 else ""

    segments = [_sanitize_segment(first)]
    if last:
        segments.append(_sanitize_segment(last))
    if company:
        segments.append(_sanitize_segment(company))
    if role:
        segments.append(_sanitize_segment(role))

    base = "_".join(s for s in segments if s)
    return f"{base}.{extension.lstrip('.')}"
