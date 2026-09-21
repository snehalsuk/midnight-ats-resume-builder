import json

from groq import Groq
from pydantic import ValidationError

from app.ai.base import AIProvider, AIProviderError
from app.ai.prompts.job_description_prompt import SYSTEM_PROMPT as JD_SYSTEM_PROMPT
from app.ai.prompts.job_description_prompt import build_user_prompt as build_jd_prompt
from app.ai.prompts.tailor_prompt import SYSTEM_PROMPT as TAILOR_SYSTEM_PROMPT
from app.ai.prompts.tailor_prompt import build_user_prompt as build_tailor_prompt
from app.schemas.ai import TailorResult
from app.schemas.job_description import ParsedJobDescription
from app.schemas.resume import ResumeData


class GroqProvider(AIProvider):
    def __init__(self, api_key: str, model: str):
        if not api_key:
            raise AIProviderError("GROQ_API_KEY is not configured.")
        self._client = Groq(api_key=api_key)
        self._model = model

    def _chat_json(self, system_prompt: str, user_prompt: str) -> dict:
        last_error: Exception | None = None
        for _ in range(2):  # one retry on malformed JSON, per spec §52
            try:
                completion = self._client.chat.completions.create(
                    model=self._model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.2,
                )
                content = completion.choices[0].message.content
                return json.loads(content)
            except Exception as exc:  # noqa: BLE001
                last_error = exc
        raise AIProviderError(f"AI provider returned an unusable response: {last_error}")

    def parse_job_description(self, raw_text: str) -> ParsedJobDescription:
        raw = self._chat_json(JD_SYSTEM_PROMPT, build_jd_prompt(raw_text))
        try:
            return ParsedJobDescription.model_validate(raw)
        except ValidationError as exc:
            raise AIProviderError(f"AI job description output failed schema validation: {exc}") from exc

    def tailor_resume(
        self,
        resume: ResumeData,
        jd: ParsedJobDescription,
        locked_field_summary: str,
        confirmed_skills: list[str] | None = None,
    ) -> TailorResult:
        resume_json = resume.model_dump_json(by_alias=True)
        jd_json = jd.model_dump_json(by_alias=True)
        raw = self._chat_json(
            TAILOR_SYSTEM_PROMPT,
            build_tailor_prompt(resume_json, jd_json, locked_field_summary, confirmed_skills),
        )
        try:
            return TailorResult.model_validate(raw)
        except ValidationError as exc:
            raise AIProviderError(f"AI tailoring output failed schema validation: {exc}") from exc
