"""ATS Parsing Simulator (spec §13): re-parses the freshly generated PDF
through the same deterministic parser used for uploads, then diffs the
result against the source resume JSON to prove the export is genuinely
machine-readable.
"""

from app.parser.pdf_parser import extract_lines_from_pdf, extract_plain_text_from_pdf, has_extractable_text
from app.parser.resume_parser import parse_lines_to_resume
from app.schemas.ats import ParsingChecklistItem
from app.schemas.resume import ResumeData


def _digits(s: str) -> str:
    return "".join(c for c in s if c.isdigit())


def run_parsing_simulation(original: ResumeData, pdf_bytes: bytes) -> dict[str, ParsingChecklistItem]:
    checklist: dict[str, ParsingChecklistItem] = {}

    if not has_extractable_text(pdf_bytes):
        reason = "The PDF has no extractable text layer (would appear as an image to an ATS)."
        return {
            key: ParsingChecklistItem(detected=False, reason=reason)
            for key in (
                "name", "email", "phone", "linkedin", "experience", "company",
                "designation", "dates", "skills", "projects", "education",
            )
        }

    lines = extract_lines_from_pdf(pdf_bytes)
    plain_text = extract_plain_text_from_pdf(pdf_bytes)
    reparsed = parse_lines_to_resume(lines)

    # name
    checklist["name"] = ParsingChecklistItem(
        detected=bool(reparsed.personal_info.name) and reparsed.personal_info.name.lower() == original.personal_info.name.lower(),
        reason=None if reparsed.personal_info.name else "Name line could not be isolated from the header.",
    )

    # email
    email_ok = bool(reparsed.personal_info.email) and reparsed.personal_info.email.lower() == original.personal_info.email.lower()
    checklist["email"] = ParsingChecklistItem(detected=email_ok, reason=None if email_ok else "Email address could not be detected in the contact line.")

    # phone
    phone_ok = bool(reparsed.personal_info.phone) and _digits(reparsed.personal_info.phone) == _digits(original.personal_info.phone)
    checklist["phone"] = ParsingChecklistItem(detected=phone_ok, reason=None if phone_ok else "Phone number could not be detected.")

    # linkedin
    linkedin_expected = bool(original.personal_info.linkedin)
    linkedin_ok = (not linkedin_expected) or bool(reparsed.personal_info.linkedin)
    checklist["linkedin"] = ParsingChecklistItem(
        detected=linkedin_ok, reason=None if linkedin_ok else "LinkedIn URL could not be detected — check it wasn't split across lines."
    )

    orig_exp = next((s for s in original.sections if s.type == "experience"), None)
    reparsed_exp = next((s for s in reparsed.sections if s.type == "experience"), None)
    orig_exp_items = orig_exp.content.get("items", []) if orig_exp else []
    reparsed_exp_items = reparsed_exp.content.get("items", []) if reparsed_exp else []

    exp_ok = (not orig_exp_items) or len(reparsed_exp_items) > 0
    checklist["experience"] = ParsingChecklistItem(detected=exp_ok, reason=None if exp_ok else "No experience entries detected in the exported PDF.")

    company_ok = True
    designation_ok = True
    if orig_exp_items:
        company_ok = any((it.get("company", "") or "").split(".")[0].strip() in plain_text for it in orig_exp_items if it.get("company"))
        designation_ok = any((it.get("title", "") or "") in plain_text for it in orig_exp_items if it.get("title"))
    checklist["company"] = ParsingChecklistItem(detected=company_ok, reason=None if company_ok else "Company name text not found verbatim in extracted text.")
    checklist["designation"] = ParsingChecklistItem(detected=designation_ok, reason=None if designation_ok else "Job title text not found verbatim in extracted text.")

    dates_ok = (not orig_exp_items) or any(it.get("startDate") for it in reparsed_exp_items)
    checklist["dates"] = ParsingChecklistItem(detected=dates_ok, reason=None if dates_ok else "Employment dates could not be isolated.")

    orig_skills = next((s for s in original.sections if s.type == "skills"), None)
    reparsed_skills = next((s for s in reparsed.sections if s.type == "skills"), None)
    skills_expected = bool(orig_skills and orig_skills.content.get("categories"))
    skills_ok = (not skills_expected) or bool(reparsed_skills and reparsed_skills.content.get("categories"))
    checklist["skills"] = ParsingChecklistItem(detected=skills_ok, reason=None if skills_ok else "Skills section not detected.")

    orig_projects = next((s for s in original.sections if s.type == "projects"), None)
    reparsed_projects = next((s for s in reparsed.sections if s.type == "projects"), None)
    projects_expected = bool(orig_projects and orig_projects.content.get("items"))
    projects_ok = (not projects_expected) or bool(reparsed_projects and reparsed_projects.content.get("items"))
    checklist["projects"] = ParsingChecklistItem(detected=projects_ok, reason=None if projects_ok else "Projects section not detected.")

    orig_edu = next((s for s in original.sections if s.type == "education"), None)
    reparsed_edu = next((s for s in reparsed.sections if s.type == "education"), None)
    edu_expected = bool(orig_edu and orig_edu.content.get("items"))
    edu_ok = (not edu_expected) or bool(reparsed_edu and reparsed_edu.content.get("items"))
    checklist["education"] = ParsingChecklistItem(detected=edu_ok, reason=None if edu_ok else "Education section not detected.")

    return checklist
