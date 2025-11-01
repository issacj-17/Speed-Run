"""
NLP processor protocol definition.

Defines the interface that all NLP adapters must implement.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Protocol


class EntityType(str, Enum):
    """Named entity types."""

    PERSON = "PERSON"
    ORGANIZATION = "ORGANIZATION"
    LOCATION = "LOCATION"
    DATE = "DATE"
    TIME = "TIME"
    MONEY = "MONEY"
    PERCENT = "PERCENT"
    PRODUCT = "PRODUCT"
    EVENT = "EVENT"
    LAW = "LAW"
    LANGUAGE = "LANGUAGE"
    QUANTITY = "QUANTITY"
    ORDINAL = "ORDINAL"
    CARDINAL = "CARDINAL"
    FAC = "FAC"  # Facility
    NORP = "NORP"  # Nationalities, religious/political groups
    WORK_OF_ART = "WORK_OF_ART"
    OTHER = "OTHER"


@dataclass
class Entity:
    """Named entity extracted from text."""

    text: str
    type: EntityType  # Entity type enum
    label: str  # Raw label from NLP library (e.g., "PERSON", "ORG", "GPE")
    start: int
    end: int


@dataclass
class Sentence:
    """Sentence extracted from text."""

    text: str
    start: int
    end: int


@dataclass
class AnalyzedText:
    """Result of NLP analysis."""

    text: str
    sentences: List[Sentence]
    entities: List[Entity]
    tokens: List[str]
    word_count: int
    language: str
    unknown_words: List[str]  # For spell checking
    metadata: Optional[dict] = None


class NLPProcessorProtocol(Protocol):
    """
    Protocol for NLP processing adapters.

    All NLP processors (spaCy, OpenAI, HuggingFace, etc.)
    must implement this interface.

    Example implementations:
        - SpacyAdapter: Uses spaCy for NLP
        - OpenAIAdapter: Uses OpenAI API for NLP
        - HuggingFaceAdapter: Uses HuggingFace models

    Usage:
        nlp: NLPProcessorProtocol = SpacyAdapter()
        result = await nlp.analyze(text)

        # Switch provider - no code changes needed
        nlp: NLPProcessorProtocol = OpenAIAdapter(api_key=key)
        result = await nlp.analyze(text)
    """

    async def analyze(self, text: str, max_length: Optional[int] = None) -> AnalyzedText:
        """
        Analyze text and extract linguistic features.

        Args:
            text: Text to analyze
            max_length: Max length to analyze (for performance)

        Returns:
            AnalyzedText with extracted features
        """
        ...

    async def extract_entities(self, text: str) -> List[Entity]:
        """
        Extract named entities from text.

        Args:
            text: Text to analyze

        Returns:
            List of entities (PERSON, ORG, GPE, etc.)
        """
        ...

    async def check_spelling(self, text: str, threshold: int = 5) -> List[str]:
        """
        Check spelling and return unknown words.

        Args:
            text: Text to check
            threshold: Max number of unknown words to return

        Returns:
            List of unknown/misspelled words
        """
        ...

    async def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words.

        Args:
            text: Text to tokenize

        Returns:
            List of tokens
        """
        ...

    async def detect_language(self, text: str) -> str:
        """
        Detect language of text.

        Args:
            text: Text to analyze

        Returns:
            Language code (e.g., "en", "fr", "de")
        """
        ...


__all__ = [
    "EntityType",
    "Entity",
    "Sentence",
    "AnalyzedText",
    "NLPProcessorProtocol",
]
