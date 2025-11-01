# Challenge Delivery Cross-Check

Validation of implemented features against the Julius Baer AML challenge requirements. Status legend: ✅ Completed · ⚠️ Partial / Mocked · ⛔ Missing.

## Part 1 – Real-Time AML Monitoring & Alerts

- ⚠️ **Regulatory ingestion engine** — No crawler or rule parser exists; alert data is hard-coded in `services/mock_data.py:8-215`, so regulations cannot be ingested or versioned.
- ⚠️ **Transaction analysis engine** — Endpoints expose mock statistics only (`api/routes/alerts.py:12-40`, `api/routes/transactions.py:12-24`); `agents/orchestrator.py:16-104` defines analysis logic but nothing invokes it.
- ⚠️ **Alerting system with role routing & prioritisation** — REST endpoints return static alerts and the remediation call just echoes success (`api/routes/alerts.py:33-40`); WebSocket channel exists but only performs echo tests (`api/routes/websocket.py:52-120`) and is never triggered.
- ⛔ **Remediation workflows & audit trail integration** — No workflow state or persistence; the remediation endpoint does not change data, and audit logs are fixed samples (`api/routes/audit.py:1-35`).
- ⛔ **Persistent data store / rule approval history** — Database service is a no-op mock (`services/database.py:11-30`); no connection to the provided transaction CSV.

## Part 2 – Document & Image Corroboration

- ✅ **Document processing engine** — `DocumentService` wraps Docling for multi-format parsing (`src/backend/services/document_service.py:40-152`), though it writes extracted text to a hard-coded `test.md`.
- ✅ **Format / structure / content validation** — Implemented in `DocumentValidator` with spaCy-powered checks (`src/backend/services/document_validator.py:18-207`).
- ⚠️ **Image authenticity analysis** — Heuristic forensics pipeline exists (`src/backend/services/image_analyzer.py:19-420`), but reverse image search is a stub returning `0` matches (`src/backend/services/image_analyzer.py:326-341`).
- ✅ **Risk scoring & reporting** — `RiskScorer` aggregates validation results (`src/backend/services/risk_scorer.py:1-399`) and `ReportGenerator` produces reports & audit logs under `/tmp` (`src/backend/services/report_generator.py:15-218`).
- ✅ **API coverage** — FastAPI routers expose analysis, validation-only, retrieval, and health endpoints (`src/backend/routers/corroboration.py:20-316`).
- ⚠️ **Operational readiness** — Dependencies rely on Docling and spaCy; `requirements.txt` still has unresolved conflict markers (`requirements.txt:1-46`) which blocks installation.

## Integration Layer

- ⛔ **Unified platform** — Two separate FastAPI apps exist (`main.py:1-86` for alerts, `src/backend/main.py:1-68` for corroboration) with no shared execution path or data model.
- ⛔ **Cross-referencing alerts & documents** — Alert details embed static document issues (`services/mock_data.py:150-215`); no runtime linkage to generated corroboration reports.
- ⛔ **Event-driven workflows & shared audit trails** — No message bus, orchestration, or combined case records; `ReportGenerator` writes to local disk while alert audit trail remains mock data.
- ⚠️ **Realtime surface** — WebSocket infrastructure is in place but disconnected from analysis outputs (`api/routes/websocket.py:52-120`).

## Additional Observations

- ⚠️ **Agent scripts outside the API boundary** — Standalone CLI utilities (`ai_image_detector.py:1-37`, `reverse_image_search.py:1-41`) prompt for input on import and contain hard-coded API keys; they are unusable in the current backend.
- ⚠️ **Side effects during parsing** — `DocumentService.save_markdown_to_file` always writes to `test.md`, which may clobber data during concurrent analyses (`src/backend/services/document_service.py:58-123`).
- ⚠️ **Missing dependency pinning for Core AML app** — `pyproject.toml` targets the Docling service only; the monitoring APIs lack equivalent dependency definitions.
