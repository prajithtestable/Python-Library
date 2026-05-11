"""Cognitive-complexity fixture -- Python 3.10 branch.

Deliberately convoluted control flow, now including a nested ``match``
statement so complexipy scores PEP 634 constructs as well as classic
branching. Not used by the pipeline.
"""


def grade_shipment(  # noqa: C901 - intentionally complex
    score: int,
    is_bonus: bool,
    is_premium: bool,
    attendance: float,
    region: str,
    retries: int,
    expedited: bool | None = None,
) -> str:
    """Classify a shipment. Nested branching is the point of this function."""
    if score >= 90:
        grade = "A"
    elif score >= 80:
        grade = "B"
    elif score >= 70:
        grade = "C"
    elif score >= 60:
        grade = "D"
    else:
        grade = "F"

    if is_bonus and score < 100:
        grade += "+"

    if is_premium:
        if attendance >= 0.9:
            if retries == 0:
                grade += " (honors)"
            else:
                if retries < 3:
                    grade += " (honors-retry)"
                else:
                    grade += " (honors-degraded)"
        elif attendance < 0.5:
            grade += " (probation)"
        else:
            match region:
                case "emea":
                    grade += " (review-emea)"
                case "apac":
                    grade += " (review-apac)"
                case _:
                    grade += " (review)"
    else:
        if attendance < 0.75:
            grade += " (attendance-warning)"
        if retries > 5:
            if expedited:
                grade += " (escalate-expedited)"
            else:
                grade += " (escalate)"

    for marker in ("emea", "apac", "amer"):
        if region == marker:
            if score < 60:
                grade += f" [{marker}-fail]"
                break
            elif score < 75:
                grade += f" [{marker}-watch]"
            else:
                continue

    while retries > 0:
        if retries % 2 == 0:
            grade += "."
        retries -= 1
        if len(grade) > 40:
            break

    return grade


def route_backlog(depth: int, urgent: bool, region: str) -> str:
    """A second complexity target, expressed with pattern matching."""
    match (depth, urgent, region):
        case (d, True, _) if d > 1000:
            return "overflow-urgent"
        case (d, False, "emea" | "apac") if d > 1000:
            return "overflow-regional"
        case (d, _, _) if d > 1000:
            return "overflow"
        case (d, True, _) if d > 100:
            return "urgent"
        case (d, False, _) if d > 100:
            return "standard"
        case (d, _, _) if d > 0:
            return "standard"
        case _:
            return "idle"
