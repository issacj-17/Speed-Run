# ============================================================================
# Multi-stage Dockerfile for FastAPI Backend
# ============================================================================

# ============================================================================
# Stage 1: Builder
# Build dependencies and prepare the application
# ============================================================================
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast Python package management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install Python dependencies using uv
RUN uv sync --frozen --no-dev

# Download spaCy language model
RUN uv run python -m spacy download en_core_web_sm

# ============================================================================
# Stage 2: Runtime
# Create a minimal image with only runtime dependencies
# ============================================================================
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:${PATH}" \
    # Application settings
    APP_HOME=/app \
    # Ensure UTF-8 encoding
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# Set working directory
WORKDIR ${APP_HOME}

# Install runtime system dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser ${APP_HOME}

# Copy virtual environment from builder
COPY --from=builder --chown=appuser:appuser /app/.venv ${APP_HOME}/.venv

# Copy application code
COPY --chown=appuser:appuser ./src ./src
COPY --chown=appuser:appuser ./tests ./tests
COPY --chown=appuser:appuser ./pyproject.toml ./
COPY --chown=appuser:appuser ./.env.example ./.env.example

# Create necessary directories
RUN mkdir -p /tmp/uploads /tmp/corroboration_audit && \
    chown -R appuser:appuser /tmp/uploads /tmp/corroboration_audit

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command (can be overridden in docker-compose.yml)
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
