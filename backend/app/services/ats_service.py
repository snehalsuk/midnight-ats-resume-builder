from sqlalchemy.orm import Session

from app.ats.parsing_simulator import run_parsing_simulation
from app.ats.scorer import compute_ats_score
from app.exceptions.errors import NotFoundError
from app.models.resume import Resume
from app.pdf.one_page_optimizer import count_pages
from app.pdf.renderer import RenderSettings, render_resume_pdf
from app.repositories.ats_repo import AtsAnalysisRepository
from app.repositories.job_description_repo import JobDescriptionRepository
from app.repositories.resume_repo import ResumeRepository
from app.schemas.ats import AtsScoreBreakdown


class AtsService:
    def __init__(self, db: Session):
        self.resume_repo = ResumeRepository(db)
        self.jd_repo = JobDescriptionRepository(db)
        self.ats_repo = AtsAnalysisRepository(db)

    def analyze(self, resume: Resume, job_description_id: int | None) -> AtsScoreBreakdown:
        resume_data = self.resume_repo.to_resume_data(resume)

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
        pdf_bytes = render_resume_pdf(resume_data, settings)
        page_count = count_pages(pdf_bytes)
        checklist = run_parsing_simulation(resume_data, pdf_bytes)

        jd = None
        jd_id = job_description_id or resume.job_description_id
        if jd_id:
            jd_row = self.jd_repo.get(jd_id)
            if jd_row is None:
                raise NotFoundError("Job description not found.")
            jd = self.jd_repo.to_parsed(jd_row)

        score = compute_ats_score(resume_data, jd, checklist, page_count)
        self.ats_repo.save(resume.id, jd_id, score)

        resume.page_count = page_count
        resume.last_ats_score = score.overall_score
        self.resume_repo.db.commit()

        return score
