import io

import pymupdf

# PyMuPDF is used over pdfplumber for extraction: on real-world resume PDFs
# (e.g. bullet glyphs embedded via a custom font subset), pdfplumber has been
# observed falling back to literal "(cid:N)" placeholders for unmapped glyphs
# while PyMuPDF resolves them to the correct Unicode code point (verified
# against this project's own sample resume fixture).


def extract_lines_from_pdf(file_bytes: bytes) -> list[str]:
    lines: list[str] = []
    with pymupdf.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            text = page.get_text("text") or ""
            for raw_line in text.split("\n"):
                stripped = raw_line.strip()
                if stripped:
                    lines.append(stripped)
    return lines


def extract_plain_text_from_pdf(file_bytes: bytes) -> str:
    return "\n".join(extract_lines_from_pdf(file_bytes))


def count_pdf_pages(file_bytes: bytes) -> int:
    with pymupdf.open(stream=file_bytes, filetype="pdf") as doc:
        return doc.page_count


def has_extractable_text(file_bytes: bytes) -> bool:
    """Sanity check that the PDF is a real text PDF, not a scanned image."""
    text = extract_plain_text_from_pdf(file_bytes)
    return len(text.strip()) > 40
