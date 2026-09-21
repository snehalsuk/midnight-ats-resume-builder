"""AI provider abstraction (spec §51/§57). Every AI-backed feature calls
through this interface, never a provider SDK directly, so Groq can be
swapped for OpenAI/Anthropic/Ollama by adding one adapter class.
"""

from abc import ABC, abstractmethod

from app.schemas.ai import TailorResult
from app.schemas.job_description import ParsedJobDescription
from app.schemas.resume import ResumeData


class AIProviderError(Exception):
    pass


class AIProvider(ABC):
    @abstractmethod
    def parse_job_description(self, raw_text: str) -> ParsedJobDescription: ...

    @abstractmethod
    def tailor_resume(
        self,
        resume: ResumeData,
        jd: ParsedJobDescription,
        locked_field_summary: str,
        confirmed_skills: list[str] | None = None,
    ) -> TailorResult: ...
