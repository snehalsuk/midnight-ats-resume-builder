"""AI Resume Tailoring orchestration (spec §18/§26). The AI proposes
changes; nothing is applied to a resume until the user explicitly accepts
it via the change-review endpoints, and anything touching a locked fact
field is stripped before it's even shown (spec §25 belt-and-suspenders
enforcement — the prompt already forbids it, this is the backstop).
"""

import re
from collections.abc import Callable

from sqlalchemy.orm import Session

from app.ai.base import AIProvider
from app.exceptions.errors import NotFoundError, ValidationAppError
from app.models.ai_change import AiChange
from app.models.resume import Resume
from app.repositories.ai_change_repo import AiChangeRepository
from app.repositories.job_description_repo import JobDescriptionRepository
from app.repositories.resume_repo import ResumeRepository
from app.schemas.ai import TailorResult
from app.schemas.resume import ResumeData

_BULLET_PATH_RE = re.compile(r"^(experience|projects)\.([^.]+)\.bullets\.(\d+)$")


class AiTailorService:
    def __init__(self, db: Session, ai_provider_factory: Callable[[], AIProvider]):
        self.resume_repo = ResumeRepository(db)
        self.jd_repo = JobDescriptionRepository(db)
        self.change_repo = AiChangeRepository(db)
        self._ai_provider_factory = ai_provider_factory

    def propose(
        self, resume: Resume, job_description_id: int, confirmed_skills: list[str] | None = None
    ) -> TailorResult:
        # resolved lazily: reviewing/accepting/rejecting already-proposed
        # changes must work even when no AI provider is configured — only
        # proposing new ones needs it.
        ai = self._ai_provider_factory()
        jd_row = self.jd_repo.get(job_description_id)
        if jd_row is None:
            raise NotFoundError("Job description not found.")

        resume_data = self.resume_repo.to_resume_data(resume)
        jd = self.jd_repo.to_parsed(jd_row)
        locked_summary = _locked_field_summary(resume_data)
        confirmed_skills = confirmed_skills or []

        result = ai.tailor_resume(resume_data, jd, locked_summary, confirmed_skills)
        blocked_paths = _validate_and_filter(result, resume_data)

        # Belt-and-suspenders (spec §25 pattern): the prompt already forbids
        # proposing a skill the candidate didn't confirm, but we never trust
        # that alone — anything the model returns that isn't in the
        # candidate's own confirmed list is dropped here before it's even
        # saved, so it can never reach the Accept/Reject UI.
        confirmed_lower = {s.strip().lower() for s in confirmed_skills if s.strip()}
        result.skill_additions = [sa for sa in result.skill_additions if sa.skill.strip().lower() in confirmed_lower]

        original_summary = _get_summary_text(resume_data)
        if result.summary and result.summary.strip() and result.summary.strip() != original_summary.strip():
            self.change_repo.save_summary_change(resume.id, original_summary, result.summary, result.fabrication_risk)
        self.change_repo.save_bullet_changes(resume.id, result, blocked_paths)
        self.change_repo.save_skill_additions(resume.id, result.skill_additions)
        self.change_repo.commit()
        return result

    def list_pending(self, resume_id: int) -> list[AiChange]:
        return [c for c in self.change_repo.list_for_resume(resume_id) if c.status == "PENDING"]

    def reject(self, change: AiChange) -> None:
        self.change_repo.set_status(change, "REJECTED")

    def accept(self, resume: Resume, change: AiChange) -> Resume:
        if change.blocked_locked_field:
            raise ValidationAppError("This change touches a locked field and cannot be applied.")
        resume_data = self.resume_repo.to_resume_data(resume)
        _apply_change(resume_data, change)
        self.change_repo.set_status(change, "ACCEPTED")
        return self.resume_repo.update(resume, sections=resume_data.sections)

    def accept_all(self, resume: Resume) -> Resume:
        pending = self.list_pending(resume.id)
        resume_data = self.resume_repo.to_resume_data(resume)
        applied_any = False
        for change in pending:
            if change.blocked_locked_field:
                continue
            _apply_change(resume_data, change)
            change.status = "ACCEPTED"
            applied_any = True
        if applied_any:
            resume = self.resume_repo.update(resume, sections=resume_data.sections)
        self.change_repo.commit()
        return resume


def _get_summary_text(resume_data: ResumeData) -> str:
    section = next((s for s in resume_data.sections if s.type == "summary"), None)
    return section.content.get("text", "") if section else ""


def _locked_field_summary(resume_data: ResumeData) -> str:
    info = resume_data.personal_info
    lines = [
        f"name={info.name}",
        f"phone={info.phone}",
        f"email={info.email}",
        f"linkedin={info.linkedin}",
        f"github={info.github}",
    ]
    for section in resume_data.sections:
        if section.type == "experience":
            for item in section.content.get("items", []):
                lines.append(
                    f"experience[{item.get('id')}]: company={item.get('company')}, title={item.get('title')}, "
                    f"dates={item.get('startDate')}-{item.get('endDate')}"
                )
        elif section.type == "education":
            for item in section.content.get("items", []):
                lines.append(f"education[{item.get('id')}]: {item.get('degree')} — {item.get('institution')}")
        elif section.type == "certifications":
            for item in section.content.get("items", []):
                lines.append(f"certification[{item.get('id')}]: {item.get('name')}")
    return "\n".join(lines)


def _validate_and_filter(result: TailorResult, resume_data: ResumeData) -> set[str]:
    """Returns the set of bullet target_paths that must be blocked because
    they don't resolve to a real, unlocked bullet on this resume."""
    valid_ids: dict[str, set[str]] = {"experience": set(), "projects": set()}
    for section in resume_data.sections:
        if section.type in valid_ids:
            for item in section.content.get("items", []):
                valid_ids[section.type].add(item.get("id", ""))

    blocked: set[str] = set()
    for bc in result.bullet_changes:
        m = _BULLET_PATH_RE.match(bc.target_path)
        if not m or m.group(2) not in valid_ids[m.group(1)]:
            blocked.add(bc.target_path)
    return blocked


_SKILL_PATH_RE = re.compile(r"^skills\.(.+)$")


def _apply_change(resume_data: ResumeData, change: AiChange) -> None:
    if change.change_type == "summary":
        section = next((s for s in resume_data.sections if s.type == "summary"), None)
        if section is not None:
            section.content["text"] = change.suggested_value
        return

    if change.change_type == "skill":
        m = _SKILL_PATH_RE.match(change.target_path)
        if not m:
            return
        category_name = m.group(1)
        section = next((s for s in resume_data.sections if s.type == "skills"), None)
        if section is None:
            return
        categories = section.content.setdefault("categories", [])
        category = next((c for c in categories if c.get("name", "").lower() == category_name.lower()), None)
        if category is None:
            category = {"name": category_name, "items": []}
            categories.append(category)
        items = category.setdefault("items", [])
        if not any(i.lower() == change.suggested_value.lower() for i in items):
            items.append(change.suggested_value)
        return

    m = _BULLET_PATH_RE.match(change.target_path)
    if not m:
        return
    section_type, item_id, index_str = m.group(1), m.group(2), int(m.group(3))
    section = next((s for s in resume_data.sections if s.type == section_type), None)
    if section is None:
        return
    item = next((i for i in section.content.get("items", []) if i.get("id") == item_id), None)
    if item is None or index_str >= len(item.get("bullets", [])):
        return
    item["bullets"][index_str] = change.suggested_value
