"""
JigsawStack adapter example (for future implementation).

Shows how easy it is to add a new provider without changing any business logic.
"""

import asyncio
import time
from pathlib import Path
from typing import List

from .protocol import DocumentParserProtocol, ParsedDocument, ParsedPage, ParsedTable
from backend.logging import get_logger

logger = get_logger(__name__)


class JigsawStackAdapter(DocumentParserProtocol):
    """
    Adapter for JigsawStack document parser API.

    Example implementation showing how to swap from Docling to JigsawStack
    without changing any business logic.

    Usage:
        # In dependency injection container or main.py
        # OLD: parser = DoclingAdapter()
        # NEW: parser = JigsawStackAdapter(api_key=settings.JIGSAWSTACK_API_KEY)

        # All services using DocumentParserProtocol work unchanged!
    """

    SUPPORTED_FORMATS = {".pdf", ".docx", ".doc", ".png", ".jpg"}

    def __init__(self, api_key: str):
        """
        Initialize JigsawStack client.

        Args:
            api_key: JigsawStack API key
        """
        self.api_key = api_key
        # self.client = JigsawStackClient(api_key)  # Hypothetical client
        logger.info("jigsawstack_adapter_initialized")

    async def parse(self, file_path: Path) -> ParsedDocument:
        """
        Parse document using JigsawStack API.

        Args:
            file_path: Path to document

        Returns:
            ParsedDocument with standardized structure
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not self.supports_format(file_path.suffix.lower()):
            raise ValueError(f"Unsupported format: {file_path.suffix}")

        logger.info("jigsawstack_parsing_started", file_name=file_path.name)

        start_time = time.time()

        try:
            # Upload file to JigsawStack
            # result = await self.client.parse_document(file_path)

            # Convert JigsawStack response to our standardized format
            # This is the ONLY place that knows about JigsawStack's format
            parsed_doc = ParsedDocument(
                text="",  # result.text
                pages=[],  # Convert result.pages to ParsedPage
                tables=[],  # Convert result.tables to ParsedTable
                file_name=file_path.name,
                file_type=file_path.suffix,
                file_size=file_path.stat().st_size,
                page_count=0,  # result.page_count
                word_count=0,  # len(result.text.split())
                processing_time_ms=(time.time() - start_time) * 1000,
                metadata={"parser": "jigsawstack", "api_version": "v1"},
            )

            logger.info("jigsawstack_parsing_completed", file_name=file_path.name)

            return parsed_doc

        except Exception as e:
            logger.error("jigsawstack_parsing_failed", error=str(e))
            raise Exception(f"JigsawStack parsing failed: {str(e)}")

    async def extract_tables(self, file_path: Path) -> List[ParsedTable]:
        """Extract tables using JigsawStack API."""
        # result = await self.client.extract_tables(file_path)
        # return [self._convert_table(t) for t in result.tables]
        return []

    def supports_format(self, file_extension: str) -> bool:
        """Check if JigsawStack supports this format."""
        return file_extension.lower() in self.SUPPORTED_FORMATS


__all__ = ["JigsawStackAdapter"]
