"""Cognitive-complexity fixture -- Python 3.9 branch.

Deliberately convoluted control flow. This file exists to give complexipy
something to score above threshold; it is not used by the pipeline.

Mirrors ``Analysis/ComplexitySample.cs`` in the C# reference repository.
"""

from typing import Optional


def grade_shipment(  # noqa: C901 - intentionally complex
    score: int,
    is_bonus: bool,
    is_premium: bool,
    attendance: float,
    region: str,
    retries: int,
    expedited: Optional[bool] = None,
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
            if region == "emea":
                grade += " (review-emea)"
            elif region == "apac":
                grade += " (review-apac)"
            else:
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
                grade += " [{0}-fail]".format(marker)
                break
            elif score < 75:
                grade += " [{0}-watch]".format(marker)
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
    """A second, smaller complexity target."""
    if depth > 1000:
        if urgent:
            return "overflow-urgent"
        if region in ("emea", "apac"):
            return "overflow-regional"
        return "overflow"
    if depth > 100:
        return "urgent" if urgent else "standard"
    if depth > 0:
        return "standard"
    return "idle"
