from typing import Any

from sqlalchemy import JSON, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.mixins import TimestampMixin


class AtsAnalysis(Base, TimestampMixin):
    __tablename__ = "ats_analysis"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id"), nullable=False, index=True)
    job_description_id: Mapped[int | None] = mapped_column(
        ForeignKey("job_descriptions.id"), nullable=True
    )

    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    keyword_match_pct: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    skills_match_pct: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    title_match_pct: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    experience_relevance_pct: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    section_completeness_pct: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    parsing_accuracy_pct: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    formatting_compatibility_pct: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    readability_pct: Mapped[float] = mapped_column(Float, nullable=False, default=0)

    matched_keywords: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    missing_keywords: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    related_keywords: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)

    formatting_warnings: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    section_warnings: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    suggestions: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)

    parsing_checklist: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    resume: Mapped["Resume"] = relationship()  # noqa: F821
