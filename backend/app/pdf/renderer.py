"""Renders a ResumeData + render-settings pair to HTML (used for both the
live preview and, via WeasyPrint, the exported PDF) so preview and export
can never visually drift (spec §10).
"""

from dataclasses import dataclass
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.pdf.link_builder import build_personal_links
from app.pdf.template_styles import get_template_style
from app.schemas.resume import ResumeData

TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "templates"

_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html", "jinja"]),
)

# every style shares this one file — only CSS branches on template_style
_TEMPLATE_FILE = "professional_ats.html.jinja"


@dataclass
class RenderSettings:
    template_id: str = "classic"
    font_family: str = "Calibri"
    font_size_pt: float = 11.0
    heading_size_pt: float = 12.5
    line_spacing: float = 1.15
    section_spacing_pt: float = 10.0
    bullet_spacing_pt: float = 3.0
    margin_in: float = 0.65
    page_size: str = "A4"


def _contact_items(personal_info: dict, links: dict[str, str]) -> tuple[list[dict], list[dict]]:
    line1 = []
    if personal_info.get("location"):
        line1.append({"text": personal_info["location"], "href": None})
    if personal_info.get("email"):
        line1.append({"text": personal_info["email"], "href": links["email"]})
    if personal_info.get("phone"):
        line1.append({"text": personal_info["phone"], "href": None})
    if personal_info.get("linkedin"):
        line1.append({"text": personal_info["linkedin"], "href": links["linkedin"]})

    line2 = []
    if personal_info.get("github"):
        line2.append({"text": f"GitHub: {personal_info['github']}", "href": links["github"]})
    if personal_info.get("portfolio"):
        line2.append({"text": f"Portfolio: {personal_info['portfolio']}", "href": links["portfolio"]})
    if personal_info.get("leetcode"):
        line2.append({"text": f"LeetCode: {personal_info['leetcode']}", "href": links["leetcode"]})
    if personal_info.get("hackerrank"):
        line2.append({"text": f"HackerRank: {personal_info['hackerrank']}", "href": links["hackerrank"]})

    return line1, line2


def render_resume_html(resume: ResumeData, settings: RenderSettings) -> str:
    template = _env.get_template(_TEMPLATE_FILE)
    style = get_template_style(settings.template_id)
    personal_info = resume.personal_info.model_dump(by_alias=True)
    links = build_personal_links(personal_info)
    contact_line_1, contact_line_2 = _contact_items(personal_info, links)
    return template.render(
        personal_info=personal_info,
        contact_line_1=contact_line_1,
        contact_line_2=contact_line_2,
        sections=[s.model_dump(by_alias=True) for s in resume.sections],
        font_family=settings.font_family,
        font_size_pt=settings.font_size_pt,
        heading_size_pt=settings.heading_size_pt,
        line_spacing=settings.line_spacing,
        section_spacing_pt=settings.section_spacing_pt,
        bullet_spacing_pt=settings.bullet_spacing_pt,
        margin_in=settings.margin_in,
        page_size=settings.page_size,
        template_style=style.id,
        accent_color=style.accent_color,
    )


def render_resume_pdf(resume: ResumeData, settings: RenderSettings) -> bytes:
    # imported lazily: WeasyPrint pulls in native deps (cairo/pango) that
    # aren't needed for the HTML preview path or in unit tests that don't
    # touch PDF generation.
    from weasyprint import HTML

    html = render_resume_html(resume, settings)
    return HTML(string=html, base_url=str(TEMPLATES_DIR)).write_pdf()
