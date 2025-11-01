"""
spaCy adapter for NLP processing.

Wraps spaCy library to implement NLPProcessorProtocol.
"""

import asyncio
from typing import List, Optional

import spacy
from spacy.language import Language

from .protocol import NLPProcessorProtocol, AnalyzedText, Entity, EntityType, Sentence
from backend.cache.decorators import cached, CacheConfig
from backend.logging import get_logger

logger = get_logger(__name__)


# Mapping from spaCy entity labels to EntityType
SPACY_ENTITY_MAPPING = {
    "PERSON": EntityType.PERSON,
    "ORG": EntityType.ORGANIZATION,
    "GPE": EntityType.LOCATION,  # Geo-political entity
    "LOC": EntityType.LOCATION,
    "FAC": EntityType.FAC,  # Facility
    "DATE": EntityType.DATE,
    "TIME": EntityType.TIME,
    "MONEY": EntityType.MONEY,
    "PERCENT": EntityType.PERCENT,
    "PRODUCT": EntityType.PRODUCT,
    "EVENT": EntityType.EVENT,
    "LAW": EntityType.LAW,
    "LANGUAGE": EntityType.LANGUAGE,
    "QUANTITY": EntityType.QUANTITY,
    "ORDINAL": EntityType.ORDINAL,
    "CARDINAL": EntityType.CARDINAL,
    "NORP": EntityType.NORP,  # Nationalities/religious/political groups
    "WORK_OF_ART": EntityType.WORK_OF_ART,
}


def map_spacy_label_to_entity_type(label: str) -> EntityType:
    """Map spaCy entity label to EntityType enum."""
    return SPACY_ENTITY_MAPPING.get(label, EntityType.OTHER)


class SpacyAdapter(NLPProcessorProtocol):
    """
    Adapter for spaCy NLP processor.

    Wraps spaCy to provide a standardized interface that can be
    easily swapped with other NLP providers (OpenAI, HuggingFace, etc.)
    """

    def __init__(self, model_name: str = "en_core_web_sm", nlp: Optional[Language] = None):
        """
        Initialize spaCy model.

        Args:
            model_name: spaCy model to load (default: en_core_web_sm)
            nlp: Optional spaCy Language instance for dependency injection.
                 If not provided, loads the model specified by model_name.

        Raises:
            OSError: If model not installed and nlp not provided
        """
        self.model_name = model_name

        # Use provided nlp or load model
        if nlp is not None:
            self.nlp: Language = nlp
            logger.info("spacy_adapter_initialized", model="custom_nlp_injected")
        else:
            try:
                self.nlp: Language = spacy.load(model_name)
                logger.info("spacy_adapter_initialized", model=model_name)
            except OSError:
                logger.error(
                    "spacy_model_not_found",
                    model=model_name,
                    suggestion="Run: python -m spacy download en_core_web_sm",
                )
                raise OSError(
                    f"spaCy model '{model_name}' not found. "
                    f"Run: python -m spacy download {model_name}"
                )

    @cached(ttl=CacheConfig.NLP_ANALYSIS_TTL, key_prefix="spacy_analyze")
    async def analyze(self, text: str, max_length: Optional[int] = None) -> AnalyzedText:
        """
        Analyze text using spaCy.

        Cached for 30 minutes as NLP analysis is expensive and deterministic.

        Args:
            text: Text to analyze
            max_length: Max length to analyze (for performance)

        Returns:
            AnalyzedText with linguistic features
        """
        if max_length:
            text = text[:max_length]

        logger.info("nlp_analysis_started", text_length=len(text))

        try:
            # Run blocking spaCy operation in thread pool
            doc = await asyncio.to_thread(self.nlp, text)

            # Extract sentences
            sentences = [
                Sentence(
                    text=sent.text,
                    start=sent.start_char,
                    end=sent.end_char,
                )
                for sent in doc.sents
            ]

            # Extract entities
            entities = [
                Entity(
                    text=ent.text,
                    type=map_spacy_label_to_entity_type(ent.label_),
                    label=ent.label_,
                    start=ent.start_char,
                    end=ent.end_char,
                )
                for ent in doc.ents
            ]

            # Extract tokens
            tokens = [token.text for token in doc if token.is_alpha]

            # Find unknown words (for spell checking)
            unknown_words = [
                token.text
                for token in doc
                if token.is_alpha
                and not token.is_stop
                and token.pos_ == "X"  # Unknown part of speech
            ]

            # Detect language (spaCy's language detector)
            language = doc.lang_

            result = AnalyzedText(
                text=text,
                sentences=sentences,
                entities=entities,
                tokens=tokens,
                word_count=len(tokens),  # Count alphabetic tokens only (same as tokens list)
                language=language,
                unknown_words=unknown_words,
                metadata={
                    "model": self.model_name,
                    "spacy_version": spacy.__version__,
                },
            )

            logger.info(
                "nlp_analysis_completed",
                sentence_count=len(sentences),
                entity_count=len(entities),
                word_count=result.word_count,
            )

            return result

        except Exception as e:
            logger.error("nlp_analysis_failed", error=str(e))
            raise

    async def extract_entities(self, text: str) -> List[Entity]:
        """
        Extract named entities using spaCy.

        Args:
            text: Text to analyze

        Returns:
            List of entities
        """
        doc = await asyncio.to_thread(self.nlp, text)

        entities = [
            Entity(
                text=ent.text,
                type=map_spacy_label_to_entity_type(ent.label_),
                label=ent.label_,
                start=ent.start_char,
                end=ent.end_char,
            )
            for ent in doc.ents
        ]

        logger.info("entities_extracted", count=len(entities))

        return entities

    async def check_spelling(self, text: str, threshold: int = 10) -> List[str]:
        """
        Check spelling using spaCy.

        Args:
            text: Text to check
            threshold: Max number of unknown words to return

        Returns:
            List of potentially misspelled words
        """
        # Limit text for performance
        text = text[:10000]

        doc = await asyncio.to_thread(self.nlp, text)

        # Find words that spaCy doesn't recognize
        unknown_words = [
            token.text
            for token in doc
            if token.is_alpha
            and not token.is_stop
            and token.pos_ == "X"  # Unknown part of speech
        ]

        # Return up to threshold
        result = unknown_words[:threshold]

        logger.info("spell_check_completed", unknown_count=len(unknown_words))

        return result

    async def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text using spaCy.

        Args:
            text: Text to tokenize

        Returns:
            List of tokens
        """
        doc = await asyncio.to_thread(self.nlp, text)

        tokens = [token.text for token in doc if token.is_alpha]

        return tokens

    async def detect_language(self, text: str) -> str:
        """
        Detect language using spaCy.

        Args:
            text: Text to analyze

        Returns:
            Language code (e.g., "en")
        """
        doc = await asyncio.to_thread(self.nlp, text[:1000])

        return doc.lang_


__all__ = ["SpacyAdapter"]
