"""
Image processor adapters.

Abstracts image processing libraries (PIL/Pillow, OpenCV, etc.)
"""

from .protocol import ImageProcessorProtocol, ProcessedImage, ImageMetadata
from .pillow import PillowAdapter

__all__ = [
    "ImageProcessorProtocol",
    "ProcessedImage",
    "ImageMetadata",
    "PillowAdapter",
]
