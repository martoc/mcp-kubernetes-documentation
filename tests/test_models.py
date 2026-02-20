"""Tests for data models."""

from mcp_kubernetes_documentation.models import Document, DocumentMetadata, SearchResult


def test_document_metadata_creation() -> None:
    """Test creating a DocumentMetadata instance."""
    metadata = DocumentMetadata(
        title="Pod Lifecycle",
        description="Describes the lifecycle of a Pod",
        license="CC BY 4.0",
    )
    assert metadata.title == "Pod Lifecycle"
    assert metadata.description == "Describes the lifecycle of a Pod"
    assert metadata.license == "CC BY 4.0"


def test_document_metadata_optional_fields() -> None:
    """Test DocumentMetadata with optional fields."""
    metadata = DocumentMetadata(title="Pods")
    assert metadata.title == "Pods"
    assert metadata.description is None
    assert metadata.license is None


def test_document_creation() -> None:
    """Test creating a Document instance."""
    doc = Document(
        path="docs/concepts/workloads/pods/pod-lifecycle.md",
        title="Pod Lifecycle",
        description="Describes the lifecycle of a Pod",
        section="docs",
        content="# Pod Lifecycle\n\nContent here",
        url="https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/",
    )
    assert doc.path == "docs/concepts/workloads/pods/pod-lifecycle.md"
    assert doc.title == "Pod Lifecycle"
    assert doc.section == "docs"
    assert "Content here" in doc.content


def test_search_result_creation() -> None:
    """Test creating a SearchResult instance."""
    result = SearchResult(
        path="docs/concepts/workloads/pods/pod-lifecycle.md",
        title="Pod Lifecycle",
        url="https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/",
        snippet="...pod lifecycle phases...",
        score=12.5,
        section="docs",
    )
    assert result.path == "docs/concepts/workloads/pods/pod-lifecycle.md"
    assert result.score == 12.5
    assert result.section == "docs"
