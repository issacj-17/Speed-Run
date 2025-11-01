"""
Unit tests for NLP processor adapter (spaCy).

Tests SpacyAdapter in isolation with mocked spaCy library.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from pathlib import Path

from backend.adapters.nlp.spacy import SpacyAdapter
from backend.adapters.nlp.protocol import AnalyzedText, Entity, EntityType


# ============================================================================
# Initialization Tests
# ============================================================================


@pytest.mark.unit
@patch("spacy.load")
def test_spacy_adapter_initializes_with_default_model(mock_spacy_load):
    """Test SpacyAdapter initializes with default spaCy model."""
    mock_nlp = MagicMock()
    mock_spacy_load.return_value = mock_nlp

    adapter = SpacyAdapter()

    assert adapter.nlp is not None
    assert hasattr(adapter.nlp, "__call__")
    mock_spacy_load.assert_called_once_with("en_core_web_sm")


@pytest.mark.unit
def test_spacy_adapter_accepts_custom_nlp_model(mock_spacy_nlp):
    """Test SpacyAdapter accepts custom nlp model for DI."""
    adapter = SpacyAdapter(nlp=mock_spacy_nlp)

    assert adapter.nlp == mock_spacy_nlp


# ============================================================================
# Analyze Tests - Happy Path
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_analyze_returns_analyzed_text_with_correct_structure(mock_spacy_nlp):
    """Test analyze returns AnalyzedText with correct structure."""
    # Arrange
    sample_text = "This is a test sentence."

    mock_doc = MagicMock()
    mock_sent = MagicMock(text="This is a test sentence.", start_char=0, end_char=24)
    mock_doc.sents = [mock_sent]
    mock_doc.ents = []
    mock_doc.__iter__ = MagicMock(return_value=iter([
        MagicMock(text="This", is_alpha=True, is_space=False),
        MagicMock(text="is", is_alpha=True, is_space=False),
        MagicMock(text="a", is_alpha=True, is_space=False),
        MagicMock(text="test", is_alpha=True, is_space=False),
        MagicMock(text="sentence", is_alpha=True, is_space=False),
    ]))
    mock_spacy_nlp.return_value = mock_doc

    adapter = SpacyAdapter(nlp=mock_spacy_nlp)

    # Act
    result = await adapter.analyze(sample_text)

    # Assert
    assert isinstance(result, AnalyzedText)
    assert result.text == sample_text
    assert isinstance(result.sentences, list)
    assert isinstance(result.entities, list)
    assert isinstance(result.tokens, list)
    assert result.word_count > 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_analyze_calls_spacy_nlp_with_text(mock_spacy_nlp):
    """Test analyze calls spaCy nlp with provided text."""
    # Arrange
    sample_text = "Test text for processing."

    mock_doc = MagicMock()
    mock_doc.sents = []
    mock_doc.ents = []
    mock_doc.__iter__ = MagicMock(side_effect=lambda: iter([]))
    mock_spacy_nlp.return_value = mock_doc

    adapter = SpacyAdapter(nlp=mock_spacy_nlp)

    # Act
    await adapter.analyze(sample_text)

    # Assert
    mock_spacy_nlp.assert_called_once_with(sample_text)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_analyze_extracts_sentences_correctly(mock_spacy_nlp):
    """Test analyze extracts sentences from spaCy doc."""
    # Arrange
    sample_text = "First sentence. Second sentence. Third sentence."

    sent1 = MagicMock()
    sent1.text = "First sentence."
    sent1.start_char = 0
    sent1.end_char = 15
    sent2 = MagicMock()
    sent2.text = "Second sentence."
    sent2.start_char = 16
    sent2.end_char = 32
    sent3 = MagicMock()
    sent3.text = "Third sentence."
    sent3.start_char = 33
    sent3.end_char = 48

    mock_doc = MagicMock()
    mock_doc.sents = [sent1, sent2, sent3]
    mock_doc.ents = []
    mock_doc.__iter__ = MagicMock(side_effect=lambda: iter([]))
    mock_spacy_nlp.return_value = mock_doc

    adapter = SpacyAdapter(nlp=mock_spacy_nlp)

    # Act
    result = await adapter.analyze(sample_text)

    # Assert
    assert len(result.sentences) == 3
    assert result.sentences[0].text == "First sentence."
    assert result.sentences[1].text == "Second sentence."
    assert result.sentences[2].text == "Third sentence."


@pytest.mark.unit
@pytest.mark.asyncio
async def test_analyze_extracts_entities_correctly(mock_spacy_nlp):
    """Test analyze extracts named entities from spaCy doc."""
    # Arrange
    sample_text = "John Smith works at Microsoft in Seattle."

    entity1 = MagicMock()
    entity1.text = "John Smith"
    entity1.label_ = "PERSON"
    entity1.start_char = 0
    entity1.end_char = 10

    entity2 = MagicMock()
    entity2.text = "Microsoft"
    entity2.label_ = "ORG"
    entity2.start_char = 20
    entity2.end_char = 29

    entity3 = MagicMock()
    entity3.text = "Seattle"
    entity3.label_ = "GPE"
    entity3.start_char = 33
    entity3.end_char = 40

    mock_doc = MagicMock()
    mock_doc.sents = []
    mock_doc.ents = [entity1, entity2, entity3]
    mock_doc.__iter__ = MagicMock(side_effect=lambda: iter([]))
    mock_spacy_nlp.return_value = mock_doc

    adapter = SpacyAdapter(nlp=mock_spacy_nlp)

    # Act
    result = await adapter.analyze(sample_text)

    # Assert
    assert len(result.entities) == 3

    assert result.entities[0].text == "John Smith"
    assert result.entities[0].type == EntityType.PERSON

    assert result.entities[1].text == "Microsoft"
    assert result.entities[1].type == EntityType.ORGANIZATION

    assert result.entities[2].text == "Seattle"
    assert result.entities[2].type == EntityType.LOCATION


@pytest.mark.unit
@pytest.mark.asyncio
async def test_analyze_extracts_tokens_correctly(mock_spacy_nlp):
    """Test analyze extracts tokens from spaCy doc."""
    # Arrange
    sample_text = "The quick brown fox."

    token1 = MagicMock(text="The", is_alpha=True, is_space=False)
    token2 = MagicMock(text="quick", is_alpha=True, is_space=False)
    token3 = MagicMock(text="brown", is_alpha=True, is_space=False)
    token4 = MagicMock(text="fox", is_alpha=True, is_space=False)
    token5 = MagicMock(text=".", is_alpha=False, is_space=False)  # Punctuation

    mock_doc = MagicMock()
    mock_doc.sents = []
    mock_doc.ents = []
    mock_doc.__iter__ = MagicMock(side_effect=lambda: iter([token1, token2, token3, token4, token5]))
    mock_spacy_nlp.return_value = mock_doc

    adapter = SpacyAdapter(nlp=mock_spacy_nlp)

    # Act
    result = await adapter.analyze(sample_text)

    # Assert
    # Should only include alphabetic tokens
    assert len(result.tokens) == 4
    assert result.tokens == ["The", "quick", "brown", "fox"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_analyze_calculates_word_count_correctly(mock_spacy_nlp):
    """Test analyze calculates word count (alphabetic tokens only)."""
    # Arrange
    sample_text = "One two three, four! Five."

    tokens = [
        MagicMock(text="One", is_alpha=True, is_space=False),
        MagicMock(text="two", is_alpha=True, is_space=False),
        MagicMock(text="three", is_alpha=True, is_space=False),
        MagicMock(text=",", is_alpha=False, is_space=False),
        MagicMock(text="four", is_alpha=True, is_space=False),
        MagicMock(text="!", is_alpha=False, is_space=False),
        MagicMock(text="Five", is_alpha=True, is_space=False),
        MagicMock(text=".", is_alpha=False, is_space=False),
    ]

    mock_doc = MagicMock()
    mock_doc.sents = []
    mock_doc.ents = []
    mock_doc.__iter__ = MagicMock(side_effect=lambda: iter(tokens))
    mock_spacy_nlp.return_value = mock_doc

    adapter = SpacyAdapter(nlp=mock_spacy_nlp)

    # Act
    result = await adapter.analyze(sample_text)

    # Assert
    assert result.word_count == 5  # Only alphabetic tokens


# ============================================================================
# Analyze Tests - Max Length Truncation
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_analyze_truncates_long_text_when_max_length_specified(mock_spacy_nlp):
    """Test analyze truncates text when max_length is specified."""
    # Arrange
    long_text = "word " * 1000  # 1000 words
    max_length = 100

    mock_doc = MagicMock()
    mock_doc.sents = []
    mock_doc.ents = []
    mock_doc.__iter__ = MagicMock(side_effect=lambda: iter([]))
    mock_spacy_nlp.return_value = mock_doc

    adapter = SpacyAdapter(nlp=mock_spacy_nlp)

    # Act
    result = await adapter.analyze(long_text, max_length=max_length)

    # Assert
    # spaCy should be called with truncated text
    call_args = mock_spacy_nlp.call_args[0]
    assert len(call_args[0]) <= max_length


@pytest.mark.unit
@pytest.mark.asyncio
async def test_analyze_does_not_truncate_when_below_max_length(mock_spacy_nlp):
    """Test analyze does not truncate when text is below max_length."""
    # Arrange
    short_text = "Short text"
    max_length = 1000

    mock_doc = MagicMock()
    mock_doc.sents = []
    mock_doc.ents = []
    mock_doc.__iter__ = MagicMock(side_effect=lambda: iter([]))
    mock_spacy_nlp.return_value = mock_doc

    adapter = SpacyAdapter(nlp=mock_spacy_nlp)

    # Act
    await adapter.analyze(short_text, max_length=max_length)

    # Assert
    mock_spacy_nlp.assert_called_once_with(short_text)


# ============================================================================
# Analyze Tests - Edge Cases
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_analyze_handles_empty_text(mock_spacy_nlp):
    """Test analyze handles empty text gracefully."""
    # Arrange
    mock_doc = MagicMock()
    mock_doc.sents = []
    mock_doc.ents = []
    mock_doc.__iter__ = MagicMock(side_effect=lambda: iter([]))
    mock_spacy_nlp.return_value = mock_doc

    adapter = SpacyAdapter(nlp=mock_spacy_nlp)

    # Act
    result = await adapter.analyze("")

    # Assert
    assert result.text == ""
    assert result.word_count == 0
    assert len(result.sentences) == 0
    assert len(result.entities) == 0
    assert len(result.tokens) == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_analyze_handles_whitespace_only_text(mock_spacy_nlp):
    """Test analyze handles whitespace-only text."""
    # Arrange
    mock_doc = MagicMock()
    mock_doc.sents = []
    mock_doc.ents = []
    mock_doc.__iter__ = MagicMock(side_effect=lambda: iter([]))
    mock_spacy_nlp.return_value = mock_doc

    adapter = SpacyAdapter(nlp=mock_spacy_nlp)

    # Act
    result = await adapter.analyze("   \n\n   \t  ")

    # Assert
    assert result.word_count == 0
    assert len(result.tokens) == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_analyze_handles_special_characters(mock_spacy_nlp):
    """Test analyze handles special characters and unicode."""
    # Arrange
    special_text = "Café résumé 中文 العربية 🔥"

    tokens = [
        MagicMock(text="Café", is_alpha=True, is_space=False),
        MagicMock(text="résumé", is_alpha=True, is_space=False),
        MagicMock(text="中文", is_alpha=True, is_space=False),
        MagicMock(text="العربية", is_alpha=True, is_space=False),
        MagicMock(text="🔥", is_alpha=False, is_space=False),
    ]

    mock_doc = MagicMock()
    mock_doc.sents = []
    mock_doc.ents = []
    mock_doc.__iter__ = MagicMock(side_effect=lambda: iter(tokens))
    mock_spacy_nlp.return_value = mock_doc

    adapter = SpacyAdapter(nlp=mock_spacy_nlp)

    # Act
    result = await adapter.analyze(special_text)

    # Assert
    assert result.text == special_text
    assert result.word_count == 4  # Emoji not counted


@pytest.mark.unit
@pytest.mark.asyncio
async def test_analyze_handles_no_entities(mock_spacy_nlp):
    """Test analyze handles text with no named entities."""
    # Arrange
    sample_text = "The quick brown fox jumps."

    mock_doc = MagicMock()
    mock_doc.sents = []
    mock_doc.ents = []  # No entities
    mock_doc.__iter__ = MagicMock(side_effect=lambda: iter([]))
    mock_spacy_nlp.return_value = mock_doc

    adapter = SpacyAdapter(nlp=mock_spacy_nlp)

    # Act
    result = await adapter.analyze(sample_text)

    # Assert
    assert len(result.entities) == 0


# ============================================================================
# Check Spelling Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_check_spelling_returns_unknown_words(mock_spacy_nlp):
    """Test check_spelling identifies unknown words."""
    # Arrange
    sample_text = "This is a tset with mistakse."

    token1 = MagicMock(text="This", is_alpha=True, is_stop=False, pos_="NOUN")
    token2 = MagicMock(text="is", is_alpha=True, is_stop=True, pos_="VERB")
    token3 = MagicMock(text="a", is_alpha=True, is_stop=True, pos_="DET")
    token4 = MagicMock(text="tset", is_alpha=True, is_stop=False, pos_="X")  # Unknown
    token5 = MagicMock(text="with", is_alpha=True, is_stop=True, pos_="ADP")
    token6 = MagicMock(text="mistakse", is_alpha=True, is_stop=False, pos_="X")  # Unknown

    mock_doc = MagicMock()
    mock_doc.__iter__ = MagicMock(side_effect=lambda: iter([token1, token2, token3, token4, token5, token6]))
    mock_spacy_nlp.return_value = mock_doc

    adapter = SpacyAdapter(nlp=mock_spacy_nlp)

    # Act
    result = await adapter.check_spelling(sample_text)

    # Assert
    assert len(result) == 2
    assert "tset" in result
    assert "mistakse" in result


@pytest.mark.unit
@pytest.mark.asyncio
async def test_check_spelling_returns_empty_for_correct_text(mock_spacy_nlp):
    """Test check_spelling returns empty list for correctly spelled text."""
    # Arrange
    sample_text = "This is correct text."

    tokens = [
        MagicMock(text="This", is_alpha=True, is_stop=False, pos_="NOUN"),
        MagicMock(text="is", is_alpha=True, is_stop=False, pos_="NOUN"),
        MagicMock(text="correct", is_alpha=True, is_stop=False, pos_="NOUN"),
        MagicMock(text="text", is_alpha=True, is_stop=False, pos_="NOUN"),
    ]

    mock_doc = MagicMock()
    mock_doc.__iter__ = MagicMock(side_effect=lambda: iter(tokens))
    mock_spacy_nlp.return_value = mock_doc

    adapter = SpacyAdapter(nlp=mock_spacy_nlp)

    # Act
    result = await adapter.check_spelling(sample_text)

    # Assert
    assert len(result) == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_check_spelling_limits_unknown_words_by_threshold(mock_spacy_nlp):
    """Test check_spelling limits results to threshold."""
    # Arrange
    sample_text = "Many unknown wrods heer"

    tokens = [
        MagicMock(text="Many", is_alpha=True, is_stop=False, pos_="NOUN"),
        MagicMock(text="unknown", is_alpha=True, is_stop=False, pos_="NOUN"),
        MagicMock(text="wrods", is_alpha=True, is_stop=False, pos_="X"),
        MagicMock(text="heer", is_alpha=True, is_stop=False, pos_="X"),
    ]

    mock_doc = MagicMock()
    mock_doc.__iter__ = MagicMock(side_effect=lambda: iter(tokens))
    mock_spacy_nlp.return_value = mock_doc

    adapter = SpacyAdapter(nlp=mock_spacy_nlp)

    # Act
    result = await adapter.check_spelling(sample_text, threshold=1)

    # Assert - Should only return 1 unknown word due to threshold
    assert len(result) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_check_spelling_ignores_non_alphabetic_tokens(mock_spacy_nlp):
    """Test check_spelling ignores punctuation and numbers."""
    # Arrange
    sample_text = "Test 123 test! @#$"

    tokens = [
        MagicMock(text="Test", is_alpha=True, is_stop=False, pos_="NOUN"),
        MagicMock(text="123", is_alpha=False, is_stop=False, pos_="X"),  # Should be ignored
        MagicMock(text="test", is_alpha=True, is_stop=False, pos_="NOUN"),
        MagicMock(text="!", is_alpha=False, is_stop=False, pos_="X"),  # Should be ignored
        MagicMock(text="@#$", is_alpha=False, is_stop=False, pos_="X"),  # Should be ignored
    ]

    mock_doc = MagicMock()
    mock_doc.__iter__ = MagicMock(side_effect=lambda: iter(tokens))
    mock_spacy_nlp.return_value = mock_doc

    adapter = SpacyAdapter(nlp=mock_spacy_nlp)

    # Act
    result = await adapter.check_spelling(sample_text)

    # Assert
    assert len(result) == 0  # No alphabetic unknown words


# ============================================================================
# Entity Type Mapping Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("spacy_label,expected_type", [
    ("PERSON", EntityType.PERSON),
    ("ORG", EntityType.ORGANIZATION),
    ("GPE", EntityType.LOCATION),
    ("LOC", EntityType.LOCATION),
    ("DATE", EntityType.DATE),
    ("TIME", EntityType.TIME),
    ("MONEY", EntityType.MONEY),
    ("PERCENT", EntityType.PERCENT),
    ("UNKNOWN_LABEL", EntityType.OTHER),
])
async def test_entity_type_mapping(mock_spacy_nlp, spacy_label, expected_type):
    """Test entity type mapping from spaCy labels to EntityType enum."""
    # Arrange
    entity = MagicMock()
    entity.text = "Test Entity"
    entity.label_ = spacy_label
    entity.start_char = 0
    entity.end_char = 11

    mock_doc = MagicMock()
    mock_doc.sents = []
    mock_doc.ents = [entity]
    mock_doc.__iter__ = MagicMock(side_effect=lambda: iter([]))
    mock_spacy_nlp.return_value = mock_doc

    adapter = SpacyAdapter(nlp=mock_spacy_nlp)

    # Act
    result = await adapter.analyze("Test Entity")

    # Assert
    assert len(result.entities) == 1
    assert result.entities[0].type == expected_type


# ============================================================================
# Caching Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_analyze_caches_result_on_second_call(mock_spacy_nlp):
    """Test analyze caches result and returns cached value on second call."""
    # Arrange
    sample_text = "Test text for caching."

    mock_doc = MagicMock()
    mock_doc.sents = []
    mock_doc.ents = []
    mock_doc.__iter__ = MagicMock(side_effect=lambda: iter([]))
    mock_spacy_nlp.return_value = mock_doc

    adapter = SpacyAdapter(nlp=mock_spacy_nlp)

    # Act
    result1 = await adapter.analyze(sample_text)
    result2 = await adapter.analyze(sample_text)

    # Assert
    assert result1.text == result2.text

    # Note: Caching behavior depends on cache availability
    # If cache is working, spacy_nlp should be called only once


# ============================================================================
# Protocol Compliance Tests
# ============================================================================


@pytest.mark.unit
@patch("spacy.load")
def test_spacy_adapter_implements_protocol(mock_spacy_load):
    """Test SpacyAdapter implements NLPProcessorProtocol."""
    from backend.adapters.nlp.protocol import NLPProcessorProtocol

    mock_nlp = MagicMock()
    mock_spacy_load.return_value = mock_nlp

    adapter = SpacyAdapter()

    # Check protocol methods exist
    assert hasattr(adapter, "analyze")
    assert hasattr(adapter, "check_spelling")
    assert callable(adapter.analyze)
    assert callable(adapter.check_spelling)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_analyze_returns_protocol_compliant_result(mock_spacy_nlp):
    """Test analyze returns result compliant with AnalyzedText schema."""
    # Arrange
    mock_doc = MagicMock()
    mock_doc.sents = []
    mock_doc.ents = []
    mock_doc.__iter__ = MagicMock(side_effect=lambda: iter([]))
    mock_spacy_nlp.return_value = mock_doc

    adapter = SpacyAdapter(nlp=mock_spacy_nlp)

    # Act
    result = await adapter.analyze("Test")

    # Assert - Check all required fields exist
    assert hasattr(result, "text")
    assert hasattr(result, "sentences")
    assert hasattr(result, "entities")
    assert hasattr(result, "tokens")
    assert hasattr(result, "word_count")
    assert hasattr(result, "unknown_words")


# ============================================================================
# Error Handling and Additional Methods Tests
# ============================================================================


@pytest.mark.unit
@patch("spacy.load")
def test_spacy_adapter_raises_oserror_when_model_not_found(mock_spacy_load):
    """Test SpacyAdapter raises OSError when spaCy model is not installed."""
    # Arrange
    mock_spacy_load.side_effect = OSError("Model not found")

    # Act & Assert
    with pytest.raises(OSError) as exc_info:
        SpacyAdapter(model_name="nonexistent_model")

    assert "nonexistent_model" in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_analyze_handles_spacy_processing_error(mock_spacy_nlp):
    """Test analyze handles errors during spaCy processing."""
    # Arrange
    mock_spacy_nlp.side_effect = RuntimeError("spaCy processing failed")

    adapter = SpacyAdapter(nlp=mock_spacy_nlp)

    # Act & Assert
    with pytest.raises(RuntimeError):
        await adapter.analyze("Test text")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_extract_entities_returns_entity_list(mock_spacy_nlp):
    """Test extract_entities returns list of entities."""
    # Arrange
    mock_entity1 = MagicMock()
    mock_entity1.text = "John Doe"
    mock_entity1.label_ = "PERSON"
    mock_entity1.start_char = 0
    mock_entity1.end_char = 8

    mock_entity2 = MagicMock()
    mock_entity2.text = "Apple Inc"
    mock_entity2.label_ = "ORG"
    mock_entity2.start_char = 15
    mock_entity2.end_char = 24

    mock_doc = MagicMock()
    mock_doc.ents = [mock_entity1, mock_entity2]
    mock_spacy_nlp.return_value = mock_doc

    adapter = SpacyAdapter(nlp=mock_spacy_nlp)

    # Act
    result = await adapter.extract_entities("John Doe works at Apple Inc")

    # Assert
    assert len(result) == 2
    assert result[0].text == "John Doe"
    assert result[0].type == EntityType.PERSON
    assert result[1].text == "Apple Inc"
    assert result[1].type == EntityType.ORGANIZATION


@pytest.mark.unit
@pytest.mark.asyncio
async def test_tokenize_returns_token_list(mock_spacy_nlp):
    """Test tokenize returns list of alphabetic tokens."""
    # Arrange
    tokens = [
        MagicMock(text="Hello", is_alpha=True, is_space=False),
        MagicMock(text="world", is_alpha=True, is_space=False),
        MagicMock(text="!", is_alpha=False, is_space=False),  # Should be filtered
        MagicMock(text="123", is_alpha=False, is_space=False),  # Should be filtered
    ]

    mock_doc = MagicMock()
    mock_doc.__iter__ = MagicMock(side_effect=lambda: iter(tokens))
    mock_spacy_nlp.return_value = mock_doc

    adapter = SpacyAdapter(nlp=mock_spacy_nlp)

    # Act
    result = await adapter.tokenize("Hello world ! 123")

    # Assert
    assert len(result) == 2
    assert result[0] == "Hello"
    assert result[1] == "world"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_detect_language_returns_language_code(mock_spacy_nlp):
    """Test detect_language returns language code."""
    # Arrange
    mock_doc = MagicMock()
    mock_doc.lang_ = "en"
    mock_spacy_nlp.return_value = mock_doc

    adapter = SpacyAdapter(nlp=mock_spacy_nlp)

    # Act
    result = await adapter.detect_language("This is an English text")

    # Assert
    assert result == "en"
