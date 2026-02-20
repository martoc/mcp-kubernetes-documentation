"""Tests for database operations."""

import tempfile
from pathlib import Path

from mcp_kubernetes_documentation.database import DocumentDatabase
from mcp_kubernetes_documentation.models import Document


def test_database_initialisation() -> None:
    """Test database initialisation creates schema."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        db = DocumentDatabase(db_path)
        assert db.db_path == db_path
        assert db_path.exists()


def test_upsert_document() -> None:
    """Test inserting and updating a document."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        db = DocumentDatabase(db_path)

        doc = Document(
            path="docs/concepts/pods.md",
            title="Pods",
            description="Understanding Pods",
            section="docs",
            content="Content about Kubernetes Pods",
            url="https://kubernetes.io/docs/concepts/pods/",
        )

        db.upsert_document(doc)
        retrieved = db.get_document("docs/concepts/pods.md")

        assert retrieved is not None
        assert retrieved.title == "Pods"
        assert retrieved.content == "Content about Kubernetes Pods"


def test_upsert_document_update() -> None:
    """Test updating an existing document."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        db = DocumentDatabase(db_path)

        doc1 = Document(
            path="docs/concepts/pods.md",
            title="Original",
            description=None,
            section="docs",
            content="Original content",
            url="https://kubernetes.io/docs/concepts/pods/",
        )
        db.upsert_document(doc1)

        doc2 = Document(
            path="docs/concepts/pods.md",
            title="Updated",
            description=None,
            section="docs",
            content="Updated content",
            url="https://kubernetes.io/docs/concepts/pods/",
        )
        db.upsert_document(doc2)

        retrieved = db.get_document("docs/concepts/pods.md")
        assert retrieved is not None
        assert retrieved.title == "Updated"
        assert retrieved.content == "Updated content"


def test_search_documents() -> None:
    """Test searching documents."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        db = DocumentDatabase(db_path)

        doc1 = Document(
            path="doc1.md",
            title="Kubernetes Deployments",
            description="Deployment guide",
            section="docs",
            content="This document covers Kubernetes Deployment concepts",
            url="https://kubernetes.io/docs/concepts/deployments/",
        )
        doc2 = Document(
            path="doc2.md",
            title="Kubernetes Services",
            description="Services guide",
            section="docs",
            content="This document covers Kubernetes Service networking",
            url="https://kubernetes.io/docs/concepts/services/",
        )

        db.upsert_document(doc1)
        db.upsert_document(doc2)

        results = db.search("deployment")
        assert len(results) > 0
        assert any("Deployment" in r.title for r in results)


def test_search_with_section_filter() -> None:
    """Test searching with section filter."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        db = DocumentDatabase(db_path)

        doc1 = Document(
            path="doc1.md",
            title="Kubernetes Pods",
            description=None,
            section="docs",
            content="Pod documentation content",
            url="https://kubernetes.io/docs/concepts/pods/",
        )
        doc2 = Document(
            path="doc2.md",
            title="Kubernetes Blog Post",
            description=None,
            section="blog",
            content="Blog post about Kubernetes",
            url="https://kubernetes.io/blog/post/",
        )

        db.upsert_document(doc1)
        db.upsert_document(doc2)

        results = db.search("Kubernetes", section="docs")
        assert len(results) == 1
        assert results[0].section == "docs"


def test_get_document_not_found() -> None:
    """Test getting a non-existent document."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        db = DocumentDatabase(db_path)

        result = db.get_document("nonexistent.md")
        assert result is None


def test_clear_database() -> None:
    """Test clearing all documents."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        db = DocumentDatabase(db_path)

        doc = Document(
            path="test.md",
            title="Test",
            description=None,
            section="docs",
            content="Content",
            url="https://kubernetes.io/docs/test/",
        )
        db.upsert_document(doc)

        assert db.get_document_count() == 1

        db.clear()

        assert db.get_document_count() == 0


def test_get_document_count() -> None:
    """Test getting document count."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        db = DocumentDatabase(db_path)

        assert db.get_document_count() == 0

        for i in range(5):
            doc = Document(
                path=f"doc{i}.md",
                title=f"Doc {i}",
                description=None,
                section="docs",
                content=f"Content {i}",
                url=f"https://kubernetes.io/docs/doc{i}/",
            )
            db.upsert_document(doc)

        assert db.get_document_count() == 5
