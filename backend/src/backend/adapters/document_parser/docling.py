"""
Docling adapter for document parsing.

Wraps Docling library to implement DocumentParserProtocol.
"""

import asyncio
import time
from pathlib import Path
from typing import List, Optional

from docling.document_converter import DocumentConverter
from docling.datamodel.pipeline_options import PdfPipelineOptions

from .protocol import DocumentParserProtocol, ParsedDocument, ParsedPage, ParsedTable
from backend.cache.decorators import cache_by_file_hash, CacheConfig
from backend.logging import get_logger

logger = get_logger(__name__)


class DoclingAdapter(DocumentParserProtocol):
    """
    Adapter for Docling document parser.

    Wraps Docling to provide a standardized interface that can be
    easily swapped with other parsers (JigsawStack, PyPDF2, etc.)
    """

    # Supported file formats (Docling supports PDF and Office documents, but not Excel)
    SUPPORTED_FORMATS = {".pdf", ".docx", ".doc", ".pptx"}

    def __init__(self, converter: Optional[DocumentConverter] = None):
        """
        Initialize Docling converter with full pipeline.

        Args:
            converter: Optional DocumentConverter instance for dependency injection.
                      If not provided, creates a new default converter.
        """
        # Configure Docling with OCR and table extraction
        self.pipeline_options = PdfPipelineOptions()
        self.pipeline_options.do_ocr = True
        self.pipeline_options.do_table_structure = True

        # Use provided converter or create default
        if converter is not None:
            self.converter = converter
        else:
            self.converter = DocumentConverter()

        logger.info("docling_adapter_initialized", formats=list(self.SUPPORTED_FORMATS))

    @cache_by_file_hash(ttl=CacheConfig.DOCUMENT_PARSE_TTL, key_prefix="docling_parse")
    async def parse(self, file_path: Path) -> ParsedDocument:
        """
        Parse document using Docling.

        Cached by file hash for 1 hour to avoid re-parsing unchanged documents.

        Args:
            file_path: Path to document

        Returns:
            ParsedDocument with standardized structure

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If format not supported
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not self.supports_format(file_path.suffix.lower()):
            raise ValueError(f"Unsupported format: {file_path.suffix}")

        logger.info(
            "document_parsing_started",
            file_name=file_path.name,
            file_size=file_path.stat().st_size,
        )

        start_time = time.time()

        try:
            # Run blocking Docling operation in thread pool
            result = await asyncio.to_thread(
                self.converter.convert,
                str(file_path)
            )

            # Extract full text as markdown
            full_text = result.document.export_to_markdown()

            # Extract pages
            pages = await self._extract_pages(result.document)

            # Extract tables
            tables = await self._extract_tables(result.document)

            # Calculate metadata
            word_count = len(full_text.split())
            processing_time_ms = (time.time() - start_time) * 1000

            parsed_doc = ParsedDocument(
                text=full_text,
                pages=pages,
                tables=tables,
                file_name=file_path.name,
                file_type=file_path.suffix,
                file_size=file_path.stat().st_size,
                page_count=result.document.num_pages(),
                word_count=word_count,
                processing_time_ms=processing_time_ms,
                author=None,  # Docling doesn't expose this easily
                created_date=None,
                modified_date=None,
                metadata={"parser": "docling", "version": "2.9.1"},
            )

            logger.info(
                "document_parsing_completed",
                file_name=file_path.name,
                page_count=parsed_doc.page_count,
                word_count=parsed_doc.word_count,
                table_count=len(tables),
                processing_time_ms=round(processing_time_ms, 2),
            )

            return parsed_doc

        except Exception as e:
            logger.error(
                "document_parsing_failed",
                file_name=file_path.name,
                error=str(e),
                error_type=type(e).__name__,
            )
            raise Exception(f"Docling parsing failed: {str(e)}")

    async def extract_tables(self, file_path: Path) -> List[ParsedTable]:
        """
        Extract only tables from document.

        Args:
            file_path: Path to document

        Returns:
            List of parsed tables
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        logger.info("table_extraction_started", file_name=file_path.name)

        try:
            # Run blocking operation in thread pool
            result = await asyncio.to_thread(
                self.converter.convert,
                str(file_path)
            )

            tables = await self._extract_tables(result.document)

            logger.info(
                "table_extraction_completed",
                file_name=file_path.name,
                table_count=len(tables),
            )

            return tables

        except Exception as e:
            logger.error(
                "table_extraction_failed",
                file_name=file_path.name,
                error=str(e),
            )
            raise

    def supports_format(self, file_extension: str) -> bool:
        """
        Check if Docling supports this format.

        Args:
            file_extension: File extension (e.g., ".pdf")

        Returns:
            True if supported
        """
        return file_extension.lower() in self.SUPPORTED_FORMATS

    async def _extract_pages(self, document) -> List[ParsedPage]:
        """
        Extract pages from Docling document.

        Args:
            document: Docling document object

        Returns:
            List of parsed pages
        """
        pages = []

        if hasattr(document, "pages"):
            for idx, page in enumerate(document.pages):
                page_text = ""
                if hasattr(page, "export_to_markdown"):
                    page_text = page.export_to_markdown()

                # Count words on page
                word_count = len(page_text.split())

                pages.append(
                    ParsedPage(
                        page_number=idx + 1,
                        text=page_text,
                        tables=[],  # Tables extracted separately
                        images_count=0,  # Could be enhanced
                        word_count=word_count,
                        metadata=None,
                    )
                )

        return pages

    async def _extract_tables(self, document) -> List[ParsedTable]:
        """
        Extract tables from Docling document.

        Args:
            document: Docling document object

        Returns:
            List of parsed tables
        """
        tables = []

        if hasattr(document, "tables"):
            for table in document.tables:
                if hasattr(table, "export_to_dict"):
                    table_dict = table.export_to_dict()

                    # Convert to 2D array format
                    data = table_dict.get("data", [])
                    headers = table_dict.get("headers")

                    tables.append(
                        ParsedTable(
                            data=data,
                            headers=headers,
                            page_number=None,  # Docling doesn't provide this
                            metadata=table_dict,
                        )
                    )

        return tables


__all__ = ["DoclingAdapter"]
