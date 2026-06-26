"""Auto-Splitter — Automatically splits large outputs into parts.

When the optimized prompt exceeds the maximum character limit,
this module splits it at natural section boundaries into
numbered parts with continuation markers.
"""

from __future__ import annotations

import re
from typing import List, Tuple, Optional
from dataclasses import dataclass, field

from .logger_setup import get_logger

logger = get_logger(__name__)


# ──────────────────────────────────────────────
# Split Result
# ──────────────────────────────────────────────

@dataclass
class SplitResult:
    """Result of splitting a large prompt into parts."""
    parts: List[str] = field(default_factory=list)
    total_parts: int = 0
    original_length: int = 0
    exceeded: bool = False


# ──────────────────────────────────────────────
# Splitter Class
# ──────────────────────────────────────────────

class PromptSplitter:
    """Splits large optimized prompts into manageable parts.

    Splitting occurs at section boundaries (## headers) to ensure
    each part contains complete, readable sections.
    """

    def __init__(self, max_chars: int = 12000) -> None:
        """Initialize the splitter.

        Args:
            max_chars: Maximum characters per part. Default 12000.
        """
        self.max_chars = max_chars

    def _find_section_boundaries(self, text: str) -> List[int]:
        """Find all section header positions in the text.

        Args:
            text: The full optimized prompt text.

        Returns:
            List of character positions where sections begin.
        """
        boundaries: List[int] = [0]  # Always include start
        # Match markdown headers (## Header, ### Header, etc.)
        pattern = re.compile(r"^#{1,4}\s+\S", re.MULTILINE)

        for match in pattern.finditer(text):
            pos = match.start()
            if pos > 0 and pos not in boundaries:
                boundaries.append(pos)

        # Also add the end of text
        if len(text) not in boundaries:
            boundaries.append(len(text))

        return sorted(boundaries)

    def _calculate_optimal_split(self, boundaries: List[int]) -> List[Tuple[int, int]]:
        """Calculate split ranges that keep each part under the limit.

        Args:
            boundaries: List of character positions of section boundaries.

        Returns:
            List of (start, end) tuples for each part.
        """
        ranges: List[Tuple[int, int]] = []
        part_start = 0

        for i in range(1, len(boundaries)):
            current_boundary = boundaries[i]
            section_size = current_boundary - part_start

            if section_size > self.max_chars:
                # This section alone exceeds the limit — split at the boundary
                ranges.append((part_start, boundaries[i - 1]))
                part_start = boundaries[i - 1]

        # Add the last part
        if part_start < boundaries[-1]:
            ranges.append((part_start, boundaries[-1]))

        # If still too large, split by paragraph
        if not ranges or ranges[-1][1] - ranges[0][0] > self.max_chars * 1.5:
            # Fall back: one range covering everything (will trigger paragraph split)
            return [(0, boundaries[-1])]

        return ranges

    def _split_by_paragraph(self, text: str) -> List[str]:
        """Last resort: split by double newline (paragraph) boundaries.

        Args:
            text: Text that is too large even at section level.

        Returns:
            List of text parts.
        """
        paragraphs = text.split("\n\n")
        parts: List[str] = []
        current_part: List[str] = []
        current_size = 0

        for para in paragraphs:
            para_size = len(para) + 2  # +2 for the newlines
            if current_size + para_size > self.max_chars and current_part:
                parts.append("\n\n".join(current_part))
                current_part = [para]
                current_size = para_size
            else:
                current_part.append(para)
                current_size += para_size

        if current_part:
            parts.append("\n\n".join(current_part))

        return parts

    def _wrap_single(self, text: str, part_num: int, total: int, title: str) -> str:
        """Wrap a single part with headers and continuation markers.

        Args:
            text: The text content for this part.
            part_num: Current part number (1-indexed).
            total: Total number of parts.
            title: The project title.

        Returns:
            Wrapped part text.
        """
        prefix_lines = [
            f"PROJECT: {title}",
            f"PART {part_num}/{total}",
            "",
        ]

        suffix_lines = [
            "",
            "—" * 50,
            f"END OF PART {part_num}/{total}",
        ]

        if part_num < total:
            suffix_lines.append("")
            suffix_lines.append(f"→ CONTINUE TO PART {part_num + 1}")

        return "\n".join(prefix_lines) + text + "\n".join(suffix_lines)

    def split(self, text: str, title: str = "Optimized Prompt") -> SplitResult:
        """Split the text into parts if it exceeds the character limit.

        Args:
            text: The full optimized prompt text.
            title: The title/name of the prompt.

        Returns:
            SplitResult with parts or single-element list if no split needed.
        """
        original_length = len(text)

        # Check if splitting is needed
        if original_length <= self.max_chars:
            logger.debug(
                "No splitting needed",
                extra={"length": original_length, "max": self.max_chars},
            )
            return SplitResult(
                parts=[text],
                total_parts=1,
                original_length=original_length,
                exceeded=False,
            )

        logger.info(
            "Splitting required",
            extra={
                "length": original_length,
                "max": self.max_chars,
                "excess": original_length - self.max_chars,
            },
        )

        # Step 1: Try section-level splitting
        boundaries = self._find_section_boundaries(text)
        ranges = self._calculate_optimal_split(boundaries)

        # If the ranges are still too big, fall back to paragraph split
        if len(ranges) == 1 and (ranges[0][1] - ranges[0][0]) > self.max_chars:
            parts_raw = self._split_by_paragraph(text)
        else:
            parts_raw = [text[start:end] for start, end in ranges]

        # Step 2: Wrap each part with headers
        total_parts = len(parts_raw)
        wrapped_parts: List[str] = []

        for i, part_text in enumerate(parts_raw, 1):
            wrapped = self._wrap_single(part_text, i, total_parts, title)
            wrapped_parts.append(wrapped)

        # Verify: each wrapped part should be within limit (or close to it)
        for i, part in enumerate(wrapped_parts):
            if len(part) > self.max_chars * 1.1:
                logger.warning(
                    f"Part {i + 1} still exceeds limit ({len(part)} chars)",
                )

        logger.info(
            "Splitting complete",
            extra={"total_parts": total_parts},
        )

        return SplitResult(
            parts=wrapped_parts,
            total_parts=total_parts,
            original_length=original_length,
            exceeded=True,
        )