"""Prompt Formatter — Handles output formatting in multiple formats.

Supported formats:
  - markdown: Readable with sections, headers, and formatting
  - json: Structured JSON for programmatic consumption
  - plain: Clean plain text without markdown
"""

from __future__ import annotations

import json
from typing import Dict, Any
from datetime import datetime

from .optimizer import OptimizedPrompt
from .analyzer import AnalysisResult
from .logger_setup import get_logger

logger = get_logger(__name__)


class PromptFormatter:
    """Formats optimized prompts into various output formats."""

    @staticmethod
    def to_markdown(optimized: OptimizedPrompt, analysis: AnalysisResult) -> str:
        """Format the optimized prompt as readable Markdown.

        Args:
            optimized: The optimized prompt result.
            analysis: The original analysis result.

        Returns:
            Formatted markdown string.
        """
        lines: list[str] = []
        lines.append(f"# {optimized.title}")
        lines.append("")
        lines.append(f"> **Generated:** {optimized.timestamp}")
        lines.append(f"> **Target Language:** {analysis.language.language}")
        lines.append(f"> **Framework:** {analysis.language.framework or 'Auto-detected'}")
        lines.append(f"> **Platform:** {analysis.language.platform}")
        lines.append(f"> **Complexity:** {analysis.estimated_complexity}")
        lines.append(f"> **Est. Size:** ~{analysis.estimated_lines} lines")
        lines.append(f"> **Word Count:** {optimized.word_count}")
        lines.append(f"> **Est. Tokens:** {optimized.estimated_tokens}")
        lines.append("")

        # Assumptions section (if any)
        if analysis.assumptions:
            lines.append("## Assumptions Made")
            lines.append("")
            for assumption in analysis.assumptions:
                lines.append(f"- *{assumption}*")
            lines.append("")

        # Missing info warning (if any)
        if analysis.missing_info:
            lines.append("## ⚠️ Missing Information")
            lines.append("")
            for info in analysis.missing_info:
                lines.append(f"- {info}")
            lines.append("")
            lines.append("> **Note:** The optimizer made reasonable assumptions. Review and adjust if needed.")
            lines.append("")

        # Main optimized content
        lines.append("---")
        lines.append("")
        lines.append(optimized.optimized_text)

        # Footer
        lines.append("")
        lines.append("---")
        lines.append(f"*Optimized by Universal Prompt Optimizer v3.0*")
        lines.append(f"*Sections: {', '.join(optimized.sections)}*")

        return "\n".join(lines)

    @staticmethod
    def to_json(optimized: OptimizedPrompt, analysis: AnalysisResult) -> str:
        """Format the optimized prompt as structured JSON.

        Args:
            optimized: The optimized prompt result.
            analysis: The original analysis result.

        Returns:
            JSON string.
        """
        output: Dict[str, Any] = {
            "meta": {
                "title": optimized.title,
                "timestamp": optimized.timestamp,
                "version": "3.0.0",
                "optimizer": "Universal Prompt Optimizer",
            },
            "analysis": {
                "language": analysis.language.language,
                "framework": analysis.language.framework,
                "platform": analysis.language.platform,
                "confidence": round(analysis.language.confidence, 2),
                "complexity": analysis.estimated_complexity,
                "estimated_lines": analysis.estimated_lines,
                "features": {
                    "file_io": analysis.features.has_file_io,
                    "network": analysis.features.has_network,
                    "database": analysis.features.has_database,
                    "authentication": analysis.features.has_auth,
                    "ui": analysis.features.has_ui,
                    "api": analysis.features.has_api,
                    "concurrency": analysis.features.has_concurrency,
                    "encryption": analysis.features.has_encryption,
                },
                "missing_info": analysis.missing_info,
                "assumptions": analysis.assumptions,
                "suggested_libraries": analysis.suggested_libraries,
            },
            "optimized": {
                "text": optimized.optimized_text,
                "sections": optimized.sections,
                "word_count": optimized.word_count,
                "estimated_tokens": optimized.estimated_tokens,
                "level": optimized.optimization_level_applied,
            },
        }
        return json.dumps(output, indent=2, ensure_ascii=False)

    @staticmethod
    def to_plain(optimized: OptimizedPrompt, analysis: AnalysisResult) -> str:
        """Format the optimized prompt as plain text (no markdown).

        Args:
            optimized: The optimized prompt result.
            analysis: The original analysis result.

        Returns:
            Plain text string.
        """
        lines: list[str] = []
        lines.append("=" * 70)
        lines.append(f"  {optimized.title}")
        lines.append("=" * 70)
        lines.append(f"Language: {analysis.language.language}")
        lines.append(f"Platform: {analysis.language.platform}")
        lines.append(f"Size: ~{analysis.estimated_lines} lines")
        lines.append("=" * 70)
        lines.append("")

        # Strip markdown headers from optimized text
        text = optimized.optimized_text
        text = text.replace("#", "").replace("*", "").replace("`", "")
        lines.append(text)

        lines.append("")
        lines.append("=" * 70)
        lines.append(f"Generated: {optimized.timestamp}")
        lines.append("=" * 70)

        return "\n".join(lines)

    @staticmethod
    def format(
        optimized: OptimizedPrompt,
        analysis: AnalysisResult,
        output_format: str = "markdown",
    ) -> str:
        """Format the output in the requested format.

        Args:
            optimized: The optimized prompt result.
            analysis: The original analysis result.
            output_format: 'markdown', 'json', or 'plain'.

        Returns:
            Formatted string.

        Raises:
            ValueError: If an unsupported format is specified.
        """
        format_map = {
            "markdown": PromptFormatter.to_markdown,
            "json": PromptFormatter.to_json,
            "plain": PromptFormatter.to_plain,
        }

        formatter = format_map.get(output_format)
        if formatter is None:
            raise ValueError(
                f"Unsupported output format: '{output_format}'. "
                f"Supported formats: {', '.join(format_map.keys())}"
            )

        logger.debug("Formatting output", extra={"format": output_format})
        return formatter(optimized, analysis)