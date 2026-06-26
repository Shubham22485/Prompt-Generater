"""Prompt Optimizer — Transforms raw requests into professional optimized prompts.

This module implements the core optimization logic from the Master Prompt:
  - Section generation
  - Professional formatting
  - Technical detail expansion
  - Quality standard enforcement
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime

from .analyzer import AnalysisResult
from .logger_setup import get_logger

logger = get_logger(__name__)


# ──────────────────────────────────────────────
# Optimization Result
# ──────────────────────────────────────────────

@dataclass
class OptimizedPrompt:
    """The fully optimized prompt with metadata."""
    title: str = ""
    raw_input: str = ""
    optimized_text: str = ""
    sections: List[str] = field(default_factory=list)
    word_count: int = 0
    estimated_tokens: int = 0
    optimization_level_applied: str = "maximum"
    target_language: str = "auto"
    target_model: str = "auto"
    timestamp: str = ""


# ──────────────────────────────────────────────
# Section Templates
# ──────────────────────────────────────────────

SECTION_TEMPLATES = {
    "objective": """## 1. OBJECTIVE
{content}""",

    "background": """## 2. BACKGROUND
{content}""",

    "role": """## 3. ROLE
You are an expert {domain} with deep knowledge of:
- {skill_1}
- {skill_2}
- {skill_3}""",

    "task": """## 4. TASK
{content}""",

    "requirements": """## 5. REQUIREMENTS
{content}""",

    "workflow": """## 6. WORKFLOW
{steps}""",

    "constraints": """## 7. CONSTRAINTS
{content}""",

    "expected_output": """## 8. EXPECTED OUTPUT
{content}""",

    "formatting": """## 9. FORMATTING REQUIREMENTS
{content}""",

    "quality_standards": """## 10. QUALITY STANDARDS
{content}""",

    "examples": """## 11. EXAMPLES
{content}""",

    "error_handling": """## 12. ERROR HANDLING
{content}""",

    "edge_cases": """## 13. EDGE CASES
{content}""",
}


# ──────────────────────────────────────────────
# Optimization Rules
# ──────────────────────────────────────────────

class OptimizationRules:
    """Collection of optimization transformation rules."""

    @staticmethod
    def expand_vague_verbs(text: str) -> str:
        """Replace vague verbs with precise technical alternatives."""
        replacements = {
            r"\bmake\b": "implement",
            r"\bdo\b": "execute",
            r"\bget\b": "retrieve",
            r"\bput\b": "place",
            r"\bthing\b": "component",
            r"\bstuff\b": "functionality",
            r"\bchange\b": "modify",
            r"\bfix\b": "resolve",
            r"\bshow\b": "display",
            r"\btell\b": "indicate",
        }
        for pattern, replacement in replacements.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text

    @staticmethod
    def add_technical_terms(text: str) -> str:
        """Add missing technical terminology context."""
        # Detect missing domain context and add boilerplate
        if "function" in text.lower() and "parameter" not in text.lower():
            text += "\n\nAll functions must have clearly defined parameters with type hints and return types."
        if "error" in text.lower() and "exception" not in text.lower():
            text += "\n\nAll error states must be handled with appropriate exception types and meaningful error messages."
        return text

    @staticmethod
    def enforce_professional_tone(text: str) -> str:
        """Remove casual language and enforce professional tone."""
        casual_phrases = [
            (r"\bjust\b", ""),
            (r"\bsimply\b", ""),
            (r"\bbasically\b", ""),
            (r"\byou know\b", ""),
            (r"\blike\b", "such as"),
            (r"\breally\b", ""),
            (r"\bkind of\b", "somewhat"),
            (r"\ba lot\b", "significantly"),
        ]
        for pattern, replacement in casual_phrases:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text.strip()

    @staticmethod
    def add_structure(text: str) -> str:
        """Add markdown structure if missing."""
        lines = text.split("\n")
        has_headers = any(line.startswith("#") for line in lines)
        if not has_headers:
            # Add a title if there are no headers
            first_line = lines[0] if lines else "Untitled Request"
            text = f"# {first_line}\n\n" + "\n".join(lines[1:])
        return text


# ──────────────────────────────────────────────
# Optimizer Class
# ──────────────────────────────────────────────

class PromptOptimizer:
    """Main optimizer that transforms raw requests into professional prompts.

    Usage:
        optimizer = PromptOptimizer()
        result = optimizer.optimize(analysis_result)
    """

    def __init__(self, optimization_level: str = "maximum") -> None:
        """Initialize the optimizer.

        Args:
            optimization_level: 'basic', 'balanced', or 'maximum'.
                'maximum' applies all rules and generates all sections.
        """
        self.level = optimization_level
        self.rules = OptimizationRules()

    def generate_sections(self, analysis: AnalysisResult) -> Dict[str, str]:
        """Generate all applicable sections for the optimized prompt.

        Args:
            analysis: The complete analysis result.

        Returns:
            Dictionary mapping section names to their rendered content.
        """
        sections: Dict[str, str] = {}
        text = analysis.original_text

        # 1. Objective
        sections["objective"] = SECTION_TEMPLATES["objective"].format(
            content=f"Develop a complete, production-ready {analysis.language.language} "
                    f"solution that fulfills the following request:\n\n{text}"
        )

        # 2. Background
        background_parts = [
            f"The user has requested a {analysis.language.language}-based solution.",
        ]
        if analysis.language.framework:
            background_parts.append(
                f"The target framework is {analysis.language.framework}."
            )
        background_parts.append(
            f"The estimated project complexity is {analysis.estimated_complexity} "
            f"(approximately {analysis.estimated_lines} lines of code)."
        )
        sections["background"] = SECTION_TEMPLATES["background"].format(
            content="\n".join(background_parts)
        )

        # 3. Role
        domain_map = {
            "python": "Python developer",
            "javascript": "JavaScript/Node.js developer",
            "typescript": "TypeScript developer",
            "rust": "Rust systems programmer",
            "go": "Go developer",
            "java": "Java enterprise developer",
            "c++": "C++ systems programmer",
            "c#": "C# .NET developer",
            "swift": "Swift/iOS developer",
            "ruby": "Ruby developer",
            "php": "PHP developer",
        }
        domain = domain_map.get(analysis.language.language, "software engineer")

        # Generate relevant skills from detected features
        features = analysis.features
        skills = [
            f"{analysis.language.language} standard library and ecosystem",
        ]
        if features.has_file_io:
            skills.append("File I/O, serialization, and data processing")
        if features.has_network:
            skills.append("Network programming and HTTP protocols")
        if features.has_database:
            skills.append("Database design, ORM, and query optimization")
        if features.has_api:
            skills.append("RESTful API design and implementation")
        if features.has_auth:
            skills.append("Authentication, authorization, and security best practices")
        if features.has_concurrency:
            skills.append("Concurrent and parallel programming patterns")
        if features.has_encryption:
            skills.append("Cryptography and secure data handling")

        # Pad to at least 3 skills
        while len(skills) < 3:
            skills.append("Software design patterns and architecture")
            if len(skills) < 3:
                skills.append("Testing and quality assurance")

        sections["role"] = SECTION_TEMPLATES["role"].format(
            domain=domain,
            skill_1=skills[0],
            skill_2=skills[1] if len(skills) > 1 else skills[0],
            skill_3=skills[2] if len(skills) > 2 else skills[0],
        )

        # 4. Task
        sections["task"] = SECTION_TEMPLATES["task"].format(
            content=(
                f"Take the following request and produce a complete, working "
                f"implementation in {analysis.language.language}.\n\n"
                f"**Original Request:**\n{text}\n\n"
                f"**Implementation Requirements:**\n"
                f"- Language: {analysis.language.language}\n"
                f"- Framework: {analysis.language.framework or 'Standard library / user preference'}\n"
                f"- Platform: {analysis.language.platform}\n"
                f"- All requested features must be fully implemented\n"
                f"- No placeholder code, TODOs, or pseudocode"
            )
        )

        # 5. Requirements
        req_items = [
            "Follow the language's official style guide",
            "All functions must include type hints / type annotations",
            "Every public function must have a docstring",
            "Input validation at all system boundaries",
            "Appropriate error handling with meaningful messages",
            "No hardcoded secrets, paths, or credentials",
        ]
        if features.has_api:
            req_items.append("Implement proper HTTP status codes and error responses")
        if features.has_database:
            req_items.append("Use parameterized queries to prevent injection attacks")
        if features.has_network:
            req_items.append("Implement timeout handling and retry logic")

        sections["requirements"] = SECTION_TEMPLATES["requirements"].format(
            content="\n".join(f"- {r}" for r in req_items)
        )

        # 6. Workflow
        workflow_steps = [
            "1. **Analyze** — Parse the original request and identify core functionality",
            "2. **Plan** — Design the architecture, module breakdown, and data flow",
            "3. **Select Libraries** — Choose appropriate libraries based on requirements",
            "4. **Implement** — Write complete, working code for each module",
            "5. **Test** — Write and run unit tests for all public functions",
            "6. **Review** — Self-review for correctness, security, and performance",
            "7. **Deliver** — Present the complete implementation with documentation",
        ]
        sections["workflow"] = SECTION_TEMPLATES["workflow"].format(
            steps="\n".join(workflow_steps)
        )

        # 7. Expected Output
        sections["expected_output"] = SECTION_TEMPLATES["expected_output"].format(
            content=(
                "Provide the complete implementation including:\n"
                "- Full project folder structure\n"
                "- All source files with complete code (no placeholders)\n"
                "- Configuration file (if applicable)\n"
                "- Dependency file (requirements.txt, package.json, etc.)\n"
                "- Installation instructions\n"
                "- Usage examples (minimum 3)\n"
                "- Testing instructions and sample tests\n"
                "- README.md documentation"
            )
        )

        # 8. Quality Standards
        sections["quality_standards"] = SECTION_TEMPLATES["quality_standards"].format(
            content=(
                "- **Correctness:** The code must compile/run without errors\n"
                "- **Completeness:** All requested features must be implemented\n"
                "- **Security:** No injection vulnerabilities, hardcoded secrets, or unsafe functions\n"
                "- **Performance:** Optimize time and memory complexity\n"
                "- **Readability:** Clear naming, comments, and documentation\n"
                "- **Production-readiness:** Handle edge cases, errors, and graceful shutdown"
            )
        )

        # 9. Error Handling (always included for maximum level)
        if self.level == "maximum":
            sections["error_handling"] = SECTION_TEMPLATES["error_handling"].format(
                content=(
                    "- Every I/O operation must have error handling\n"
                    "- Network timeouts must have retry logic (max 3 retries, exponential backoff)\n"
                    "- Invalid user input must produce clear error messages\n"
                    "- File operations must handle missing files, permission errors, and disk full\n"
                    "- Database operations must handle connection failures and constraint violations\n"
                    "- Resource cleanup must occur in all exit paths (use context managers / try-finally)"
                )
            )

        # 10. Edge Cases
        sections["edge_cases"] = SECTION_TEMPLATES["edge_cases"].format(
            content=(
                "- Empty input / null values\n"
                "- Very large input (streaming/chunking required)\n"
                "- Special characters and Unicode\n"
                "- Concurrent access (if applicable)\n"
                "- Network failures and timeouts\n"
                "- Missing configuration values\n"
                "- Invalid configuration types\n"
                "- Cross-platform path separators and line endings"
            )
        )

        return sections

    def optimize(self, analysis: AnalysisResult) -> OptimizedPrompt:
        """Execute the full optimization pipeline.

        Args:
            analysis: The complete analysis result from the analyzer.

        Returns:
            OptimizedPrompt with the full optimized text and metadata.
        """
        logger.info("Starting prompt optimization", extra={"level": self.level})

        # Step 1: Apply transformation rules
        text = analysis.original_text
        text = self.rules.expand_vague_verbs(text)
        text = self.rules.enforce_professional_tone(text)
        text = self.rules.add_technical_terms(text)
        text = self.rules.add_structure(text)

        # Step 2: Generate sections
        sections = self.generate_sections(analysis)

        # Step 3: Assemble the optimized prompt
        optimized_parts: List[str] = []
        ordered_sections = [
            "objective",
            "background",
            "role",
            "task",
            "requirements",
            "workflow",
            "expected_output",
            "quality_standards",
        ]

        # Add additional sections for maximum level
        if self.level == "maximum":
            ordered_sections.extend(["error_handling", "edge_cases"])

        if self.level in ("balanced", "maximum"):
            ordered_sections.append("constraints")
            sections["constraints"] = SECTION_TEMPLATES["constraints"].format(
                content=(
                    "- Do NOT add disclaimers about authorization or consultation\n"
                    "- Do NOT replace working code with pseudocode\n"
                    "- Do NOT use placeholder comments (TODO, FIXME, etc.)\n"
                    "- Do NOT skip error handling\n"
                    "- Output the complete solution in one response (or split automatically if needed)"
                )
            )

        for section_name in ordered_sections:
            if section_name in sections:
                optimized_parts.append(sections[section_name])

        optimized_text = "\n\n".join(optimized_parts)

        # Step 4: Add final instruction block
        optimized_text += (
            "\n\n---\n\n"
            "**FINAL INSTRUCTION:**\n"
            "Execute the above workflow step by step. "
            "Deliver the complete, production-ready implementation. "
            "If the output exceeds your context limit, split into numbered parts "
            "at natural file boundaries. Verify all code before delivery."
        )

        # Step 5: Build result object
        word_count = len(optimized_text.split())
        estimated_tokens = int(word_count * 1.3)  # Rough estimate

        result = OptimizedPrompt(
            title=f"Optimized Prompt — {analysis.language.language.upper()}",
            raw_input=analysis.original_text,
            optimized_text=optimized_text,
            sections=ordered_sections,
            word_count=word_count,
            estimated_tokens=estimated_tokens,
            optimization_level_applied=self.level,
            target_language=analysis.language.language,
            timestamp=datetime.utcnow().isoformat() + "Z",
        )

        logger.info(
            "Optimization complete",
            extra={
                "word_count": word_count,
                "estimated_tokens": estimated_tokens,
                "section_count": len(ordered_sections),
            },
        )

        return result