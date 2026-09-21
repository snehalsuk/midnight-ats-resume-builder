"""Handles resume file upload validation (spec §38) and parsing into the
Master Resume (spec §45). Deterministic only — the parser never rewrites
content, it only structures it.
"""

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.exceptions.errors import FileTooLargeError, UnparsableResumeError, UnsupportedFileTypeError
from app.models.resume import Resume
from app.parser.docx_parser import extract_lines_from_docx
from app.parser.pdf_parser import extract_lines_from_pdf, has_extractable_text
from app.parser.resume_parser import parse_lines_to_resume
from app.parser.txt_parser import extract_lines_from_txt
from app.repositories.resume_repo import ResumeRepository


def _sniff_kind(filename: str, content: bytes) -> str:
    lower = filename.lower()
    if content[:4] == b"%PDF" or lower.endswith(".pdf"):
        return "pdf"
    if content[:2] == b"PK" or lower.endswith(".docx"):
        return "docx"
    if lower.endswith(".txt"):
        return "txt"
    raise UnsupportedFileTypeError("Only PDF, DOCX, and TXT resumes are supported.")


class UploadService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ResumeRepository(db)
        self.settings = get_settings()

    def validate_upload(self, filename: str, content: bytes) -> str:
        if len(content) > self.settings.max_upload_size_bytes:
            raise FileTooLargeError(
                f"File exceeds the {self.settings.max_upload_size_bytes // (1024 * 1024)}MB upload limit."
            )
        kind = _sniff_kind(filename, content)
        if kind == "pdf" and not has_extractable_text(content):
            raise UnparsableResumeError(
                "This PDF has no extractable text layer (it may be a scanned image). "
                "Upload a text-based PDF, DOCX, or TXT resume instead."
            )
        return kind

    def parse_upload(self, filename: str, content: bytes):
        kind = self.validate_upload(filename, content)
        if kind == "pdf":
            lines = extract_lines_from_pdf(content)
        elif kind == "docx":
            lines = extract_lines_from_docx(content)
        else:
            lines = extract_lines_from_txt(content)

        if not lines:
            raise UnparsableResumeError("No readable text could be extracted from this file.")

        resume_data = parse_lines_to_resume(lines)
        if not resume_data.personal_info.name:
            raise UnparsableResumeError("Could not detect a name — please check the file and try again.")
        return resume_data

    def create_master_resume_from_upload(self, owner_id: int, filename: str, content: bytes) -> Resume:
        resume_data = self.parse_upload(filename, content)
        return self.repo.create(
            owner_id=owner_id,
            name="Master Resume",
            personal_info=resume_data.personal_info,
            sections=resume_data.sections,
            kind="MASTER",
            source_filename=filename,
        )
