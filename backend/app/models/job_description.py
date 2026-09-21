from typing import Any

from sqlalchemy import JSON, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.mixins import TimestampMixin


class JobDescription(Base, TimestampMixin):
    __tablename__ = "job_descriptions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    company: Mapped[str | None] = mapped_column(String(150), nullable=True)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)

    # structured extraction result (spec §15), Pydantic-validated before save
    parsed: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    owner: Mapped["User"] = relationship(back_populates="job_descriptions")  # noqa: F821
