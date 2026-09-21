from app.pdf.docx_renderer import render_resume_docx
from app.pdf.filename import generate_export_filename
from app.pdf.link_builder import build_href
from app.pdf.one_page_optimizer import auto_optimize_to_one_page, count_pages
from app.pdf.renderer import RenderSettings, render_resume_html, render_resume_pdf
from app.schemas.resume import PersonalInfo, ResumeData, ResumeSectionDTO


def _resume_with_n_bullets(n: int) -> ResumeData:
    bullets = [f"Delivered feature number {i} with measurable impact on production systems." for i in range(n)]
    return ResumeData(
        personal_info=PersonalInfo(name="Test User", email="test@example.com", phone="+1-555-000-1111"),
        sections=[
            ResumeSectionDTO(id="summary", type="summary", title="PROFESSIONAL SUMMARY", order=1, visible=True, content={"text": "Experienced engineer."}),
            ResumeSectionDTO(
                id="experience", type="experience", title="PROFESSIONAL EXPERIENCE", order=2, visible=True,
                content={"items": [{"id": "e1", "title": "Engineer", "company": "Acme", "startDate": "2020", "endDate": "Present", "bullets": bullets}]},
            ),
        ],
    )


def test_pdf_is_text_extractable_and_selectable():
    resume = _resume_with_n_bullets(3)
    pdf_bytes = render_resume_pdf(resume, RenderSettings())
    from app.parser.pdf_parser import has_extractable_text

    assert has_extractable_text(pdf_bytes)


def test_short_resume_fits_one_page():
    resume = _resume_with_n_bullets(3)
    pdf_bytes = render_resume_pdf(resume, RenderSettings())
    assert count_pages(pdf_bytes) == 1


def test_auto_optimizer_brings_long_resume_to_one_page():
    resume = _resume_with_n_bullets(40)
    pdf_bytes, final_settings, pages = auto_optimize_to_one_page(resume, RenderSettings())
    assert pages == 1
    assert final_settings.font_size_pt >= 10.0  # never below the configured floor


def test_docx_export_produces_valid_bytes():
    resume = _resume_with_n_bullets(3)
    docx_bytes = render_resume_docx(resume, RenderSettings())
    assert docx_bytes[:2] == b"PK"  # docx is a zip archive
    assert len(docx_bytes) > 1000


def test_filename_with_company_and_role():
    name = generate_export_filename("Snehal Sukhadeve", "Barclays", "Java Full Stack Developer", "pdf")
    assert name == "Snehal_Sukhadeve_Barclays_Java_Full_Stack_Developer.pdf"


def test_filename_without_role():
    name = generate_export_filename("Snehal Sukhadeve", "TCS", None, "pdf")
    assert name == "Snehal_Sukhadeve_TCS.pdf"


def test_filename_sanitizes_illegal_characters():
    name = generate_export_filename("Snehal Sukhadeve", "Acme/Corp: Inc?", None, "pdf")
    assert "/" not in name and ":" not in name and "?" not in name


def test_build_href_resolves_bare_handles_to_profile_urls():
    assert build_href("leetcode", "sqZl5JZ6jP") == "https://leetcode.com/sqZl5JZ6jP"
    assert build_href("hackerrank", "ssnehalsukhadeve") == "https://www.hackerrank.com/profile/ssnehalsukhadeve"
    assert build_href("email", "a@b.com") == "mailto:a@b.com"
    assert build_href("linkedin", "linkedin.com/in/x") == "https://linkedin.com/in/x"
    assert build_href("linkedin", "https://linkedin.com/in/x") == "https://linkedin.com/in/x"


def test_pdf_html_renders_real_clickable_links_not_plain_text():
    resume = ResumeData(
        personal_info=PersonalInfo(
            name="Test User",
            email="test@example.com",
            linkedin="linkedin.com/in/testuser",
            github="github.com/testuser",
        ),
        sections=[],
    )
    html = render_resume_html(resume, RenderSettings())
    assert '<a href="mailto:test@example.com">test@example.com</a>' in html
    assert '<a href="https://linkedin.com/in/testuser">linkedin.com/in/testuser</a>' in html
    assert '<a href="https://github.com/testuser">GitHub: github.com/testuser</a>' in html


def test_colored_skill_tag_styles_keep_skills_on_one_extractable_line():
    """The 'bold' and 'accent' template styles render each skill as its own
    colored chip. Chips built with horizontal CSS padding make WeasyPrint
    emit a separate PDF text run per chip, which real-world ATS text
    extractors then read as N one-word lines instead of a single
    comma-separated skills line — silently breaking keyword matching. Guards
    against that regression for every style, not just the two colored ones."""
    from app.parser.pdf_parser import extract_lines_from_pdf

    resume = ResumeData(
        personal_info=PersonalInfo(name="Test User", email="test@example.com", phone="+1-555-000-1111"),
        sections=[
            ResumeSectionDTO(
                id="skills", type="skills", title="TECHNICAL SKILLS", order=1, visible=True,
                content={"categories": [{"name": "Languages", "items": ["Python", "TypeScript", "Go", "SQL"]}]},
            ),
        ],
    )
    for style_id in ["classic", "modern", "minimal", "executive", "compact", "bold", "accent"]:
        pdf_bytes = render_resume_pdf(resume, RenderSettings(template_id=style_id))
        lines = extract_lines_from_pdf(pdf_bytes)
        skills_lines = [l for l in lines if "Languages" in l]
        assert len(skills_lines) == 1, f"style={style_id}: skills split across {len(skills_lines)} lines: {lines}"
        for skill in ["Python", "TypeScript", "Go", "SQL"]:
            assert skill in skills_lines[0], f"style={style_id}: {skill!r} missing from skills line {skills_lines[0]!r}"


def test_docx_contact_links_are_real_hyperlinks_not_plain_text():
    resume = ResumeData(
        personal_info=PersonalInfo(
            name="Test User", email="test@example.com", linkedin="linkedin.com/in/testuser", leetcode="handle123"
        ),
        sections=[],
    )
    docx_bytes = render_resume_docx(resume, RenderSettings())

    import zipfile
    import io

    z = zipfile.ZipFile(io.BytesIO(docx_bytes))
    rels = z.read("word/_rels/document.xml.rels").decode("utf-8")
    doc_xml = z.read("word/document.xml").decode("utf-8")

    assert "<w:hyperlink " in doc_xml
    assert 'Target="mailto:test@example.com"' in rels
    assert 'Target="https://linkedin.com/in/testuser"' in rels
    assert 'Target="https://leetcode.com/handle123"' in rels
