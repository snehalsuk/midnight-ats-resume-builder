from pydantic import BaseModel, ConfigDict, Field

from app.schemas.resume import _to_camel


class BulletChange(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=_to_camel)
    target_path: str  # e.g. "experience.exp-1.bullets.0"
    original_text: str
    suggested_text: str


class SkillReorderSuggestion(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=_to_camel)
    category: str
    ordered_items: list[str] = Field(default_factory=list)


class SkillAddition(BaseModel):
    """A skill to add to the resume's Skills section — only ever proposed
    for skills the candidate explicitly confirmed they have (spec §18/§41:
    the AI itself may never introduce a skill unprompted). Still goes
    through the normal Accept/Reject diff flow like any other change."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=_to_camel)
    category: str
    skill: str


class TailorResult(BaseModel):
    """Structured output contract for the resume-tailoring AI prompt
    (spec §52). Validated with Pydantic before any part of it is trusted or
    surfaced to the user; anything touching a locked fact field is stripped
    server-side regardless of what the model returns.
    """

    model_config = ConfigDict(populate_by_name=True, alias_generator=_to_camel)

    summary: str = ""
    recommended_skills: list[str] = Field(default_factory=list)
    skill_additions: list[SkillAddition] = Field(default_factory=list)
    skill_reorder: list[SkillReorderSuggestion] = Field(default_factory=list)
    keyword_matches: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    bullet_changes: list[BulletChange] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    fabrication_risk: bool = False
