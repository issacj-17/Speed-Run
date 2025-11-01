"""OCR service using Docling."""

import time
from pathlib import Path
from typing import Dict, Any
import tempfile

from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions

from backend.schemas.ocr import OCRResponse, OCRTextResult, BoundingBox


class OCRService:
    """Service for performing OCR on images using Docling."""

    def __init__(self):
        """Initialize the OCR service."""
        # Configure Docling with OCR pipeline options
        self.pipeline_options = PdfPipelineOptions()
        self.pipeline_options.do_ocr = True
        self.pipeline_options.do_table_structure = True

        self.converter = DocumentConverter()

    async def process_image(
        self,
        file_path: Path,
    ) -> OCRResponse:
        """
        Process an image file and extract text using Docling's OCR.
        Assumes English language.

        Args:
            file_path: Path to the image file

        Returns:
            OCRResponse with extracted text and metadata
        """
        start_time = time.time()
        print("Processing Image...")

        try:
            # Convert the image using Docling
            result = self.converter.convert(str(file_path))

            # Extract text content
            text = result.document.export_to_markdown()
            print(text)

            # Build detailed results (Docling provides structured content)
            results = []
            if hasattr(result.document, 'texts') and result.document.texts:
                for idx, text_block in enumerate(result.document.texts):
                    results.append(OCRTextResult(
                        text=text_block.text if hasattr(text_block, 'text') else str(text_block),
                        confidence=1.0,  # Docling doesn't provide confidence scores directly
                        bounding_box=None  # Can be enhanced with bbox info if available
                    ))

            print(results)

            processing_time = time.time() - start_time

            return OCRResponse(
                text=text,
                results=results,
                metadata={
                    "engine": "docling",
                    "language": "en",
                    "file_name": file_path.name,
                },
                processing_time=processing_time,
            )

        except Exception as e:
            raise Exception(f"OCR processing failed: {str(e)}")

    async def process_image_bytes(
        self,
        file_bytes: bytes,
        filename: str,
    ) -> OCRResponse:
        """
        Process image bytes and extract text.
        Assumes English language.

        Args:
            file_bytes: Image file bytes
            filename: Original filename

        Returns:
            OCRResponse with extracted text and metadata
        """
        # Save bytes to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix) as tmp_file:
            tmp_file.write(file_bytes)
            tmp_path = Path(tmp_file.name)

        try:
            return await self.process_image(tmp_path)
        finally:
            # Clean up temporary file
            if tmp_path.exists():
                tmp_path.unlink()
