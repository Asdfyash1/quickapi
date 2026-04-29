"""Tests for QuickAPI scaffolding."""

import tempfile
from pathlib import Path

from quickapi.scaffold import ProjectConfig, scaffold_project


def test_basic_scaffold():
    config = ProjectConfig(name="testapp")
    with tempfile.TemporaryDirectory() as tmpdir:
        created = scaffold_project(config, Path(tmpdir))
        root = Path(tmpdir) / "testapp"

        assert root.exists()
        assert (root / "testapp" / "main.py").exists()
        assert (root / "testapp" / "routes.py").exists()
        assert (root / "testapp" / "models.py").exists()
        assert (root / "testapp" / "config.py").exists()
        assert (root / "testapp" / "database.py").exists()
        assert (root / "requirements.txt").exists()
        assert (root / "README.md").exists()
        assert (root / "Dockerfile").exists()
        assert (root / "docker-compose.yml").exists()
        assert (root / "tests" / "test_api.py").exists()
        assert len(created) > 0


def test_scaffold_no_docker():
    config = ProjectConfig(name="nodockerapp", include_docker=False)
    with tempfile.TemporaryDirectory() as tmpdir:
        scaffold_project(config, Path(tmpdir))
        root = Path(tmpdir) / "nodockerapp"

        assert not (root / "Dockerfile").exists()
        assert not (root / "docker-compose.yml").exists()


def test_scaffold_with_auth():
    config = ProjectConfig(name="authapp", include_auth=True)
    with tempfile.TemporaryDirectory() as tmpdir:
        scaffold_project(config, Path(tmpdir))
        root = Path(tmpdir) / "authapp"

        assert (root / "authapp" / "auth.py").exists()
        main_content = (root / "authapp" / "main.py").read_text()
        assert "auth_router" in main_content


def test_scaffold_no_database():
    config = ProjectConfig(name="nodb", database="none")
    with tempfile.TemporaryDirectory() as tmpdir:
        scaffold_project(config, Path(tmpdir))
        root = Path(tmpdir) / "nodb"

        assert not (root / "nodb" / "database.py").exists()


def test_scaffold_custom_port():
    config = ProjectConfig(name="customport", port=3000)
    with tempfile.TemporaryDirectory() as tmpdir:
        scaffold_project(config, Path(tmpdir))
        root = Path(tmpdir) / "customport"

        dockerfile = (root / "Dockerfile").read_text()
        assert "3000" in dockerfile


def test_generated_project_structure():
    config = ProjectConfig(name="fullapp", include_auth=True)
    with tempfile.TemporaryDirectory() as tmpdir:
        created = scaffold_project(config, Path(tmpdir))
        root = Path(tmpdir) / "fullapp"

        expected_files = [
            "fullapp/__init__.py",
            "fullapp/main.py",
            "fullapp/routes.py",
            "fullapp/models.py",
            "fullapp/config.py",
            "fullapp/database.py",
            "fullapp/auth.py",
            "tests/__init__.py",
            "tests/test_api.py",
            "requirements.txt",
            ".env.example",
            ".gitignore",
            "README.md",
            "Dockerfile",
            "docker-compose.yml",
        ]

        for f in expected_files:
            assert (root / f).exists(), f"Missing: {f}"
