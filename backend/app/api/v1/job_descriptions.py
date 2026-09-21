from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.ai.factory import get_ai_provider
from app.core.db import get_db
from app.models.user import User
from app.schemas.job_description import JobDescriptionCreateRequest, JobDescriptionResponse
from app.security.deps import get_current_user
from app.services.jd_service import JobDescriptionService

router = APIRouter(prefix="/job-descriptions", tags=["job-descriptions"])


def _to_response(jd) -> JobDescriptionResponse:
    return JobDescriptionResponse(id=jd.id, company=jd.company, raw_text=jd.raw_text, parsed=jd.parsed)


@router.post("/analyze", response_model=JobDescriptionResponse, status_code=201)
def analyze_job_description(
    req: JobDescriptionCreateRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    service = JobDescriptionService(db, get_ai_provider)
    jd = service.analyze_and_save(user.id, req.company, req.raw_text)
    return _to_response(jd)


@router.get("", response_model=list[JobDescriptionResponse])
def list_job_descriptions(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service = JobDescriptionService(db, get_ai_provider)
    return [_to_response(jd) for jd in service.list_for_owner(user.id)]


@router.get("/{jd_id}", response_model=JobDescriptionResponse)
def get_job_description(jd_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service = JobDescriptionService(db, get_ai_provider)
    jd = service.get_owned(jd_id, user.id)
    return _to_response(jd)
