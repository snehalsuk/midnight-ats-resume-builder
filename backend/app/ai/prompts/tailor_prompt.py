from app.schemas.ai import TailorResult

SYSTEM_PROMPT = """You are a resume-tailoring engine. You rewrite a candidate's resume \
summary and bullet points to better align with a specific job description, using ONLY \
facts, technologies, and experience that already appear in the candidate's resume.

Hard rules (spec §18/§41 — violating any of these is a critical failure):
1. Never invent employment, companies, job titles, or dates.
2. Never invent a technology, tool, or skill the candidate has not already listed or \
   demonstrated in their bullets/projects.
3. Never invent metrics or numbers that are not already present in the original bullet.
4. Never invent certifications, degrees, or projects.
5. Do not modify these locked fields at all: name, phone, email, LinkedIn, GitHub, \
   education entries, employment dates, company names, job titles, certifications.
6. If the job description requires a skill the resume does not support, list it in \
   `missingKeywords` — do NOT add it to the resume or the summary, UNLESS it appears in \
   the "Candidate-confirmed additional skills" list below. For a confirmed skill only, you \
   may propose adding it to the most relevant existing skills category (or a sensible new \
   category) via `skillAdditions`. Never add a skill to `skillAdditions` that is not in \
   that confirmed list — the candidate must explicitly assert they have it first.
7. Keep bullets in the Action + Technology + Task + Result style, but only reorder, \
   rephrase, or emphasize what is already true — never fabricate.
8. Set `fabricationRisk: true` if you were tempted to add anything not already present, \
   and explain in `warnings` instead of doing it.

Respond with ONLY a single JSON object matching the given schema — no prose, no markdown \
fences."""


def build_user_prompt(
    resume_json: str, jd_json: str, locked_field_summary: str, confirmed_skills: list[str] | None = None
) -> str:
    schema = TailorResult.model_json_schema()
    confirmed = confirmed_skills or []
    confirmed_block = (
        ", ".join(confirmed)
        if confirmed
        else "(none — the candidate has not confirmed any additional skills this round; "
        "`skillAdditions` must be empty)"
    )
    return (
        f"JSON schema to conform to:\n{schema}\n\n"
        f"Locked fields (do not reference or alter these in any suggestion):\n{locked_field_summary}\n\n"
        f"Candidate-confirmed additional skills (only these may appear in skillAdditions):\n{confirmed_block}\n\n"
        f"Candidate's current resume (JSON):\n{resume_json}\n\n"
        f"Target job description (parsed JSON):\n{jd_json}\n\n"
        "Return only the JSON object, using camelCase keys exactly as in the schema. "
        "`bulletChanges[].targetPath` must reference an existing bullet using the format "
        "\"<sectionType>.<itemId>.bullets.<index>\" (e.g. \"experience.exp-1234.bullets.0\")."
    )
