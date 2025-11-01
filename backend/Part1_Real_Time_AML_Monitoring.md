# Part 1 · Real-Time AML Monitoring & Alerts

## Mission
Deliver an agentic monitoring layer that ingests regulatory guidance and internal policies, tags relevant clauses, and evaluates client activity in real time to surface actionable AML alerts with defensible audit history.

## Functional Scope
- Ingest external circulars and internal policy updates with metadata (regulator, jurisdiction, effective date, version history).
- Translate unstructured guidance into machine-readable monitoring rules and risk indicators.
- Execute streaming or scheduled transaction evaluations against the active rule book.
- Produce role-specific alert payloads (Front Office, Compliance, Legal) with contextual evidence and recommended next actions.
- Maintain full audit trails, including rule provenance, alert lifecycle, and user actions.

## Subsystem Requirements

### Regulatory Ingestion Engine
- Core: continuously pull circulars and policy updates across MAS, FINMA, HKMA, and internal sources with configurable polling cadence.
- Core: normalize inbound artefacts with standard metadata (jurisdiction, business line, effective/expiry dates, regulatory references).
- Core: persist source documents and extracted clauses with immutable version history for audit replay.
- Detailed: auto-classify obligations by risk theme and map them to impacted products, channels, and customer archetypes.
- Detailed: support human-in-the-loop review queue with diff view for clause changes and approval workflows before activation.
- Detailed: expose change events via webhook and message bus to downstream rule-management services.

### Transaction Analysis Engine
- Core: evaluate live and batch transactions against active rules with sub-second latency targets for high-risk scenarios.
- Core: incorporate KYC data, historical behaviour statistics, sanctions lists, and external risk scores into each evaluation.
- Core: produce explainable scoring outputs, including triggered conditions, contributing features, and confidence scores.
- Detailed: maintain adaptive baselines per client, segment, and geography with automated drift monitoring and retraining hooks.
- Detailed: support scenario simulation and backtesting to validate rules before production rollout.
- Detailed: capture full transaction payload snapshots and feature vectors for audit, retraining, and lineage tracking.

### Alert System
- Core: publish alerts with severity tiers, channel routing rules, and SLA timers aligned to user role (Front, Compliance, Legal).
- Core: attach contextual artefacts (triggered regulations, related transactions, client profile, risk narrative) to every alert.
- Core: expose REST and WebSocket interfaces for downstream dashboards and notification pipelines.
- Detailed: implement deduplication, suppression, and correlation logic to group related alerts and minimize noise.
- Detailed: integrate with messaging tools (email, Teams/Slack) and case systems via pluggable notification adapters.
- Detailed: track end-to-end lifecycle timestamps (created, acknowledged, escalated, closed) for operational analytics.

### Remediation Workflows & Audit Service
- Core: provide configurable workflow templates per alert type with required tasks, documentation checklists, and approval gates.
- Core: record every user action, decision, and attached evidence into an immutable audit log with tamper detection.
- Core: expose dashboards summarizing remediation progress, overdue tasks, and SLA breaches.
- Detailed: embed AI-generated playbooks suggesting next-best-actions, escalation contacts, and regulatory references.
- Detailed: support automated control execution (e.g., transaction block, enhanced due diligence request) via API integrations.
- Detailed: enable regulatory reporting exports (PDF/CSV) with full chronology, evidence links, and responsible parties.

## Key User Journeys
1. **Compliance Analyst** subscribes to new FINMA circular → system parses obligations → analyst approves generated rules → rules go live with change log.
2. **Transaction Monitor** detects unusual velocity on a client account → risk score exceeds tier threshold → Compliance receives high-priority alert with regulator references and suggested remediation workflow.
3. **Front Officer** receives medium-risk alert → reviews summarized rationale and recommended outreach template → logs disposition, which updates the audit trail.

## Automation & AI Components
- Natural language processing to classify regulatory clauses and extract conditions.
- Rule synthesis agent that proposes monitoring logic with confidence scores.
- Transaction scoring pipeline combining statistical baselines, machine learning models, and rule-based overrides.
- Alert summarization agent that translates technical findings into business-context narratives.

## Data & Integration Requirements
- Regulatory data lake or document repository with versioned storage.
- Transaction stream or batch ingestion supporting SWIFT, screening flags, KYC attributes, and behavioral statistics.
- Integration hooks for case management or ticketing systems (e.g., ServiceNow, Jira) and secure messaging channels.

## Deliverables & Acceptance Criteria
- [ ] Automated regulatory ingestion with traceable rule derivation and approval workflow.
- [ ] Configurable rules engine that can run against the supplied `transactions_mock_1000_for_participants.csv` and live feeds.
- [ ] Alerting fabric with priority tiers, role routing, and acknowledgment tracking.
- [ ] Remediation workflow templates with automated suggestions and escalation paths.
- [ ] Immutable audit log summarizing rules, alerts, dispositions, and user actions.

## Success Metrics
- Time from new regulatory circular upload to activated monitoring rule (< 2 hours target).
- Percentage of alerts acknowledged within SLA thresholds (e.g., 95% of high-priority alerts in 30 minutes).
- Precision/recall on labeled suspicious transaction scenarios from historical data.
- Audit readiness score (completeness of evidence captured per alert).

## Stretch Opportunities
- Adaptive learning loop that prioritizes rule tuning based on analyst feedback.
- Explainability dashboards that visualize risk score contributions.
- Simulation sandbox to replay past regulatory scenarios against current rule sets.
