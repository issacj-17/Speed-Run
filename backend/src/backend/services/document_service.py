"""Document parsing service using Docling."""

import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import tempfile
from datetime import datetime

from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions

from backend.schemas.document import (
    DocumentParseResponse,
    DocumentMetadata,
    DocumentPage,
)


class DocumentService:
    """Service for parsing documents (PDF, DOCX, etc.) using Docling."""

    def __init__(self):
        """Initialize the document service."""
        # Configure Docling with full pipeline options
        self.pipeline_options = PdfPipelineOptions()
        self.pipeline_options.do_ocr = True
        self.pipeline_options.do_table_structure = True

        self.converter = DocumentConverter(
            # format_options={
            #     InputFormat.PDF: PdfFormatOption(
            #         pipeline_cls=VlmPipeline,
            #     ),
            # }
        )

    async def parse_document(
        self,
        file_path: Path,
    ) -> DocumentParseResponse:
        """
        Parse a document and extract text, tables, and metadata.

        Args:
            file_path: Path to the document file

        Returns:
            DocumentParseResponse with extracted content and metadata
        """
        start_time = time.time()

        try:
            # Convert the document using Docling
            result = self.converter.convert(str(file_path))
            # print(result)

            # Extract full text as markdown
            full_text = result.document.export_to_markdown()

            # Extract metadata
            metadata = DocumentMetadata(
                file_name=file_path.name,
                file_type=file_path.suffix,
                file_size=file_path.stat().st_size,
                page_count=result.document.num_pages(),
                author=None,  # Can be extracted from document properties if available
                created_date=None,
                modified_date=datetime.fromtimestamp(file_path.stat().st_mtime),
            )

            # Extract pages
            pages = []
            if hasattr(result.document, 'pages'):
                for idx, page in enumerate(result.document.pages):
                    page_text = ""
                    if hasattr(page, 'export_to_markdown'):
                        page_text = page.export_to_markdown()

                    pages.append(DocumentPage(
                        page_number=idx + 1,
                        text=page_text,
                        images_count=0,  # Can be enhanced
                        tables_count=0,  # Can be enhanced
                    ))

            # Extract tables
            tables = []
            if hasattr(result.document, 'tables'):
                for table in result.document.tables:
                    # Convert table to dictionary format
                    if hasattr(table, 'export_to_dict'):
                        tables.append(table.export_to_dict())

            processing_time = time.time() - start_time

            return DocumentParseResponse(
                text=full_text,
                pages=pages,
                metadata=metadata,
                tables=tables if tables else None,
                images=None,  # Can be enhanced with image extraction
                processing_time=processing_time,
            )

        except Exception as e:
            raise Exception(f"Document parsing failed: {str(e)}")

    async def parse_document_bytes(
        self,
        file_bytes: bytes,
        filename: str,
    ) -> DocumentParseResponse:
        """
        Parse document bytes.

        Args:
            file_bytes: Document file bytes
            filename: Original filename

        Returns:
            DocumentParseResponse with extracted content and metadata
        """
        # Save bytes to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix) as tmp_file:
            tmp_file.write(file_bytes)
            tmp_path = Path(tmp_file.name)

        try:
            return await self.parse_document(tmp_path)
        finally:
            # Clean up temporary file
            if tmp_path.exists():
                tmp_path.unlink()

    async def extract_tables(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Extract only tables from a document.

        Args:
            file_path: Path to the document file

        Returns:
            List of tables as dictionaries
        """
        result = self.converter.convert(str(file_path))

        tables = []
        if hasattr(result.document, 'tables'):
            for table in result.document.tables:
                if hasattr(table, 'export_to_dict'):
                    tables.append(table.export_to_dict())

        return tables
