"""
Knowledge Base Document Loader & Smart Section-Aware Chunker.
Supports Markdown (.md), plain text (.txt), and PDF (.pdf) documents.
"""

from dataclasses import dataclass, field, asdict
import hashlib
import logging
from pathlib import Path
import re
from typing import Dict, List, Tuple

logger = logging.getLogger("sahai_coop.ai.loader")

# Map subfolder names to frontend TOPIC_DISPLAY keys
FOLDER_TO_TOPIC = {
    "pmfby": "crop_insurance",
    "crop_insurance": "crop_insurance",
    "cooperative_laws": "cooperative_rules",
    "cooperative_rules": "cooperative_rules",
    "grievance": "grievance",
    "government_schemes": "government_schemes",
    "pacs": "pacs",
    "financial_literacy": "documents",
    "documents": "documents",
}


@dataclass
class DocumentChunk:
    chunk_id: str
    content: str
    topic: str
    source_title: str
    source_url: str
    file_name: str
    section: str = ""
    keywords: str = ""
    metadata: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "DocumentChunk":
        return cls(**data)


def _parse_frontmatter(raw_text: str) -> Tuple[Dict[str, str], str]:
    """Parse lightweight YAML-like frontmatter delimited by --- at the top of a file."""
    meta: Dict[str, str] = {}
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", raw_text, flags=re.DOTALL)
    if not match:
        return meta, raw_text

    header_block = match.group(1)
    body = raw_text[match.end():].strip()
    for line in header_block.splitlines():
        if ":" in line:
            key, val = line.split(":", 1)
            meta[key.strip().lower()] = val.strip()
    return meta, body


def _read_pdf_text(file_path: Path) -> str:
    """Extract text from a PDF file using pypdf if available."""
    try:
        from pypdf import PdfReader
    except ImportError:
        logger.warning(f"pypdf not installed; skipping PDF file {file_path.name}")
        return ""

    try:
        reader = PdfReader(str(file_path))
        pages = []
        for idx, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if text.strip():
                pages.append(f"## Page {idx + 1}\n{text.strip()}")
        return "\n\n".join(pages)
    except Exception as e:
        logger.error(f"Failed to read PDF {file_path}: {e}")
        return ""


def _split_into_sections(text: str) -> List[Tuple[str, str]]:
    """
    Split markdown text into (section_heading, section_body) tuples
    so semantic units remain intact before length-based chunking.
    """
    lines = text.splitlines()
    sections: List[Tuple[str, str]] = []
    current_heading = "Overview"
    current_lines: List[str] = []

    for line in lines:
        heading_match = re.match(r"^(#{1,3})\s+(.+)$", line.strip())
        if heading_match:
            if current_lines:
                body = "\n".join(current_lines).strip()
                if body:
                    sections.append((current_heading, body))
                current_lines = []
            current_heading = heading_match.group(2).strip()
        else:
            current_lines.append(line)

    if current_lines:
        body = "\n".join(current_lines).strip()
        if body:
            sections.append((current_heading, body))

    return sections or [("General", text.strip())]


def _chunk_text(text: str, chunk_size: int = 900, overlap: int = 150) -> List[str]:
    """Split a long section cleanly on paragraph/line boundaries with overlap."""
    text = text.strip()
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks: List[str] = []
    current = ""

    for para in paragraphs:
        if len(current) + len(para) + 2 <= chunk_size:
            current = f"{current}\n\n{para}".strip() if current else para
        else:
            if current:
                chunks.append(current)
                tail = current[-overlap:] if overlap > 0 and len(current) > overlap else ""
                current = f"{tail}\n\n{para}".strip() if tail else para
            else:
                # Single very long paragraph: split by sentence/window
                start = 0
                while start < len(para):
                    end = min(start + chunk_size, len(para))
                    chunks.append(para[start:end].strip())
                    if end >= len(para):
                        break
                    start = max(end - overlap, start + 1)
                current = ""

    if current:
        chunks.append(current)

    return chunks


def compute_kb_fingerprint(kb_dir: Path) -> str:
    """Compute a SHA-256 fingerprint over all supported files in the knowledge base."""
    hasher = hashlib.sha256()
    if not kb_dir.exists():
        return ""
    files = sorted(
        p for p in kb_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in {".md", ".txt", ".pdf"}
    )
    for file_path in files:
        rel = str(file_path.relative_to(kb_dir)).replace("\\", "/")
        hasher.update(rel.encode("utf-8"))
        hasher.update(file_path.read_bytes())
    return hasher.hexdigest()


def load_knowledge_base(
    kb_dir: Path,
    chunk_size: int = 900,
    chunk_overlap: int = 150,
) -> Tuple[List[DocumentChunk], List[Dict[str, str]]]:
    """
    Walk knowledge_base/ recursively and return (chunks, document_summaries).
    """
    chunks: List[DocumentChunk] = []
    documents: List[Dict[str, str]] = []

    if not kb_dir.exists():
        logger.warning(f"Knowledge base directory does not exist: {kb_dir}")
        return chunks, documents

    supported_files = sorted(
        p for p in kb_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in {".md", ".txt", ".pdf"}
    )

    for file_path in supported_files:
        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            raw_text = _read_pdf_text(file_path)
            meta: Dict[str, str] = {}
            body = raw_text
        else:
            raw_text = file_path.read_text(encoding="utf-8", errors="ignore")
            meta, body = _parse_frontmatter(raw_text)

        if not body.strip():
            continue

        parent_folder = file_path.parent.name.lower()
        topic = meta.get("topic") or FOLDER_TO_TOPIC.get(parent_folder, "government_schemes")
        source_title = meta.get("source_title") or file_path.stem.replace("_", " ").title()
        source_url = meta.get("source_url") or "https://cooperation.gov.in"
        keywords = meta.get("keywords", "")
        rel_name = str(file_path.relative_to(kb_dir)).replace("\\", "/")

        sections = _split_into_sections(body)
        file_chunk_count = 0

        for sec_idx, (sec_heading, sec_body) in enumerate(sections):
            sub_chunks = _chunk_text(sec_body, chunk_size=chunk_size, overlap=chunk_overlap)
            for sub_idx, text_piece in enumerate(sub_chunks):
                enriched_content = f"[{source_title} | {sec_heading}]\n{text_piece}"
                chunk_id = f"{file_path.stem}_s{sec_idx}_c{sub_idx}"
                chunks.append(
                    DocumentChunk(
                        chunk_id=chunk_id,
                        content=enriched_content,
                        topic=topic,
                        source_title=source_title,
                        source_url=source_url,
                        file_name=rel_name,
                        section=sec_heading,
                        keywords=keywords,
                        metadata={"folder": parent_folder},
                    )
                )
                file_chunk_count += 1

        documents.append(
            {
                "file_name": rel_name,
                "topic": topic,
                "source_title": source_title,
                "source_url": source_url,
                "chunks": str(file_chunk_count),
            }
        )

    logger.info(f"Loaded {len(documents)} documents into {len(chunks)} chunks from {kb_dir}")
    return chunks, documents
