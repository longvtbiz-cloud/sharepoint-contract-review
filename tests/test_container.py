from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_dockerfile_uses_python_311_slim() -> None:
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")

    assert "FROM python:3.11-slim" in dockerfile


def test_dockerfile_runs_as_non_root_user() -> None:
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")

    assert "USER appuser" in dockerfile
    assert "useradd" in dockerfile


def test_dockerfile_exposes_healthcheck() -> None:
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")

    assert "HEALTHCHECK" in dockerfile
    assert "http://127.0.0.1:8080/health" in dockerfile


def test_dockerignore_excludes_local_only_paths() -> None:
    dockerignore = (ROOT / ".dockerignore").read_text(encoding="utf-8")

    for path in [".pytest_cache/", ".tools/", ".github/", "tests/", "git.cmd"]:
        assert path in dockerignore
