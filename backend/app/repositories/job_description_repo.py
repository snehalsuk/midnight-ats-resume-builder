from sqlalchemy.orm import Session

from app.models.job_description import JobDescription
from app.schemas.job_description import ParsedJobDescription


class JobDescriptionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, jd_id: int) -> JobDescription | None:
        return self.db.query(JobDescription).filter(JobDescription.id == jd_id).first()

    def list_for_owner(self, owner_id: int) -> list[JobDescription]:
        return (
            self.db.query(JobDescription)
            .filter(JobDescription.owner_id == owner_id)
            .order_by(JobDescription.created_at.desc())
            .all()
        )

    def create(self, owner_id: int, company: str | None, raw_text: str, parsed: ParsedJobDescription) -> JobDescription:
        jd = JobDescription(
            owner_id=owner_id, company=company, raw_text=raw_text, parsed=parsed.model_dump(by_alias=True)
        )
        self.db.add(jd)
        self.db.commit()
        self.db.refresh(jd)
        return jd

    def to_parsed(self, jd: JobDescription) -> ParsedJobDescription:
        return ParsedJobDescription.model_validate(jd.parsed)
