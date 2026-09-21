from sqlalchemy.orm import Session

from app.models.resume_export import ResumeExport


class ResumeExportRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, resume_id: int, fmt: str, filename: str, storage_path: str, page_count: int | None) -> ResumeExport:
        record = ResumeExport(
            resume_id=resume_id, format=fmt, filename=filename, storage_path=storage_path, page_count=page_count
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def list_for_resume(self, resume_id: int) -> list[ResumeExport]:
        return (
            self.db.query(ResumeExport)
            .filter(ResumeExport.resume_id == resume_id)
            .order_by(ResumeExport.created_at.desc())
            .all()
        )
