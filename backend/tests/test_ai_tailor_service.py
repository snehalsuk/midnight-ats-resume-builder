"""Unit tests for the confirmed-skills safety mechanism in AiTailorService:
the AI is asked to only ever suggest adding a skill the candidate explicitly
confirmed they have, but the service must not simply trust that instruction —
it re-filters the model's response before anything is saved or shown for
review (spec §25 belt-and-suspenders pattern, same as locked-field filtering).
"""

from app.core.db import SessionLocal
from app.repositories.job_description_repo import JobDescriptionRepository
from app.repositories.resume_repo import ResumeRepository
from app.schemas.ai import SkillAddition, TailorResult
from app.schemas.job_description import ParsedJobDescription
from app.schemas.resume import PersonalInfo, ResumeSectionDTO
from app.services.ai_tailor_service import AiTailorService


class _FakeProvider:
    """Simulates a model that (correctly or not) proposes both a confirmed
    and an unconfirmed skill — the service, not the prompt, must be what
    actually stops the unconfirmed one from landing on the resume."""

    def __init__(self, skill_additions):
        self._skill_additions = skill_additions

    def tailor_resume(self, resume, jd, locked_field_summary, confirmed_skills=None):
        return TailorResult(skill_additions=self._skill_additions)


def _make_resume_with_skills():
    db = SessionLocal()
    repo = ResumeRepository(db)
    resume = repo.create(
        owner_id=1,
        name="Test Resume",
        personal_info=PersonalInfo(name="Test User", email="test@example.com"),
        sections=[
            ResumeSectionDTO(
                id="skills", type="skills", title="TECHNICAL SKILLS", order=1, visible=True,
                content={"categories": [{"name": "Cloud", "items": ["AWS"]}]},
            ),
        ],
    )
    jd = JobDescriptionRepository(db).create(
        owner_id=1,
        company="Acme",
        raw_text="Need Redis and Kubernetes experience.",
        parsed=ParsedJobDescription(job_title="Engineer", required_skills=["Redis", "Kubernetes"]),
    )
    resume_id, jd_id = resume.id, jd.id
    db.close()
    return resume_id, jd_id


def test_propose_drops_skill_additions_the_candidate_did_not_confirm():
    resume_id, jd_id = _make_resume_with_skills()
    db = SessionLocal()
    try:
        resume = ResumeRepository(db).get(resume_id)
        provider = _FakeProvider(
            [
                SkillAddition(category="Cloud", skill="Redis"),
                SkillAddition(category="Cloud", skill="Kubernetes"),
            ]
        )
        service = AiTailorService(db, lambda: provider)

        result = service.propose(resume, jd_id, confirmed_skills=["Redis"])

        assert [sa.skill for sa in result.skill_additions] == ["Redis"]
        pending = service.list_pending(resume_id)
        skill_changes = [c for c in pending if c.change_type == "skill"]
        assert len(skill_changes) == 1
        assert skill_changes[0].suggested_value == "Redis"
    finally:
        db.close()


def test_propose_with_no_confirmed_skills_adds_nothing():
    resume_id, jd_id = _make_resume_with_skills()
    db = SessionLocal()
    try:
        resume = ResumeRepository(db).get(resume_id)
        provider = _FakeProvider([SkillAddition(category="Cloud", skill="Redis")])
        service = AiTailorService(db, lambda: provider)

        result = service.propose(resume, jd_id, confirmed_skills=[])

        assert result.skill_additions == []
        assert [c for c in service.list_pending(resume_id) if c.change_type == "skill"] == []
    finally:
        db.close()


def test_accepting_a_skill_change_adds_it_to_the_matching_category():
    resume_id, jd_id = _make_resume_with_skills()
    db = SessionLocal()
    try:
        resume = ResumeRepository(db).get(resume_id)
        provider = _FakeProvider([SkillAddition(category="Cloud", skill="Redis")])
        service = AiTailorService(db, lambda: provider)
        service.propose(resume, jd_id, confirmed_skills=["Redis"])

        change = next(c for c in service.list_pending(resume_id) if c.change_type == "skill")
        resume = ResumeRepository(db).get(resume_id)
        updated = service.accept(resume, change)

        data = ResumeRepository(db).to_resume_data(updated)
        skills_section = next(s for s in data.sections if s.type == "skills")
        cloud_items = next(c["items"] for c in skills_section.content["categories"] if c["name"] == "Cloud")
        assert cloud_items == ["AWS", "Redis"]
    finally:
        db.close()


def test_accepting_a_skill_change_for_a_new_category_creates_it():
    resume_id, jd_id = _make_resume_with_skills()
    db = SessionLocal()
    try:
        resume = ResumeRepository(db).get(resume_id)
        provider = _FakeProvider([SkillAddition(category="Databases", skill="Redis")])
        service = AiTailorService(db, lambda: provider)
        service.propose(resume, jd_id, confirmed_skills=["Redis"])

        change = next(c for c in service.list_pending(resume_id) if c.change_type == "skill")
        resume = ResumeRepository(db).get(resume_id)
        updated = service.accept(resume, change)

        data = ResumeRepository(db).to_resume_data(updated)
        skills_section = next(s for s in data.sections if s.type == "skills")
        names = [c["name"] for c in skills_section.content["categories"]]
        assert "Databases" in names
    finally:
        db.close()
