from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.resume import Resume
from app.models.user import User
from app.pdf.template_styles import TEMPLATE_STYLES
from app.repositories.resume_repo import ResumeRepository
from app.schemas.resume import ResumeCreateRequest, ResumeResponse, ResumeUpdateRequest, TemplateStyleResponse
from app.security.deps import get_current_user
from app.services.resume_service import ResumeService
from app.services.upload_service import UploadService

router = APIRouter(prefix="/resumes", tags=["resumes"])


def _to_response(db: Session, resume: Resume) -> ResumeResponse:
    data = ResumeRepository(db).to_resume_data(resume)
    return ResumeResponse(
        id=resume.id,
        kind=resume.kind,
        name=resume.name,
        company=resume.company,
        role_title=resume.role_title,
        template_id=resume.template_id,
        font_family=resume.font_family,
        font_size_pt=resume.font_size_pt,
        heading_size_pt=resume.heading_size_pt,
        line_spacing=resume.line_spacing,
        section_spacing_pt=resume.section_spacing_pt,
        bullet_spacing_pt=resume.bullet_spacing_pt,
        margin_in=resume.margin_in,
        page_count=resume.page_count,
        last_ats_score=resume.last_ats_score,
        parent_id=resume.parent_id,
        job_description_id=resume.job_description_id,
        personal_info=data.personal_info,
        sections=data.sections,
    )


@router.get("/templates", response_model=list[TemplateStyleResponse])
def list_templates():
    return [TemplateStyleResponse(**vars(style)) for style in TEMPLATE_STYLES.values()]


@router.post("/upload", response_model=ResumeResponse, status_code=201)
async def upload_resume(
    file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    content = await file.read()
    resume = UploadService(db).create_master_resume_from_upload(user.id, file.filename or "resume", content)
    return _to_response(db, resume)


@router.post("", response_model=ResumeResponse, status_code=201)
def create_resume(req: ResumeCreateRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    resume = ResumeService(db).create_blank(user.id, req)
    return _to_response(db, resume)


@router.get("", response_model=list[ResumeResponse])
def list_resumes(kind: str | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    resumes = ResumeService(db).list_for_owner(user.id, kind)
    return [_to_response(db, r) for r in resumes]


@router.get("/{resume_id}", response_model=ResumeResponse)
def get_resume(resume_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    resume = ResumeService(db).get_owned(resume_id, user.id)
    return _to_response(db, resume)


@router.put("/{resume_id}", response_model=ResumeResponse)
def update_resume(
    resume_id: int, req: ResumeUpdateRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    service = ResumeService(db)
    resume = service.get_owned(resume_id, user.id)
    resume = service.update(resume, req)
    return _to_response(db, resume)


@router.delete("/{resume_id}", status_code=204)
def delete_resume(resume_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service = ResumeService(db)
    resume = service.get_owned(resume_id, user.id)
    service.delete(resume)


@router.post("/{resume_id}/duplicate", response_model=ResumeResponse, status_code=201)
def duplicate_resume(resume_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service = ResumeService(db)
    resume = service.get_owned(resume_id, user.id)
    duplicate = service.duplicate(resume)
    return _to_response(db, duplicate)


@router.get("/{resume_id}/versions", response_model=list[ResumeResponse])
def list_versions(resume_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service = ResumeService(db)
    service.get_owned(resume_id, user.id)  # ownership check
    versions = service.versions_for_master(resume_id)
    return [_to_response(db, v) for v in versions]


@router.get("/{resume_id}/diff")
def diff_resume(
    resume_id: int, compare_to_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    """Compare this resume (typically the Master) against another version
    of it (spec §31) — added/removed/modified/reordered sections."""
    from app.services.diff_service import diff_resumes

    service = ResumeService(db)
    resume_a = service.get_owned(resume_id, user.id)
    resume_b = service.get_owned(compare_to_id, user.id)
    repo = ResumeRepository(db)
    return diff_resumes(repo.to_resume_data(resume_a), repo.to_resume_data(resume_b))
