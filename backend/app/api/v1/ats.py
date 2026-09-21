from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.user import User
from app.schemas.ats import AtsScoreBreakdown
from app.schemas.resume import _to_camel
from app.security.deps import get_current_user
from app.services.ats_service import AtsService
from app.services.resume_service import ResumeService

router = APIRouter(prefix="/resumes", tags=["ats"])


class AtsAnalyzeRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=_to_camel)
    job_description_id: int | None = None


@router.post("/{resume_id}/ats/analyze", response_model=AtsScoreBreakdown)
def analyze_ats(
    resume_id: int,
    req: AtsAnalyzeRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    resume = ResumeService(db).get_owned(resume_id, user.id)
    return AtsService(db).analyze(resume, req.job_description_id)
