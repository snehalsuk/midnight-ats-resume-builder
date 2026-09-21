from sqlalchemy.orm import Session, selectinload

from app.models.resume import Resume
from app.models.resume_fact import ResumeFact
from app.models.resume_section import ResumeSection
from app.schemas.resume import PersonalInfo, ResumeData, ResumeSectionDTO


class ResumeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, resume_id: int) -> Resume | None:
        return (
            self.db.query(Resume)
            .options(selectinload(Resume.sections), selectinload(Resume.facts))
            .filter(Resume.id == resume_id)
            .first()
        )

    def list_for_owner(self, owner_id: int, kind: str | None = None) -> list[Resume]:
        q = self.db.query(Resume).filter(Resume.owner_id == owner_id)
        if kind:
            q = q.filter(Resume.kind == kind)
        return q.order_by(Resume.updated_at.desc()).all()

    def versions_for_master(self, master_id: int) -> list[Resume]:
        return (
            self.db.query(Resume)
            .filter(Resume.parent_id == master_id, Resume.kind == "VERSION")
            .order_by(Resume.created_at.desc())
            .all()
        )

    def create(
        self,
        owner_id: int,
        name: str,
        personal_info: PersonalInfo,
        sections: list[ResumeSectionDTO],
        kind: str = "MASTER",
        parent_id: int | None = None,
        job_description_id: int | None = None,
        source_filename: str | None = None,
        template_id: str | None = None,
    ) -> Resume:
        resume = Resume(
            owner_id=owner_id,
            name=name,
            personal_info=personal_info.model_dump(by_alias=True),
            kind=kind,
            parent_id=parent_id,
            job_description_id=job_description_id,
            source_filename=source_filename,
            **({"template_id": template_id} if template_id else {}),
        )
        self.db.add(resume)
        self.db.flush()
        self._replace_sections(resume, sections)
        self._sync_locked_facts(resume, personal_info, sections)
        self.db.commit()
        self.db.refresh(resume)
        return resume

    def update(
        self,
        resume: Resume,
        name: str | None = None,
        personal_info: PersonalInfo | None = None,
        sections: list[ResumeSectionDTO] | None = None,
        company: str | None = None,
        role_title: str | None = None,
        **render_settings,
    ) -> Resume:
        if name is not None:
            resume.name = name
        if personal_info is not None:
            resume.personal_info = personal_info.model_dump(by_alias=True)
        if company is not None:
            resume.company = company
        if role_title is not None:
            resume.role_title = role_title
        for key, value in render_settings.items():
            if value is not None and hasattr(resume, key):
                setattr(resume, key, value)
        if sections is not None:
            self._replace_sections(resume, sections)
        if personal_info is not None or sections is not None:
            self._sync_locked_facts(
                resume,
                personal_info or PersonalInfo.model_validate(resume.personal_info),
                sections if sections is not None else self._sections_as_dto(resume),
            )
        self.db.commit()
        self.db.refresh(resume)
        return resume

    def delete(self, resume: Resume) -> None:
        self.db.delete(resume)
        self.db.commit()

    def duplicate(self, resume: Resume, new_name: str) -> Resume:
        return self.create(
            owner_id=resume.owner_id,
            name=new_name,
            personal_info=PersonalInfo.model_validate(resume.personal_info),
            sections=self._sections_as_dto(resume),
            kind=resume.kind,
            parent_id=resume.parent_id,
            job_description_id=resume.job_description_id,
            source_filename=resume.source_filename,
            template_id=resume.template_id,
        )

    def to_resume_data(self, resume: Resume) -> ResumeData:
        return ResumeData(
            personal_info=PersonalInfo.model_validate(resume.personal_info),
            sections=self._sections_as_dto(resume),
        )

    def _sections_as_dto(self, resume: Resume) -> list[ResumeSectionDTO]:
        return [
            ResumeSectionDTO(
                id=s.section_key,
                type=s.type,
                title=s.title,
                order=s.order,
                visible=s.visible,
                content=s.content,
            )
            for s in sorted(resume.sections, key=lambda x: x.order)
        ]

    def _replace_sections(self, resume: Resume, sections: list[ResumeSectionDTO]) -> None:
        for existing in list(resume.sections):
            self.db.delete(existing)
        self.db.flush()
        for dto in sections:
            self.db.add(
                ResumeSection(
                    resume_id=resume.id,
                    section_key=dto.id,
                    type=dto.type,
                    title=dto.title,
                    order=dto.order,
                    visible=dto.visible,
                    content=dto.content,
                )
            )
        self.db.flush()

    def _sync_locked_facts(
        self, resume: Resume, personal_info: PersonalInfo, sections: list[ResumeSectionDTO]
    ) -> None:
        for existing in list(resume.facts):
            self.db.delete(existing)
        self.db.flush()

        facts: dict[str, str] = {
            "personalInfo.name": personal_info.name,
            "personalInfo.phone": personal_info.phone,
            "personalInfo.email": personal_info.email,
            "personalInfo.linkedin": personal_info.linkedin,
            "personalInfo.github": personal_info.github,
        }
        for section in sections:
            if section.type == "experience":
                for item in section.content.get("items", []):
                    facts[f"experience.{item.get('id')}.company"] = item.get("company", "")
                    facts[f"experience.{item.get('id')}.title"] = item.get("title", "")
                    facts[f"experience.{item.get('id')}.dates"] = (
                        f"{item.get('startDate', '')}-{item.get('endDate', '')}"
                    )
            elif section.type == "education":
                for item in section.content.get("items", []):
                    facts[f"education.{item.get('id')}"] = f"{item.get('degree', '')} — {item.get('institution', '')}"
            elif section.type == "certifications":
                for item in section.content.get("items", []):
                    facts[f"certifications.{item.get('id')}"] = item.get("name", "")

        for key, value in facts.items():
            if value:
                self.db.add(ResumeFact(resume_id=resume.id, fact_key=key, value=value, locked=True))
        self.db.flush()
