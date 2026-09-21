from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.mixins import TimestampMixin


class ResumeExport(Base, TimestampMixin):
    __tablename__ = "resume_exports"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id"), nullable=False, index=True)

    format: Mapped[str] = mapped_column(String(10), nullable=False)  # PDF | DOCX
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    resume: Mapped["Resume"] = relationship()  # noqa: F821
