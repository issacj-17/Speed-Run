"""
Image processor protocol definition.

Defines the interface that all image processing adapters must implement.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Protocol, Tuple


@dataclass
class ImageMetadata:
    """Metadata extracted from image."""

    width: int
    height: int
    format: str  # JPEG, PNG, etc.
    mode: str  # RGB, RGBA, L, etc.
    file_size: int
    exif: Optional[Dict] = None
    created_date: Optional[datetime] = None
    camera_make: Optional[str] = None
    camera_model: Optional[str] = None


@dataclass
class ProcessedImage:
    """Result of image processing."""

    file_path: Path
    metadata: ImageMetadata
    thumbnail_path: Optional[Path] = None
    hash: Optional[str] = None


class ImageProcessorProtocol(Protocol):
    """
    Protocol for image processing adapters.

    All image processors (PIL/Pillow, OpenCV, ImageMagick, etc.)
    must implement this interface.

    Example implementations:
        - PillowAdapter: Uses PIL/Pillow for image processing
        - OpenCVAdapter: Uses OpenCV for advanced processing
        - ImageMagickAdapter: Uses ImageMagick CLI

    Usage:
        processor: ImageProcessorProtocol = PillowAdapter()
        result = await processor.load(Path("image.jpg"))

        # Switch provider - no code changes needed
        processor: ImageProcessorProtocol = OpenCVAdapter()
        result = await processor.load(Path("image.jpg"))
    """

    async def load(self, file_path: Path) -> ProcessedImage:
        """
        Load and process an image.

        Args:
            file_path: Path to image file

        Returns:
            ProcessedImage with metadata

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is not a valid image
        """
        ...

    async def extract_metadata(self, file_path: Path) -> ImageMetadata:
        """
        Extract metadata from image.

        Args:
            file_path: Path to image file

        Returns:
            ImageMetadata with EXIF and basic info
        """
        ...

    async def create_thumbnail(
        self, file_path: Path, output_path: Path, size: Tuple[int, int] = (200, 200)
    ) -> Path:
        """
        Create thumbnail of image.

        Args:
            file_path: Path to source image
            output_path: Path for thumbnail
            size: Thumbnail size (width, height)

        Returns:
            Path to created thumbnail
        """
        ...

    async def compute_hash(self, file_path: Path) -> str:
        """
        Compute perceptual hash of image.

        Args:
            file_path: Path to image

        Returns:
            Perceptual hash string
        """
        ...

    async def convert_format(
        self, file_path: Path, output_path: Path, target_format: str
    ) -> Path:
        """
        Convert image to different format.

        Args:
            file_path: Path to source image
            output_path: Path for converted image
            target_format: Target format (JPEG, PNG, etc.)

        Returns:
            Path to converted image
        """
        ...

    def supports_format(self, file_extension: str) -> bool:
        """
        Check if this processor supports a format.

        Args:
            file_extension: File extension (e.g., ".jpg", ".png")

        Returns:
            True if format is supported
        """
        ...


__all__ = [
    "ImageMetadata",
    "ProcessedImage",
    "ImageProcessorProtocol",
]
