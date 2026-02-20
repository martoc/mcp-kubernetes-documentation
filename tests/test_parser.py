"""Tests for document parser."""

import tempfile
from pathlib import Path
from typing import Any

import yaml

from mcp_kubernetes_documentation.parser import DocumentParser


def test_extract_section_root() -> None:
    """Test extracting section from root-level file."""
    parser = DocumentParser()
    section = parser._extract_section(Path("_index.md"))
    assert section == "root"


def test_extract_section_nested() -> None:
    """Test extracting section from nested file."""
    parser = DocumentParser()
    section = parser._extract_section(Path("docs/concepts/overview.md"))
    assert section == "docs"


def test_compute_url_regular_file() -> None:
    """Test computing documentation URL for a regular file."""
    parser = DocumentParser()
    url = parser._compute_url(Path("docs/concepts/overview/what-is-kubernetes.md"))
    assert url == "https://kubernetes.io/docs/concepts/overview/what-is-kubernetes/"


def test_compute_url_index_file() -> None:
    """Test computing URL for an _index.md file."""
    parser = DocumentParser()
    url = parser._compute_url(Path("docs/concepts/_index.md"))
    assert url == "https://kubernetes.io/docs/concepts/"


def test_compute_url_root_index() -> None:
    """Test computing URL for root _index.md."""
    parser = DocumentParser()
    url = parser._compute_url(Path("_index.md"))
    assert url == "https://kubernetes.io/"


def test_clean_content_removes_hugo_shortcodes() -> None:
    """Test cleaning content removes Hugo shortcode tags."""
    parser = DocumentParser()
    content = "{{< note >}}\nThis is a note.\n{{< /note >}}\nRegular content."
    cleaned = parser._clean_content(content)
    assert "{{<" not in cleaned
    assert "This is a note." in cleaned
    assert "Regular content." in cleaned


def test_clean_content_extracts_glossary_text() -> None:
    """Test cleaning content extracts text from glossary_tooltip shortcodes."""
    parser = DocumentParser()
    content = 'A {{< glossary_tooltip text="Pod" term_id="pod" >}} runs containers.'
    cleaned = parser._clean_content(content)
    assert "A Pod runs containers." == cleaned


def test_clean_content_removes_html_comments() -> None:
    """Test cleaning content removes HTML comments."""
    parser = DocumentParser()
    content = "<!-- Comment -->\nContent\n<!-- Another -->"
    cleaned = parser._clean_content(content)
    assert "<!--" not in cleaned
    assert "Content" in cleaned


def test_parse_file_with_frontmatter() -> None:
    """Test parsing a file with YAML frontmatter."""
    parser = DocumentParser()

    with tempfile.TemporaryDirectory() as temp_dir:
        base_path = Path(temp_dir)
        file_path = base_path / "test.md"

        content = """---
title: Pod Lifecycle
description: Describes the lifecycle of a Pod
---

# Pod Lifecycle

This is a test.
"""
        file_path.write_text(content)

        doc = parser.parse_file(file_path, base_path)

        assert doc is not None
        assert doc.title == "Pod Lifecycle"
        assert doc.description == "Describes the lifecycle of a Pod"
        assert "Pod Lifecycle" in doc.content
        assert doc.path == "test.md"


def test_parse_file_without_frontmatter() -> None:
    """Test parsing a file without YAML frontmatter."""
    parser = DocumentParser()

    with tempfile.TemporaryDirectory() as temp_dir:
        base_path = Path(temp_dir)
        file_path = base_path / "test-file.md"

        content = "# Test Content\n\nThis is a test."
        file_path.write_text(content)

        doc = parser.parse_file(file_path, base_path)

        assert doc is not None
        assert doc.title == "Test File"  # Fallback from filename
        assert "Test Content" in doc.content


def test_parse_release_schedule_yaml() -> None:
    """Test parsing release schedule YAML data."""
    parser = DocumentParser()

    data: dict[str, Any] = {
        "schedules": [
            {
                "release": "1.35",
                "releaseDate": "2025-12-17",
                "endOfLifeDate": "2027-02-28",
                "maintenanceModeStartDate": "2026-12-28",
                "next": {
                    "cherryPickDeadline": "2026-03-06",
                    "release": 1.352,
                    "targetDate": "2026-03-10",
                },
                "previousPatches": [
                    {
                        "cherryPickDeadline": "2026-02-06",
                        "release": 1.351,
                        "targetDate": "2026-02-10",
                        "note": "January 2026 patches consolidated with February",
                    }
                ],
            }
        ]
    }

    documents = parser._parse_release_schedule(data, "data/releases/schedule.yaml")
    assert len(documents) == 1
    assert documents[0].path == "data/releases/schedule.yaml#1.35"
    assert documents[0].title == "Kubernetes 1.35 Release Schedule"
    assert documents[0].section == "releases"
    assert "2025-12-17" in documents[0].content
    assert "2027-02-28" in documents[0].content


def test_parse_eol_yaml() -> None:
    """Test parsing end-of-life releases YAML data."""
    parser = DocumentParser()

    data: dict[str, Any] = {
        "branches": [
            {
                "release": "1.26",
                "endOfLifeDate": "2024-02-28",
                "finalPatchRelease": 1.2615,
                "note": "Final patch after EOL for Go CVEs",
            }
        ]
    }

    documents = parser._parse_eol_releases(data, "data/releases/eol.yaml")
    assert len(documents) == 1
    assert documents[0].path == "data/releases/eol.yaml#1.26"
    assert documents[0].title == "Kubernetes 1.26 End of Life"
    assert documents[0].section == "releases"
    assert "2024-02-28" in documents[0].content
    assert "Go CVEs" in documents[0].content


def test_parse_announcements_yaml() -> None:
    """Test parsing announcements YAML data."""
    parser = DocumentParser()

    data: dict[str, Any] = {
        "announcements": [
            {
                "name": "Dockershim removal",
                "startTime": "2022-04-07T00:00:00",
                "endTime": "2022-05-09T00:00:00",
                "message": "Dockershim is no longer included in Kubernetes.",
            }
        ]
    }

    documents = parser._parse_announcements(data, "data/announcements/scheduled.yaml")
    assert len(documents) == 1
    assert documents[0].title == "Dockershim removal"
    assert documents[0].section == "announcements"
    assert "Dockershim" in documents[0].content


def test_parse_announcements_yaml_empty() -> None:
    """Test parsing announcements YAML with empty announcements list."""
    parser = DocumentParser()

    data: dict[str, Any] = {"announcements": []}

    documents = parser._parse_announcements(data, "data/announcements/scheduled.yaml")
    assert len(documents) == 0


def test_parse_yaml_file_produces_multiple_documents() -> None:
    """Test that parse_yaml_file produces multiple documents from one YAML file."""
    parser = DocumentParser()

    with tempfile.TemporaryDirectory() as temp_dir:
        repo_root = Path(temp_dir)
        releases_dir = repo_root / "data" / "releases"
        releases_dir.mkdir(parents=True)

        schedule_data = {
            "schedules": [
                {
                    "release": "1.34",
                    "releaseDate": "2025-08-13",
                    "endOfLifeDate": "2026-10-28",
                    "maintenanceModeStartDate": "2026-08-13",
                },
                {
                    "release": "1.35",
                    "releaseDate": "2025-12-17",
                    "endOfLifeDate": "2027-02-28",
                    "maintenanceModeStartDate": "2026-12-28",
                },
            ]
        }

        schedule_file = releases_dir / "schedule.yaml"
        with open(schedule_file, "w") as f:
            yaml.dump(schedule_data, f)

        documents = parser.parse_yaml_file(schedule_file, repo_root)
        assert len(documents) == 2
        assert documents[0].path == "data/releases/schedule.yaml#1.34"
        assert documents[1].path == "data/releases/schedule.yaml#1.35"
