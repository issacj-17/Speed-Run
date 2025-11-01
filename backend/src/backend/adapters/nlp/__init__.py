"""
NLP processor adapters.

Abstracts NLP libraries (spaCy, OpenAI, HuggingFace, etc.)
"""

from .protocol import NLPProcessorProtocol, AnalyzedText, Entity, Sentence
from .spacy import SpacyAdapter

__all__ = [
    "NLPProcessorProtocol",
    "AnalyzedText",
    "Entity",
    "Sentence",
    "SpacyAdapter",
]
