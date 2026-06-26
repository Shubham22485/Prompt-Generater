# Prompt Optimizer v3.0

> Transform rough, vague instructions into structured, production-ready AI prompts — automatically.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](pyproject.toml)
[![Status: Beta](https://img.shields.io/badge/status-beta-orange.svg)](pyproject.toml)

---

## Overview

**Universal Prompt Optimizer** takes a short, informal request — like *"write a python script to parse CSV files"* — and runs it through a five-stage pipeline that turns it into a fully structured, professional prompt suitable for any LLM:

1. **Analyze** — detects the target programming language, framework, platform, and required features (file I/O, network, database, auth, concurrency, encryption, etc.) from the raw text.
2. **Optimize** — rewrites vague phrasing, injects technical context, and expands the request into 10+ structured sections (Objective, Role, Task, Requirements, Workflow, Quality Standards, Error Handling, Edge Cases, and more).
3. **Format** — renders the result as clean **Markdown**, structured **JSON**, or **plain text**.
4. **Split** — automatically breaks oversized prompts into numbered, continuation-tagged parts at natural section boundaries.
5. **Validate** — runs a self-review pass checking for placeholders, missing sections, and risky code patterns before delivery.

---

## How It Works

```
Raw Request
    │
    ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Analyzer   │ ──▶ │  Optimizer  │ ──▶│  Formatter  │ ──▶ │  Splitter   │ ──▶│  Validator  │
│  (detect)   │     │  (expand)   │     │  (render)   │     │ (if needed) │     │  (verify)   │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                                                                                        │
                                                                                        ▼
                                                                              Optimized Prompt Output
```

| Module | Responsibility |
|---|---|
| `analyzer.py` | Detects language, framework, platform, and features via pattern matching; flags missing info and suggests libraries |
| `optimizer.py` | Generates the 10–13 structured prompt sections and assembles the final optimized text |
| `formatter.py` | Converts the optimized prompt into Markdown, JSON, or plain text |
| `splitter.py` | Splits oversized output into numbered parts at `##` section boundaries (falls back to paragraph-level splitting) |
| `validator.py` | Checks for placeholders/TODOs, required sections, and risky code patterns (`eval`, `exec`, `os.system`, etc.) |
| `config.py` | Layered configuration loader (defaults → YAML → env vars → CLI args) |
| `logger_setup.py` | Structured JSON/text logging with automatic sensitive-field masking |

---

## Features

- 🔍 **Automatic language & framework detection** — Python, JavaScript/TypeScript, Rust, Go, Java, C++, C#, Swift, Ruby, PHP, and their common frameworks (FastAPI, Flask, Django, React, Next.js, Spring Boot, etc.)
- 🧩 **Feature-aware analysis** — detects file I/O, networking, databases, authentication, UI, APIs, concurrency, and encryption needs from plain language
- 📋 **Gap detection with assumptions** — flags missing details (input source, output format, scale) and fills them with explicit, labeled assumptions instead of guessing silently
- 📚 **Library suggestions** — recommends idiomatic libraries per language (e.g. `httpx`, `sqlalchemy`, `clap`, `tokio`, `zod`)
- 📦 **Three output formats** — Markdown, JSON, or plain text
- ✂️ **Smart auto-splitting** — keeps each part under a configurable character limit without breaking mid-section
- ✅ **Built-in validation** — completeness, structure, and basic security pattern checks with a pass/fail score
- ⚙️ **Layered configuration** — hardcoded defaults → `config/default.yaml` → `config/custom.yaml` / `--config` → environment variables (`PROMPTOPT_*`) → CLI flags
- 🪵 **Structured logging** — JSON or colored console output, with automatic masking of sensitive fields (passwords, tokens, API keys, etc.)

---

## Installation

**Requirements:** Python 3.10+

```bash
# Clone the repository
git clone https://github.com/universalai/prompt-optimizer.git
cd prompt-optimizer

# Install dependencies
pip install -r requirements.txt

# (Optional) Install as an editable package, enables the `prompt-optimizer` CLI command
pip install -e .
```

---

## Quick Start

```bash
# Basic usage — pass the request as a positional argument
python src/main.py "Write a Python script to parse CSV files"

# Read the request from a file, write the result to a file
python src/main.py --input request.txt --output optimized.md

# Force a specific target language
python src/main.py --language rust "Build a CLI tool"

# Output as structured JSON with verbose logging
python src/main.py --format json --verbose "Create a FastAPI backend"

# Limit optimization level and disable auto-splitting
python src/main.py --level balanced --no-split "Build a desktop GUI app"
```

If installed via `pip install -e .`, the same commands work with the `prompt-optimizer` entry point:

```bash
prompt-optimizer "Build a CLI tool in Rust using Cargo"
```

---

## CLI Reference

| Flag | Description | Default |
|---|---|---|
| `text` (positional) | Raw prompt text to optimize | — |
| `-i, --input <path>` | Read the prompt from a file instead of the command line | — |
| `-o, --output <path>` | Write the result to a file instead of stdout | stdout |
| `-f, --format {markdown,json,plain}` | Output format | `markdown` |
| `-c, --config <path>` | Path to a custom YAML config file | — |
| `-l, --language <lang>` | Override auto-detected target language | auto-detect |
| `--level {basic,balanced,maximum}` | Optimization depth / number of sections generated | `maximum` |
| `--max-chars <int>` | Max characters per part before auto-splitting | `12000` |
| `-v, --verbose` | Enable debug logging and run the validation phase | off |
| `-q, --quiet` | Suppress non-essential console output | off |
| `--no-split` | Disable automatic splitting of large outputs | off |

> Note: `text` and `--input` are mutually exclusive — provide exactly one.

---

## Configuration

Configuration is resolved in layered priority order (each layer overrides the one before it):

1. Hardcoded defaults (`AppConfig` in `config.py`)
2. `config/default.yaml`
3. `config/custom.yaml` or a path passed via `--config`
4. Environment variables prefixed with `PROMPTOPT_`
5. Command-line arguments (highest priority)

### Example: `config/default.yaml`

```yaml
output_format: "markdown"      # markdown | json | plain
optimization_level: "maximum"  # basic | balanced | maximum
max_output_chars: 12000
auto_split: true
log_level: "INFO"
log_format: "json"             # json | text
```

### Example: environment variables (`.env`)

Copy `.env.example` to `.env` and adjust as needed:

```bash
PROMPTOPT_LOG_LEVEL=INFO
PROMPTOPT_OUTPUT_FORMAT=markdown
PROMPTOPT_OPTIMIZATION_LEVEL=maximum
PROMPTOPT_MAX_OUTPUT_CHARS=12000
PROMPTOPT_TARGET_LANGUAGE=
PROMPTOPT_OUTPUT_DIR=./outputs
```

---

## Optimized Prompt Structure

At `maximum` optimization level, every request is expanded into the following sections:

1. **Objective** — the high-level goal
2. **Background** — detected language, framework, and estimated complexity
3. **Role** — an expert persona tailored to the detected domain
4. **Task** — the original request plus explicit implementation requirements
5. **Requirements** — style, typing, validation, and security baseline
6. **Workflow** — a 7-step analyze → plan → implement → test → review → deliver process
7. **Constraints** — explicit "do not" rules (no pseudocode, no placeholders, no TODOs)
8. **Expected Output** — deliverable checklist (code, config, README, tests, usage examples)
9. **Quality Standards** — correctness, completeness, security, performance, readability
10. **Error Handling** — I/O, network retry, input validation, and resource cleanup rules
11. **Edge Cases** — empty input, large input, Unicode, concurrency, missing config, etc.

---

## Project Structure

```
prompt-optimizer/
├── src/
│   ├── __init__.py
│   ├── main.py            # CLI entry point and pipeline orchestration
│   ├── analyzer.py        # Language/framework/feature detection
│   ├── optimizer.py       # Section generation and prompt assembly
│   ├── formatter.py       # Markdown / JSON / plain-text rendering
│   ├── splitter.py        # Auto-splitting for large outputs
│   ├── validator.py       # Self-review / quality validation
│   ├── config.py          # Layered configuration loader
│   └── logger_setup.py    # Structured logging setup
├── config/
│   ├── default.yaml       # Default configuration
│   └── custom.yaml        # User overrides (optional)
├── tests/
│   └── test_analyzer.py   # Unit tests for the analyzer module
├── .env.example            # Environment variable template
├── requirements.txt
├── pyproject.toml
├── LICENSE
└── README.md
```

---

## Running Tests

```bash
pytest tests/ -v --cov=src --cov-report=term-missing
```

Or, using the project's lint/test tooling directly:

```bash
ruff check src/ tests/   # Linting
mypy src/                 # Static type checking
```

---

## Example Output (Markdown format)

```markdown
# Optimized Prompt — PYTHON

> **Generated:** 2026-06-25T00:00:00Z
> **Target Language:** python
> **Framework:** fastapi
> **Platform:** api
> **Complexity:** medium
> **Est. Size:** ~200 lines

## 1. OBJECTIVE
Develop a complete, production-ready python solution that fulfills...

## 3. ROLE
You are an expert backend engineer with deep knowledge of:
- REST API design
- Database integration
- Authentication and security
...
```

---

## License

Released under the **MIT License**. See [LICENSE](LICENSE) for details.

---
