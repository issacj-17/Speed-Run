"""
PIL/Pillow adapter for image processing.

Wraps PIL/Pillow library to implement ImageProcessorProtocol.
"""

import asyncio
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

from PIL import Image
from PIL.ExifTags import TAGS
import imagehash

from .protocol import ImageProcessorProtocol, ProcessedImage, ImageMetadata
from backend.cache.decorators import cache_by_file_hash, CacheConfig
from backend.logging import get_logger

logger = get_logger(__name__)


class PillowAdapter(ImageProcessorProtocol):
    """
    Adapter for PIL/Pillow image processor.

    Wraps Pillow to provide a standardized interface that can be
    easily swapped with other image processors (OpenCV, ImageMagick, etc.)
    """

    # Supported file formats
    SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp"}

    def __init__(self):
        """Initialize Pillow adapter."""
        logger.info("pillow_adapter_initialized", formats=list(self.SUPPORTED_FORMATS))

    async def load(self, file_path: Path) -> ProcessedImage:
        """
        Load and process image using Pillow.

        Args:
            file_path: Path to image

        Returns:
            ProcessedImage with metadata
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Image not found: {file_path}")

        if not self.supports_format(file_path.suffix.lower()):
            raise ValueError(f"Unsupported format: {file_path.suffix}")

        logger.info("image_loading_started", file_name=file_path.name)

        try:
            # Extract metadata
            metadata = await self.extract_metadata(file_path)

            # Compute hash
            image_hash = await self.compute_hash(file_path)

            result = ProcessedImage(
                file_path=file_path,
                metadata=metadata,
                thumbnail_path=None,
                hash=image_hash,
            )

            logger.info(
                "image_loading_completed",
                file_name=file_path.name,
                width=metadata.width,
                height=metadata.height,
                format=metadata.format,
            )

            return result

        except Exception as e:
            logger.error(
                "image_loading_failed",
                file_name=file_path.name,
                error=str(e),
            )
            raise

    @cache_by_file_hash(ttl=CacheConfig.IMAGE_METADATA_TTL, key_prefix="pillow_metadata")
    async def extract_metadata(self, file_path: Path) -> ImageMetadata:
        """
        Extract metadata from image using Pillow.

        Cached by file hash for 1 hour to avoid re-extracting unchanged metadata.

        Args:
            file_path: Path to image

        Returns:
            ImageMetadata with EXIF and basic info
        """
        def _extract():
            with Image.open(file_path) as img:
                # Extract basic metadata
                width, height = img.size
                file_format = img.format
                mode = img.mode
                file_size = file_path.stat().st_size

                # Extract EXIF data
                exif = None
                created_date = None
                camera_make = None
                camera_model = None

                try:
                    if hasattr(img, "_getexif") and img._getexif():
                        exif_data = img._getexif()
                        exif = {}

                        for tag, value in exif_data.items():
                            tag_name = TAGS.get(tag, tag)
                            exif[tag_name] = str(value)

                            # Extract specific fields
                            if tag_name in ("DateTime", "DateTimeOriginal", "DateTimeDigitized"):
                                try:
                                    created_date = datetime.strptime(
                                        str(value), "%Y:%m:%d %H:%M:%S"
                                    )
                                except:
                                    pass
                            elif tag_name == "Make":
                                camera_make = str(value)
                            elif tag_name == "Model":
                                camera_model = str(value)
                except Exception:
                    # If EXIF extraction fails, continue with None values
                    pass

                return ImageMetadata(
                    width=width,
                    height=height,
                    format=file_format or "UNKNOWN",
                    mode=mode,
                    file_size=file_size,
                    exif=exif,
                    created_date=created_date,
                    camera_make=camera_make,
                    camera_model=camera_model,
                )

        # Run blocking operation in thread pool
        metadata = await asyncio.to_thread(_extract)

        logger.info("metadata_extracted", file_name=file_path.name)

        return metadata

    async def create_thumbnail(
        self, file_path: Path, output_path: Path, size: Tuple[int, int] = (200, 200)
    ) -> Path:
        """
        Create thumbnail using Pillow.

        Args:
            file_path: Path to source image
            output_path: Path for thumbnail
            size: Thumbnail size

        Returns:
            Path to created thumbnail
        """
        def _create_thumbnail():
            with Image.open(file_path) as img:
                # Maintain aspect ratio
                img.thumbnail(size, Image.Resampling.LANCZOS)
                img.save(output_path)

        await asyncio.to_thread(_create_thumbnail)

        logger.info(
            "thumbnail_created",
            source=file_path.name,
            output=output_path.name,
            size=size,
        )

        return output_path

    async def compute_hash(self, file_path: Path) -> str:
        """
        Compute perceptual hash using imagehash library.

        Args:
            file_path: Path to image

        Returns:
            Perceptual hash string
        """
        def _compute_hash():
            with Image.open(file_path) as img:
                # Use average hash for perceptual similarity
                return str(imagehash.average_hash(img))

        image_hash = await asyncio.to_thread(_compute_hash)

        return image_hash

    async def convert_format(
        self, file_path: Path, output_path: Path, target_format: str
    ) -> Path:
        """
        Convert image format using Pillow.

        Args:
            file_path: Path to source image
            output_path: Path for converted image
            target_format: Target format (JPEG, PNG, etc.)

        Returns:
            Path to converted image
        """
        def _convert():
            with Image.open(file_path) as img:
                # Convert RGBA to RGB for JPEG
                if target_format.upper() == "JPEG" and img.mode == "RGBA":
                    img = img.convert("RGB")

                img.save(output_path, format=target_format.upper())

        await asyncio.to_thread(_convert)

        logger.info(
            "format_converted",
            source=file_path.name,
            output=output_path.name,
            format=target_format,
        )

        return output_path

    def supports_format(self, file_extension: str) -> bool:
        """
        Check if Pillow supports this format.

        Args:
            file_extension: File extension

        Returns:
            True if supported
        """
        return file_extension.lower() in self.SUPPORTED_FORMATS


__all__ = ["PillowAdapter"]
