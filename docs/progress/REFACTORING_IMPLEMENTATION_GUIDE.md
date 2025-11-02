# Backend Refactoring Implementation Guide
## Step-by-Step Instructions for Completing the Refactoring

> **Status:** Phase 1 (Database) completed. This guide covers Phases 2-6.
> **Created:** 2025-01-15
> **Purpose:** Provide detailed instructions for continuing the backend refactoring

---

## What's Been Completed ✅

### Phase 1: Database Infrastructure (33% of Phase 1)

**Files Created:**
1. `backend/database/models.py` - 10 SQLAlchemy models (650 lines)
2. `backend/database/connection.py` - Async connection pooling (150 lines)
3. `backend/database/session.py` - Session management (110 lines)
4. `backend/database/schema.sql` - Raw SQL schema (345 lines)
5. `backend/database/__init__.py` - Package initialization
6. `backend/docker-compose.yml` - PostgreSQL + Redis containers
7. `backend/src/backend/config.py` - Database & Redis settings added

**Database Models:**
- Client, Document, DocumentValidation, Image, RiskScore
- Alert, AlertRecipient, Transaction, AuditLog, Report

**What You Can Do Now:**
```bash
# Start database and Redis
cd backend
docker-compose up -d

# Verify
docker-compose ps
psql -U speedrun -d speedrun_aml -h localhost
```

---

## Quick Start: Run the Database

```bash
# 1. Start infrastructure
cd /Users/issacj/Desktop/hackathons/Singhacks/Speed-Run/backend
docker-compose up -d

# 2. Verify PostgreSQL
docker exec -it speedrun-postgres psql -U speedrun -d speedrun_aml
# Run: \dt   (list tables)
# Run: \q    (quit)

# 3. Verify Redis
docker exec -it speedrun-redis redis-cli ping
# Should return: PONG

# 4. Optional: Access pgAdmin
# Open browser: http://localhost:5050
# Login: admin@speedrun.com / admin
```

---

## Phase 1 Remaining Tasks

### Task 1.2: Redis Cache Layer

**Files to Create:**

#### 1. `backend/cache/__init__.py`
```python
"""
Redis cache layer for Speed-Run AML Platform.
"""

from .redis_client import redis_client, init_redis, close_redis
from .cache_decorator import cached
from .cache_keys import CacheKeyGenerator

__all__ = [
    "redis_client",
    "init_redis",
    "close_redis",
    "cached",
    "CacheKeyGenerator",
]
```

#### 2. `backend/cache/redis_client.py`
```python
"""
Redis connection management.
"""

import logging
from typing import Optional

import redis.asyncio as aioredis
from redis.asyncio import Redis

from ..src/backend.config import settings

logger = logging.getLogger(__name__)

# Global Redis client
redis_client: Optional[Redis] = None


async def init_redis() -> Redis:
    """
    Initialize Redis connection.

    Returns:
        Redis: Async Redis client
    """
    global redis_client

    if redis_client is None:
        redis_client = await aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
            socket_connect_timeout=settings.REDIS_SOCKET_CONNECT_TIMEOUT,
        )
        logger.info("Redis client initialized")

    return redis_client


async def close_redis() -> None:
    """Close Redis connection."""
    global redis_client

    if redis_client is not None:
        await redis_client.close()
        redis_client = None
        logger.info("Redis connection closed")


async def check_redis_health() -> bool:
    """
    Check Redis health.

    Returns:
        bool: True if Redis is healthy
    """
    if redis_client is None:
        return False

    try:
        await redis_client.ping()
        return True
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return False


__all__ = ["redis_client", "init_redis", "close_redis", "check_redis_health"]
```

#### 3. `backend/cache/cache_keys.py`
```python
"""
Cache key generation utilities.
"""

import hashlib
from typing import Any


class CacheKeyGenerator:
    """Generate consistent cache keys."""

    @staticmethod
    def document_parse(file_hash: str) -> str:
        """Key for document parsing results."""
        return f"document:parse:{file_hash}"

    @staticmethod
    def ocr_extract(image_hash: str) -> str:
        """Key for OCR extraction results."""
        return f"ocr:extract:{image_hash}"

    @staticmethod
    def image_analysis(image_hash: str) -> str:
        """Key for image analysis results."""
        return f"image:analysis:{image_hash}"

    @staticmethod
    def validation(document_hash: str, validation_type: str) -> str:
        """Key for validation results."""
        return f"validation:{validation_type}:{document_hash}"

    @staticmethod
    def compute_file_hash(content: bytes) -> str:
        """
        Compute SHA-256 hash of file content.

        Args:
            content: File content as bytes

        Returns:
            str: Hex digest of SHA-256 hash
        """
        return hashlib.sha256(content).hexdigest()


__all__ = ["CacheKeyGenerator"]
```

#### 4. `backend/cache/cache_decorator.py`
```python
"""
Cache decorator for expensive operations.
"""

import functools
import json
import logging
from typing import Any, Callable, Optional

from .redis_client import redis_client
from ..src/backend.config import settings

logger = logging.getLogger(__name__)


def cached(
    ttl: Optional[int] = None,
    key_prefix: str = "",
    enabled: bool = None,
):
    """
    Decorator to cache function results in Redis.

    Args:
        ttl: Time to live in seconds (default from settings)
        key_prefix: Prefix for cache key
        enabled: Whether caching is enabled (default from settings)

    Usage:
        @cached(ttl=3600, key_prefix="document")
        async def parse_document(file_hash: str):
            ...
    """
    if enabled is None:
        enabled = settings.CACHE_ENABLED

    if ttl is None:
        ttl = settings.CACHE_DEFAULT_TTL

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # If caching disabled, just call function
            if not enabled or redis_client is None:
                return await func(*args, **kwargs)

            # Generate cache key from function name and arguments
            key_parts = [key_prefix, func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = ":".join(key_parts)

            # Try to get from cache
            try:
                cached_value = await redis_client.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"Cache hit: {cache_key}")
                    return json.loads(cached_value)
            except Exception as e:
                logger.warning(f"Cache read error: {e}")

            # Cache miss - compute value
            logger.debug(f"Cache miss: {cache_key}")
            result = await func(*args, **kwargs)

            # Store in cache
            try:
                await redis_client.setex(
                    cache_key,
                    ttl,
                    json.dumps(result, default=str),
                )
                logger.debug(f"Cached result: {cache_key} (TTL: {ttl}s)")
            except Exception as e:
                logger.warning(f"Cache write error: {e}")

            return result

        return wrapper

    return decorator


__all__ = ["cached"]
```

**To Use Cache:**
```python
# In document_service.py
from cache import cached, CacheKeyGenerator

class DocumentService:
    @cached(ttl=86400, key_prefix="document")
    async def parse_document(self, file_hash: str, file_path: Path):
        # Only parsed once per file hash
        ...
```

**Dependencies to Add:**
```bash
pip install redis[hiredis]
```

---

### Task 1.3: Logging & Audit Trail

**Files to Create:**

#### 1. `backend/logging/config.py`
```python
"""
Structured logging configuration.
"""

import logging
import sys
from pathlib import Path

import structlog


def configure_logging(level: str = "INFO", log_file: Path = None):
    """
    Configure structured logging with structlog.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional file path for logs
    """
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper()),
    )

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),  # JSON output
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


__all__ = ["configure_logging"]
```

#### 2. `backend/logging/audit_logger.py`
```python
"""
Audit logging for compliance.
"""

import logging
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

import structlog

logger = structlog.get_logger(__name__)


class AuditLogger:
    """
    Specialized logger for audit trail.

    Logs all compliance-critical events with full context.
    """

    @staticmethod
    async def log(
        event_type: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        user_role: Optional[str] = None,
        action: Optional[str] = None,
        before_state: Optional[dict] = None,
        after_state: Optional[dict] = None,
        **kwargs,
    ):
        """
        Log audit event.

        Args:
            event_type: Type of event (e.g., "document_uploaded")
            entity_type: Type of entity (e.g., "DOCUMENT")
            entity_id: ID of entity
            user_id: User who performed action
            user_role: Role of user
            action: Action performed
            before_state: State before action
            after_state: State after action
            **kwargs: Additional context
        """
        logger.info(
            event_type,
            severity="AUDIT",
            timestamp=datetime.utcnow().isoformat(),
            entity_type=entity_type,
            entity_id=str(entity_id) if entity_id else None,
            user_id=str(user_id) if user_id else None,
            user_role=user_role,
            action=action,
            before_state=before_state,
            after_state=after_state,
            **kwargs,
        )


audit_logger = AuditLogger()

__all__ = ["AuditLogger", "audit_logger"]
```

#### 3. `backend/middleware/logging_middleware.py`
```python
"""
FastAPI middleware for request/response logging.
"""

import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

logger = structlog.get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Log all HTTP requests and responses with correlation ID.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Log request
        logger.info(
            "request_started",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            query_params=dict(request.query_params),
            client_ip=request.client.host if request.client else None,
        )

        # Process request
        start_time = time.time()
        try:
            response = await call_next(request)
            duration = time.time() - start_time

            # Log response
            logger.info(
                "request_completed",
                request_id=request_id,
                status_code=response.status_code,
                duration_ms=round(duration * 1000, 2),
            )

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            return response

        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                "request_failed",
                request_id=request_id,
                error=str(e),
                duration_ms=round(duration * 1000, 2),
                exc_info=True,
            )
            raise


__all__ = ["LoggingMiddleware"]
```

**To Use Logging:**
```python
# In main.py
from logging.config import configure_logging
from middleware.logging_middleware import LoggingMiddleware

# Configure logging
configure_logging(level="INFO")

# Add middleware
app.add_middleware(LoggingMiddleware)

# In services
import structlog
logger = structlog.get_logger(__name__)

logger.info("document_analyzed", document_id=doc_id, risk_score=score)
```

**Dependencies to Add:**
```bash
pip install structlog python-json-logger
```

---

## Phase 2: Adapter Pattern (Weeks 2)

### Task 2.1: Document Parser Adapter

**Goal:** Abstract Docling so it can be swapped for JigsawStack or others.

**Create Directory Structure:**
```bash
mkdir -p backend/src/backend/adapters/document_parser
```

**Files to Create:**

#### 1. `backend/src/backend/adapters/__init__.py`
```python
"""Adapters for 3rd party services."""

__all__ = []
```

#### 2. `backend/src/backend/adapters/base.py`
```python
"""
Base protocols for all adapters.
"""

from pathlib import Path
from typing import Protocol, List, Dict, Any


class ParsedDocument:
    """Result of document parsing."""

    def __init__(
        self,
        content: str,
        metadata: Dict[str, Any],
        tables: List[Dict[str, Any]],
        images: List[str],
    ):
        self.content = content
        self.metadata = metadata
        self.tables = tables
        self.images = images


class IDocumentParser(Protocol):
    """Interface for document parsing adapters."""

    async def parse(self, file_path: Path) -> ParsedDocument:
        """Parse document and extract content."""
        ...

    async def extract_tables(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract tables from document."""
        ...


__all__ = ["ParsedDocument", "IDocumentParser"]
```

#### 3. `backend/src/backend/adapters/document_parser/docling_adapter.py`
```python
"""
Docling adapter for document parsing.
"""

import asyncio
from pathlib import Path
from typing import List, Dict, Any

from docling.document_converter import DocumentConverter
from docling.datamodel.pipeline_options import PdfPipelineOptions

from ..base import IDocumentParser, ParsedDocument


class DoclingAdapter(IDocumentParser):
    """
    Adapter for Docling document parsing library.

    Wraps Docling to implement IDocumentParser interface.
    """

    def __init__(self):
        self.pipeline_options = PdfPipelineOptions()
        self.pipeline_options.do_ocr = True
        self.converter = DocumentConverter()

    async def parse(self, file_path: Path) -> ParsedDocument:
        """
        Parse document using Docling.

        Args:
            file_path: Path to document

        Returns:
            ParsedDocument: Parsed content
        """
        # Run blocking Docling in thread pool
        result = await asyncio.to_thread(
            self.converter.convert,
            str(file_path)
        )

        # Extract content
        content = result.document.export_to_markdown()

        # Extract metadata
        metadata = {
            "pages": len(result.document.pages),
            "word_count": len(content.split()),
        }

        # Extract tables
        tables = await self.extract_tables(file_path)

        # Extract images
        images = []  # TODO: Implement image extraction

        return ParsedDocument(
            content=content,
            metadata=metadata,
            tables=tables,
            images=images,
        )

    async def extract_tables(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract tables from document."""
        result = await asyncio.to_thread(
            self.converter.convert,
            str(file_path)
        )

        tables = []
        # TODO: Implement table extraction from Docling result
        return tables


__all__ = ["DoclingAdapter"]
```

#### 4. `backend/src/backend/adapters/document_parser/jigsawstack_adapter.py`
```python
"""
JigsawStack adapter for document parsing (placeholder).
"""

from pathlib import Path
from typing import List, Dict, Any

from ..base import IDocumentParser, ParsedDocument


class JigsawStackAdapter(IDocumentParser):
    """
    Adapter for JigsawStack document parsing API.

    TODO: Implement when switching from Docling.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        # TODO: Initialize JigsawStack client

    async def parse(self, file_path: Path) -> ParsedDocument:
        """Parse document using JigsawStack API."""
        # TODO: Implement
        raise NotImplementedError("JigsawStack adapter not implemented yet")

    async def extract_tables(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract tables from document."""
        # TODO: Implement
        raise NotImplementedError("JigsawStack adapter not implemented yet")


__all__ = ["JigsawStackAdapter"]
```

**Refactor Document Service:**
```python
# In document_service.py
from adapters.base import IDocumentParser
from adapters.document_parser.docling_adapter import DoclingAdapter


class DocumentService:
    def __init__(self, parser: IDocumentParser = None):
        # Dependency injection
        self.parser = parser or DoclingAdapter()

    async def parse_document(self, file_path: Path):
        result = await self.parser.parse(file_path)
        # Use result.content, result.metadata, etc.
        return result
```

---

## Phase 2 Remaining: Repeat for NLP and Image

**Follow same pattern for:**
1. NLP Processor (spaCy → alternatives)
2. Image Processor (PIL → OpenCV)

---

## Next Steps Summary

1. **Complete Phase 1 (This Week):**
   - Finish Redis cache layer
   - Implement logging system
   - Test database with Alembic migrations

2. **Start Phase 2 (Next Week):**
   - Create adapter layer for Docling
   - Create adapter layer for spaCy
   - Create adapter layer for PIL

3. **Phase 3 (Week 3):**
   - Split large services
   - Implement DI container

For detailed continuation, see REFACTORING_PROGRESS.md for current status.

---

**Created:** 2025-01-15
**Last Updated:** 2025-01-15
**Status:** Phase 1 (33% complete)
