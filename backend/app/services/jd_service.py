from collections.abc import Callable

from sqlalchemy.orm import Session

from app.ai.base import AIProvider
from app.ats.jd_sanitizer import sanitize_atomic_terms
from app.exceptions.errors import NotFoundError
from app.models.job_description import JobDescription
from app.repositories.job_description_repo import JobDescriptionRepository

_ATOMIC_TERM_FIELDS = (
    "required_skills", "preferred_skills", "technologies", "tools",
    "cloud_technologies", "frameworks", "databases",
)


class JobDescriptionService:
    def __init__(self, db: Session, ai_provider_factory: Callable[[], AIProvider]):
        self.repo = JobDescriptionRepository(db)
        self._ai_provider_factory = ai_provider_factory

    def analyze_and_save(self, owner_id: int, company: str | None, raw_text: str) -> JobDescription:
        # resolved lazily: listing/reading a JD must work even when no AI
        # provider is configured — only analyzing a *new* JD needs it.
        ai = self._ai_provider_factory()
        parsed = ai.parse_job_description(raw_text)

        # deterministic backstop: even with explicit prompt instructions, the
        # model can still emit a full requirement sentence instead of an
        # atomic skill name — strip anything sentence-shaped before it
        # pollutes keyword matching and the ATS score.
        for field in _ATOMIC_TERM_FIELDS:
            setattr(parsed, field, sanitize_atomic_terms(getattr(parsed, field)))

        return self.repo.create(owner_id=owner_id, company=company, raw_text=raw_text, parsed=parsed)

    def get_owned(self, jd_id: int, owner_id: int) -> JobDescription:
        jd = self.repo.get(jd_id)
        if jd is None or jd.owner_id != owner_id:
            raise NotFoundError("Job description not found.")
        return jd

    def list_for_owner(self, owner_id: int) -> list[JobDescription]:
        return self.repo.list_for_owner(owner_id)
