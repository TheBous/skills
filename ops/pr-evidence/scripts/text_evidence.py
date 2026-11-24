"""Text evidence: database rows, log excerpts and tool output, shown inline in the PR description as collapsible blocks."""

import html
import re
from pathlib import Path

SUFFIXES = {".txt", ".log", ".json", ".sql", ".csv", ".out"}
BLOCK = re.compile(r"^<details><summary>", re.M)
# Text that would close or fake the evidence section, or read as a screenshot link, cannot go inline.
FORBIDDEN = ("<!-- pr-evidence:", "![")
BACKTICKS = re.compile(r"`+")


class TextEvidenceError(ValueError):
    pass


def is_text(path: Path) -> bool:
    return path.suffix.lower() in SUFFIXES


def read(path: Path) -> str:
    try:
        content = path.read_text(encoding="utf-8").strip("\n")
    except UnicodeDecodeError as error:
        raise TextEvidenceError(f"{path.name} is not UTF-8 text") from error
    if not content.strip():
        raise TextEvidenceError(f"{path.name} is empty")
    if any(token in content for token in FORBIDDEN):
        raise TextEvidenceError(f"{path.name} contains `<!-- pr-evidence:` or `![`; remove those lines from the excerpt")
    return content


def block(caption: str, content: str) -> str:
    """A collapsed block titled with the caption; the fence is longer than any backtick run in the content."""
    fence = "`" * max(3, 1 + max((len(run) for run in BACKTICKS.findall(content)), default=0))
    return f"<details><summary>{html.escape(caption)}</summary>\n\n{fence}text\n{content}\n{fence}\n\n</details>"
