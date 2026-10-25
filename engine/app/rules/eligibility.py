# For: Evaluating candidate application eligibility against vacancy criteria
# Must never: Alter candidate eligibility without evaluating all defined vacancy rules

from datetime import datetime
from typing import Any


def calculate_age_on_date(dob_str: str, target_date_str: str) -> int | None:
    """Calculates age in completed years between dob and closing date."""
    try:
        dob = datetime.strptime(dob_str.strip(), "%Y-%m-%d")
        target = datetime.strptime(target_date_str.strip(), "%Y-%m-%d")
        age = target.year - dob.year - ((target.month, target.day) < (dob.month, dob.day))
        return age
    except Exception:
        return None


def evaluate_age_rule(biodata: dict[str, Any], rules: dict[str, Any], closing_date: str) -> dict[str, Any]:
    """Evaluates age against category-specific relaxation limits."""
    dob = biodata.get("dob")
    cat = (biodata.get("category") or "UR").upper()
    is_pwd = bool(biodata.get("pwd", False))
    
    if not dob:
        return {"rule": "age_limit", "required": "Valid DOB", "actual": "Missing", "passed": False}
    
    age = calculate_age_on_date(str(dob), closing_date)
    if age is None:
        return {"rule": "age_limit", "required": "Valid DOB", "actual": dob, "passed": False}
    
    max_age_dict = rules.get("max_age", {"UR": 28, "OBC": 31, "SC": 33, "ST": 33, "PwD_extra": 10})
    limit = max_age_dict.get(cat, max_age_dict.get("UR", 28))
    if is_pwd:
        limit += max_age_dict.get("PwD_extra", 10)
        
    return {
        "rule": "age_limit",
        "required": limit,
        "actual": age,
        "passed": age <= limit,
        "message": f"Age {age} within limit {limit} for category {cat}" if age <= limit else f"Age {age} exceeds limit {limit}"
    }


def evaluate_qualification_rules(biodata: dict[str, Any], rules: dict[str, Any]) -> list[dict[str, Any]]:
    """Evaluates branch and minimum percentage criteria."""
    outcomes: list[dict[str, Any]] = []
    qual = biodata.get("qualification", {})
    if not isinstance(qual, dict):
        qual = {}
    
    # 1. Branch check
    allowed_branches = [b.upper() for b in rules.get("allowed_branches", [])]
    actual_branch = str(qual.get("branch", "")).upper()
    branch_pass = not allowed_branches or actual_branch in allowed_branches
    outcomes.append({
        "rule": "allowed_branches",
        "required": allowed_branches,
        "actual": actual_branch,
        "passed": branch_pass
    })
    
    # 2. Percentage check
    min_pct = float(rules.get("min_percentage", 60.0))
    actual_pct = float(qual.get("percentage", 0.0) or 0.0)
    pct_pass = actual_pct >= min_pct
    outcomes.append({
        "rule": "min_percentage",
        "required": min_pct,
        "actual": actual_pct,
        "passed": pct_pass
    })
    return outcomes


def evaluate_gate_rules(biodata: dict[str, Any], rules: dict[str, Any], closing_date: str) -> dict[str, Any] | None:
    """Evaluates GATE scorecard validity if required for vacancy."""
    if not rules.get("gate_required", False):
        return None
    
    gate_info = biodata.get("gate", {})
    if not gate_info or not gate_info.get("score"):
        return {"rule": "gate_scorecard", "required": "Valid GATE Score", "actual": "None", "passed": False}
    
    try:
        closing_year = datetime.strptime(closing_date, "%Y-%m-%d").year
        gate_year = int(gate_info.get("year", 0))
        validity_years = int(rules.get("gate_validity_years", 3))
        valid = (closing_year - gate_year) <= validity_years
        return {
            "rule": "gate_validity",
            "required": f"Within {validity_years} years of {closing_date}",
            "actual": gate_year,
            "passed": valid
        }
    except Exception:
        return {"rule": "gate_validity", "required": "Valid year", "actual": gate_info.get("year"), "passed": False}


def evaluate_application_eligibility(
    biodata: dict[str, Any],
    vacancy_rules: dict[str, Any],
    closing_date: str
) -> dict[str, Any]:
    """Evaluates all vacancy rules against applicant biodata.
    
    Returns verdict (eligible, not_eligible, needs_review) and per-rule breakdown.
    """
    reasons: list[dict[str, Any]] = []
    
    # 1. Age
    reasons.append(evaluate_age_rule(biodata, vacancy_rules, closing_date))
    # 2. Qualification & Percentage
    reasons.extend(evaluate_qualification_rules(biodata, vacancy_rules))
    # 3. GATE
    gate_outcome = evaluate_gate_rules(biodata, vacancy_rules, closing_date)
    if gate_outcome:
        reasons.append(gate_outcome)
        
    all_passed = all(r.get("passed", False) for r in reasons)
    verdict = "eligible" if all_passed else "not_eligible"
    return {
        "verdict": verdict,
        "reasons": reasons
    }
