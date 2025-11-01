# Engineering Principles & Best Practices
## Speed-Run AML Platform Backend

> **Purpose:** Reference document for all development decisions
> **Status:** Living Document
> **Last Updated:** 2025-01-15

---

## Table of Contents
1. [Core Principles](#core-principles)
2. [SOLID Principles](#solid-principles)
3. [Design Patterns](#design-patterns)
4. [Code Organization](#code-organization)
5. [Testing Strategy](#testing-strategy)
6. [Performance Guidelines](#performance-guidelines)
7. [Security Principles](#security-principles)
8. [API Design](#api-design)
9. [Error Handling](#error-handling)
10. [Logging & Observability](#logging--observability)

---

## Core Principles

### 1. Modular Monolith Architecture

**Goal:** Easy pivot to microservices when needed

**Guidelines:**
- Each module is self-contained with clear boundaries
- Modules communicate through well-defined interfaces
- No circular dependencies between modules
- Each module can be extracted as a microservice

**Module Structure:**
```
backend/
├── database/           # Database layer (can become DB service)
├── cache/             # Cache layer (can become cache service)
├── logging/           # Logging infrastructure
├── adapters/          # 3rd party service adapters
│   ├── document_parser/  # Can swap Docling → JigsawStack
│   ├── nlp/             # Can swap spaCy → another NLP
│   └── image/           # Can swap PIL → another library
└── src/backend/
    ├── services/      # Business logic (can become services)
    ├── routers/       # API layer
    └── schemas/       # Data contracts
```

### 2. Dependency Injection First

**Why:** Easy testing, easy service swapping, loose coupling

**Pattern:**
```python
# ❌ BAD - Tight coupling
class DocumentService:
    def __init__(self):
        self.parser = DoclingParser()  # Hard-coded dependency

# ✅ GOOD - Dependency injection
class DocumentService:
    def __init__(self, parser: DocumentParserProtocol):
        self.parser = parser  # Can inject any parser

# Usage
service = DocumentService(DoclingAdapter())
# Or swap to different provider
service = DocumentService(JigsawStackAdapter())
```

### 3. Interface-Based Design

**Why:** Easy to mock, easy to swap implementations

**Pattern:**
```python
from typing import Protocol

# Define interface
class DocumentParserProtocol(Protocol):
    async def parse(self, file_path: Path) -> ParsedDocument:
        ...

# Multiple implementations
class DoclingAdapter(DocumentParserProtocol):
    async def parse(self, file_path: Path) -> ParsedDocument:
        # Docling implementation
        ...

class JigsawStackAdapter(DocumentParserProtocol):
    async def parse(self, file_path: Path) -> ParsedDocument:
        # JigsawStack implementation
        ...
```

### 4. Async First

**Why:** Better scalability, non-blocking I/O

**Guidelines:**
- All I/O operations are async
- Use `asyncio.to_thread()` for blocking operations
- Connection pooling for databases
- Async HTTP clients

---

## SOLID Principles

### 1. Single Responsibility Principle (SRP)

**Rule:** Each class/module should have ONE reason to change

**Examples:**

```python
# ❌ BAD - Multiple responsibilities
class DocumentService:
    def parse_document(self): ...
    def validate_format(self): ...
    def detect_ai_images(self): ...
    def calculate_risk(self): ...
    def send_email_alert(self): ...

# ✅ GOOD - Single responsibility each
class DocumentParser:
    def parse(self): ...

class DocumentValidator:
    def validate_format(self): ...

class ImageAnalyzer:
    def detect_ai_generation(self): ...

class RiskCalculator:
    def calculate_risk(self): ...

class AlertNotifier:
    def send_alert(self): ...
```

### 2. Open/Closed Principle (OCP)

**Rule:** Open for extension, closed for modification

**Example:**

```python
# ❌ BAD - Need to modify for new cache type
class CacheManager:
    def __init__(self, cache_type: str):
        if cache_type == "redis":
            self.cache = RedisCache()
        elif cache_type == "memcached":
            self.cache = MemcachedCache()
        # Need to modify this for new types

# ✅ GOOD - Extend without modification
class CacheManager:
    def __init__(self, backend: CacheBackend):
        self.backend = backend  # Accept any CacheBackend

# Add new backend without changing CacheManager
class SupabaseCache(CacheBackend):
    ...
```

### 3. Liskov Substitution Principle (LSP)

**Rule:** Subtypes must be substitutable for their base types

**Example:**

```python
# ✅ GOOD - All implementations are interchangeable
def process_document(parser: DocumentParserProtocol):
    result = await parser.parse(file_path)
    return result

# All these work the same way
process_document(DoclingAdapter())
process_document(JigsawStackAdapter())
process_document(PyPDF2Adapter())
```

### 4. Interface Segregation Principle (ISP)

**Rule:** Clients should not depend on interfaces they don't use

**Example:**

```python
# ❌ BAD - Fat interface
class DataStore(Protocol):
    async def read(self): ...
    async def write(self): ...
    async def cache(self): ...
    async def search(self): ...
    async def index(self): ...

# ✅ GOOD - Segregated interfaces
class Readable(Protocol):
    async def read(self): ...

class Writable(Protocol):
    async def write(self): ...

class Cacheable(Protocol):
    async def cache(self): ...
```

### 5. Dependency Inversion Principle (DIP)

**Rule:** Depend on abstractions, not concretions

**Example:**

```python
# ❌ BAD - Depends on concrete class
class CorroborationService:
    def __init__(self):
        self.docling = DoclingParser()  # Concrete dependency

# ✅ GOOD - Depends on abstraction
class CorroborationService:
    def __init__(self, parser: DocumentParserProtocol):
        self.parser = parser  # Abstract dependency
```

---

## Design Patterns

### 1. Adapter Pattern (PRIMARY)

**Use Case:** Wrap 3rd party libraries to enable easy swapping

**Implementation:**

```python
# 1. Define interface
class DocumentParserProtocol(Protocol):
    async def parse(self, file: Path) -> ParsedDocument:
        ...

# 2. Create adapters for each library
class DoclingAdapter(DocumentParserProtocol):
    def __init__(self):
        self._converter = DocumentConverter()

    async def parse(self, file: Path) -> ParsedDocument:
        result = await asyncio.to_thread(self._converter.convert, str(file))
        return self._convert_to_parsed_document(result)

class JigsawStackAdapter(DocumentParserProtocol):
    def __init__(self, api_key: str):
        self._client = JigsawStackClient(api_key)

    async def parse(self, file: Path) -> ParsedDocument:
        result = await self._client.parse(file)
        return self._convert_to_parsed_document(result)

# 3. Use through interface
class DocumentService:
    def __init__(self, parser: DocumentParserProtocol):
        self.parser = parser

    async def process(self, file: Path):
        return await self.parser.parse(file)
```

### 2. Strategy Pattern

**Use Case:** Interchangeable algorithms (risk scoring, validation rules)

**Implementation:**

```python
class RiskScoringStrategy(Protocol):
    def calculate(self, data: dict) -> float:
        ...

class ConservativeScoring(RiskScoringStrategy):
    def calculate(self, data: dict) -> float:
        # More strict scoring
        return score * 1.5

class StandardScoring(RiskScoringStrategy):
    def calculate(self, data: dict) -> float:
        # Normal scoring
        return score

class RiskCalculator:
    def __init__(self, strategy: RiskScoringStrategy):
        self.strategy = strategy

    def calculate_risk(self, document: Document):
        return self.strategy.calculate(document.data)
```

### 3. Factory Pattern

**Use Case:** Create appropriate adapters/services

**Implementation:**

```python
class AdapterFactory:
    @staticmethod
    def create_document_parser(provider: str) -> DocumentParserProtocol:
        if provider == "docling":
            return DoclingAdapter()
        elif provider == "jigsawstack":
            return JigsawStackAdapter(api_key=settings.JIGSAWSTACK_KEY)
        elif provider == "pypdf2":
            return PyPDF2Adapter()
        else:
            raise ValueError(f"Unknown provider: {provider}")
```

### 4. Repository Pattern

**Use Case:** Abstract database operations

**Implementation:**

```python
class ClientRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, client_id: UUID) -> Optional[Client]:
        result = await self.db.execute(
            select(Client).where(Client.id == client_id)
        )
        return result.scalar_one_or_none()

    async def create(self, client: Client) -> Client:
        self.db.add(client)
        await self.db.commit()
        await self.db.refresh(client)
        return client
```

### 5. Dependency Injection Container

**Use Case:** Centralized dependency management

**Implementation:**

```python
class Container:
    """DI container for managing dependencies."""

    def __init__(self):
        self._document_parser = None
        self._nlp_processor = None
        self._image_processor = None
        self._cache = None

    @property
    def document_parser(self) -> DocumentParserProtocol:
        if self._document_parser is None:
            self._document_parser = DoclingAdapter()
        return self._document_parser

    @document_parser.setter
    def document_parser(self, parser: DocumentParserProtocol):
        self._document_parser = parser

# Global container
container = Container()

# Swap implementations at startup
container.document_parser = JigsawStackAdapter()

# Services use container
class DocumentService:
    def __init__(self):
        self.parser = container.document_parser
```

---

## Code Organization

### Module Structure

```
backend/
├── adapters/           # 3rd party wrappers
│   ├── __init__.py
│   ├── base.py        # Protocol definitions
│   ├── document_parser/
│   │   ├── __init__.py
│   │   ├── protocol.py
│   │   ├── docling.py
│   │   └── jigsawstack.py
│   ├── nlp/
│   │   ├── protocol.py
│   │   ├── spacy.py
│   │   └── openai.py
│   └── image/
│       ├── protocol.py
│       └── pillow.py
├── domain/             # Business logic (domain-driven design)
│   ├── models/        # Domain models
│   ├── services/      # Domain services
│   └── repositories/  # Data access
├── infrastructure/     # Technical concerns
│   ├── database/
│   ├── cache/
│   └── logging/
└── api/               # HTTP layer
    ├── routers/
    ├── schemas/
    └── dependencies/  # FastAPI dependencies
```

### File Naming Conventions

- **Protocols/Interfaces:** `*_protocol.py` or `base.py`
- **Implementations:** Descriptive names (e.g., `docling_adapter.py`)
- **Services:** `*_service.py`
- **Repositories:** `*_repository.py`
- **Schemas:** `*_schema.py`
- **Tests:** `test_*.py`

### Import Organization

```python
# 1. Standard library
import asyncio
from pathlib import Path
from typing import Optional, Protocol

# 2. Third-party
from fastapi import APIRouter, Depends
from sqlalchemy import select

# 3. Local - absolute imports
from backend.adapters.document_parser import DocumentParserProtocol
from backend.domain.services import DocumentService
from backend.infrastructure.cache import cached

# Avoid relative imports for better module independence
```

---

## Testing Strategy

### Test Pyramid

```
        E2E Tests (5%)
       /            \
  Integration Tests (15%)
    /                    \
  Unit Tests (80%)
```

### Unit Testing

**Focus:** Individual components in isolation

```python
import pytest
from unittest.mock import AsyncMock
from backend.domain.services import DocumentService

@pytest.mark.asyncio
async def test_document_parsing():
    # Arrange - Mock dependencies
    mock_parser = AsyncMock(spec=DocumentParserProtocol)
    mock_parser.parse.return_value = ParsedDocument(text="test")

    service = DocumentService(parser=mock_parser)

    # Act
    result = await service.parse_document(Path("test.pdf"))

    # Assert
    assert result.text == "test"
    mock_parser.parse.assert_called_once()
```

### Integration Testing

**Focus:** Multiple components working together

```python
@pytest.mark.asyncio
async def test_document_flow_with_real_cache():
    # Use real cache but mocked parser
    cache = MemoryBackend()
    await cache.connect()

    mock_parser = AsyncMock()
    service = DocumentService(parser=mock_parser, cache=cache)

    # Test cache behavior
    await service.parse_document(Path("test.pdf"))
    await service.parse_document(Path("test.pdf"))

    # Parser should only be called once (second call cached)
    assert mock_parser.parse.call_count == 1
```

### E2E Testing

**Focus:** Full user flows

```python
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_full_document_upload_flow():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Upload document
        files = {"file": ("test.pdf", pdf_content, "application/pdf")}
        response = await client.post("/api/v1/documents/parse", files=files)

        assert response.status_code == 200
        assert "text" in response.json()
```

### Test Fixtures

```python
# conftest.py
@pytest.fixture
async def db_session():
    """Provide database session for tests."""
    async with async_session_maker() as session:
        yield session
        await session.rollback()

@pytest.fixture
async def cache():
    """Provide in-memory cache for tests."""
    cache = MemoryBackend()
    await cache.connect()
    yield cache
    await cache.close()

@pytest.fixture
def mock_parser():
    """Provide mocked document parser."""
    return AsyncMock(spec=DocumentParserProtocol)
```

---

## Performance Guidelines

### 1. Async Operations

```python
# ✅ GOOD - Parallel async operations
async def process_documents(files: List[Path]):
    tasks = [parse_document(f) for f in files]
    results = await asyncio.gather(*tasks)
    return results

# ❌ BAD - Sequential processing
async def process_documents(files: List[Path]):
    results = []
    for f in files:
        result = await parse_document(f)  # Waits for each
        results.append(result)
    return results
```

### 2. Blocking Operations

```python
# ✅ GOOD - Run blocking ops in thread pool
async def parse_pdf(file_path: Path):
    result = await asyncio.to_thread(
        blocking_pdf_parser.parse,  # Blocking call
        file_path
    )
    return result

# ❌ BAD - Blocking the event loop
async def parse_pdf(file_path: Path):
    result = blocking_pdf_parser.parse(file_path)  # Blocks!
    return result
```

### 3. Database Queries

```python
# ✅ GOOD - Eager loading with joinedload
async def get_client_with_documents(client_id: UUID):
    result = await db.execute(
        select(Client)
        .options(joinedload(Client.documents))
        .where(Client.id == client_id)
    )
    return result.scalar_one()

# ❌ BAD - N+1 query problem
async def get_client_with_documents(client_id: UUID):
    client = await db.get(Client, client_id)
    for doc in client.documents:  # Triggers N queries
        print(doc.filename)
```

### 4. Caching Strategy

```python
# Cache expensive operations
@cached(ttl=86400, key_prefix="document")
async def parse_large_document(file_hash: str):
    # Only parsed once per file hash
    return await expensive_parsing()

# Cache database queries
@cached(ttl=300, key_prefix="client")
async def get_client_summary(client_id: str):
    return await db.query(...)
```

### 5. Connection Pooling

```python
# Database: 20 connections, 10 overflow
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
)

# Redis: 50 max connections
redis = await aioredis.from_url(
    REDIS_URL,
    max_connections=50,
)
```

---

## Security Principles

### 1. Input Validation

```python
from pydantic import BaseModel, validator, Field

class DocumentUpload(BaseModel):
    file_size: int = Field(..., gt=0, le=10485760)  # Max 10MB

    @validator("file_size")
    def validate_size(cls, v):
        if v > 10 * 1024 * 1024:
            raise ValueError("File too large")
        return v
```

### 2. SQL Injection Prevention

```python
# ✅ GOOD - Parameterized queries
result = await db.execute(
    select(Client).where(Client.id == client_id)
)

# ❌ BAD - String interpolation
query = f"SELECT * FROM clients WHERE id = '{client_id}'"
```

### 3. Secrets Management

```python
# ✅ GOOD - Environment variables
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    API_KEY: str

    class Config:
        env_file = ".env"

# ❌ BAD - Hard-coded secrets
DATABASE_URL = "postgresql://user:password@localhost/db"
```

### 4. File Upload Security

```python
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".docx"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

async def validate_upload(file: UploadFile):
    # Check extension
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError("Invalid file type")

    # Check size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise ValueError("File too large")

    # Check content type (not just extension)
    if not content.startswith(b"%PDF") and ext == ".pdf":
        raise ValueError("Invalid PDF file")
```

---

## API Design

### RESTful Conventions

```python
# ✅ GOOD - RESTful routes
POST   /api/v1/clients                    # Create
GET    /api/v1/clients/{id}              # Read one
GET    /api/v1/clients                    # Read all
PUT    /api/v1/clients/{id}              # Update (full)
PATCH  /api/v1/clients/{id}              # Update (partial)
DELETE /api/v1/clients/{id}              # Delete

# Nested resources
GET    /api/v1/clients/{id}/documents
POST   /api/v1/clients/{id}/documents

# Actions (when not CRUD)
POST   /api/v1/alerts/{id}/acknowledge
POST   /api/v1/documents/{id}/reprocess
```

### Response Format

```python
# Success response
{
    "data": {...},
    "message": "Document parsed successfully",
    "timestamp": "2025-01-15T10:30:00Z"
}

# Error response
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid file format",
        "details": ["File must be PDF or DOCX"]
    },
    "timestamp": "2025-01-15T10:30:00Z"
}
```

### Pagination

```python
@router.get("/clients")
async def list_clients(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    offset = (page - 1) * page_size
    clients = await db.execute(
        select(Client)
        .offset(offset)
        .limit(page_size)
    )
    return {
        "data": clients.scalars().all(),
        "page": page,
        "page_size": page_size,
        "total": total_count,
    }
```

### Versioning

```python
# Version in URL
app.include_router(router, prefix="/api/v1")

# Or version in header
@router.get("/clients")
async def list_clients(
    api_version: str = Header("1.0", alias="X-API-Version")
):
    if api_version == "1.0":
        # Old format
    elif api_version == "2.0":
        # New format
```

---

## Error Handling

### Exception Hierarchy

```python
class SpeedRunException(Exception):
    """Base exception for all application errors."""
    pass

class ValidationError(SpeedRunException):
    """Invalid input data."""
    pass

class NotFoundError(SpeedRunException):
    """Resource not found."""
    pass

class ServiceUnavailableError(SpeedRunException):
    """External service unavailable."""
    pass
```

### Error Handling Middleware

```python
@app.exception_handler(SpeedRunException)
async def handle_app_exception(request, exc):
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": type(exc).__name__,
                "message": str(exc),
            }
        }
    )
```

### Try-Except Patterns

```python
# ✅ GOOD - Specific exceptions
try:
    result = await parse_document(file)
except FileNotFoundError:
    logger.error(f"File not found: {file}")
    raise NotFoundError(f"Document not found: {file}")
except DoclingException as e:
    logger.error(f"Parsing failed: {e}")
    raise ServiceUnavailableError("Document parsing service unavailable")

# ❌ BAD - Bare except
try:
    result = await parse_document(file)
except:
    pass  # Silent failures
```

---

## Logging & Observability

### Structured Logging

```python
import structlog

logger = structlog.get_logger(__name__)

# ✅ GOOD - Structured logs
logger.info(
    "document_parsed",
    document_id=doc_id,
    file_size=file.size,
    processing_time_ms=elapsed,
    user_id=user_id,
)

# ❌ BAD - Unstructured logs
logger.info(f"Parsed document {doc_id} in {elapsed}ms")
```

### Log Levels

- **DEBUG**: Detailed diagnostic info (cache hits, query plans)
- **INFO**: General info (API calls, successful operations)
- **WARNING**: Warning messages (fallback to cache, retries)
- **ERROR**: Error messages (failed operations, exceptions)
- **AUDIT**: Compliance-critical events (KYC actions, risk decisions)

### Audit Trail

```python
from backend.logging import audit_logger

await audit_logger.log(
    event_type="document_uploaded",
    entity_type="DOCUMENT",
    entity_id=document.id,
    user_id=current_user.id,
    user_role=current_user.role,
    action="UPLOAD",
    before_state=None,
    after_state={"filename": document.filename},
    ip_address=request.client.host,
)
```

### Correlation IDs

```python
# Add correlation ID to all requests
@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid4()))
    structlog.contextvars.bind_contextvars(correlation_id=correlation_id)

    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    return response
```

---

## Documentation Standards

### Code Documentation

```python
def calculate_risk_score(
    document: Document,
    weights: RiskWeights,
) -> RiskScore:
    """
    Calculate risk score for a document.

    This function computes a weighted risk score based on multiple
    validation results (format, structure, content, image analysis).

    Args:
        document: Document to analyze
        weights: Risk calculation weights

    Returns:
        RiskScore with total score (0-100) and risk level

    Raises:
        ValidationError: If document has no validation results
        ValueError: If weights don't sum to 1.0

    Example:
        >>> weights = RiskWeights(format=0.2, structure=0.3, content=0.5)
        >>> score = calculate_risk_score(document, weights)
        >>> assert 0 <= score.total_score <= 100
    """
```

### API Documentation

```python
@router.post(
    "/documents/parse",
    response_model=DocumentParseResponse,
    summary="Parse document and extract text",
    description="""
    Parse a document (PDF, DOCX) and extract:
    - Full text content
    - Tables
    - Metadata
    - Page-by-page breakdown

    Supports caching based on file hash.
    """,
    responses={
        200: {"description": "Document parsed successfully"},
        400: {"description": "Invalid file format"},
        413: {"description": "File too large"},
    }
)
async def parse_document(file: UploadFile):
    ...
```

---

**Status:** Active Reference Document
**Maintained By:** Speed-Run Team
**Review Cycle:** Weekly during active development
