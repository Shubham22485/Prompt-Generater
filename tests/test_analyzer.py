"""Tests for the PromptAnalyzer module."""

import pytest
from src.analyzer import PromptAnalyzer, LanguageDetection


class TestLanguageDetection:
    """Test suite for language detection."""

    def test_detect_python(self):
        analyzer = PromptAnalyzer("Write a Python script to parse CSV files")
        result = analyzer.detect_language()
        assert result.language == "python"
        assert result.confidence >= 0.5

    def test_detect_javascript(self):
        analyzer = PromptAnalyzer("Create a React component with TypeScript")
        result = analyzer.detect_language()
        assert result.language in ("javascript", "typescript")

    def test_detect_rust(self):
        analyzer = PromptAnalyzer("Build a CLI tool in Rust using Cargo")
        result = analyzer.detect_language()
        assert result.language == "rust"

    def test_detect_fastapi(self):
        analyzer = PromptAnalyzer("Create a FastAPI backend with PostgreSQL")
        result = analyzer.detect_language()
        assert result.language == "python"
        assert result.framework == "fastapi"

    def test_low_confidence_defaults_to_python(self):
        analyzer = PromptAnalyzer("Make something useful")
        result = analyzer.detect_language()
        assert result.language == "python"

    def test_empty_string(self):
        analyzer = PromptAnalyzer("")
        result = analyzer.detect_language()
        assert result.language == "python"


class TestFeatureDetection:
    """Test suite for feature detection."""

    def test_detect_file_io(self):
        analyzer = PromptAnalyzer("Read a CSV file and write results to JSON")
        assert analyzer.detect_features().has_file_io is True

    def test_detect_network(self):
        analyzer = PromptAnalyzer("Fetch data from an API endpoint")
        assert analyzer.detect_features().has_network is True

    def test_detect_database(self):
        analyzer = PromptAnalyzer("Connect to PostgreSQL and run queries")
        assert analyzer.detect_features().has_database is True

    def test_detect_auth(self):
        analyzer = PromptAnalyzer("Implement JWT login and password hashing")
        assert analyzer.detect_features().has_auth is True

    def test_detect_concurrency(self):
        analyzer = PromptAnalyzer("Use async/await for concurrent requests")
        assert analyzer.detect_features().has_concurrency is True

    def test_detect_encryption(self):
        analyzer = PromptAnalyzer("Encrypt data with AES-256-GCM")
        assert analyzer.detect_features().has_encryption is True


class TestMissingInfoDetection:
    """Test suite for missing information detection."""

    def test_vague_request_identifies_gaps(self):
        analyzer = PromptAnalyzer("Do something")
        missing = analyzer.detect_missing_info()
        assert len(missing) > 0

    def test_detailed_request_has_few_gaps(self):
        analyzer = PromptAnalyzer(
            "Write a Python CLI tool using Click that reads a JSON input "
            "file and outputs a formatted report as HTML"
        )
        missing = analyzer.detect_missing_info()
        assert len(missing) < 3  # Should have few gaps


class TestLibrarySuggestions:
    """Test suite for library suggestions."""

    def test_python_suggestions(self):
        analyzer = PromptAnalyzer("Write a Python script")
        from src.analyzer import RequestFeatures
        features = RequestFeatures(has_network=True, has_database=True)
        suggestions = analyzer.suggest_libraries("python", features)
        assert any("httpx" in s for s in suggestions)
        assert any("sqlalchemy" in s for s in suggestions)

    def test_rust_suggestions(self):
        analyzer = PromptAnalyzer("Build CLI tool")
        from src.analyzer import RequestFeatures
        features = RequestFeatures()
        suggestions = analyzer.suggest_libraries("rust", features)
        assert any("clap" in s for s in suggestions)