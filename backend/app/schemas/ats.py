from pydantic import BaseModel, ConfigDict, Field

from app.schemas.resume import _to_camel


class ParsingChecklistItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=_to_camel)
    detected: bool
    reason: str | None = None


class AtsScoreBreakdown(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=_to_camel)

    overall_score: float
    keyword_match_pct: float
    skills_match_pct: float
    title_match_pct: float
    experience_relevance_pct: float
    section_completeness_pct: float
    parsing_accuracy_pct: float
    formatting_compatibility_pct: float
    readability_pct: float

    matched_keywords: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    related_keywords: list[str] = Field(default_factory=list)

    formatting_warnings: list[str] = Field(default_factory=list)
    section_warnings: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)

    parsing_checklist: dict[str, ParsingChecklistItem] = Field(default_factory=dict)
    page_count: int | None = None
    one_page_ok: bool = False


class QualityGateResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=_to_camel)
    passed: bool
    failed_checks: list[str] = Field(default_factory=list)
