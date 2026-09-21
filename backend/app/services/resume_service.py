from sqlalchemy.orm import Session

from app.exceptions.errors import NotFoundError, ValidationAppError
from app.models.resume import Resume
from app.pdf.template_styles import TEMPLATE_STYLES
from app.repositories.resume_repo import ResumeRepository
from app.schemas.resume import DEFAULT_SECTION_ORDER, PersonalInfo, ResumeCreateRequest, ResumeSectionDTO, ResumeUpdateRequest


class ResumeService:
    def __init__(self, db: Session):
        self.repo = ResumeRepository(db)

    def get_owned(self, resume_id: int, owner_id: int) -> Resume:
        resume = self.repo.get(resume_id)
        if resume is None or resume.owner_id != owner_id:
            raise NotFoundError("Resume not found.")
        return resume

    def list_for_owner(self, owner_id: int, kind: str | None = None) -> list[Resume]:
        return self.repo.list_for_owner(owner_id, kind)

    def create_blank(self, owner_id: int, req: ResumeCreateRequest) -> Resume:
        _validate_template_id(req.template_id)
        sections = req.sections or [
            ResumeSectionDTO(id=key, type=stype, title=title, order=i, visible=True, content=_default_content(stype))
            for i, (key, stype, title) in enumerate(DEFAULT_SECTION_ORDER, start=1)
        ]
        return self.repo.create(
            owner_id=owner_id,
            name=req.name,
            personal_info=req.personal_info,
            sections=sections,
            template_id=req.template_id,
        )

    def update(self, resume: Resume, req: ResumeUpdateRequest) -> Resume:
        if req.sections is not None:
            _validate_section_orders(req.sections)
        if req.template_id is not None:
            _validate_template_id(req.template_id)
        return self.repo.update(
            resume,
            name=req.name,
            personal_info=req.personal_info,
            sections=req.sections,
            company=req.company,
            role_title=req.role_title,
            template_id=req.template_id,
            font_size_pt=req.font_size_pt,
            margin_in=req.margin_in,
            section_spacing_pt=req.section_spacing_pt,
            bullet_spacing_pt=req.bullet_spacing_pt,
        )

    def delete(self, resume: Resume) -> None:
        self.repo.delete(resume)

    def duplicate(self, resume: Resume, new_name: str | None = None) -> Resume:
        return self.repo.duplicate(resume, new_name or f"{resume.name} (copy)")

    def versions_for_master(self, master_id: int) -> list[Resume]:
        return self.repo.versions_for_master(master_id)


def _default_content(section_type: str) -> dict:
    if section_type == "summary":
        return {"text": ""}
    if section_type == "skills":
        return {"categories": []}
    if section_type in ("experience", "projects", "education", "certifications"):
        return {"items": []}
    return {"text": ""}


def _validate_section_orders(sections: list[ResumeSectionDTO]) -> None:
    ids = [s.id for s in sections]
    if len(ids) != len(set(ids)):
        raise ValidationAppError("Duplicate section ids are not allowed.")


def _validate_template_id(template_id: str) -> None:
    if template_id not in TEMPLATE_STYLES:
        raise ValidationAppError(
            f"Unknown template '{template_id}'.", details={"available": list(TEMPLATE_STYLES)}
        )
