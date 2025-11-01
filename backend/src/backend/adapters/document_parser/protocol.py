"""
Document parser protocol definition.

Defines the interface that all document parser adapters must implement.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Protocol, Dict, Any


@dataclass
class ParsedTable:
    """Represents a parsed table from a document."""

    data: List[List[str]]  # 2D array of table cells
    headers: Optional[List[str]] = None
    page_number: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ParsedPage:
    """Represents a parsed page from a document."""

    page_number: int
    text: str
    tables: List[ParsedTable]
    images_count: int
    word_count: int
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ParsedDocument:
    """
    Standardized output from document parsing.

    All adapters must return data in this format.
    """

    # Content
    text: str  # Full document text
    pages: List[ParsedPage]
    tables: List[ParsedTable]

    # Metadata
    file_name: str
    file_type: str
    file_size: int
    page_count: int
    word_count: int
    processing_time_ms: float

    # Optional metadata
    author: Optional[str] = None
    created_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class DocumentParserProtocol(Protocol):
    """
    Protocol for document parsing adapters.

    All document parsers (Docling, JigsawStack, PyPDF2, etc.)
    must implement this interface.

    Example implementations:
        - DoclingAdapter: Uses Docling for parsing
        - JigsawStackAdapter: Uses JigsawStack API
        - PyPDF2Adapter: Uses PyPDF2 for simple PDF parsing
        - UnstructuredIOAdapter: Uses Unstructured.io

    Usage:
        parser: DocumentParserProtocol = DoclingAdapter()
        result = await parser.parse(Path("document.pdf"))

        # Switch provider - no code changes needed
        parser: DocumentParserProtocol = JigsawStackAdapter()
        result = await parser.parse(Path("document.pdf"))
    """

    async def parse(self, file_path: Path) -> ParsedDocument:
        """
        Parse a document and extract text, tables, and metadata.

        Args:
            file_path: Path to document file

        Returns:
            ParsedDocument with standardized structure

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format not supported
            Exception: If parsing fails
        """
        ...

    async def extract_tables(self, file_path: Path) -> List[ParsedTable]:
        """
        Extract only tables from a document.

        Args:
            file_path: Path to document file

        Returns:
            List of parsed tables

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format not supported
        """
        ...

    def supports_format(self, file_extension: str) -> bool:
        """
        Check if this parser supports a file format.

        Args:
            file_extension: File extension (e.g., ".pdf", ".docx")

        Returns:
            True if format is supported
        """
        ...


__all__ = [
    "ParsedDocument",
    "ParsedPage",
    "ParsedTable",
    "DocumentParserProtocol",
]
