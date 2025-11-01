"""Document parsing request and response schemas."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class DocumentMetadata(BaseModel):
    """Metadata extracted from document."""

    file_name: str
    file_type: str
    file_size: int
    page_count: Optional[int] = None
    author: Optional[str] = None
    created_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None


class DocumentPage(BaseModel):
    """Individual page content."""

    page_number: int
    text: str
    images_count: int = 0
    tables_count: int = 0


class DocumentParseResponse(BaseModel):
    """Document parsing response."""

    text: str = Field(description="Full extracted text from document")
    pages: List[DocumentPage] = Field(
        default=[],
        description="Per-page content breakdown"
    )
    metadata: DocumentMetadata
    tables: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Extracted tables data"
    )
    images: Optional[List[str]] = Field(
        default=None,
        description="Base64 encoded images extracted from document"
    )
    processing_time: float = Field(description="Time taken to process in seconds")
