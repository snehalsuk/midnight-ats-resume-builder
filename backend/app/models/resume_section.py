from typing import Any

from sqlalchemy import JSON, Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.mixins import TimestampMixin


class ResumeSection(Base, TimestampMixin):
    """One row per resume section. `content` holds the type-specific
    structured payload (summary text, skill categories, experience items,
    project items, education items, certification items, or free-form
    content for custom sections) so new section types never require a
    schema migration.
    """

    __tablename__ = "resume_sections"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id"), nullable=False, index=True)

    section_key: Mapped[str] = mapped_column(String(80), nullable=False)  # stable id, e.g. "experience"
    type: Mapped[str] = mapped_column(String(40), nullable=False)  # summary|skills|experience|projects|...
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    visible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    content: Mapped[dict[str, Any] | list[Any]] = mapped_column(JSON, nullable=False, default=dict)

    resume: Mapped["Resume"] = relationship(back_populates="sections")  # noqa: F821
