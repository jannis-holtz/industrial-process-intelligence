from pathlib import Path
import re


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_core_project_files_exist():
    """The repository should contain the core application, dashboard and pipeline files."""
    required_files = [
        "README.md",
        "requirements.txt",
        ".gitignore",
        "app/streamlit_app.py",
        "src/dashboard/components.py",
        "src/dashboard/data_access.py",
        "src/dashboard/styles.py",
        "src/dashboard/views/__init__.py",
        "src/dashboard/views/executive_overview.py",
        "src/dashboard/views/process_explorer.py",
        "src/dashboard/views/data_quality.py",
        "src/dashboard/views/variant_intelligence.py",
        "src/dashboard/views/bottleneck_analysis.py",
        "src/dashboard/views/sla_compliance.py",
        "src/dashboard/views/rework_detection.py",
        "src/dashboard/views/root_cause.py",
        "src/dashboard/views/recommendations.py",
        "src/dashboard/views/prediction.py",
        "src/dashboard/views/platform_layers.py",
        "scripts/09_validate_pipeline_outputs.py",
    ]

    missing_files = [
        file_path
        for file_path in required_files
        if not (PROJECT_ROOT / file_path).exists()
    ]

    assert not missing_files, f"Missing required project files: {missing_files}"


def test_readme_referenced_screenshots_exist():
    """Every screenshot referenced in the README should exist in the repository."""
    readme_path = PROJECT_ROOT / "README.md"
    readme_text = readme_path.read_text(encoding="utf-8")

    image_paths = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", readme_text)

    missing_images = [
        image_path
        for image_path in image_paths
        if not (PROJECT_ROOT / image_path).exists()
    ]

    assert not missing_images, f"README references missing screenshots: {missing_images}"


def test_gitignore_excludes_large_or_generated_artifacts():
    """Large data files, raw logs and generated ML outputs should not be committed."""
    gitignore_path = PROJECT_ROOT / ".gitignore"
    gitignore_text = gitignore_path.read_text(encoding="utf-8")

    required_patterns = [
        ".venv/",
        "data/raw/",
        "data/processed/",
        "*.xes",
        "*.parquet",
        "outputs/ml/",
        "__pycache__/",
    ]

    missing_patterns = [
        pattern
        for pattern in required_patterns
        if pattern not in gitignore_text
    ]

    assert not missing_patterns, f"Missing .gitignore patterns: {missing_patterns}"