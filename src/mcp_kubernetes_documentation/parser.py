"""Parser for Kubernetes documentation markdown and YAML files."""

import re
from pathlib import Path

import frontmatter  # type: ignore[import-untyped]
import yaml

from mcp_kubernetes_documentation.models import Document, DocumentMetadata


class DocumentParser:
    """Parses markdown files with YAML frontmatter and structured YAML data files."""

    KUBERNETES_DOCS_BASE_URL = "https://kubernetes.io"

    def parse_file(self, file_path: Path, base_path: Path) -> Document | None:
        """Parse a markdown file and extract metadata and content.

        Args:
            file_path: Path to the markdown file.
            base_path: Base path of the documentation directory.

        Returns:
            Document instance or None if parsing fails.
        """
        try:
            post = frontmatter.load(file_path)
            metadata = self._extract_metadata(post.metadata, file_path)
            relative_path = file_path.relative_to(base_path)
            section = self._extract_section(relative_path)
            url = self._compute_url(relative_path)
            content = self._clean_content(post.content)

            return Document(
                path=str(relative_path),
                title=metadata.title,
                description=metadata.description,
                section=section,
                content=content,
                url=url,
            )
        except Exception:
            return None

    def parse_yaml_file(self, file_path: Path, base_path: Path) -> list[Document]:
        """Parse a YAML data file and extract documents.

        Supports release schedules, end-of-life releases, and announcements.

        Args:
            file_path: Path to the YAML file.
            base_path: Base path of the repository root.

        Returns:
            List of Document instances extracted from the YAML data.
        """
        try:
            with open(file_path) as f:
                data = yaml.safe_load(f)

            if not isinstance(data, dict):
                return []

            relative_path = file_path.relative_to(base_path)
            relative_str = str(relative_path)

            if relative_str == "data/releases/schedule.yaml":
                return self._parse_release_schedule(data, relative_str)
            elif relative_str == "data/releases/eol.yaml":
                return self._parse_eol_releases(data, relative_str)
            elif relative_str == "data/announcements/scheduled.yaml":
                return self._parse_announcements(data, relative_str)

            return []
        except Exception:
            return []

    def _extract_metadata(self, metadata: dict[str, object], file_path: Path) -> DocumentMetadata:
        """Extract structured metadata from frontmatter.

        Args:
            metadata: Dictionary of frontmatter fields.
            file_path: Path to the file for fallback title extraction.

        Returns:
            DocumentMetadata instance.
        """
        title = metadata.get("title")
        if not isinstance(title, str):
            # Fallback to filename if no title in frontmatter
            title = file_path.stem.replace("-", " ").replace("_", " ").title()

        description = metadata.get("description")
        if not isinstance(description, str):
            description = None

        license_info = metadata.get("license")
        if not isinstance(license_info, str):
            license_info = None

        return DocumentMetadata(
            title=title,
            description=description,
            license=license_info,
        )

    def _extract_section(self, relative_path: Path) -> str:
        """Extract the top-level section from the path.

        Args:
            relative_path: Path relative to docs directory.

        Returns:
            Section name (first directory component or 'root').
        """
        parts = relative_path.parts
        return parts[0] if len(parts) > 1 else "root"

    def _compute_url(self, relative_path: Path) -> str:
        """Compute the kubernetes.io documentation URL.

        Args:
            relative_path: Path relative to the content/en directory.

        Returns:
            Full URL to the documentation page.
        """
        path_str = str(relative_path)
        # Remove .md extension
        path_str = re.sub(r"\.md$", "", path_str)
        # Handle _index pages (Hugo section pages)
        path_str = re.sub(r"/_index$", "", path_str)
        # Handle root _index
        if path_str == "_index":
            path_str = ""

        if path_str:
            return f"{self.KUBERNETES_DOCS_BASE_URL}/{path_str}/"
        return f"{self.KUBERNETES_DOCS_BASE_URL}/"

    def _clean_content(self, content: str) -> str:
        """Clean markdown content for indexing.

        Removes Hugo-specific syntax and other markup artifacts.

        Args:
            content: Raw markdown content.

        Returns:
            Cleaned content suitable for indexing.
        """
        # Extract text from glossary_tooltip shortcodes
        content = re.sub(
            r'\{\{<\s*glossary_tooltip\s+text="([^"]+)"\s+term_id="[^"]*"\s*>\}\}',
            r"\1",
            content,
        )
        # Remove Hugo shortcode tags ({{< >}} form) while preserving inner content
        content = re.sub(r"\{\{<[^>]*>\}\}", "", content)
        # Remove Hugo shortcode tags ({{% %}} form) while preserving inner content
        content = re.sub(r"\{\{%[^%]*%\}\}", "", content)
        # Remove HTML comments
        content = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)
        # Remove HTML tags
        content = re.sub(r"<[^>]+>", "", content)
        return content.strip()

    def _parse_release_schedule(self, data: dict[str, object], file_path: str) -> list[Document]:
        """Parse release schedule YAML into documents.

        Each schedule entry becomes a separate document.

        Args:
            data: Parsed YAML data.
            file_path: Relative path to the YAML file.

        Returns:
            List of Document instances for each release schedule.
        """
        documents: list[Document] = []
        schedules = data.get("schedules")

        if not isinstance(schedules, list):
            return documents

        for schedule in schedules:
            if not isinstance(schedule, dict):
                continue

            version = str(schedule.get("release", "unknown"))
            release_date = schedule.get("releaseDate", "unknown")
            eol_date = schedule.get("endOfLifeDate", "unknown")
            maintenance_date = schedule.get("maintenanceModeStartDate", "unknown")

            lines = [
                f"Kubernetes {version} Release Schedule",
                "",
                f"Release date: {release_date}",
                f"End of life date: {eol_date}",
                f"Maintenance mode start date: {maintenance_date}",
            ]

            next_patch = schedule.get("next")
            if isinstance(next_patch, dict):
                lines.extend([
                    "",
                    f"Next patch release: {next_patch.get('release', 'unknown')}",
                    f"Target date: {next_patch.get('targetDate', 'unknown')}",
                    f"Cherry pick deadline: {next_patch.get('cherryPickDeadline', 'unknown')}",
                ])

            previous = schedule.get("previousPatches")
            if isinstance(previous, list) and previous:
                lines.extend(["", "Previous patches:"])
                for patch in previous:
                    if isinstance(patch, dict):
                        release_ver = patch.get("release", "unknown")
                        target_date = patch.get("targetDate", "unknown")
                        patch_line = f"  - {release_ver} (released {target_date})"
                        note = patch.get("note")
                        if isinstance(note, str):
                            patch_line += f" - {note}"
                        lines.append(patch_line)

            documents.append(
                Document(
                    path=f"{file_path}#{version}",
                    title=f"Kubernetes {version} Release Schedule",
                    description=f"Release schedule for Kubernetes {version}",
                    section="releases",
                    content="\n".join(lines),
                    url=f"{self.KUBERNETES_DOCS_BASE_URL}/releases/patch-releases/",
                )
            )

        return documents

    def _parse_eol_releases(self, data: dict[str, object], file_path: str) -> list[Document]:
        """Parse end-of-life releases YAML into documents.

        Each EOL entry becomes a separate document.

        Args:
            data: Parsed YAML data.
            file_path: Relative path to the YAML file.

        Returns:
            List of Document instances for each EOL release.
        """
        documents: list[Document] = []
        branches = data.get("branches")

        if not isinstance(branches, list):
            return documents

        for branch in branches:
            if not isinstance(branch, dict):
                continue

            version = str(branch.get("release", "unknown"))
            eol_date = branch.get("endOfLifeDate", "unknown")
            final_patch = branch.get("finalPatchRelease", "unknown")

            lines = [
                f"Kubernetes {version} End of Life",
                "",
                f"End of life date: {eol_date}",
                f"Final patch release: {final_patch}",
            ]

            note = branch.get("note")
            if isinstance(note, str):
                lines.extend(["", f"Note: {note}"])

            documents.append(
                Document(
                    path=f"{file_path}#{version}",
                    title=f"Kubernetes {version} End of Life",
                    description=f"End of life information for Kubernetes {version}",
                    section="releases",
                    content="\n".join(lines),
                    url=f"{self.KUBERNETES_DOCS_BASE_URL}/releases/patch-releases/",
                )
            )

        return documents

    def _parse_announcements(self, data: dict[str, object], file_path: str) -> list[Document]:
        """Parse announcements YAML into documents.

        Each announcement becomes a separate document.

        Args:
            data: Parsed YAML data.
            file_path: Relative path to the YAML file.

        Returns:
            List of Document instances for each announcement.
        """
        documents: list[Document] = []
        announcements = data.get("announcements")

        if not isinstance(announcements, list):
            return documents

        for announcement in announcements:
            if not isinstance(announcement, dict):
                continue

            name = announcement.get("name")
            if not isinstance(name, str):
                name = announcement.get("title", "Untitled announcement")
                if not isinstance(name, str):
                    name = "Untitled announcement"

            # Clean HTML from title for the document title
            clean_name = re.sub(r"<[^>]+>", "", name).strip()
            if not clean_name:
                clean_name = "Untitled announcement"

            message = announcement.get("message", "")
            if not isinstance(message, str):
                message = ""

            start_time = announcement.get("startTime", "")
            end_time = announcement.get("endTime", "")

            lines = [clean_name, ""]

            if start_time:
                lines.append(f"Start: {start_time}")
            if end_time:
                lines.append(f"End: {end_time}")
            if start_time or end_time:
                lines.append("")

            # Clean HTML from message content
            clean_message = re.sub(r"<[^>]+>", "", message).strip()
            if clean_message:
                lines.append(clean_message)

            # Sanitise name for use as fragment identifier
            fragment = re.sub(r"[^a-zA-Z0-9-]", "-", clean_name.lower()).strip("-")
            fragment = re.sub(r"-+", "-", fragment)

            documents.append(
                Document(
                    path=f"{file_path}#{fragment}",
                    title=clean_name,
                    description=None,
                    section="announcements",
                    content="\n".join(lines),
                    url=f"{self.KUBERNETES_DOCS_BASE_URL}/",
                )
            )

        return documents
