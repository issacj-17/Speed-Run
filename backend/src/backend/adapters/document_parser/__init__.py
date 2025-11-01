"""
Document parser adapters.

Abstracts document parsing libraries (Docling, JigsawStack, PyPDF2, etc.)
"""

from .protocol import DocumentParserProtocol, ParsedDocument, ParsedPage, ParsedTable
from .docling import DoclingAdapter

__all__ = [
    "DocumentParserProtocol",
    "ParsedDocument",
    "ParsedPage",
    "ParsedTable",
    "DoclingAdapter",
]
