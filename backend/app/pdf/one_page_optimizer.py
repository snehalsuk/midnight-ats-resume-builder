"""Deterministic one-page enforcement (spec §50). Steps through decreasing
spacing, then font size, then margins — each within safe, readability-
preserving bounds — re-rendering and re-counting pages after every step.
Never reduces font below the configured floor.
"""

import io
from dataclasses import replace

from pypdf import PdfReader

from app.core.config import get_settings
from app.pdf.renderer import RenderSettings, render_resume_pdf
from app.schemas.resume import ResumeData


def count_pages(pdf_bytes: bytes) -> int:
    reader = PdfReader(io.BytesIO(pdf_bytes))
    return len(reader.pages)


def auto_optimize_to_one_page(
    resume: ResumeData, settings: RenderSettings
) -> tuple[bytes, RenderSettings, int]:
    """Returns (pdf_bytes, final_settings, final_page_count)."""
    cfg = get_settings()
    current = settings
    pdf_bytes = render_resume_pdf(resume, current)
    pages = count_pages(pdf_bytes)
    if pages <= 1:
        return pdf_bytes, current, pages

    steps = [
        lambda s: replace(s, section_spacing_pt=max(6.0, s.section_spacing_pt - 2.0)),
        lambda s: replace(s, line_spacing=max(1.0, round(s.line_spacing - 0.05, 2))),
        lambda s: replace(s, bullet_spacing_pt=max(1.0, s.bullet_spacing_pt - 1.0)),
        lambda s: replace(s, font_size_pt=max(cfg.min_font_size_pt, round(s.font_size_pt - 0.25, 2))),
        lambda s: replace(s, margin_in=max(cfg.min_margin_in, round(s.margin_in - 0.05, 2))),
    ]

    step_idx = 0
    iterations = 0
    while pages > 1 and iterations < cfg.one_page_max_iterations:
        step = steps[step_idx % len(steps)]
        candidate = step(current)
        if candidate == current:
            step_idx += 1
            if step_idx >= len(steps) * 2:
                break
            continue
        current = candidate
        pdf_bytes = render_resume_pdf(resume, current)
        pages = count_pages(pdf_bytes)
        iterations += 1
        step_idx += 1

    return pdf_bytes, current, pages


def estimate_overflow_section(resume: ResumeData) -> str | None:
    """Rough heuristic (used only when auto-optimize still leaves >1 page):
    flags the section with the most bullet/content volume as the likely
    overflow cause, with an estimated percentage over budget.
    """
    weights: list[tuple[str, int]] = []
    for section in resume.sections:
        if not section.visible:
            continue
        weight = 0
        content = section.content
        if "text" in content:
            weight = len(content.get("text", "").split())
        elif "items" in content:
            for item in content["items"]:
                weight += len(item.get("bullets", [])) * 12
                weight += len(str(item))
        elif "categories" in content:
            for cat in content.get("categories", []):
                weight += len(cat.get("items", []))
        weights.append((section.title, weight))

    if not weights:
        return None
    weights.sort(key=lambda x: x[1], reverse=True)
    top_title, top_weight = weights[0]
    total = sum(w for _, w in weights) or 1
    pct = round(100 * top_weight / total - 100 / len(weights), 0)
    if pct <= 0:
        return None
    return f"{top_title} section is likely contributing the most overflow (~{int(pct)}% above an even share)."
