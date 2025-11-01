"""
Adapter layer for 3rd party services.

This layer abstracts all external dependencies (Docling, spaCy, PIL, etc.)
to enable easy swapping between providers.

Architecture:
    Each adapter implements a Protocol interface, allowing easy
    replacement without changing business logic.

Example:
    # Current: Using Docling
    parser = DoclingAdapter()

    # Future: Switch to JigsawStack
    parser = JigsawStackAdapter()

    # Service code remains unchanged
    result = await parser.parse(file_path)
"""

from .document_parser import DocumentParserProtocol, DoclingAdapter
from .nlp import NLPProcessorProtocol, SpacyAdapter
from .image import ImageProcessorProtocol, PillowAdapter

__all__ = [
    # Document parsing
    "DocumentParserProtocol",
    "DoclingAdapter",
    # NLP processing
    "NLPProcessorProtocol",
    "SpacyAdapter",
    # Image processing
    "ImageProcessorProtocol",
    "PillowAdapter",
]
