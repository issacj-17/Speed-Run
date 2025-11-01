# Testing Best Practices and Principles

**Version:** 1.0
**Last Updated:** 2025-11-02
**Status:** Gold Standard for All Testing

---

## Table of Contents

1. [Testing Philosophy](#testing-philosophy)
2. [Testing Pyramid](#testing-pyramid)
3. [Coverage Requirements](#coverage-requirements)
4. [Test Types](#test-types)
5. [Best Practices](#best-practices)
6. [Testing Patterns](#testing-patterns)
7. [Naming Conventions](#naming-conventions)
8. [Test Organization](#test-organization)
9. [Fixtures and Mocking](#fixtures-and-mocking)
10. [Async Testing](#async-testing)
11. [Performance Testing](#performance-testing)
12. [CI/CD Integration](#cicd-integration)

---

## Testing Philosophy

### Core Principles

1. **Tests are Documentation**
   - Tests should clearly communicate intent
   - Test names should describe what is being tested and expected outcome
   - Arrange-Act-Assert (AAA) pattern should be obvious

2. **Tests are Safety Nets**
   - High coverage prevents regressions
   - Tests should fail fast and provide clear error messages
   - Every bug should result in a new test

3. **Tests Enable Refactoring**
   - Good tests allow confident code changes
   - Tests should verify behavior, not implementation
   - Tests should be independent and isolated

4. **Tests are First-Class Code**
   - Apply same quality standards as production code
   - Avoid duplication, use fixtures and helpers
   - Tests should be maintainable and readable

---

## Testing Pyramid

```
                    /\
                   /  \
                  / E2E \          10% - End-to-End Tests
                 /______\
                /        \
               /Integration\       20% - Integration Tests
              /____________\
             /              \
            /   Unit Tests   \    70% - Unit Tests
           /__________________\
```

### Distribution Guidelines

- **70% Unit Tests**: Fast, isolated, test single components
- **20% Integration Tests**: Test component interactions
- **10% E2E Tests**: Test complete user workflows

### Why This Distribution?

- **Speed**: Unit tests run in milliseconds, E2E in seconds/minutes
- **Reliability**: Unit tests are deterministic, E2E can be flaky
- **Debugging**: Unit test failures pinpoint exact issue
- **Maintenance**: Unit tests are easier to maintain

---

## Coverage Requirements

### Minimum Coverage Targets

| Metric | Target | Critical Code Target |
|--------|--------|----------------------|
| **Line Coverage** | 85% | 95% |
| **Branch Coverage** | 80% | 90% |
| **Function Coverage** | 90% | 95% |
| **Statement Coverage** | 85% | 95% |

### Critical Code Areas

Critical code requires higher coverage:
- Authentication and authorization
- Payment processing
- Data validation and sanitization
- Security-related operations
- Audit trail generation
- Alert triggering logic

### Coverage Tools

```bash
# Run tests with coverage
pytest --cov=backend --cov-report=term-missing --cov-report=html

# Check branch coverage
pytest --cov=backend --cov-branch --cov-report=term-missing

# Fail if coverage below threshold
pytest --cov=backend --cov-fail-under=85
```

### Uncovered Code Strategy

1. **Identify uncovered branches**: Use coverage reports
2. **Categorize**:
   - Error handling paths
   - Edge cases
   - Defensive programming
3. **Prioritize**: Cover critical paths first
4. **Create tests**: Use parametrize for multiple scenarios

---

## Test Types

### 1. Unit Tests

**Definition**: Test single function/method in isolation

**Characteristics**:
- No external dependencies (DB, API, filesystem)
- Use mocks/stubs for dependencies
- Fast execution (< 100ms per test)
- Deterministic results

**Example**:
```python
# Good: Isolated unit test
async def test_format_validator_detects_double_spacing(mock_nlp_processor):
    validator = FormatValidationService(nlp_processor=mock_nlp_processor)
    text = "This has  double  spacing issues."

    result = await validator.validate(text, Path("test.txt"))

    assert result.has_formatting_issues is True
    assert any("spacing" in issue.description.lower() for issue in result.issues)
    assert result.double_spacing_count > 0

# Bad: Not isolated (depends on real NLP)
async def test_format_validator_with_real_nlp():
    validator = FormatValidationService()  # Uses real spaCy
    # This is slow and brittle
```

**File Location**: `backend/tests/unit/`

---

### 2. Integration Tests

**Definition**: Test interaction between 2+ components

**Characteristics**:
- Real database (test database, isolated)
- Real cache (or test cache)
- Test actual integrations
- Moderate speed (< 1 second per test)

**Example**:
```python
# Good: Tests service + database integration
async def test_alert_service_create_and_retrieve(test_db):
    service = AlertService(test_db)

    # Create
    alert_data = AlertCreate(
        alert_type="TEST",
        severity=AlertSeverity.HIGH,
        client_id=uuid4(),
        title="Test alert",
        risk_score=85,
    )
    created = await service.create_alert(alert_data)

    # Retrieve
    retrieved = await service.get_alert(created.id)

    assert retrieved.id == created.id
    assert retrieved.title == "Test alert"
```

**File Location**: `backend/tests/integration/`

---

### 3. System Tests

**Definition**: Test complete subsystems with real infrastructure

**Characteristics**:
- Real database, cache, file system
- Test complete workflows
- Slower (1-5 seconds per test)
- More realistic scenarios

**Example**:
```python
# Good: Tests complete document processing pipeline
async def test_document_processing_pipeline(test_db, temp_upload_dir):
    # Use real adapters, not mocks
    container = get_container()
    service = CorroborationService(
        document_parser=container.document_parser,
        nlp_processor=container.nlp_processor,
        image_processor=container.image_processor,
    )

    # Test complete workflow
    pdf_path = temp_upload_dir / "test_invoice.pdf"
    result = await service.analyze_document(pdf_path)

    assert result.is_valid is True
    assert result.format_validation.has_formatting_issues is False
    assert len(result.extracted_text) > 0
```

**File Location**: `backend/tests/system/`

---

### 4. End-to-End Tests

**Definition**: Test complete user workflows through API

**Characteristics**:
- HTTP requests to running application
- Test user-facing functionality
- Slowest tests (2-10 seconds)
- Most realistic

**Example**:
```python
# Good: Tests complete API workflow
async def test_alert_creation_workflow(client: TestClient):
    # 1. Upload document
    files = {"file": ("test.pdf", pdf_content, "application/pdf")}
    upload_response = client.post("/api/v1/documents/parse", files=files)
    assert upload_response.status_code == 200
    document_id = upload_response.json()["id"]

    # 2. Create alert for document
    alert_data = {
        "alert_type": "DOCUMENT_RISK",
        "severity": "HIGH",
        "document_id": document_id,
        "title": "Suspicious document detected",
        "risk_score": 85,
    }
    alert_response = client.post("/api/v1/alerts", json=alert_data)
    assert alert_response.status_code == 201
    alert_id = alert_response.json()["id"]

    # 3. Update alert status
    update_response = client.patch(
        f"/api/v1/alerts/{alert_id}/status",
        json={"status": "ACKNOWLEDGED"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "ACKNOWLEDGED"
```

**File Location**: `backend/tests/e2e/`

---

## Best Practices

### 1. Test Independence

**Principle**: Each test should run independently

```python
# Good: Independent test
async def test_create_alert(test_db):
    service = AlertService(test_db)
    alert_data = AlertCreate(...)
    result = await service.create_alert(alert_data)
    assert result.id is not None

# Bad: Depends on previous test state
async def test_update_alert_created_by_previous_test(test_db):
    # Assumes alert from previous test exists - WRONG!
    service = AlertService(test_db)
    result = await service.update_alert_status(alert_id, AlertStatus.RESOLVED)
```

### 2. Test Isolation

**Principle**: Tests should not affect each other

```python
# Good: Uses fixture that cleans up
@pytest.fixture
async def alert_in_db(test_db):
    service = AlertService(test_db)
    alert = await service.create_alert(AlertCreate(...))
    yield alert
    # Cleanup happens automatically via test_db fixture rollback

# Bad: Leaves data in database
async def test_that_pollutes_database(test_db):
    service = AlertService(test_db)
    await service.create_alert(AlertCreate(...))
    # No cleanup - affects other tests
```

### 3. Arrange-Act-Assert (AAA)

**Principle**: Clear structure for every test

```python
# Good: Clear AAA structure
async def test_alert_assignment():
    # Arrange
    alert = Alert(status=AlertStatus.NEW)
    user_id = uuid4()

    # Act
    alert.assigned_to = user_id
    alert.status = AlertStatus.ACKNOWLEDGED

    # Assert
    assert alert.assigned_to == user_id
    assert alert.status == AlertStatus.ACKNOWLEDGED

# Bad: Mixed structure
async def test_messy():
    alert = Alert(status=AlertStatus.NEW)
    assert alert.status == AlertStatus.NEW  # Assert too early
    alert.assigned_to = uuid4()
    user_id = uuid4()  # Arrange after Act
    assert alert.assigned_to is not None
```

### 4. One Assertion Per Concept

**Principle**: Test one logical concept per test

```python
# Good: Tests one concept - alert creation
async def test_create_alert_sets_correct_fields(test_db):
    service = AlertService(test_db)
    alert_data = AlertCreate(
        alert_type="TEST",
        severity=AlertSeverity.HIGH,
        title="Test",
        risk_score=85,
    )

    result = await service.create_alert(alert_data)

    # Multiple asserts OK - same concept
    assert result.alert_type == "TEST"
    assert result.severity == AlertSeverity.HIGH
    assert result.status == AlertStatus.NEW  # Default status
    assert result.created_at is not None

# Bad: Tests multiple concepts
async def test_alert_crud_everything(test_db):
    # Tests create, update, delete, list - too much!
    service = AlertService(test_db)
    created = await service.create_alert(...)
    updated = await service.update_alert_status(...)
    await service.delete_alert(...)
    alerts = await service.list_alerts()
```

### 5. Test Edge Cases and Error Paths

**Principle**: Cover happy path AND error paths

```python
# Good: Tests error handling
async def test_get_alert_not_found(test_db):
    service = AlertService(test_db)
    non_existent_id = uuid4()

    result = await service.get_alert(non_existent_id)

    assert result is None

async def test_create_alert_with_invalid_risk_score(test_db):
    service = AlertService(test_db)

    with pytest.raises(ValidationError) as exc_info:
        alert_data = AlertCreate(
            alert_type="TEST",
            severity=AlertSeverity.HIGH,
            risk_score=150,  # Invalid: > 100
        )

    assert "risk_score" in str(exc_info.value)
```

### 6. Parametrized Tests for Multiple Scenarios

**Principle**: Use parametrize for similar tests with different inputs

```python
# Good: Parametrized test
@pytest.mark.parametrize("risk_score,expected_severity", [
    (0, AlertSeverity.LOW),
    (40, AlertSeverity.MEDIUM),
    (70, AlertSeverity.HIGH),
    (95, AlertSeverity.CRITICAL),
])
async def test_calculate_severity_from_risk_score(risk_score, expected_severity):
    severity = calculate_severity(risk_score)
    assert severity == expected_severity

# Bad: Duplicate tests
async def test_low_risk_score():
    assert calculate_severity(0) == AlertSeverity.LOW

async def test_medium_risk_score():
    assert calculate_severity(40) == AlertSeverity.MEDIUM

async def test_high_risk_score():
    assert calculate_severity(70) == AlertSeverity.HIGH
```

### 7. Descriptive Test Names

**Principle**: Test names should describe scenario and expected outcome

```python
# Good: Descriptive names
async def test_format_validator_detects_double_spacing_in_text()
async def test_alert_service_creates_alert_with_new_status()
async def test_corroboration_service_returns_none_for_unsupported_format()

# Bad: Vague names
async def test_validator()
async def test_alert()
async def test_service()
```

### 8. Avoid Test Logic

**Principle**: Tests should be simple and obvious

```python
# Good: Simple test
async def test_filter_alerts_by_severity(test_db):
    service = AlertService(test_db)
    await create_test_alert(test_db, severity=AlertSeverity.HIGH)
    await create_test_alert(test_db, severity=AlertSeverity.LOW)

    high_alerts = await service.list_alerts(severity=AlertSeverity.HIGH)

    assert len(high_alerts) == 1
    assert high_alerts[0].severity == AlertSeverity.HIGH

# Bad: Complex logic in test
async def test_complex_filtering(test_db):
    service = AlertService(test_db)

    # Creating alerts with loop - test logic!
    for i in range(10):
        severity = AlertSeverity.HIGH if i % 2 == 0 else AlertSeverity.LOW
        await create_test_alert(test_db, severity=severity)

    # Filtering with logic - test logic!
    alerts = await service.list_alerts()
    high_count = sum(1 for a in alerts if a.severity == AlertSeverity.HIGH)

    assert high_count == 5  # Magic number - where did 5 come from?
```

---

## Testing Patterns

### 1. Test Data Builders

**Pattern**: Use builder functions for complex test data

```python
# Good: Reusable builder
def build_alert_data(
    alert_type: str = "TEST",
    severity: AlertSeverity = AlertSeverity.MEDIUM,
    **overrides
) -> AlertCreate:
    """Build alert data with sensible defaults."""
    defaults = {
        "alert_type": alert_type,
        "severity": severity,
        "client_id": uuid4(),
        "title": "Test alert",
        "description": "Test description",
        "risk_score": 50,
        "triggered_rules": {},
        "context": {},
        "recommended_actions": [],
    }
    defaults.update(overrides)
    return AlertCreate(**defaults)

# Usage
async def test_with_custom_severity(test_db):
    alert_data = build_alert_data(severity=AlertSeverity.CRITICAL)
    result = await service.create_alert(alert_data)
    assert result.severity == AlertSeverity.CRITICAL
```

### 2. Fixture Composition

**Pattern**: Compose complex fixtures from simple ones

```python
# Good: Composable fixtures
@pytest.fixture
async def alert_service(test_db):
    return AlertService(test_db)

@pytest.fixture
async def alert_in_db(test_db, alert_service):
    alert_data = build_alert_data()
    return await alert_service.create_alert(alert_data)

@pytest.fixture
async def resolved_alert(test_db, alert_service, alert_in_db):
    await alert_service.update_alert_status(
        alert_in_db.id,
        AlertStatus.RESOLVED
    )
    return await alert_service.get_alert(alert_in_db.id)

# Usage
async def test_resolved_alert_has_resolution_timestamp(resolved_alert):
    assert resolved_alert.resolved_at is not None
```

### 3. Mock Verification

**Pattern**: Verify mock interactions for side effects

```python
# Good: Verify mock called correctly
async def test_forensic_analyzer_calls_all_services(
    mock_metadata_analyzer,
    mock_ai_detector,
    mock_tampering_detector
):
    analyzer = ForensicAnalysisService(
        metadata_analyzer=mock_metadata_analyzer,
        ai_detector=mock_ai_detector,
        tampering_detector=mock_tampering_detector,
    )

    file_path = Path("test.jpg")
    await analyzer.analyze(file_path)

    # Verify all services called
    mock_metadata_analyzer.analyze.assert_called_once_with(file_path)
    mock_ai_detector.detect.assert_called_once_with(file_path)
    mock_tampering_detector.detect.assert_called_once_with(file_path)
```

### 4. Snapshot Testing

**Pattern**: Compare output to stored snapshot

```python
# Good: Snapshot testing for complex output
async def test_document_parse_output_structure(document_parser, snapshot):
    result = await document_parser.parse(Path("test.pdf"))

    # Compare to stored snapshot
    snapshot.assert_match(result.model_dump(mode="json"), "parsed_document.json")
```

---

## Naming Conventions

### Test File Names

- `test_<module_name>.py` - Unit tests for module
- `test_<service_name>_integration.py` - Integration tests
- `test_<feature>_system.py` - System tests
- `test_<workflow>_e2e.py` - End-to-end tests

### Test Function Names

Pattern: `test_<component>_<scenario>_<expected_outcome>`

Examples:
```python
# Unit tests
test_format_validator_detects_double_spacing()
test_alert_service_creates_alert_with_default_status()
test_cache_decorator_returns_cached_result_on_second_call()

# Integration tests
test_alert_service_persists_to_database()
test_corroboration_service_uses_real_adapters()

# System tests
test_document_processing_pipeline_end_to_end()
test_alert_workflow_from_detection_to_resolution()

# Edge cases
test_alert_service_handles_invalid_uuid()
test_document_parser_rejects_unsupported_format()

# Error paths
test_format_validator_raises_on_empty_text()
test_database_rollback_on_integrity_error()
```

---

## Test Organization

### Directory Structure

```
backend/
├── src/
│   └── backend/
│       ├── services/
│       ├── adapters/
│       └── routers/
└── tests/
    ├── conftest.py              # Shared fixtures
    ├── unit/
    │   ├── conftest.py          # Unit test fixtures
    │   ├── adapters/
    │   │   ├── test_document_parser.py
    │   │   ├── test_nlp_processor.py
    │   │   └── test_image_processor.py
    │   └── services/
    │       ├── test_alert_service.py
    │       ├── test_format_validator.py
    │       └── test_forensic_analyzer.py
    ├── integration/
    │   ├── conftest.py          # Integration test fixtures
    │   ├── test_alert_service_integration.py
    │   ├── test_document_service_integration.py
    │   └── test_cache_integration.py
    ├── system/
    │   ├── conftest.py          # System test fixtures
    │   ├── test_document_processing_pipeline.py
    │   └── test_alert_workflow.py
    └── e2e/
        ├── conftest.py          # E2E test fixtures
        ├── test_api_document_workflow.py
        └── test_api_alert_workflow.py
```

### Test Markers

Use pytest markers to categorize tests:

```python
# In pytest.ini or pyproject.toml
[tool.pytest.ini_options]
markers = [
    "unit: Unit tests (fast, isolated)",
    "integration: Integration tests (moderate speed)",
    "system: System tests (slower, realistic)",
    "e2e: End-to-end tests (slow, full workflows)",
    "slow: Slow tests (> 1 second)",
    "cache: Tests requiring Redis cache",
    "database: Tests requiring database",
]

# Usage in tests
@pytest.mark.unit
async def test_format_validator():
    pass

@pytest.mark.integration
@pytest.mark.database
async def test_alert_service_integration():
    pass

# Run specific markers
pytest -m unit                    # Fast unit tests
pytest -m "not slow"              # Skip slow tests
pytest -m "integration or system" # Integration and system tests
```

---

## Fixtures and Mocking

### Fixture Scope

Choose appropriate scope:

```python
# Function scope (default) - new instance per test
@pytest.fixture
async def alert_service(test_db):
    return AlertService(test_db)

# Module scope - shared within module
@pytest.fixture(scope="module")
def app_config():
    return Settings(TESTING=True)

# Session scope - shared across all tests
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
```

### Mock Best Practices

```python
# Good: Mock external dependencies only
async def test_document_parser_with_mock_docling():
    mock_docling = AsyncMock()
    mock_docling.convert.return_value = MockResult(text="Sample")

    parser = DoclingAdapter(docling_client=mock_docling)
    result = await parser.parse(Path("test.pdf"))

    assert result.text == "Sample"
    mock_docling.convert.assert_called_once()

# Bad: Over-mocking (mocking your own code)
async def test_alert_service_with_all_mocks():
    mock_service = AsyncMock()  # Mocking the thing we're testing!
    mock_service.create_alert.return_value = Alert(...)
    result = await mock_service.create_alert(...)
    # This tests nothing - we're testing the mock!
```

### When to Mock vs Use Real

| Component | Unit Test | Integration Test | System Test | E2E Test |
|-----------|-----------|------------------|-------------|----------|
| Database | Mock | Real (test DB) | Real (test DB) | Real (test DB) |
| Cache | Mock | Real (test Redis) | Real (test Redis) | Real (test Redis) |
| External API | Mock | Mock | Mock/Stub | Real/Staging |
| File System | Mock | Real (temp) | Real (temp) | Real (temp) |
| Time | Mock | Mock | Real | Real |
| Random | Mock | Mock | Real | Real |

---

## Async Testing

### Pytest-asyncio Configuration

```python
# conftest.py
import pytest
import asyncio

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Async test
@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result is not None
```

### Async Context Managers

```python
# Good: Proper async context manager testing
async def test_database_session_cleanup(test_db):
    async with test_db.begin():
        alert = Alert(...)
        test_db.add(alert)
        # Commit happens automatically

    # Verify committed
    result = await test_db.execute(select(Alert))
    assert result.scalar_one().id == alert.id

# Test rollback on error
async def test_database_rollback_on_error(test_db):
    with pytest.raises(IntegrityError):
        async with test_db.begin():
            alert = Alert(id=None, title=None)  # Invalid
            test_db.add(alert)

    # Verify rollback happened
    result = await test_db.execute(select(Alert))
    assert result.first() is None
```

### Async Timeouts

```python
# Good: Protect against hanging tests
@pytest.mark.asyncio
@pytest.mark.timeout(5)  # Fail if test takes > 5 seconds
async def test_document_parsing_completes_quickly():
    parser = DoclingAdapter()
    result = await parser.parse(Path("small.pdf"))
    assert result is not None
```

---

## Performance Testing

### Benchmarking

```python
# Use pytest-benchmark
def test_cache_performance(benchmark):
    def parse_document():
        # This will be cached
        return expensive_parse_operation()

    # First call (cache miss)
    result1 = benchmark(parse_document)

    # Second call (cache hit) - should be much faster
    result2 = parse_document()

    assert result1 == result2

# Set performance thresholds
def test_alert_creation_performance(test_db, benchmark):
    service = AlertService(test_db)
    alert_data = build_alert_data()

    result = benchmark(lambda: asyncio.run(service.create_alert(alert_data)))

    # Assert creation time < 100ms
    assert benchmark.stats['mean'] < 0.1
```

### Load Testing

```python
# Test concurrent operations
@pytest.mark.slow
async def test_concurrent_alert_creation(test_db):
    service = AlertService(test_db)

    # Create 100 alerts concurrently
    tasks = [
        service.create_alert(build_alert_data())
        for _ in range(100)
    ]

    results = await asyncio.gather(*tasks)

    assert len(results) == 100
    assert all(r.id is not None for r in results)
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio

      - name: Run unit tests
        run: pytest tests/unit -v --cov=backend --cov-report=xml

      - name: Run integration tests
        run: pytest tests/integration -v
        env:
          DATABASE_URL: postgresql://postgres:test@localhost/test
          REDIS_URL: redis://localhost:6379

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: true
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest-unit
        name: Run unit tests
        entry: pytest tests/unit -v --tb=short
        language: system
        pass_filenames: false
        always_run: true

      - id: coverage-check
        name: Check coverage
        entry: pytest tests/unit --cov=backend --cov-fail-under=85
        language: system
        pass_filenames: false
        always_run: true
```

---

## Summary Checklist

When writing tests, ensure:

- [ ] High branch coverage (80%+), not just line coverage
- [ ] Tests follow AAA pattern (Arrange, Act, Assert)
- [ ] Tests are independent and isolated
- [ ] Descriptive test names (`test_<component>_<scenario>_<expected>`)
- [ ] Edge cases and error paths covered
- [ ] Appropriate use of parametrize for similar scenarios
- [ ] Mocks used only for external dependencies
- [ ] Fixtures are composable and reusable
- [ ] Test markers applied for categorization
- [ ] No test logic (loops, conditionals) in tests
- [ ] Performance tests for critical paths
- [ ] Integration tests for component interactions
- [ ] System tests for complete workflows
- [ ] E2E tests for user-facing features

---

**This document is the gold standard for all testing in this project.**
**All tests must adhere to these principles and practices.**
