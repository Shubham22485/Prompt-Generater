#!/usr/bin/env python3
"""Universal Prompt Optimizer v3.0 — Main Entry Point.

Usage:
    prompt-optimizer "Write a Python script that..."
    prompt-optimizer --input request.txt --output optimized.md
    prompt-optimizer --language python --level maximum "Build an API"
"""

from __future__ import annotations

import sys
import os
from pathlib import Path

# Add src to path for direct execution
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import get_config, AppConfig, PROJECT_ROOT, DEFAULT_OUTPUT_DIR
from src.logger_setup import get_logger
from src.analyzer import PromptAnalyzer
from src.optimizer import PromptOptimizer
from src.formatter import PromptFormatter
from src.splitter import PromptSplitter
from src.validator import PromptValidator


def create_output_dir(config: AppConfig) -> Path:
    """Ensure output directory exists."""
    out_dir = Path(config.output_dir or DEFAULT_OUTPUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def read_input(source: str) -> str:
    """Read input from a file or treat as raw text."""
    if source and Path(source).exists():
        with open(source, "r", encoding="utf-8") as f:
            return f.read().strip()
    return source.strip()


def save_output(text: str, filepath: Path) -> None:
    """Save output text to a file."""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)


def run_pipeline(raw_input: str, config: AppConfig) -> str:
    """Execute the full optimization pipeline.

    Steps:
        1. Analyze
        2. Optimize
        3. Format
        4. Split (if needed)
        5. Validate
        6. Output
    """
    logger = get_logger(
        level=config.log_level,
        log_file=config.log_file,
        log_format=config.log_format,
        verbose=config.verbose,
    )

    logger.info("=== Pipeline Start ===")

    # ── Step 1: Analyze ──
    logger.info("Phase 1: Analyzing request...")
    analyzer = PromptAnalyzer(raw_input)
    analysis = analyzer.analyze()

    if analysis.requires_clarification:
        logger.warning(f"Clarification needed: {analysis.clarification_question}")
        return f"⚠️ CLARIFICATION NEEDED\n\n{analysis.clarification_question}"

    # Log analysis summary
    logger.info(f"  Language: {analysis.language.language}")
    logger.info(f"  Framework: {analysis.language.framework or 'auto'}")
    logger.info(f"  Platform: {analysis.language.platform}")
    logger.info(f"  Complexity: {analysis.estimated_complexity}")
    logger.info(f"  Est. Lines: {analysis.estimated_lines}")
    if analysis.assumptions:
        for a in analysis.assumptions:
            logger.info(f"  Assumption: {a}")
    if analysis.missing_info:
        for m in analysis.missing_info:
            logger.warning(f"  Missing: {m}")

    # ── Step 2: Optimize ──
    logger.info("Phase 2: Optimizing prompt...")
    optimizer = PromptOptimizer(optimization_level=config.optimization_level)
    optimized = optimizer.optimize(analysis)

    # ── Step 3: Format ──
    logger.info(f"Phase 3: Formatting as {config.output_format}...")
    formatter = PromptFormatter()
    formatted = formatter.format(optimized, analysis, config.output_format)

    # ── Step 4: Split ──
    if config.auto_split:
        logger.info("Phase 4: Checking if splitting is needed...")
        splitter = PromptSplitter(max_chars=config.max_output_chars)
        split_result = splitter.split(formatted, optimized.title)
        
        if split_result.exceeded:
            logger.info(f"  Splitting into {split_result.total_parts} parts")
            # Join parts with part separators
            final_output = "\n\n=== NEXT PART ===\n\n".join(split_result.parts)
        else:
            logger.info("  No splitting needed")
            final_output = formatted
    else:
        final_output = formatted

    # ── Step 5: Validate ──
    if config.verbose:
        logger.info("Phase 5: Validating output...")
        validator = PromptValidator()
        validation = validator.validate(optimized.optimized_text)
        if validation.passed:
            logger.info(f"  ✅ Validation passed (score: {validation.score:.0%})")
        else:
            logger.warning(f"  ⚠️ Validation issues found (score: {validation.score:.0%})")
            for err in validation.errors:
                logger.warning(f"    - {err}")

    logger.info("=== Pipeline Complete ===")
    return final_output


def display_summary(final_output: str, config: AppConfig) -> None:
    """Display a brief summary to the user."""
    lines = final_output.split("\n")
    part_count = final_output.count("=== NEXT PART ===") + 1
    word_count = len(final_output.split())
    
    summary = [
        "\n" + "=" * 60,
        "  ✅ OPTIMIZATION COMPLETE",
        "=" * 60,
        f"  Output format: {config.output_format}",
        f"  Total parts: {part_count}",
        f"  Total words: ~{word_count}",
        f"  Saved to: {config.output_file or 'stdout'}",
        "=" * 60,
    ]
    print("\n".join(summary))


def main() -> None:
    """Main CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Universal Prompt Optimizer v3.0 — Transform rough prompts into professional, production-ready instructions.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "Write a Python script to parse CSV files"
  %(prog)s --input request.txt --output optimized.md
  %(prog)s --language rust --level maximum "Build a CLI tool"
  %(prog)s --format json --verbose "Create a FastAPI backend"
        """,
    )

    # Input
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "text", nargs="?", type=str, default=None,
        help="Raw prompt text to optimize (positional argument)",
    )
    input_group.add_argument(
        "-i", "--input", type=str, default=None,
        help="Path to input file containing the prompt",
    )

    # Output
    parser.add_argument(
        "-o", "--output", type=str, default=None,
        help="Output file path (default: stdout)",
    )
    parser.add_argument(
        "-f", "--format", type=str, default="markdown",
        choices=["markdown", "json", "plain"],
        help="Output format (default: markdown)",
    )

    # Configuration
    parser.add_argument(
        "-c", "--config", type=str, default=None,
        help="Path to YAML config file",
    )
    parser.add_argument(
        "-l", "--language", type=str, default=None,
        help="Target programming language (overrides auto-detection)",
    )
    parser.add_argument(
        "--level", type=str, default="maximum",
        choices=["basic", "balanced", "maximum"],
        help="Optimization level (default: maximum)",
    )
    parser.add_argument(
        "--max-chars", type=int, default=12000,
        help="Maximum characters per part when splitting (default: 12000)",
    )

    # Behavior
    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="Enable verbose/debug logging",
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true",
        help="Suppress non-essential output",
    )
    parser.add_argument(
        "--no-split", action="store_true",
        help="Disable automatic splitting for large outputs",
    )

    args = parser.parse_args()

    # ── Load Configuration ──
    config_loader = get_config.__wrapped__ if hasattr(get_config, "__wrapped__") else None
    config = get_config(args.config)

    # Apply CLI overrides
    if args.format:
        config.output_format = args.format
    if args.output:
        config.output_file = args.output
    if args.level:
        config.optimization_level = args.level
    if args.verbose:
        config.verbose = True
        config.log_level = "DEBUG"
    if args.quiet:
        config.quiet = True
    if args.no_split:
        config.auto_split = False
    if args.max_chars:
        config.max_output_chars = args.max_chars

    # ── Initialize Logger ──
    logger = get_logger(
        level=config.log_level,
        log_file=config.log_file,
        log_format=config.log_format,
        verbose=config.verbose,
    )

    # ── Read Input ──
    if args.input:
        raw_input = read_input(args.input)
        if not raw_input:
            print("Error: Input file is empty or not found.")
            sys.exit(1)
    elif args.text:
        raw_input = args.text
    else:
        parser.print_help()
        sys.exit(1)

    # Inject language override
    if args.language:
        # Prepend a language hint for the analyzer
        raw_input = f"[LANGUAGE: {args.language}]\n{raw_input}"

    # ── Execute Pipeline ──
    try:
        final_output = run_pipeline(raw_input, config)
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        print(f"Error: {e}")
        sys.exit(1)

    # ── Output ──
    if config.output_file:
        out_path = Path(config.output_file)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        save_output(final_output, out_path)
        if not config.quiet:
            display_summary(final_output, config)
        logger.info(f"Output saved to: {out_path}")
    else:
        print(final_output)


if __name__ == "__main__":
    main()