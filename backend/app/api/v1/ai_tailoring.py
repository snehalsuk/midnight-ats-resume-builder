from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.ai.factory import get_ai_provider
from app.core.db import get_db
from app.exceptions.errors import NotFoundError
from app.models.user import User
from app.schemas.ai import TailorResult
from app.schemas.resume import _to_camel
from app.security.deps import get_current_user
from app.services.ai_tailor_service import AiTailorService
from app.services.resume_service import ResumeService

router = APIRouter(prefix="/resumes", tags=["ai-tailoring"])


class OptimizeRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=_to_camel)
    job_description_id: int
    # skills the candidate explicitly asserted they genuinely have, from the
    # ATS panel's missing-keywords list — the only skills Optimize is
    # allowed to propose adding to the resume (see ai_tailor_service.propose).
    confirmed_skills: list[str] = []


class AiChangeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, alias_generator=_to_camel)

    id: int
    target_path: str
    change_type: str
    original_value: str
    suggested_value: str
    status: str
    fabrication_risk: bool
    blocked_locked_field: bool


@router.post("/{resume_id}/optimize", response_model=TailorResult)
def optimize_resume(
    resume_id: int, req: OptimizeRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    resume = ResumeService(db).get_owned(resume_id, user.id)
    service = AiTailorService(db, get_ai_provider)
    return service.propose(resume, req.job_description_id, req.confirmed_skills)


@router.get("/{resume_id}/ai-changes", response_model=list[AiChangeResponse])
def list_ai_changes(resume_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ResumeService(db).get_owned(resume_id, user.id)
    service = AiTailorService(db, get_ai_provider)
    return service.list_pending(resume_id)


@router.post("/{resume_id}/ai-changes/{change_id}/accept", response_model=AiChangeResponse)
def accept_ai_change(
    resume_id: int, change_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    resume = ResumeService(db).get_owned(resume_id, user.id)
    service = AiTailorService(db, get_ai_provider)
    change = service.change_repo.get(change_id)
    if change is None or change.resume_id != resume.id:
        raise NotFoundError("AI change not found.")
    service.accept(resume, change)
    return change


@router.post("/{resume_id}/ai-changes/{change_id}/reject", response_model=AiChangeResponse)
def reject_ai_change(
    resume_id: int, change_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    resume = ResumeService(db).get_owned(resume_id, user.id)
    service = AiTailorService(db, get_ai_provider)
    change = service.change_repo.get(change_id)
    if change is None or change.resume_id != resume.id:
        raise NotFoundError("AI change not found.")
    service.reject(change)
    return change


@router.post("/{resume_id}/ai-changes/accept-all", status_code=204)
def accept_all_ai_changes(resume_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    resume = ResumeService(db).get_owned(resume_id, user.id)
    service = AiTailorService(db, get_ai_provider)
    service.accept_all(resume)
