"""OCR request and response schemas."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class OCRRequest(BaseModel):
    """OCR request parameters (currently not used, reserved for future enhancements)."""

    detect_orientation: bool = Field(
        default=True,
        description="Detect and correct image orientation"
    )


class BoundingBox(BaseModel):
    """Bounding box coordinates for detected text."""

    x: float
    y: float
    width: float
    height: float


class OCRTextResult(BaseModel):
    """Individual text detection result."""

    text: str
    confidence: float
    bounding_box: Optional[BoundingBox] = None


class OCRResponse(BaseModel):
    """OCR response with extracted text and metadata."""

    text: str = Field(description="Extracted text from the image")
    results: List[OCRTextResult] = Field(
        default=[],
        description="Detailed results with bounding boxes and confidence"
    )
    metadata: Dict[str, Any] = Field(
        default={},
        description="Additional metadata about the OCR process"
    )
    processing_time: float = Field(description="Time taken to process in seconds")
