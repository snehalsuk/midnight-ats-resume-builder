from pydantic import BaseModel, ConfigDict, Field

from app.schemas.resume import _to_camel


class ParsedJobDescription(BaseModel):
    """Structured JD extraction result (spec §15). This exact shape is what
    the AI provider must return for the job-description-parsing prompt;
    validated before being persisted or trusted.
    """

    model_config = ConfigDict(populate_by_name=True, alias_generator=_to_camel)

    job_title: str = ""
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    years_of_experience: str = ""
    education_requirements: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    domain_keywords: list[str] = Field(default_factory=list)
    soft_skills: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    cloud_technologies: list[str] = Field(default_factory=list)
    frameworks: list[str] = Field(default_factory=list)
    databases: list[str] = Field(default_factory=list)


class JobDescriptionCreateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=_to_camel)
    company: str | None = None
    raw_text: str


class JobDescriptionResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=_to_camel)
    id: int
    company: str | None
    raw_text: str
    parsed: ParsedJobDescription
