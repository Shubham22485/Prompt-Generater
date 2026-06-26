"""Prompt Analyzer — Parses and analyzes raw user requests.

This module performs the INPUT ANALYSIS PHASE defined in the Master Prompt.
It identifies language, framework, missing information, and intent.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field

import logging
from .logger_setup import get_logger

logger = get_logger(__name__)


# ──────────────────────────────────────────────
# Analysis Result Data Classes
# ──────────────────────────────────────────────

@dataclass
class LanguageDetection:
    """Detected programming language and framework information."""
    language: str = "python"
    framework: str = ""
    platform: str = "cli"
    confidence: float = 0.0
    alternatives: List[str] = field(default_factory=list)

    def __post_init__(self):
        if self.framework is None:
            self.framework = ""


@dataclass
class RequestFeatures:
    """Extracted features from the user's request."""
    has_file_io: bool = False
    has_network: bool = False
    has_database: bool = False
    has_auth: bool = False
    has_ui: bool = False
    has_api: bool = False
    has_concurrency: bool = False
    has_encryption: bool = False


@dataclass
class AnalysisResult:
    """Complete analysis result for a user prompt request."""
    original_text: str
    summary: str
    language: LanguageDetection
    features: RequestFeatures
    missing_info: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    suggested_libraries: List[str] = field(default_factory=list)
    estimated_complexity: str = "low"  # low | medium | high
    estimated_lines: int = 50
    requires_clarification: bool = False
    clarification_question: str = ""


# ──────────────────────────────────────────────
# Language Detection Patterns
# ──────────────────────────────────────────────

LANGUAGE_PATTERNS: Dict[str, List[str]] = {
    "python": [
        r"\bpython\b", r"\bflask\b", r"\bdjango\b", r"\bfastapi\b",
        r"\bpip\b", r"\bvenv\b", r"\bconda\b", r"\bpyinstaller\b",
        r"\brequirements\.txt\b",
    ],
    "javascript": [
        r"\bjavascript\b", r"\bnode\.?js\b", r"\bnpm\b", r"\byarn\b",
        r"\bpackage\.json\b", r"\breact\b", r"\bvue\b", r"\bangul ar\b",
        r"\bexpress\b", r"\bnext\.?js\b",
    ],
    "typescript": [
        r"\btypescript\b", r"\bts\b", r"\btsx\b", r"\bdeno\b",
        r"\bnext\.?js\b", r"\bnest\.?js\b", r"\bangular\b",
    ],
    "rust": [
        r"\brust\b", r"\bcargo\b", r"\bcrate\b", r"\brs\b",
        r"\btokio\b", r"\bclap\b",
    ],
    "go": [
        r"\bgo\b", r"\bgolang\b", r"\bgoroutine\b", r"\bmodule\b",
    ],
    "java": [
        r"\bjava\b", r"\bmaven\b", r"\bgradle\b", r"\bspring\b",
        r"\bkotlin\b", r"\bjvm\b",
    ],
    "c++": [
        r"\bc\+\+\b", r"\bcpp\b", r"\bcmake\b", r"\bmakefile\b",
    ],
    "c#": [
        r"\bc#\b", r"\bcsharp\b", r"\b\.net\b", r"\bdotnet\b",
        r"\bnuget\b",
    ],
    "swift": [
        r"\bswift\b", r"\bios\b", r"\bmacos\b", r"\bswiftui\b",
    ],
    "ruby": [
        r"\bruby\b", r"\brails\b", r"\bgem\b", r"\brvm\b",
    ],
    "php": [
        r"\bphp\b", r"\blaravel\b", r"\bsymfony\b", r"\bcomposer\b",
    ],
}

PLATFORM_PATTERNS: Dict[str, List[str]] = {
    "web": [r"\bweb\b", r"\bwebsite\b", r"\bhtml\b", r"\bcss\b",
            r"\bfrontend\b", r"\bbackend\b", r"\bapi\b", r"\brest\b"],
    "mobile": [r"\bmobile\b", r"\bandroid\b", r"\bios\b",
               r"\bapp\b", r"\bsmartphone\b"],
    "desktop": [r"\bdesktop\b", r"\bgui\b", r"\bwindow\b",
                r"\bpyqt\b", r"\belectron\b", r"\bgtk\b"],
    "cli": [r"\bcli\b", r"\bcommand\b", r"\bterminal\b",
            r"\bscript\b", r"\bconsole\b"],
    "api": [r"\bapi\b", r"\brest\b", r"\bgraphql\b", r"\bendpoint\b",
            r"\bmicroservice\b"],
    "database": [r"\bdatabase\b", r"\bdb\b", r"\bsql\b",
                 r"\bnosql\b", r"\bmigration\b"],
}

FRAMEWORK_PATTERNS: Dict[str, Dict[str, List[str]]] = {
    "python": {
        "fastapi": [r"\bfastapi\b"],
        "flask": [r"\bflask\b"],
        "django": [r"\bdjango\b"],
        "click": [r"\bclick\b", r"\bcli\b"],
        "typer": [r"\btyper\b"],
    },
    "javascript": {
        "express": [r"\bexpress\b"],
        "react": [r"\breact\b"],
        "vue": [r"\bvue\b"],
        "nextjs": [r"\bnext\.?js\b", r"\bnextjs\b"],
    },
    "typescript": {
        "nextjs": [r"\bnext\.?js\b"],
        "nestjs": [r"\bnest\.?js\b", r"\bnestjs\b"],
        "angular": [r"\bangular\b"],
    },
    "java": {
        "spring_boot": [r"\bspring\b", r"\bspring\s*boot\b"],
        "quarkus": [r"\bquarkus\b"],
    },
}


# ──────────────────────────────────────────────
# Analyzer Class
# ──────────────────────────────────────────────

class PromptAnalyzer:
    """Analyzes raw user requests and produces structured analysis."""

    def __init__(self, text: str) -> None:
        """Initialize the analyzer with the user's raw input text.

        Args:
            text: The raw prompt or request from the user.
        """
        self.text = text.strip()
        self.text_lower = self.text.lower()

    def detect_language(self) -> LanguageDetection:
        """Detect the programming language and framework from the request text.

        Returns:
            LanguageDetection object with detected language, framework, and confidence.
        """
        detection = LanguageDetection()
        scores: Dict[str, float] = {}
        total_matches = 0

        # Score each language based on pattern matches
        for lang, patterns in LANGUAGE_PATTERNS.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, self.text_lower)
                score += len(matches)
            if score > 0:
                scores[lang] = score
                total_matches += score

        if not scores:
            # Default to Python with low confidence
            detection.language = "python"
            detection.confidence = 0.3
            detection.alternatives = ["python", "javascript", "bash"]
            return detection

        # Sort by score descending
        sorted_langs = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        # Primary language
        detection.language = sorted_langs[0][0]
        detection.confidence = sorted_langs[0][1] / max(total_matches, 1)

        # Alternatives
        detection.alternatives = [lang for lang, _ in sorted_langs[1:4]]

        # Detect framework
        lang_frameworks = FRAMEWORK_PATTERNS.get(detection.language, {})
        for fw_name, fw_patterns in lang_frameworks.items():
            for pattern in fw_patterns:
                if re.search(pattern, self.text_lower):
                    detection.framework = fw_name
                    break
            if detection.framework:
                break

        # Detect platform
        for platform, patterns in PLATFORM_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, self.text_lower):
                    detection.platform = platform
                    break
            if detection.platform:
                break

        logger.debug(
            "Language detection complete",
            extra={
                "language": detection.language,
                "framework": detection.framework,
                "platform": detection.platform,
                "confidence": round(detection.confidence, 2),
            },
        )

        return detection

    def detect_features(self) -> RequestFeatures:
        """Detect required features from the request text.

        Returns:
            RequestFeatures object indicating which capabilities are needed.
        """
        features = RequestFeatures()

        # File I/O
        features.has_file_io = bool(re.search(
            r"\b(file|read|write|open|save|load|import|export|csv|json|xml|yaml|txt)\b",
            self.text_lower,
        ))

        # Network / HTTP
        features.has_network = bool(re.search(
            r"\b(http|request|api|endpoint|url|fetch|curl|rest|socket|webhook)\b",
            self.text_lower,
        ))

        # Database
        features.has_database = bool(re.search(
            r"\b(database|db|sql|nosql|postgres|mysql|mongodb|redis|sqlite|query|orm)\b",
            self.text_lower,
        ))

        # Authentication
        features.has_auth = bool(re.search(
            r"\b(auth|login|password|token|jwt|oauth|session|cookie|permission|role)\b",
            self.text_lower,
        ))

        # UI
        features.has_ui = bool(re.search(
            r"\b(ui|gui|interface|button|form|webpage|template|react|vue|angular|html)\b",
            self.text_lower,
        ))

        # API
        features.has_api = bool(re.search(
            r"\b(api|rest|graphql|grpc|endpoint|route|swagger|openapi)\b",
            self.text_lower,
        ))

        # Concurrency
        features.has_concurrency = bool(re.search(
            r"\b(async|await|thread|parallel|concurrent|multi.?thread|coroutine)\b",
            self.text_lower,
        ))

        # Encryption
        features.has_encryption = bool(re.search(
            r"\b(encrypt|decrypt|hash|cipher|aes|rsa|sha|bcrypt|argon2)\b",
            self.text_lower,
        ))

        logger.debug(
            "Feature detection complete",
            extra={"features": features.__dict__},
        )

        return features

    def detect_missing_info(self) -> List[str]:
        """Identify missing critical information in the request.

        Returns:
            List of missing information items.
        """
        missing: List[str] = []

        # Check for language specification
        lang_detected = self.detect_language()
        if lang_detected.confidence < 0.5:
            missing.append("Programming language not explicitly specified")

        # Check for output format
        if not re.search(r"\b(output|format|return|result|generate|create|build|csv|json|html|pdf)\b", self.text_lower):
            missing.append("Desired output format not specified")

        # Check for input specification
        if not re.search(r"\b(input|from|read|take|accept|argument|parameter|file)\b", self.text_lower):
            missing.append("Input source not clearly defined")

        # Check for scale indication
        if not re.search(r"\b(small|large|production|enterprise|simple|complex|scale|big|performance)\b", self.text_lower):
            missing.append("Project scale or complexity not indicated")

        logger.debug(
            "Missing info detection complete",
            extra={"missing_items": missing},
        )

        return missing

    def generate_assumptions(self, missing_info: List[str], language: LanguageDetection) -> List[str]:
        """Generate reasonable assumptions to fill missing information gaps.

        Args:
            missing_info: List of missing items (from detect_missing_info).
            language: The detected language information.

        Returns:
            List of assumption statements.
        """
        assumptions: List[str] = []

        for item in missing_info:
            if "language" in item.lower():
                assumptions.append(
                    f"Language inferred as '{language.language}' "
                    f"(confidence: {language.confidence:.0%})"
                )
            elif "output" in item.lower():
                assumptions.append("Output format assumed as plain text / stdout")
            elif "input" in item.lower():
                assumptions.append("Input source assumed as command-line argument")
            elif "scale" in item.lower():
                assumptions.append("Project scale assumed as 'medium' (moderate complexity)")

        logger.debug(
            "Assumptions generated",
            extra={"assumptions": assumptions},
        )

        return assumptions

    def suggest_libraries(self, language: str, features: RequestFeatures) -> List[str]:
        """Suggest appropriate libraries based on the language and required features.

        Args:
            language: The detected programming language.
            features: The detected feature requirements.

        Returns:
            List of suggested library names with brief justifications.
        """
        suggestions: List[str] = []

        if language == "python":
            suggestions.append("argparse / click — CLI argument parsing")
            if features.has_network:
                suggestions.append("httpx / requests — HTTP client")
            if features.has_api:
                suggestions.append("fastapi / flask — Web API framework")
            if features.has_database:
                suggestions.append("sqlalchemy — ORM / database access")
            if features.has_concurrency:
                suggestions.append("asyncio — Async I/O support")
            if features.has_encryption:
                suggestions.append("bcrypt / cryptography — Security utilities")
            if features.has_ui:
                suggestions.append("pyqt6 / tkinter — Desktop GUI")
            suggestions.append("pytest — Testing framework")
            suggestions.append("pydantic — Data validation")
            suggestions.append("pyyaml — Configuration files")

        elif language == "rust":
            suggestions.append("clap — CLI argument parsing")
            suggestions.append("anyhow — Error handling")
            suggestions.append("serde + serde_json — Serialization")
            suggestions.append("tokio — Async runtime")
            if features.has_database:
                suggestions.append("sqlx / diesel — Database access")
            if features.has_network:
                suggestions.append("reqwest — HTTP client")

        elif language in ("javascript", "typescript"):
            suggestions.append("commander / yargs — CLI parsing")
            if features.has_api:
                suggestions.append("express / fastify — Web framework")
            if features.has_database:
                suggestions.append("prisma / drizzle — ORM")
            suggestions.append("vitest / jest — Testing")
            suggestions.append("zod — Validation")

        else:
            suggestions.append("Standard library utilities for the detected language")
            suggestions.append("Recommended framework for target platform")

        return suggestions

    def estimate_complexity(self, features: RequestFeatures) -> Tuple[str, int]:
        """Estimate the complexity and size of the requested project.

        Args:
            features: The detected feature requirements.

        Returns:
            Tuple of (complexity_level: str, estimated_lines: int).
        """
        score = 0
        for attr, value in features.__dict__.items():
            if value:
                score += 1

        if score <= 2:
            return ("low", 50)
        elif score <= 4:
            return ("medium", 200)
        elif score <= 6:
            return ("high", 800)
        else:
            return ("very_high", 2000)

    def analyze(self) -> AnalysisResult:
        """Perform a complete analysis of the user's request.

        This is the main entry point for the analysis phase.

        Returns:
            Complete AnalysisResult with all extracted information.
        """
        logger.info("Starting request analysis", extra={"text_length": len(self.text)})

        # Core analysis steps
        language = self.detect_language()
        features = self.detect_features()
        missing_info = self.detect_missing_info()
        assumptions = self.generate_assumptions(missing_info, language)
        suggested_libs = self.suggest_libraries(language.language, features)
        complexity, est_lines = self.estimate_complexity(features)

        # Generate summary
        if len(self.text) > 200:
            summary = self.text[:197] + "..."
        else:
            summary = self.text

        # Determine if clarification is needed
        needs_clarification = False
        clarification = ""

        # If no language detected and confidence is very low
        if language.confidence < 0.3 and not missing_info:
            needs_clarification = True
            clarification = (
                "I couldn't determine the programming language or platform "
                "from your request. Please specify: What language/framework "
                "would you like to use?"
            )

        result = AnalysisResult(
            original_text=self.text,
            summary=summary,
            language=language,
            features=features,
            missing_info=missing_info,
            assumptions=assumptions,
            suggested_libraries=suggested_libs,
            estimated_complexity=complexity,
            estimated_lines=est_lines,
            requires_clarification=needs_clarification,
            clarification_question=clarification,
        )

        logger.info(
            "Analysis complete",
            extra={
                "language": language.language,
                "framework": language.framework,
                "platform": language.platform,
                "complexity": complexity,
                "estimated_lines": est_lines,
                "missing_info_count": len(missing_info),
            },
        )

        return result