"""Configuration management with layered priority system.

Priority hierarchy (lowest to highest):
    1. Hardcoded defaults
    2. Default config file (config/default.yaml)
    3. User config file (config/custom.yaml or --config path)
    4. Command-line arguments
    5. Environment variables
"""

from __future__ import annotations

import os
import json
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, field, asdict

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore


# ──────────────────────────────────────────────
# Configuration Data Class
# ──────────────────────────────────────────────

@dataclass
class AppConfig:
    """Central configuration object for the Prompt Optimizer."""

    # ── General ──
    verbose: bool = False
    quiet: bool = False
    output_dir: str = "./outputs"
    config_path: Optional[str] = None

    # ── Input / Output ──
    input_file: Optional[str] = None
    input_text: Optional[str] = None
    output_file: Optional[str] = None
    output_format: str = "markdown"  # markdown | json | plain

    # ── Optimization Settings ──
    target_model: str = "auto"
    target_language: str = "auto"
    optimization_level: str = "maximum"  # basic | balanced | maximum
    preserve_intent: bool = True
    add_sections: bool = True
    add_examples: bool = True
    add_edge_cases: bool = True
    add_error_handling: bool = True

    # ── Splitting ──
    max_output_chars: int = 12000
    auto_split: bool = True
    split_at_sections: bool = True

    # ── Logging ──
    log_level: str = "INFO"
    log_file: Optional[str] = None
    log_format: str = "json"  # json | text

    # ── Testing ──
    generate_tests: bool = False
    generate_requirements: bool = True
    generate_readme: bool = True

    # ── Templates ──
    template_dir: str = ""
    template_name: str = "master_prompt.j2"


# ──────────────────────────────────────────────
# Default values (hardcoded fallback)
# ──────────────────────────────────────────────

DEFAULT_CONFIG: Dict[str, Any] = asdict(AppConfig())

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_DIR = PROJECT_ROOT / "config"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "outputs"
DEFAULT_TEMPLATE_DIR = PROJECT_ROOT / "src" / "templates"


# ──────────────────────────────────────────────
# Configuration Loader
# ──────────────────────────────────────────────

class ConfigLoader:
    """Loads configuration from multiple sources with proper layering."""

    def __init__(self) -> None:
        self.config = AppConfig()

    def load_defaults(self) -> None:
        """Start with hardcoded defaults."""
        self.config = AppConfig()

    def load_yaml(self, path: str) -> Dict[str, Any]:
        """Load configuration from a YAML file.

        Args:
            path: Absolute or relative path to the YAML file.

        Returns:
            Parsed configuration dictionary.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the YAML is invalid or PyYAML is not installed.
        """
        if yaml is None:
            raise ValueError(
                "PyYAML is not installed. Install it with: pip install pyyaml"
            )

        filepath = Path(path)
        if not filepath.exists():
            raise FileNotFoundError(f"Config file not found: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            try:
                data = yaml.safe_load(f)
                if not isinstance(data, dict):
                    raise ValueError(f"Config file must contain a top-level mapping: {path}")
                return data
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML in {path}: {e}")

    def load_json(self, path: str) -> Dict[str, Any]:
        """Load configuration from a JSON file."""
        filepath = Path(path)
        if not filepath.exists():
            raise FileNotFoundError(f"Config file not found: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_env(self) -> Dict[str, Any]:
        """Load configuration from environment variables.

        Reads all env vars prefixed with `PROMPTOPT_`.
        """
        env_config: Dict[str, Any] = {}
        prefix = "PROMPTOPT_"

        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower()
                # Type coercion
                if value.lower() in ("true", "yes", "1"):
                    value = True
                elif value.lower() in ("false", "no", "0"):
                    value = False
                elif value.isdigit():
                    value = int(value)
                env_config[config_key] = value

        return env_config

    def apply_dict(self, data: Dict[str, Any]) -> None:
        """Merge a dictionary into the current config (overwrites matching keys)."""
        for key, value in data.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)

    def load(self, config_path: Optional[str] = None) -> AppConfig:
        """Full layered configuration load.

        Args:
            config_path: Optional explicit path to a config file.

        Returns:
            Fully resolved AppConfig object.
        """
        # 1. Hardcoded defaults
        self.load_defaults()

        # 2. Default config file
        default_file = DEFAULT_CONFIG_DIR / "default.yaml"
        if default_file.exists():
            try:
                data = self.load_yaml(str(default_file))
                self.apply_dict(data)
            except (FileNotFoundError, ValueError):
                pass  # Silently skip if default is missing

        # 3. User config file
        if config_path:
            try:
                data = self.load_yaml(config_path)
                self.apply_dict(data)
            except (FileNotFoundError, ValueError) as e:
                if not self.config.quiet:
                    print(f"Warning: Could not load config {config_path}: {e}")

        # 4. Environment variables (highest priority after CLI)
        env_data = self.load_env()
        self.apply_dict(env_data)

        return self.config

    def update_from_cli(self, cli_args: Dict[str, Any]) -> None:
        """Apply CLI argument overrides (highest priority)."""
        # Filter out None values (unset CLI args)
        filtered = {k: v for k, v in cli_args.items() if v is not None}
        self.apply_dict(filtered)


# ──────────────────────────────────────────────
# Singleton accessor
# ──────────────────────────────────────────────

_config_loader: Optional[ConfigLoader] = None


def get_config(config_path: Optional[str] = None) -> AppConfig:
    """Get the application configuration (singleton pattern)."""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader.load(config_path)