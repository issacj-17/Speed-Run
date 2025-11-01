"""
Cache key generation utilities.
"""

import hashlib
from typing import Any
from uuid import UUID


class CacheKeyGenerator:
    """
    Utilities for generating consistent cache keys.

    All cache keys follow the pattern:
        prefix:operation:identifier
    """

    # Cache key prefixes
    PREFIX_DOCUMENT = "document"
    PREFIX_OCR = "ocr"
    PREFIX_IMAGE = "image"
    PREFIX_VALIDATION = "validation"
    PREFIX_RISK = "risk"

    @staticmethod
    def document_parse(file_hash: str) -> str:
        """
        Generate cache key for document parsing results.

        Args:
            file_hash: SHA-256 hash of document

        Returns:
            Cache key like "document:parse:abc123..."
        """
        return f"{CacheKeyGenerator.PREFIX_DOCUMENT}:parse:{file_hash}"

    @staticmethod
    def document_tables(file_hash: str) -> str:
        """
        Generate cache key for table extraction results.

        Args:
            file_hash: SHA-256 hash of document

        Returns:
            Cache key like "document:tables:abc123..."
        """
        return f"{CacheKeyGenerator.PREFIX_DOCUMENT}:tables:{file_hash}"

    @staticmethod
    def ocr_extract(image_hash: str) -> str:
        """
        Generate cache key for OCR extraction results.

        Args:
            image_hash: SHA-256 hash of image

        Returns:
            Cache key like "ocr:extract:def456..."
        """
        return f"{CacheKeyGenerator.PREFIX_OCR}:extract:{image_hash}"

    @staticmethod
    def image_analysis(image_hash: str, analysis_type: str = "full") -> str:
        """
        Generate cache key for image analysis results.

        Args:
            image_hash: SHA-256 hash of image
            analysis_type: Type of analysis (full, metadata, tampering, etc.)

        Returns:
            Cache key like "image:full:ghi789..."
        """
        return f"{CacheKeyGenerator.PREFIX_IMAGE}:{analysis_type}:{image_hash}"

    @staticmethod
    def validation(document_hash: str, validation_type: str) -> str:
        """
        Generate cache key for validation results.

        Args:
            document_hash: SHA-256 hash of document
            validation_type: Type of validation (format, structure, content)

        Returns:
            Cache key like "validation:format:jkl012..."
        """
        return f"{CacheKeyGenerator.PREFIX_VALIDATION}:{validation_type}:{document_hash}"

    @staticmethod
    def risk_score(entity_type: str, entity_id: UUID) -> str:
        """
        Generate cache key for risk score results.

        Args:
            entity_type: Type of entity (DOCUMENT, TRANSACTION, CLIENT)
            entity_id: UUID of entity

        Returns:
            Cache key like "risk:DOCUMENT:uuid"
        """
        return f"{CacheKeyGenerator.PREFIX_RISK}:{entity_type}:{entity_id}"

    @staticmethod
    def compute_hash(content: bytes) -> str:
        """
        Compute SHA-256 hash of content.

        Args:
            content: File content as bytes

        Returns:
            Hex digest of SHA-256 hash
        """
        return hashlib.sha256(content).hexdigest()

    @staticmethod
    def compute_string_hash(text: str) -> str:
        """
        Compute SHA-256 hash of text string.

        Args:
            text: String content

        Returns:
            Hex digest of SHA-256 hash
        """
        return hashlib.sha256(text.encode("utf-8")).hexdigest()


__all__ = ["CacheKeyGenerator"]
