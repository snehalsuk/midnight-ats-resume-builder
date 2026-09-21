"""Export pipeline (spec §44): validate -> one-page check/auto-optimize ->
render -> re-parse the generated file -> compare -> final quality gate ->
export. Nothing is silently exported if the quality gate fails.
"""

from pathlib import Path

from sqlalchemy.orm import Session

from app.ats.link_validator import validate_links
from app.ats.parsing_simulator import run_parsing_simulation
from app.core.config import get_settings
from app.exceptions.errors import QualityGateError
from app.models.resume import Resume
from app.pdf.docx_renderer import render_resume_docx
from app.pdf.filename import generate_export_filename
from app.pdf.one_page_optimizer import auto_optimize_to_one_page, estimate_overflow_section
from app.pdf.renderer import RenderSettings
from app.repositories.export_repo import ResumeExportRepository
from app.repositories.resume_repo import ResumeRepository
from app.schemas.ats import QualityGateResult

EXPORTS_DIR = Path(__file__).resolve().parent.parent.parent / "exports"


class ExportService:
    def __init__(self, db: Session):
        self.resume_repo = ResumeRepository(db)
        self.export_repo = ResumeExportRepository(db)
        EXPORTS_DIR.mkdir(exist_ok=True)

    def _render_settings(self, resume: Resume) -> RenderSettings:
        return RenderSettings(
            template_id=resume.template_id,
            font_family=resume.font_family,
            font_size_pt=resume.font_size_pt,
            heading_size_pt=resume.heading_size_pt,
            line_spacing=resume.line_spacing,
            section_spacing_pt=resume.section_spacing_pt,
            bullet_spacing_pt=resume.bullet_spacing_pt,
            margin_in=resume.margin_in,
        )

    def run_quality_gate(self, resume: Resume) -> tuple[QualityGateResult, bytes, int, RenderSettings]:
        resume_data = self.resume_repo.to_resume_data(resume)
        settings = self._render_settings(resume)

        pdf_bytes, final_settings, page_count = auto_optimize_to_one_page(resume_data, settings)
        checklist = run_parsing_simulation(resume_data, pdf_bytes)
        link_problems = validate_links(resume_data)

        failed: list[str] = []
        if page_count != 1:
            overflow = estimate_overflow_section(resume_data)
            failed.append(f"Resume exceeds one page ({page_count} pages)." + (f" {overflow}" if overflow else ""))
        if not checklist.get("name", None) or not checklist["name"].detected:
            failed.append("Name could not be verified in the exported document.")
        if not checklist.get("email") or not checklist["email"].detected:
            failed.append("Email could not be verified in the exported document.")
        if not checklist.get("phone") or not checklist["phone"].detected:
            failed.append("Phone number could not be verified in the exported document.")
        exp_section = next((s for s in resume_data.sections if s.type == "experience"), None)
        if exp_section and exp_section.content.get("items") and not checklist.get("experience", None):
            failed.append("Experience entries could not be verified in the exported document.")
        headings_present = any(s.visible for s in resume_data.sections)
        if not headings_present:
            failed.append("No visible section headings found.")
        failed.extend(link_problems)

        return QualityGateResult(passed=len(failed) == 0, failed_checks=failed), pdf_bytes, page_count, final_settings

    def export_pdf(self, resume: Resume) -> tuple[bytes, str, int]:
        gate_result, pdf_bytes, page_count, final_settings = self.run_quality_gate(resume)
        if not gate_result.passed:
            raise QualityGateError(
                "Resume did not pass the pre-export quality gate. Run Auto Optimize or fix the listed issues.",
                details={"failedChecks": gate_result.failed_checks},
            )

        filename = generate_export_filename(
            resume.personal_info.get("name", "Resume"), resume.company, resume.role_title, "pdf"
        )
        storage_path = EXPORTS_DIR / filename
        storage_path.write_bytes(pdf_bytes)
        self.export_repo.save(resume.id, "PDF", filename, str(storage_path), page_count)

        resume.page_count = page_count
        resume.font_size_pt = final_settings.font_size_pt
        resume.margin_in = final_settings.margin_in
        resume.section_spacing_pt = final_settings.section_spacing_pt
        resume.bullet_spacing_pt = final_settings.bullet_spacing_pt
        resume.line_spacing = final_settings.line_spacing
        self.resume_repo.db.commit()

        return pdf_bytes, filename, page_count

    def export_docx(self, resume: Resume) -> tuple[bytes, str]:
        resume_data = self.resume_repo.to_resume_data(resume)
        settings = self._render_settings(resume)
        docx_bytes = render_resume_docx(resume_data, settings)

        filename = generate_export_filename(
            resume_data.personal_info.name, resume.company, resume.role_title, "docx"
        )
        storage_path = EXPORTS_DIR / filename
        storage_path.write_bytes(docx_bytes)
        self.export_repo.save(resume.id, "DOCX", filename, str(storage_path), None)

        return docx_bytes, filename
