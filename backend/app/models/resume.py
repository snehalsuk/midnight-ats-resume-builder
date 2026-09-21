from typing import Any

from sqlalchemy import JSON, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.mixins import TimestampMixin


class Resume(Base, TimestampMixin):
    """Represents both the Master Resume (kind=MASTER) and tailored resume
    versions (kind=VERSION). A VERSION always has parent_id pointing at its
    MASTER and, usually, a job_description_id it was tailored against.
    """

    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("resumes.id"), nullable=True, index=True)
    job_description_id: Mapped[int | None] = mapped_column(
        ForeignKey("job_descriptions.id"), nullable=True
    )

    kind: Mapped[str] = mapped_column(String(20), nullable=False, default="MASTER")  # MASTER | VERSION
    name: Mapped[str] = mapped_column(String(255), nullable=False, default="Master Resume")

    # personalInfo block from the resume JSON schema (spec §4)
    personal_info: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    # template / rendering settings, adjusted by the one-page optimizer
    template_id: Mapped[str] = mapped_column(String(50), nullable=False, default="classic")
    font_family: Mapped[str] = mapped_column(String(50), nullable=False, default="Calibri")
    font_size_pt: Mapped[float] = mapped_column(Float, nullable=False, default=11.0)
    heading_size_pt: Mapped[float] = mapped_column(Float, nullable=False, default=12.5)
    line_spacing: Mapped[float] = mapped_column(Float, nullable=False, default=1.15)
    section_spacing_pt: Mapped[float] = mapped_column(Float, nullable=False, default=10.0)
    bullet_spacing_pt: Mapped[float] = mapped_column(Float, nullable=False, default=3.0)
    margin_in: Mapped[float] = mapped_column(Float, nullable=False, default=0.65)

    company: Mapped[str | None] = mapped_column(String(150), nullable=True)
    role_title: Mapped[str | None] = mapped_column(String(150), nullable=True)

    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_ats_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    source_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)

    owner: Mapped["User"] = relationship(back_populates="resumes")  # noqa: F821
    job_description: Mapped["JobDescription | None"] = relationship()  # noqa: F821
    sections: Mapped[list["ResumeSection"]] = relationship(
        back_populates="resume", cascade="all, delete-orphan", order_by="ResumeSection.order"
    )
    facts: Mapped[list["ResumeFact"]] = relationship(back_populates="resume", cascade="all, delete-orphan")

    parent: Mapped["Resume | None"] = relationship(remote_side=[id], back_populates="versions")
    versions: Mapped[list["Resume"]] = relationship(back_populates="parent")
