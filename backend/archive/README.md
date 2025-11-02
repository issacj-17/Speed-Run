# Backend Archive

This directory contains archived code and documentation from previous implementations.

## Directory Structure

### `old_implementation/`
Contains the original implementation before the refactoring to `src/backend/`:

- **agents/** - Original multi-agent system (orchestrator, document_forensics, transaction_analyst, regulatory_watcher)
- **api/** - Original API routes (alerts, audit, transactions, websocket)
- **models/** - Original database models and schemas
- **services/** - Original service implementations (database, mock_data)
- **main.py** - Original FastAPI application entry point
- **ai_image_detector.py** - Standalone AI image detection script
- **reverse_image_search.py** - Standalone reverse image search functionality
- **image_analysis.py** - Original image analysis implementation

## Why Archived?

These files were part of the initial implementation and have been superseded by the current structure in `src/backend/`. They are kept here for reference and potential future use.

## Current Implementation

The active codebase is now located in:
- `src/backend/` - Main application code
- `tests/` - Test suite (369 tests passing)

See the main [README.md](../README.md) for information about the current implementation.
