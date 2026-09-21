import datetime
import re

_MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


def _parse_month_year(value: str) -> tuple[int, int] | None:
    value = value.strip().lower().rstrip(".")
    if value in ("present", "current", "now"):
        today = datetime.date.today()
        return today.year, today.month
    m = re.match(r"([a-z]{3,9})\.?\s+(\d{4})", value)
    if m:
        mon = _MONTHS.get(m.group(1)[:3])
        if mon:
            return int(m.group(2)), mon
    m2 = re.match(r"^(\d{4})$", value)
    if m2:
        return int(m2.group(1)), 1
    return None


def total_experience_years(experience_items: list[dict]) -> float:
    """Sums non-overlapping month spans across all experience entries."""
    spans: list[tuple[int, int]] = []  # (start_month_index, end_month_index)
    for item in experience_items:
        start = _parse_month_year(item.get("startDate", "") or item.get("start_date", ""))
        end = _parse_month_year(item.get("endDate", "") or item.get("end_date", ""))
        if not start or not end:
            continue
        start_idx = start[0] * 12 + start[1]
        end_idx = end[0] * 12 + end[1]
        if end_idx >= start_idx:
            spans.append((start_idx, end_idx))

    if not spans:
        return 0.0

    spans.sort()
    merged: list[list[int]] = [list(spans[0])]
    for s, e in spans[1:]:
        if s <= merged[-1][1] + 1:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])

    total_months = sum(e - s + 1 for s, e in merged)
    return round(total_months / 12, 1)


def parse_required_years(years_text: str) -> float | None:
    if not years_text:
        return None
    m = re.search(r"(\d+(?:\.\d+)?)", years_text)
    return float(m.group(1)) if m else None
