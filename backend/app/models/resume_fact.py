from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.mixins import TimestampMixin

# Fields that the AI is never allowed to silently rewrite (spec §25).
LOCKED_FACT_KEYS = (
    "personalInfo.name",
    "personalInfo.phone",
    "personalInfo.email",
    "personalInfo.linkedin",
    "personalInfo.github",
    "education",
    "experience.dates",
    "experience.company",
    "experience.title",
    "certifications",
)


class ResumeFact(Base, TimestampMixin):
    """Snapshot of a locked factual value, keyed by a dotted path into the
    resume JSON, so AI diffs and change-review can be checked against it.
    """

    __tablename__ = "resume_facts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id"), nullable=False, index=True)

    fact_key: Mapped[str] = mapped_column(String(150), nullable=False)  # e.g. "personalInfo.email"
    value: Mapped[str] = mapped_column(Text, nullable=False)
    locked: Mapped[bool] = mapped_column(default=True)

    resume: Mapped["Resume"] = relationship(back_populates="facts")  # noqa: F821
