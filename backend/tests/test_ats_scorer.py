from app.ats.keyword_matcher import match_keywords
from app.ats.scorer import compute_ats_score
from app.schemas.ats import ParsingChecklistItem
from app.schemas.job_description import ParsedJobDescription
from app.schemas.resume import PersonalInfo, ResumeData, ResumeSectionDTO


def _make_resume() -> ResumeData:
    return ResumeData(
        personal_info=PersonalInfo(name="Jane Doe", title="Java Full Stack Developer", email="jane@x.com"),
        sections=[
            ResumeSectionDTO(
                id="skills", type="skills", title="TECHNICAL SKILLS", order=1, visible=True,
                content={"categories": [{"name": "Backend", "items": ["Java", "Spring Boot", "Docker", "Microservices", "CI/CD"]}]},
            ),
            ResumeSectionDTO(
                id="experience", type="experience", title="EXPERIENCE", order=2, visible=True,
                content={"items": [{
                    "id": "e1", "title": "Software Engineer", "company": "Acme",
                    "startDate": "Jan 2021", "endDate": "Present", "current": True,
                    "bullets": ["Built scalable backend services using Java and Spring Boot for production systems."],
                }]},
            ),
        ],
    )


def _full_checklist() -> dict:
    keys = ["name", "email", "phone", "linkedin", "experience", "company", "designation", "dates", "skills", "projects", "education"]
    return {k: ParsingChecklistItem(detected=True) for k in keys}


def test_canonicalize_all_dedupes_case_insensitively_without_a_synonym_table():
    """canonicalize_all only does mechanical case-insensitive dedup now —
    semantic/vendor-prefix normalization ("Apache Kafka" -> "Kafka") is the
    AI's job at JD-extraction time, not a hardcoded word list here."""
    from app.ats.keyword_normalizer import canonicalize_all

    assert canonicalize_all(["Kafka", "kafka", "KAFKA"]) == ["Kafka"]
    # no synonym table left, so this does NOT merge — that's expected now
    assert canonicalize_all(["Kafka", "Apache Kafka"]) == ["Kafka", "Apache Kafka"]


def test_jd_prompt_instructs_dynamic_vendor_prefix_deduplication():
    """Guards against silently losing the de-dup instruction — the prompt
    must tell the model to resolve variants like "Apache Kafka"/"Kafka"
    itself, per request, rather than relying on a fixed list."""
    from app.ai.prompts.job_description_prompt import SYSTEM_PROMPT

    assert "Apache Kafka" in SYSTEM_PROMPT
    assert "do not rely on a fixed list" in SYSTEM_PROMPT.lower()


def test_keyword_match_uses_normalization():
    resume = _make_resume()
    jd = ParsedJobDescription(job_title="Java Full Stack Developer", required_skills=["Spring Boot", "Java", "Kafka"])
    matched, missing, related = match_keywords(resume, jd)
    assert "Spring Boot" in matched
    assert "Java" in matched
    assert "Kafka" in missing


def test_keyword_match_finds_terms_inside_compound_skill_entries():
    """Regression: a resume that writes AWS services as one compound
    entry, e.g. "AWS (S3, EC2, IAM, CloudWatch)", must still match JD
    keywords "AWS", "EC2", "S3" individually — real ATS keyword scanners
    do full-text substring search, not exact-list-item equality."""
    resume = ResumeData(
        personal_info=PersonalInfo(name="Jane Doe"),
        sections=[
            ResumeSectionDTO(
                id="skills", type="skills", title="TECHNICAL SKILLS", order=1, visible=True,
                content={"categories": [{"name": "Cloud", "items": ["AWS (S3, EC2, IAM, CloudWatch)"]}]},
            ),
        ],
    )
    jd = ParsedJobDescription(required_skills=["AWS", "EC2", "S3", "CloudWatch"])
    matched, missing, related = match_keywords(resume, jd)
    assert set(matched) == {"AWS", "EC2", "S3", "CloudWatch"}
    assert missing == []


def test_short_keyword_does_not_false_match_inside_unrelated_word():
    """Regression: "RDS" must not match because the resume happens to
    contain "standards" (which contains the substring "rds"). Matching
    must respect word/token boundaries, not scan a flattened blob."""
    resume = ResumeData(
        personal_info=PersonalInfo(name="Jane Doe"),
        sections=[
            ResumeSectionDTO(
                id="summary", type="summary", title="SUMMARY", order=1, visible=True,
                content={"text": "Contributes to architecture, design patterns, coding standards, and delivery."},
            ),
        ],
    )
    jd = ParsedJobDescription(required_skills=["RDS"])
    matched, missing, _ = match_keywords(resume, jd)
    assert matched == []
    assert missing == ["RDS"]


def test_related_keywords_surface_for_missing():
    resume = _make_resume()
    jd = ParsedJobDescription(required_skills=["Kubernetes"])
    matched, missing, related = match_keywords(resume, jd)
    assert "Kubernetes" in missing
    assert "Docker" in related  # resume has Docker, related to missing Kubernetes


def test_score_is_weighted_average_within_bounds():
    resume = _make_resume()
    jd = ParsedJobDescription(job_title="Java Full Stack Developer", required_skills=["Java", "Spring Boot"])
    score = compute_ats_score(resume, jd, _full_checklist(), page_count=1)
    assert 0 <= score.overall_score <= 100
    assert score.parsing_accuracy_pct == 100.0
    assert score.one_page_ok is True


def test_score_without_jd_zeroes_jd_dependent_components():
    resume = _make_resume()
    score = compute_ats_score(resume, None, _full_checklist(), page_count=1)
    assert score.keyword_match_pct == 0.0
    assert score.skills_match_pct == 0.0


def test_two_page_resume_flags_not_one_page():
    resume = _make_resume()
    score = compute_ats_score(resume, None, _full_checklist(), page_count=2)
    assert score.one_page_ok is False
    assert any("one page" in s.lower() for s in score.suggestions)
