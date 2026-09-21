from sqlalchemy.orm import Session

from app.models.ai_change import AiChange
from app.schemas.ai import SkillAddition, TailorResult


class AiChangeRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_summary_change(self, resume_id: int, original: str, suggested: str, fabrication_risk: bool) -> AiChange:
        change = AiChange(
            resume_id=resume_id,
            target_path="sections.summary.content.text",
            change_type="summary",
            original_value=original,
            suggested_value=suggested,
            fabrication_risk=fabrication_risk,
        )
        self.db.add(change)
        return change

    def save_bullet_changes(self, resume_id: int, tailor_result: TailorResult, blocked_paths: set[str]) -> list[AiChange]:
        changes = []
        for bc in tailor_result.bullet_changes:
            change = AiChange(
                resume_id=resume_id,
                target_path=bc.target_path,
                change_type="bullet",
                original_value=bc.original_text,
                suggested_value=bc.suggested_text,
                fabrication_risk=tailor_result.fabrication_risk,
                blocked_locked_field=bc.target_path in blocked_paths,
            )
            self.db.add(change)
            changes.append(change)
        return changes

    def save_skill_additions(self, resume_id: int, skill_additions: list[SkillAddition]) -> list[AiChange]:
        changes = []
        for sa in skill_additions:
            change = AiChange(
                resume_id=resume_id,
                target_path=f"skills.{sa.category}",
                change_type="skill",
                original_value="",
                suggested_value=sa.skill,
                fabrication_risk=False,  # only ever created for candidate-confirmed skills
            )
            self.db.add(change)
            changes.append(change)
        return changes

    def commit(self) -> None:
        self.db.commit()

    def list_for_resume(self, resume_id: int) -> list[AiChange]:
        return self.db.query(AiChange).filter(AiChange.resume_id == resume_id).order_by(AiChange.created_at).all()

    def get(self, change_id: int) -> AiChange | None:
        return self.db.query(AiChange).filter(AiChange.id == change_id).first()

    def set_status(self, change: AiChange, status: str) -> None:
        change.status = status
        self.db.commit()
