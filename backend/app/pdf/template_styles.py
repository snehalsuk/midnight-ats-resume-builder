"""Registry of selectable visual template styles (spec §48: a reusable
template engine, not one hardcoded resume). All styles share the exact
same section-rendering markup — single-column, no tables/images/icons —
so every one of them stays ATS-safe by construction (spec §12); only
typography, alignment, and accent color differ between them.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class TemplateStyle:
    id: str
    name: str
    description: str
    accent_color: str = "#111111"


TEMPLATE_STYLES: dict[str, TemplateStyle] = {
    "classic": TemplateStyle(
        id="classic",
        name="Classic",
        description="Centered header, underlined section headings. The safest, most universally recognized ATS layout.",
    ),
    "modern": TemplateStyle(
        id="modern",
        name="Modern",
        description="Left-aligned header with a colored accent on your name and section headings.",
        accent_color="#1d4ed8",
    ),
    "minimal": TemplateStyle(
        id="minimal",
        name="Minimal",
        description="No borders or color — just spacing and weight for hierarchy. Ultra-clean.",
    ),
    "executive": TemplateStyle(
        id="executive",
        name="Executive",
        description="Larger name, shaded section heading bands, generous whitespace.",
    ),
    "compact": TemplateStyle(
        id="compact",
        name="Compact",
        description="Tighter spacing and a smaller base size — fits more content on one page.",
    ),
    "bold": TemplateStyle(
        id="bold",
        name="Bold",
        description="Full-width colored header band behind your name and contact details — a strong first impression, still single-column.",
        accent_color="#1e3a5f",
    ),
    "accent": TemplateStyle(
        id="accent",
        name="Vibrant",
        description="Colored section accents, skill tag chips, and checkmarked highlights for a more energetic look.",
        accent_color="#4f46e5",
    ),
}

DEFAULT_TEMPLATE_STYLE_ID = "classic"


def get_template_style(template_id: str | None) -> TemplateStyle:
    return TEMPLATE_STYLES.get(template_id or "", TEMPLATE_STYLES[DEFAULT_TEMPLATE_STYLE_ID])
