"""Pydantic DTOs matching the resume JSON model in spec §4. All models use
camelCase aliases on the wire (to match the TypeScript frontend) while
staying snake_case in Python.
"""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

SectionType = Literal[
    "summary",
    "skills",
    "experience",
    "projects",
    "education",
    "certifications",
    "achievements",
    "publications",
    "awards",
    "open_source",
    "volunteer",
    "languages",
    "interests",
    "custom",
]

def _to_camel(s: str) -> str:
    parts = s.split("_")
    return parts[0] + "".join(p.title() for p in parts[1:])


class PersonalInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=_to_camel)

    name: str = ""
    title: str = ""
    location: str = ""
    email: str = ""
    phone: str = ""
    linkedin: str = ""
    github: str = ""
    portfolio: str = ""
    leetcode: str = ""
    hackerrank: str = ""


class SkillCategory(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=_to_camel)
    name: str
    items: list[str] = Field(default_factory=list)


class ExperienceItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=_to_camel)
    id: str
    title: str = ""
    company: str = ""
    location: str = ""
    start_date: str = ""
    end_date: str = ""
    current: bool = False
    bullets: list[str] = Field(default_factory=list)


class ProjectItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=_to_camel)
    id: str
    name: str = ""
    technologies: list[str] = Field(default_factory=list)
    link: str = ""
    bullets: list[str] = Field(default_factory=list)


class EducationItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=_to_camel)
    id: str
    degree: str = ""
    institution: str = ""
    location: str = ""
    gpa: str = ""
    year: str = ""


class CertificationItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=_to_camel)
    id: str
    name: str = ""
    issuer: str = ""
    year: str = ""
    credential_url: str = ""


class ResumeSectionDTO(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=_to_camel)

    id: str
    type: SectionType
    title: str
    order: int
    visible: bool = True
    # Flexible payload: {"text": str} for summary/custom, {"categories": [...]}
    # for skills, {"items": [...]} for experience/projects/education/certifications.
    content: dict[str, Any] = Field(default_factory=dict)


class ResumeData(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=_to_camel)

    personal_info: PersonalInfo = Field(default_factory=PersonalInfo)
    sections: list[ResumeSectionDTO] = Field(default_factory=list)


class ResumeMeta(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=_to_camel)

    id: int
    kind: str
    name: str
    company: str | None = None
    role_title: str | None = None
    template_id: str
    font_family: str
    font_size_pt: float
    heading_size_pt: float
    line_spacing: float
    section_spacing_pt: float
    bullet_spacing_pt: float
    margin_in: float
    page_count: int | None = None
    last_ats_score: float | None = None
    parent_id: int | None = None
    job_description_id: int | None = None


class ResumeResponse(ResumeMeta):
    model_config = ConfigDict(populate_by_name=True, alias_generator=_to_camel)
    personal_info: PersonalInfo
    sections: list[ResumeSectionDTO]


class ResumeCreateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=_to_camel)
    name: str = "Master Resume"
    template_id: str = "classic"
    personal_info: PersonalInfo = Field(default_factory=PersonalInfo)
    sections: list[ResumeSectionDTO] = Field(default_factory=list)


class ResumeUpdateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=_to_camel)
    name: str | None = None
    template_id: str | None = None
    personal_info: PersonalInfo | None = None
    sections: list[ResumeSectionDTO] | None = None
    company: str | None = None
    role_title: str | None = None
    font_size_pt: float | None = None
    margin_in: float | None = None
    section_spacing_pt: float | None = None
    bullet_spacing_pt: float | None = None


class TemplateStyleResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=_to_camel)
    id: str
    name: str
    description: str
    accent_color: str


DEFAULT_SECTION_ORDER: list[tuple[str, str, str]] = [
    ("professional-summary", "summary", "PROFESSIONAL SUMMARY"),
    ("technical-skills", "skills", "TECHNICAL SKILLS"),
    ("experience", "experience", "PROFESSIONAL EXPERIENCE"),
    ("projects", "projects", "KEY PROJECTS"),
    ("education", "education", "EDUCATION"),
    ("certifications", "certifications", "CERTIFICATIONS"),
]

STANDARD_SECTION_TITLES = {
    "summary": "PROFESSIONAL SUMMARY",
    "skills": "TECHNICAL SKILLS",
    "experience": "PROFESSIONAL EXPERIENCE",
    "projects": "KEY PROJECTS",
    "education": "EDUCATION",
    "certifications": "CERTIFICATIONS",
    "achievements": "ACHIEVEMENTS",
    "publications": "PUBLICATIONS",
    "awards": "AWARDS",
    "open_source": "OPEN SOURCE",
    "volunteer": "VOLUNTEER EXPERIENCE",
    "languages": "LANGUAGES",
    "interests": "INTERESTS",
}
