from sqlalchemy.orm import Session

from app.models.ats_analysis import AtsAnalysis
from app.schemas.ats import AtsScoreBreakdown


class AtsAnalysisRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, resume_id: int, job_description_id: int | None, score: AtsScoreBreakdown) -> AtsAnalysis:
        record = AtsAnalysis(
            resume_id=resume_id,
            job_description_id=job_description_id,
            overall_score=score.overall_score,
            keyword_match_pct=score.keyword_match_pct,
            skills_match_pct=score.skills_match_pct,
            title_match_pct=score.title_match_pct,
            experience_relevance_pct=score.experience_relevance_pct,
            section_completeness_pct=score.section_completeness_pct,
            parsing_accuracy_pct=score.parsing_accuracy_pct,
            formatting_compatibility_pct=score.formatting_compatibility_pct,
            readability_pct=score.readability_pct,
            matched_keywords=score.matched_keywords,
            missing_keywords=score.missing_keywords,
            related_keywords=score.related_keywords,
            formatting_warnings=score.formatting_warnings,
            section_warnings=score.section_warnings,
            suggestions=score.suggestions,
            parsing_checklist={k: v.model_dump(by_alias=True) for k, v in score.parsing_checklist.items()},
            page_count=score.page_count,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def latest_for_resume(self, resume_id: int) -> AtsAnalysis | None:
        return (
            self.db.query(AtsAnalysis)
            .filter(AtsAnalysis.resume_id == resume_id)
            .order_by(AtsAnalysis.created_at.desc())
            .first()
        )
