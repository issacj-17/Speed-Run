-- Speed-Run AML Platform Database Schema
-- PostgreSQL 15+
--
-- This schema defines all tables for the AML compliance platform.
-- Run this file to initialize a fresh database.
--
-- Usage: psql -U speedrun -d speedrun_aml -f schema.sql

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable CIDR/INET types
CREATE EXTENSION IF NOT EXISTS "cidr";

-- =============================================================================
-- TABLE: clients
-- Purpose: Client profiles and KYC information
-- =============================================================================

CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_name VARCHAR(255) NOT NULL,
    client_type VARCHAR(50) NOT NULL CHECK (client_type IN ('INDIVIDUAL', 'CORPORATE', 'TRUST', 'FOUNDATION')),
    risk_rating VARCHAR(20) NOT NULL CHECK (risk_rating IN ('LOW', 'MEDIUM', 'HIGH')),
    kyc_status VARCHAR(50) NOT NULL CHECK (kyc_status IN ('CURRENT', 'EXPIRING_SOON', 'EXPIRED')),
    kyc_last_updated TIMESTAMP WITH TIME ZONE,
    onboarding_date TIMESTAMP WITH TIME ZONE NOT NULL,
    relationship_manager_id UUID,
    jurisdiction VARCHAR(3),
    industry VARCHAR(100),
    pep_status BOOLEAN DEFAULT FALSE,
    sanctions_status BOOLEAN DEFAULT FALSE,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_clients_name ON clients(client_name);
CREATE INDEX idx_clients_rm ON clients(relationship_manager_id);
CREATE INDEX idx_clients_risk ON clients(risk_rating);
CREATE INDEX idx_clients_kyc ON clients(kyc_status);
CREATE INDEX idx_clients_risk_kyc ON clients(risk_rating, kyc_status);
CREATE INDEX idx_clients_flags ON clients(pep_status, sanctions_status);

COMMENT ON TABLE clients IS 'Client entities (individuals, corporates, trusts, foundations)';
COMMENT ON COLUMN clients.metadata IS 'Flexible JSON storage for additional client data';

-- =============================================================================
-- TABLE: documents
-- Purpose: Document metadata and storage references
-- =============================================================================

CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    document_type VARCHAR(100) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size_bytes INTEGER NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    file_hash VARCHAR(64),
    page_count INTEGER,
    word_count INTEGER,
    extracted_text TEXT,
    processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMP WITH TIME ZONE,
    processing_error TEXT,
    uploaded_by UUID,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_documents_client ON documents(client_id);
CREATE INDEX idx_documents_type ON documents(document_type);
CREATE INDEX idx_documents_processed ON documents(processed);
CREATE INDEX idx_documents_client_type ON documents(client_id, document_type);
CREATE INDEX idx_documents_hash ON documents(file_hash);

COMMENT ON TABLE documents IS 'Uploaded documents for KYC and compliance';
COMMENT ON COLUMN documents.file_hash IS 'SHA-256 hash for deduplication';
COMMENT ON COLUMN documents.extracted_text IS 'Full text extracted via OCR/parsing';

-- =============================================================================
-- TABLE: document_validations
-- Purpose: Validation results for documents
-- =============================================================================

CREATE TABLE document_validations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    format_validation JSONB NOT NULL,
    structure_validation JSONB NOT NULL,
    content_validation JSONB NOT NULL,
    format_score INTEGER NOT NULL CHECK (format_score >= 0 AND format_score <= 100),
    structure_score INTEGER NOT NULL CHECK (structure_score >= 0 AND structure_score <= 100),
    content_score INTEGER NOT NULL CHECK (content_score >= 0 AND content_score <= 100),
    validated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_validations_document ON document_validations(document_id);

COMMENT ON TABLE document_validations IS 'Format, structure, and content validation results';
COMMENT ON COLUMN document_validations.format_score IS 'Risk score 0-100 (higher = more risk)';

-- =============================================================================
-- TABLE: images
-- Purpose: Image analysis results
-- =============================================================================

CREATE TABLE images (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    image_path TEXT NOT NULL,
    image_hash VARCHAR(64),
    image_type VARCHAR(50),
    ai_generated_result JSONB,
    tampering_result JSONB,
    authenticity_result JSONB,
    forensic_result JSONB,
    exif_data JSONB,
    risk_score INTEGER NOT NULL CHECK (risk_score >= 0 AND risk_score <= 100),
    analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_images_document ON images(document_id);
CREATE INDEX idx_images_risk ON images(risk_score);
CREATE INDEX idx_images_hash ON images(image_hash);

COMMENT ON TABLE images IS 'Image forensic analysis results (AI detection, tampering, EXIF)';
COMMENT ON COLUMN images.risk_score IS 'Overall image risk score 0-100';

-- =============================================================================
-- TABLE: risk_scores
-- Purpose: Risk calculations for documents, transactions, clients
-- =============================================================================

CREATE TABLE risk_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    transaction_id UUID REFERENCES transactions(id) ON DELETE CASCADE,
    client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
    entity_type VARCHAR(50) NOT NULL CHECK (entity_type IN ('DOCUMENT', 'TRANSACTION', 'CLIENT')),
    entity_id UUID NOT NULL,
    total_score INTEGER NOT NULL CHECK (total_score >= 0 AND total_score <= 100),
    risk_level VARCHAR(20) NOT NULL CHECK (risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    component_scores JSONB NOT NULL,
    component_weights JSONB NOT NULL,
    contributing_factors JSONB NOT NULL,
    recommendations JSONB,
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_risk_entity ON risk_scores(entity_type, entity_id);
CREATE INDEX idx_risk_level ON risk_scores(risk_level, calculated_at);

COMMENT ON TABLE risk_scores IS 'Risk score calculations with component breakdown';
COMMENT ON COLUMN risk_scores.entity_type IS 'Polymorphic: DOCUMENT, TRANSACTION, or CLIENT';

-- =============================================================================
-- TABLE: alerts
-- Purpose: Compliance alerts and their lifecycle
-- =============================================================================

CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    alert_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    status VARCHAR(50) NOT NULL DEFAULT 'NEW' CHECK (status IN ('NEW', 'ACKNOWLEDGED', 'IN_REVIEW', 'ESCALATED', 'RESOLVED', 'FALSE_POSITIVE')),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    transaction_id UUID REFERENCES transactions(id) ON DELETE SET NULL,
    document_id UUID REFERENCES documents(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    risk_score INTEGER NOT NULL,
    triggered_rules JSONB,
    context JSONB,
    recommended_actions JSONB,
    due_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolved_by UUID,
    resolution_type VARCHAR(50),
    resolution_notes TEXT
);

CREATE INDEX idx_alerts_client ON alerts(client_id);
CREATE INDEX idx_alerts_status ON alerts(status);
CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_alerts_document ON alerts(document_id);
CREATE INDEX idx_alerts_transaction ON alerts(transaction_id);
CREATE INDEX idx_alerts_created ON alerts(created_at DESC);
CREATE INDEX idx_alerts_status_severity ON alerts(status, severity);
CREATE INDEX idx_alerts_client_status ON alerts(client_id, status);

COMMENT ON TABLE alerts IS 'Compliance alerts for transaction risks, document issues, etc.';
COMMENT ON COLUMN alerts.triggered_rules IS 'Array of rule IDs that triggered this alert';

-- =============================================================================
-- TABLE: alert_recipients
-- Purpose: Alert routing and tracking
-- =============================================================================

CREATE TABLE alert_recipients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    alert_id UUID NOT NULL REFERENCES alerts(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    user_role VARCHAR(50) NOT NULL CHECK (user_role IN ('RM', 'COMPLIANCE', 'LEGAL')),
    notified_at TIMESTAMP WITH TIME ZONE,
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    viewed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_recipients_alert ON alert_recipients(alert_id);
CREATE INDEX idx_recipients_user ON alert_recipients(user_id);

COMMENT ON TABLE alert_recipients IS 'Tracks who was notified and when they responded';

-- =============================================================================
-- TABLE: transactions
-- Purpose: Transaction data for AML monitoring (Part 1 - placeholder)
-- =============================================================================

CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    transaction_external_id VARCHAR(255) UNIQUE NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    amount DECIMAL(20, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    transaction_type VARCHAR(50) NOT NULL CHECK (transaction_type IN ('WIRE', 'CASH', 'TRADE', 'FX', 'OTHER')),
    source_account VARCHAR(255),
    destination_account VARCHAR(255),
    counterparty_name VARCHAR(255),
    counterparty_jurisdiction VARCHAR(3),
    swift_code VARCHAR(50),
    purpose TEXT,
    reference VARCHAR(255),
    screening_flags JSONB,
    status VARCHAR(50) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'BLOCKED')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_transactions_client ON transactions(client_id);
CREATE INDEX idx_transactions_timestamp ON transactions(timestamp DESC);
CREATE INDEX idx_transactions_amount ON transactions(amount);
CREATE INDEX idx_transactions_client_timestamp ON transactions(client_id, timestamp);

COMMENT ON TABLE transactions IS 'Transaction records for AML monitoring (Part 1)';
COMMENT ON COLUMN transactions.screening_flags IS 'PEP, SANCTIONS, ADVERSE_MEDIA flags';

-- =============================================================================
-- TABLE: audit_logs
-- Purpose: Immutable audit trail for compliance
-- =============================================================================

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    event_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) DEFAULT 'INFO' CHECK (severity IN ('INFO', 'WARNING', 'ERROR', 'AUDIT')),
    user_id UUID,
    user_role VARCHAR(50),
    session_id VARCHAR(255),
    ip_address INET,
    entity_type VARCHAR(50),
    entity_id UUID,
    action VARCHAR(100),
    before_state JSONB,
    after_state JSONB,
    metadata JSONB
);

CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX idx_audit_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_user ON audit_logs(user_id, timestamp);
CREATE INDEX idx_audit_event ON audit_logs(event_type, timestamp);

COMMENT ON TABLE audit_logs IS 'Immutable audit log for all system activities';
COMMENT ON COLUMN audit_logs.severity IS 'INFO, WARNING, ERROR, or AUDIT (custom level)';

-- =============================================================================
-- TABLE: reports
-- Purpose: Generated compliance reports
-- =============================================================================

CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    report_type VARCHAR(100) NOT NULL,
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    alert_id UUID REFERENCES alerts(id) ON DELETE CASCADE,
    client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    generated_by UUID,
    content JSONB NOT NULL,
    pdf_path TEXT,
    markdown_path TEXT,
    json_path TEXT
);

CREATE INDEX idx_reports_type ON reports(report_type);
CREATE INDEX idx_reports_document ON reports(document_id);
CREATE INDEX idx_reports_alert ON reports(alert_id);
CREATE INDEX idx_reports_type_generated ON reports(report_type, generated_at);

COMMENT ON TABLE reports IS 'Generated compliance reports (JSON, PDF, Markdown)';
COMMENT ON COLUMN reports.content IS 'Full report content as JSON';

-- =============================================================================
-- FUNCTIONS & TRIGGERS
-- =============================================================================

-- Function to update 'updated_at' timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for clients table
CREATE TRIGGER update_clients_updated_at
    BEFORE UPDATE ON clients
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for alerts table
CREATE TRIGGER update_alerts_updated_at
    BEFORE UPDATE ON alerts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- SAMPLE DATA (for testing)
-- =============================================================================

-- Insert sample client
INSERT INTO clients (
    id, client_name, client_type, risk_rating, kyc_status,
    onboarding_date, jurisdiction, pep_status
) VALUES (
    uuid_generate_v4(),
    'Sample Client Ltd',
    'CORPORATE',
    'MEDIUM',
    'CURRENT',
    CURRENT_TIMESTAMP - INTERVAL '1 year',
    'CH',
    FALSE
);

-- =============================================================================
-- GRANTS (if needed for specific users)
-- =============================================================================

-- Grant all privileges to speedrun user (already owner)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO speedrun;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO speedrun;

-- =============================================================================
-- END OF SCHEMA
-- =============================================================================

-- Verify schema
SELECT
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
ORDER BY table_name;

COMMENT ON SCHEMA public IS 'Speed-Run AML Platform Schema - v1.0.0';
