"""Parser test suite (spec §42): name/email/phone/URL/section/date/company/
title/skills/bullet extraction, validated against both the project's real
resume fixture and a synthetic edge-case resume.
"""

from app.parser.pdf_parser import count_pdf_pages, extract_lines_from_pdf
from app.parser.resume_parser import parse_lines_to_resume
from app.parser.txt_parser import extract_lines_from_txt
from app.parser.resume_parser import TITLE_COMPANY_RE
from tests.conftest import FIXTURES_DIR


def _parse_real_resume():
    content = (FIXTURES_DIR / "sample_resume.pdf").read_bytes()
    lines = extract_lines_from_pdf(content)
    return parse_lines_to_resume(lines)


def _parse_synthetic_resume():
    content = (FIXTURES_DIR / "synthetic_resume.txt").read_bytes()
    lines = extract_lines_from_txt(content)
    return parse_lines_to_resume(lines)


def test_real_resume_name():
    resume = _parse_real_resume()
    assert resume.personal_info.name == "SNEHAL SUKHADEVE"


def test_real_resume_email():
    resume = _parse_real_resume()
    assert resume.personal_info.email == "ssnehalsukhadeve@gmail.com"


def test_real_resume_phone():
    resume = _parse_real_resume()
    assert "9765179473" in resume.personal_info.phone


def test_real_resume_links():
    resume = _parse_real_resume()
    assert "linkedin.com/in/snehal-sukhadeve" in resume.personal_info.linkedin
    assert "github.com/snehalsuk" in resume.personal_info.github
    assert resume.personal_info.leetcode == "sqZl5JZ6jP"
    assert resume.personal_info.hackerrank == "ssnehalsukhadeve"


def test_real_resume_sections_present_in_order():
    resume = _parse_real_resume()
    types = [s.type for s in resume.sections]
    assert types == ["summary", "skills", "experience", "projects", "education", "certifications"]


def test_title_company_separator_accepts_pipe_and_dash():
    """Regression: the PDF/DOCX renderers use "Title | Company" (no em
    dash), and the ATS Parsing Simulator re-parses that exact output to
    verify round-trip fidelity (spec §13) — if this regex only recognized
    a dash, re-parsing our own generated export would silently fail to
    detect any experience entries at all."""
    m = TITLE_COMPANY_RE.match("Software Engineer | Techbird IT Services Pvt. Ltd.")
    assert m and m.group("title") == "Software Engineer" and m.group("company") == "Techbird IT Services Pvt. Ltd."

    m2 = TITLE_COMPANY_RE.match("Software Engineer — Techbird IT Services Pvt. Ltd.")
    assert m2 and m2.group("title") == "Software Engineer"

    # mid-word hyphens must still not falsely split ("full-stack" etc.)
    assert TITLE_COMPANY_RE.match("Designed a full-stack Inventory System") is None


def test_real_resume_experience_dates_and_company():
    resume = _parse_real_resume()
    exp = next(s for s in resume.sections if s.type == "experience")
    items = exp.content["items"]
    assert len(items) == 3
    first = items[0]
    assert first["title"] == "Software Engineer"
    assert first["company"] == "Techbird IT Services Pvt. Ltd."
    assert first["startDate"] == "Oct 2023"
    assert first["current"] is True
    assert len(first["bullets"]) == 3
    # no bullet should be a stray sentence fragment from a wrapped line
    for b in first["bullets"]:
        assert b[0].isupper() or b[0].isdigit()


def test_real_resume_projects_count():
    resume = _parse_real_resume()
    proj = next(s for s in resume.sections if s.type == "projects")
    assert len(proj.content["items"]) == 2


def test_real_resume_skills_no_paren_split():
    resume = _parse_real_resume()
    skills = next(s for s in resume.sections if s.type == "skills")
    db_cloud = next(c for c in skills.content["categories"] if c["name"] == "Database & Cloud")
    assert "AWS (S3, EC2, IAM, CloudWatch)" in db_cloud["items"]


def test_real_resume_pdf_page_count():
    content = (FIXTURES_DIR / "sample_resume.pdf").read_bytes()
    assert count_pdf_pages(content) >= 1


def test_synthetic_resume_name_and_email():
    resume = _parse_synthetic_resume()
    assert resume.personal_info.name == "JANE DOE"
    assert resume.personal_info.email == "jane.doe@example.com"


def test_synthetic_resume_phone():
    resume = _parse_synthetic_resume()
    digits = "".join(c for c in resume.personal_info.phone if c.isdigit())
    assert digits == "5551234567"


def test_synthetic_resume_recognized_extra_section_detected():
    # "AWARDS" is a recognized standard heading (spec §6), not a custom one
    resume = _parse_synthetic_resume()
    awards = next(s for s in resume.sections if s.type == "awards")
    assert awards.title == "AWARDS"
    assert "Employee of the Year 2022" in awards.content["text"]


def test_synthetic_resume_certifications():
    resume = _parse_synthetic_resume()
    certs = next(s for s in resume.sections if s.type == "certifications")
    item = certs.content["items"][0]
    assert item["name"] == "AWS Certified Solutions Architect"
    assert "aws.amazon.com" in item["credentialUrl"]


def test_synthetic_resume_education():
    resume = _parse_synthetic_resume()
    edu = next(s for s in resume.sections if s.type == "education")
    item = edu.content["items"][0]
    assert "State University" in item["institution"]
    assert item["year"] == "2018"
