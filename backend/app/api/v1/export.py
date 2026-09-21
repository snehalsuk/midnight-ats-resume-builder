import base64

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.user import User
from app.pdf.one_page_optimizer import count_pages
from app.pdf.renderer import RenderSettings, render_resume_html, render_resume_pdf
from app.repositories.resume_repo import ResumeRepository
from app.schemas.ats import QualityGateResult
from app.schemas.resume import ResumeData
from app.security.deps import get_current_user
from app.services.export_service import ExportService
from app.services.resume_service import ResumeService

router = APIRouter(prefix="/resumes", tags=["export"])


class PreviewResponse(BaseModel):
    html: str
    # authoritative page count from the real WeasyPrint render — the HTML
    # preview's on-screen height is not a reliable proxy for this (browsers
    # and WeasyPrint use different font metrics and don't handle @page
    # margins the same way), so this is computed from the actual PDF
    # pipeline the export button will use, not guessed from CSS pixels.
    pageCount: int


class ExportFileResponse(BaseModel):
    filename: str
    pageCount: int | None = None
    contentBase64: str


@router.get("/{resume_id}/preview", response_model=PreviewResponse)
def preview_resume(resume_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    resume = ResumeService(db).get_owned(resume_id, user.id)
    resume_data = ResumeRepository(db).to_resume_data(resume)
    settings = RenderSettings(
        template_id=resume.template_id,
        font_family=resume.font_family,
        font_size_pt=resume.font_size_pt,
        heading_size_pt=resume.heading_size_pt,
        line_spacing=resume.line_spacing,
        section_spacing_pt=resume.section_spacing_pt,
        bullet_spacing_pt=resume.bullet_spacing_pt,
        margin_in=resume.margin_in,
    )
    html = render_resume_html(resume_data, settings)
    page_count = count_pages(render_resume_pdf(resume_data, settings))
    return PreviewResponse(html=html, pageCount=page_count)


@router.post("/{resume_id}/preview", response_model=PreviewResponse)
def preview_resume_draft(
    resume_id: int, draft: ResumeData, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    """Renders unsaved editor state on the fly, so the live preview can
    reflect in-progress edits without writing to the database on every
    keystroke (spec §53)."""
    resume = ResumeService(db).get_owned(resume_id, user.id)
    settings = RenderSettings(
        template_id=resume.template_id,
        font_family=resume.font_family,
        font_size_pt=resume.font_size_pt,
        heading_size_pt=resume.heading_size_pt,
        line_spacing=resume.line_spacing,
        section_spacing_pt=resume.section_spacing_pt,
        bullet_spacing_pt=resume.bullet_spacing_pt,
        margin_in=resume.margin_in,
    )
    html = render_resume_html(draft, settings)
    page_count = count_pages(render_resume_pdf(draft, settings))
    return PreviewResponse(html=html, pageCount=page_count)


@router.post("/{resume_id}/validate", response_model=QualityGateResult)
def validate_resume(resume_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    resume = ResumeService(db).get_owned(resume_id, user.id)
    result, _pdf, _pages, _settings = ExportService(db).run_quality_gate(resume)
    return result


@router.post("/{resume_id}/export/pdf", response_model=ExportFileResponse)
def export_pdf(resume_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    resume = ResumeService(db).get_owned(resume_id, user.id)
    pdf_bytes, filename, page_count = ExportService(db).export_pdf(resume)
    return ExportFileResponse(
        filename=filename, pageCount=page_count, contentBase64=base64.b64encode(pdf_bytes).decode()
    )


@router.post("/{resume_id}/export/docx", response_model=ExportFileResponse)
def export_docx(resume_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    resume = ResumeService(db).get_owned(resume_id, user.id)
    docx_bytes, filename = ExportService(db).export_docx(resume)
    return ExportFileResponse(filename=filename, contentBase64=base64.b64encode(docx_bytes).decode())
