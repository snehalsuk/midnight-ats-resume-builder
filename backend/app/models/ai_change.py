from typing import Any

from sqlalchemy import JSON, Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.mixins import TimestampMixin


class AiChange(Base, TimestampMixin):
    """One proposed AI edit (summary rewrite, bullet rewrite, skill reorder,
    etc.) surfaced for Accept/Reject review (spec §26). Never applied until
    the user accepts it.
    """

    __tablename__ = "ai_changes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id"), nullable=False, index=True)

    target_path: Mapped[str] = mapped_column(String(200), nullable=False)  # e.g. "sections.summary.content"
    change_type: Mapped[str] = mapped_column(String(40), nullable=False)  # summary|bullet|skills_reorder
    original_value: Mapped[str] = mapped_column(Text, nullable=False)
    suggested_value: Mapped[str] = mapped_column(Text, nullable=False)
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDING")  # PENDING|ACCEPTED|REJECTED
    fabrication_risk: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    blocked_locked_field: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    resume: Mapped["Resume"] = relationship()  # noqa: F821
