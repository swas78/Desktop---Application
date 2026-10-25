# For: Deterministic field matching and validation comparison rules
# Must never: Alter threshold defaults dynamically without persistent configuration

import re
from datetime import datetime
from rapidfuzz import fuzz

DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%Y/%m/%d"]


def normalize_name_string(name: str) -> str:
    """Normalizes honorifics, punctuation, and extra spaces in names."""
    cleaned = re.sub(r"\b(mr|mrs|ms|shri|smt|km|dr)\b\.?", "", name, flags=re.IGNORECASE)
    cleaned = re.sub(r"[^\w\s]", " ", cleaned)
    return " ".join(cleaned.lower().split())


def compare_names(extracted: str, expected: str) -> tuple[str, float, str | None]:
    """Compares names using normalized token-set fuzzy ratio.
    
    Returns status (match, low_confidence, mismatch), similarity ratio, and reason.
    """
    norm_ext = normalize_name_string(extracted)
    norm_exp = normalize_name_string(expected)
    ratio = fuzz.token_set_ratio(norm_ext, norm_exp)
    
    if ratio >= 90.0:
        return "match", ratio / 100.0, None
    if ratio >= 75.0:
        return "low_confidence", ratio / 100.0, f"Name similarity is {ratio:.1f}%; manual check advised"
    return "mismatch", ratio / 100.0, f"Extracted '{extracted}' does not match expected '{expected}' (similarity {ratio:.1f}%)"


def parse_date_to_iso(date_str: str) -> str | None:
    """Tries parsing several common Indian date formats into ISO YYYY-MM-DD."""
    cleaned = date_str.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(cleaned, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def compare_dates(extracted: str, expected: str) -> tuple[str, str | None]:
    """Compares extracted and expected dates normalized to ISO format."""
    ext_iso = parse_date_to_iso(extracted)
    exp_iso = parse_date_to_iso(expected)
    if not ext_iso or not exp_iso:
        if extracted.strip().lower() == expected.strip().lower():
            return "match", None
        return "mismatch", f"Unrecognized date format or mismatch: '{extracted}' vs '{expected}'"
    if ext_iso == exp_iso:
        return "match", None
    return "mismatch", f"Date in document ({ext_iso}) does not match biodata ({exp_iso})"


def compare_percentages(extracted: str, expected: str, tolerance: float = 0.01) -> tuple[str, str | None]:
    """Compares marks percentage with tolerance for rounding variations."""
    try:
        val_ext = float(re.sub(r"[^\d\.]", "", extracted))
        val_exp = float(re.sub(r"[^\d\.]", "", expected))
        diff = abs(val_ext - val_exp)
        if diff <= tolerance:
            return "match", None
        return "mismatch", f"Value differs by {diff:.2f} (document has {val_ext}, form has {val_exp})"
    except ValueError:
        return "mismatch", f"Could not parse numeric percentage: '{extracted}'"


def verify_field_value(field_name: str, extracted_val: str, expected_val: str) -> tuple[str, float, str | None]:
    """Dispatches verification to specific rules by field name."""
    clean_name = field_name.lower()
    if "name" in clean_name:
        return compare_names(extracted_val, expected_val)
    if "dob" in clean_name or "date" in clean_name:
        status, reason = compare_dates(extracted_val, expected_val)
        return status, 0.98 if status == "match" else 0.95, reason
    if "percentage" in clean_name or "marks" in clean_name or "cgpa" in clean_name:
        status, reason = compare_percentages(extracted_val, expected_val)
        return status, 0.98 if status == "match" else 0.95, reason
    
    # Generic exact match
    if extracted_val.strip().lower() == expected_val.strip().lower():
        return "match", 0.98, None
    return "mismatch", 0.95, f"Expected '{expected_val}', document shows '{extracted_val}'"
