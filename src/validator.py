"""Validator — Self-review and quality verification system.

Implements the SELF-REVIEW PROTOCOL from the Master Prompt,
verifying correctness, security, completeness, and quality
before final delivery.
"""

from __future__ import annotations

import re
from typing import List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime

from .logger_setup import get_logger

logger = get_logger(__name__)


@dataclass
class ValidationResult:
    """Result of validating an optimized prompt."""
    passed: bool = False
    checks: Dict[str, bool] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    score: float = 0.0
    timestamp: str = ""


class PromptValidator:
    """Validates optimized prompts against quality standards."""

    def __init__(self, strict: bool = True) -> None:
        self.strict = strict

    def check_completeness(self, text: str) -> tuple[bool, str]:
        """Check that the prompt has no placeholders or TODOs."""
        placeholders = re.findall(
            r"\b(TODO|FIXME|XXX|HACK|implement\s*this|add\s*code|placeholder)\b",
            text, re.IGNORECASE
        )
        if placeholders:
            return False, f"Found placeholders: {', '.join(set(placeholders))}"
        return True, ""

    def check_structure(self, text: str) -> tuple[bool, str]:
        """Check that the prompt has proper section structure."""
        has_objective = bool(re.search(r"##\s*1[\.\)]\s*OBJECTIVE", text, re.IGNORECASE))
        has_task = bool(re.search(r"##\s*TASK", text, re.IGNORECASE))
        has_output = bool(re.search(r"(OUTPUT|DELIVERABLE|RESULT)", text, re.IGNORECASE))
        
        sections_found = sum([has_objective, has_task, has_output])
        if sections_found < 2:
            return False, f"Only {sections_found}/3 key sections found"
        return True, ""

    def check_security(self, text: str) -> tuple[bool, str]:
        """Check for security-relevant content patterns."""
        dangerous = re.findall(
            r"\b(eval\s*\(|exec\s*\(|os\.system|subprocess\.call|rm\s*-rf)\b",
            text, re.IGNORECASE
        )
        if dangerous and self.strict:
            return False, f"Potentially dangerous patterns: {dangerous}"
        return True, ""

    def validate(self, text: str) -> ValidationResult:
        """Run all validation checks."""
        checks = {}
        errors = []

        # Check 1: Not empty
        checks["not_empty"] = bool(text.strip())
        if not checks["not_empty"]:
            errors.append("Optimized prompt is empty")

        # Check 2: Minimum length
        word_count = len(text.split())
        checks["minimum_length"] = word_count >= 20
        if not checks["minimum_length"]:
            errors.append(f"Too short: {word_count} words (minimum 20)")

        # Check 3: Completeness
        complete, msg = self.check_completeness(text)
        checks["no_placeholders"] = complete
        if not complete:
            errors.append(msg)

        # Check 4: Structure
        structured, msg = self.check_structure(text)
        checks["has_structure"] = structured
        if not structured:
            errors.append(msg)

        # Check 5: Security
        secure, msg = self.check_security(text)
        checks["security_ok"] = secure
        if not secure:
            errors.append(msg)

        # Calculate score
        passed_checks = sum(1 for v in checks.values() if v)
        score = passed_checks / max(len(checks), 1)

        result = ValidationResult(
            passed=len(errors) == 0,
            checks=checks,
            errors=errors,
            score=score,
            timestamp=datetime.utcnow().isoformat() + "Z",
        )

        logger.info("Validation complete", extra={"score": score, "passed": result.passed})
        return result