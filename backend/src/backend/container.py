"""
Dependency Injection Container.

Centralized container for managing all service dependencies.
Enables easy swapping of implementations (Docling → JigsawStack, spaCy → OpenAI, etc.)
"""

from typing import Optional

from backend.adapters.document_parser import DocumentParserProtocol, DoclingAdapter
from backend.adapters.nlp import NLPProcessorProtocol, SpacyAdapter
from backend.adapters.image import ImageProcessorProtocol, PillowAdapter
from backend.cache import CacheManager, cache_manager
from backend.config import settings
from backend.logging import get_logger

logger = get_logger(__name__)


class Container:
    """
    Dependency Injection Container.

    Manages all service dependencies and provides easy swapping
    between implementations.

    Usage:
        # Get singleton instance
        container = Container()

        # Use default implementations
        parser = container.document_parser
        result = await parser.parse(file_path)

        # Swap to different implementation
        container.document_parser = JigsawStackAdapter(api_key=key)

        # All services now use new implementation!
    """

    _instance: Optional["Container"] = None

    def __new__(cls):
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize container with default implementations."""
        if not hasattr(self, "_initialized"):
            self._document_parser: Optional[DocumentParserProtocol] = None
            self._nlp_processor: Optional[NLPProcessorProtocol] = None
            self._image_processor: Optional[ImageProcessorProtocol] = None
            self._cache: Optional[CacheManager] = None
            self._initialized = True

            logger.info("dependency_container_initialized")

    # ============================================================================
    # Document Parser
    # ============================================================================

    @property
    def document_parser(self) -> DocumentParserProtocol:
        """
        Get document parser instance.

        Returns:
            DocumentParserProtocol implementation

        Example:
            # Default: Docling
            parser = container.document_parser

            # Swap to JigsawStack
            container.document_parser = JigsawStackAdapter(api_key)
        """
        if self._document_parser is None:
            # Default to Docling
            self._document_parser = DoclingAdapter()
            logger.info("document_parser_initialized", implementation="DoclingAdapter")
        return self._document_parser

    @document_parser.setter
    def document_parser(self, parser: DocumentParserProtocol):
        """
        Set document parser implementation.

        Args:
            parser: DocumentParserProtocol implementation
        """
        self._document_parser = parser
        logger.info(
            "document_parser_set",
            implementation=type(parser).__name__,
        )

    # ============================================================================
    # NLP Processor
    # ============================================================================

    @property
    def nlp_processor(self) -> NLPProcessorProtocol:
        """
        Get NLP processor instance.

        Returns:
            NLPProcessorProtocol implementation

        Example:
            # Default: spaCy
            nlp = container.nlp_processor

            # Swap to OpenAI
            container.nlp_processor = OpenAIAdapter(api_key)
        """
        if self._nlp_processor is None:
            # Default to spaCy
            try:
                self._nlp_processor = SpacyAdapter()
                logger.info("nlp_processor_initialized", implementation="SpacyAdapter")
            except OSError:
                logger.warning(
                    "spacy_model_not_found",
                    fallback="NLP features will be limited",
                )
                # Could fallback to a simple tokenizer
                self._nlp_processor = None

        return self._nlp_processor

    @nlp_processor.setter
    def nlp_processor(self, processor: NLPProcessorProtocol):
        """
        Set NLP processor implementation.

        Args:
            processor: NLPProcessorProtocol implementation
        """
        self._nlp_processor = processor
        logger.info(
            "nlp_processor_set",
            implementation=type(processor).__name__,
        )

    # ============================================================================
    # Image Processor
    # ============================================================================

    @property
    def image_processor(self) -> ImageProcessorProtocol:
        """
        Get image processor instance.

        Returns:
            ImageProcessorProtocol implementation

        Example:
            # Default: Pillow
            processor = container.image_processor

            # Swap to OpenCV
            container.image_processor = OpenCVAdapter()
        """
        if self._image_processor is None:
            # Default to Pillow
            self._image_processor = PillowAdapter()
            logger.info("image_processor_initialized", implementation="PillowAdapter")
        return self._image_processor

    @image_processor.setter
    def image_processor(self, processor: ImageProcessorProtocol):
        """
        Set image processor implementation.

        Args:
            processor: ImageProcessorProtocol implementation
        """
        self._image_processor = processor
        logger.info(
            "image_processor_set",
            implementation=type(processor).__name__,
        )

    # ============================================================================
    # Cache Manager
    # ============================================================================

    @property
    def cache(self) -> CacheManager:
        """
        Get cache manager instance.

        Returns:
            CacheManager instance

        Example:
            # Get cache
            cache = container.cache
            await cache.set("key", "value", ttl=3600)
        """
        if self._cache is None:
            # Use global cache manager
            self._cache = cache_manager
            logger.info("cache_manager_initialized")
        return self._cache

    @cache.setter
    def cache(self, manager: CacheManager):
        """
        Set cache manager implementation.

        Args:
            manager: CacheManager instance
        """
        self._cache = manager
        logger.info("cache_manager_set")

    # ============================================================================
    # Configuration Methods
    # ============================================================================

    def configure_for_production(self):
        """
        Configure container for production environment.

        Uses production-ready implementations (Docling, spaCy, Redis, etc.)
        """
        logger.info("configuring_for_production")

        # Use default implementations (already production-ready)
        _ = self.document_parser
        _ = self.nlp_processor
        _ = self.image_processor
        _ = self.cache

        logger.info("production_configuration_complete")

    def configure_for_testing(self):
        """
        Configure container for testing environment.

        Uses mock/in-memory implementations for fast testing.
        """
        from cache import MemoryBackend, CacheManager

        logger.info("configuring_for_testing")

        # Use in-memory cache for testing
        test_cache = CacheManager(MemoryBackend())
        self.cache = test_cache

        # Could also swap to mock adapters
        # self.document_parser = MockDocumentParser()
        # self.nlp_processor = MockNLPProcessor()
        # self.image_processor = MockImageProcessor()

        logger.info("testing_configuration_complete")

    def configure_for_alternative_providers(
        self,
        document_parser: Optional[DocumentParserProtocol] = None,
        nlp_processor: Optional[NLPProcessorProtocol] = None,
        image_processor: Optional[ImageProcessorProtocol] = None,
    ):
        """
        Configure container with alternative providers.

        Args:
            document_parser: Alternative document parser (e.g., JigsawStack)
            nlp_processor: Alternative NLP processor (e.g., OpenAI)
            image_processor: Alternative image processor (e.g., OpenCV)

        Example:
            container.configure_for_alternative_providers(
                document_parser=JigsawStackAdapter(api_key),
                nlp_processor=OpenAIAdapter(api_key),
            )
        """
        logger.info("configuring_alternative_providers")

        if document_parser:
            self.document_parser = document_parser
        if nlp_processor:
            self.nlp_processor = nlp_processor
        if image_processor:
            self.image_processor = image_processor

        logger.info("alternative_providers_configured")

    def reset(self):
        """Reset container to default state (for testing)."""
        logger.info("resetting_container")

        self._document_parser = None
        self._nlp_processor = None
        self._image_processor = None
        self._cache = None

        logger.info("container_reset_complete")


# Global singleton instance
container = Container()


def get_container() -> Container:
    """
    Get global container instance.

    Returns:
        Container singleton

    Example:
        from container import get_container

        container = get_container()
        parser = container.document_parser
    """
    return container


__all__ = ["Container", "container", "get_container"]
