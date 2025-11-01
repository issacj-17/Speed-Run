# Backend Test Suite

Comprehensive test suite following the testing pyramid and industry best practices.

## Quick Start

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov pytest-timeout

# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=term-missing --cov-report=html
```

## Test Organization

```
tests/
├── conftest.py              # Shared fixtures for all tests
├── unit/                    # Unit tests (70% of tests)
│   ├── conftest.py          # Unit test fixtures
│   ├── adapters/            # Adapter tests
│   │   ├── test_document_parser.py
│   │   ├── test_nlp_processor.py
│   │   └── test_image_processor.py
│   └── services/            # Service tests
│       ├── test_format_validator.py
│       ├── test_content_validator.py
│       └── test_alert_service.py
├── integration/             # Integration tests (20% of tests)
│   ├── conftest.py          # Integration test fixtures
│   └── test_alert_service_integration.py
├── system/                  # System tests (10% of tests) [TODO]
└── e2e/                     # End-to-end tests [TODO]
```

## Running Tests

### By Test Type

```bash
# Unit tests only (fast)
pytest tests/unit -v

# Integration tests only (moderate speed)
pytest tests/integration -v

# Unit and integration tests
pytest tests/unit tests/integration -v
```

### By Test Marker

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run tests requiring database
pytest -m database

# Skip slow tests
pytest -m "not slow"
```

### By Component

```bash
# Test specific adapter
pytest tests/unit/adapters/test_document_parser.py -v

# Test specific service
pytest tests/unit/services/test_alert_service.py -v

# Test all adapters
pytest tests/unit/adapters/ -v

# Test all services
pytest tests/unit/services/ -v
```

### With Coverage

```bash
# Generate coverage report
pytest --cov=backend --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=backend --cov-report=html
open htmlcov/index.html

# Check branch coverage
pytest --cov=backend --cov-branch --cov-report=term-missing

# Fail if coverage below threshold
pytest --cov=backend --cov-fail-under=85
```

## Test Markers

| Marker | Description | Usage |
|--------|-------------|-------|
| `unit` | Fast, isolated unit tests | `pytest -m unit` |
| `integration` | Tests with real database/cache | `pytest -m integration` |
| `system` | Complete subsystem tests | `pytest -m system` |
| `e2e` | End-to-end API tests | `pytest -m e2e` |
| `slow` | Tests taking > 1 second | `pytest -m slow` |
| `database` | Tests requiring database | `pytest -m database` |
| `cache` | Tests requiring cache | `pytest -m cache` |

## Test Statistics

- **Total Tests**: ~245+
- **Unit Tests**: ~205+
  - Adapters: ~105
  - Services: ~100
- **Integration Tests**: ~40+
- **System Tests**: 0 (TODO)
- **E2E Tests**: 0 (TODO)

## Coverage Targets

| Metric | Target | Current |
|--------|--------|---------|
| Line Coverage | 85% | ~70% |
| Branch Coverage | 80% | ~65% |
| Function Coverage | 90% | ~75% |

## Environment Variables

### For Integration Tests (Optional)

```bash
# Database (defaults to in-memory SQLite)
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/test_db

# Cache (optional, tests run without Redis)
REDIS_URL=redis://localhost:6379/1
```

### For System/E2E Tests (Future)

```bash
# Testing mode
TESTING=true

# Log level for debugging
LOG_LEVEL=DEBUG

# External services (if needed)
DOCLING_API_KEY=your_key
SPACY_MODEL=en_core_web_sm
```

## Writing Tests

### Test Structure (AAA Pattern)

```python
@pytest.mark.unit
@pytest.mark.asyncio
async def test_example():
    # Arrange - Set up test data and mocks
    service = MyService()
    input_data = create_test_data()

    # Act - Execute the code under test
    result = await service.process(input_data)

    # Assert - Verify the outcome
    assert result.status == "success"
    assert result.value > 0
```

### Test Naming Convention

Pattern: `test_<component>_<scenario>_<expected_outcome>`

Examples:
- `test_document_parser_parses_pdf_successfully`
- `test_alert_service_creates_alert_with_default_status`
- `test_format_validator_detects_double_spacing`

### Using Fixtures

```python
@pytest.mark.unit
@pytest.mark.asyncio
async def test_with_fixtures(mock_nlp_processor, temp_pdf_file):
    # Fixtures are automatically injected
    validator = FormatValidationService(nlp_processor=mock_nlp_processor)
    result = await validator.validate_file(temp_pdf_file)
    assert result.is_valid
```

### Parametrized Tests

```python
@pytest.mark.unit
@pytest.mark.parametrize("input,expected", [
    ("valid text", True),
    ("invalid  spacing", False),
    ("", True),
])
def test_multiple_scenarios(input, expected):
    result = validate(input)
    assert result == expected
```

## Debugging Tests

### Run Single Test

```bash
# Run specific test function
pytest tests/unit/adapters/test_document_parser.py::test_parse_returns_parsed_document_with_correct_structure -v

# Run tests matching pattern
pytest -k "test_create_alert" -v
```

### Enable Debug Output

```bash
# Show print statements
pytest -s

# Show full traceback
pytest --tb=long

# Show local variables on failure
pytest -l

# Enable SQL logging (for integration tests)
pytest --log-cli-level=DEBUG
```

### Debug with pdb

```python
import pytest

def test_example():
    result = my_function()
    pytest.set_trace()  # Debugger will stop here
    assert result == expected
```

## Continuous Integration

### Example GitHub Actions

```yaml
- name: Run tests
  run: |
    pytest tests/unit -v --cov=backend --cov-report=xml
    pytest tests/integration -v

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

## Best Practices

1. ✅ **Keep tests fast** - Unit tests should run in < 100ms
2. ✅ **Test one thing** - Each test should verify one behavior
3. ✅ **Use descriptive names** - Test names should describe what is tested
4. ✅ **Arrange-Act-Assert** - Follow AAA pattern consistently
5. ✅ **Test edge cases** - Include boundary values and error cases
6. ✅ **Mock external deps** - Unit tests should not hit external services
7. ✅ **Use fixtures** - DRY principle with reusable fixtures
8. ✅ **Parametrize** - Use `@pytest.mark.parametrize` for similar tests
9. ✅ **Independent tests** - Tests should not depend on each other
10. ✅ **Clean up** - Use fixtures with `yield` for automatic cleanup

## Resources

- **Testing Best Practices**: `backend/TESTING_BEST_PRACTICES.md`
- **Phase 6 Summary**: `backend/PHASE_6_TESTING_SUMMARY.md`
- **Pytest Documentation**: https://docs.pytest.org/
- **pytest-asyncio**: https://pytest-asyncio.readthedocs.io/
- **pytest-cov**: https://pytest-cov.readthedocs.io/

## Troubleshooting

### Tests Not Found

Ensure you're in the backend directory:
```bash
cd backend
pytest
```

### Import Errors

Install the package in development mode:
```bash
pip install -e .
```

### Async Tests Not Running

Install pytest-asyncio:
```bash
pip install pytest-asyncio
```

### Slow Tests

Skip slow tests during development:
```bash
pytest -m "not slow"
```

### Database Errors

Integration tests use in-memory SQLite by default. If you see database errors, check that SQLAlchemy and aiosqlite are installed:
```bash
pip install sqlalchemy aiosqlite
```

## Contributing

When adding new code:

1. Write tests first (TDD)
2. Ensure tests pass: `pytest`
3. Check coverage: `pytest --cov=backend --cov-report=term-missing`
4. Aim for 85%+ line coverage and 80%+ branch coverage
5. Add appropriate markers (`@pytest.mark.unit`, etc.)
6. Follow naming conventions
7. Update this README if needed

---

**For detailed testing guidelines, see `TESTING_BEST_PRACTICES.md`**
