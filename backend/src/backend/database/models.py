"""
SQLAlchemy ORM Models for Speed-Run AML Platform.

Models:
1. Client - Client profiles and KYC information
2. Document - Document metadata and storage
3. DocumentValidation - Validation results (format, structure, content)
4. Image - Image analysis results
5. RiskScore - Risk calculations and scores
6. Alert - Alert management
7. AlertRecipient - Alert routing to users
8. Transaction - Transaction data (Part 1 - placeholder)
9. AuditLog - Compliance audit trail
10. Report - Generated reports
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    Boolean, Column, DateTime, Enum, Float, ForeignKey,
    Integer, JSON, String, Text, DECIMAL, ARRAY, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


class Client(Base):
    """
    Client entity representing individuals or corporate entities.

    Used for: KYC management, risk profiling, relationship management
    """
    __tablename__ = "clients"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Basic Information
    client_name = Column(String(255), nullable=False, index=True)
    client_type = Column(
        String(50),
        nullable=False,
        comment="INDIVIDUAL, CORPORATE, TRUST, FOUNDATION"
    )

    # Risk Information
    risk_rating = Column(
        String(20),
        nullable=False,
        index=True,
        comment="LOW, MEDIUM, HIGH"
    )
    kyc_status = Column(
        String(50),
        nullable=False,
        index=True,
        comment="CURRENT, EXPIRING_SOON, EXPIRED"
    )
    kyc_last_updated = Column(DateTime(timezone=True))

    # Onboarding
    onboarding_date = Column(DateTime(timezone=True), nullable=False)
    relationship_manager_id = Column(UUID(as_uuid=True), index=True)

    # Geographic & Business
    jurisdiction = Column(String(3), comment="ISO 3166 country code")
    industry = Column(String(100))

    # Flags
    pep_status = Column(Boolean, default=False, index=True)
    sanctions_status = Column(Boolean, default=False, index=True)

    # Additional Metadata
    meta_data = Column(JSONB, comment="Flexible additional data")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    documents = relationship("Document", back_populates="client", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="client", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="client", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_client_risk_kyc', 'risk_rating', 'kyc_status'),
        Index('idx_client_flags', 'pep_status', 'sanctions_status'),
    )

    def __repr__(self):
        return f"<Client(id={self.id}, name={self.client_name}, risk={self.risk_rating})>"


class Document(Base):
    """
    Document entity for uploaded files.

    Used for: Document storage, processing tracking, corroboration analysis
    """
    __tablename__ = "documents"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Foreign Keys
    client_id = Column(
        UUID(as_uuid=True),
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Document Classification
    document_type = Column(
        String(100),
        nullable=False,
        index=True,
        comment="KYC, PROOF_OF_ADDRESS, SOURCE_OF_WEALTH, CONTRACT, etc."
    )

    # File Information
    filename = Column(String(255), nullable=False)
    file_path = Column(Text, nullable=False, comment="Path to stored file")
    file_size_bytes = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_hash = Column(String(64), index=True, comment="SHA-256 hash for deduplication")

    # Content Metadata
    page_count = Column(Integer)
    word_count = Column(Integer)
    extracted_text = Column(Text, comment="Full extracted text")

    # Processing Status
    processed = Column(Boolean, default=False, index=True)
    processed_at = Column(DateTime(timezone=True))
    processing_error = Column(Text, comment="Error message if processing failed")

    # Upload Information
    uploaded_by = Column(UUID(as_uuid=True), comment="User ID who uploaded")
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    # Document Metadata (from file)
    meta_data = Column(JSONB, comment="Author, creation date, etc.")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    client = relationship("Client", back_populates="documents")
    validations = relationship("DocumentValidation", back_populates="document", cascade="all, delete-orphan")
    images = relationship("Image", back_populates="document", cascade="all, delete-orphan")
    risk_scores = relationship("RiskScore", back_populates="document", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="document")
    reports = relationship("Report", back_populates="document")

    # Indexes
    __table_args__ = (
        Index('idx_document_client_type', 'client_id', 'document_type'),
        Index('idx_document_processed', 'processed', 'processed_at'),
        Index('idx_document_hash', 'file_hash'),
    )

    def __repr__(self):
        return f"<Document(id={self.id}, filename={self.filename}, type={self.document_type})>"


class DocumentValidation(Base):
    """
    Validation results for documents.

    Stores: Format validation, structure validation, content validation
    """
    __tablename__ = "document_validations"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Foreign Key
    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Validation Results (stored as JSONB for flexibility)
    format_validation = Column(JSONB, nullable=False, comment="FormatValidationResult")
    structure_validation = Column(JSONB, nullable=False, comment="StructureValidationResult")
    content_validation = Column(JSONB, nullable=False, comment="ContentValidationResult")

    # Individual Scores (0-100, higher = more risk)
    format_score = Column(Integer, nullable=False, comment="0-100 risk score")
    structure_score = Column(Integer, nullable=False, comment="0-100 risk score")
    content_score = Column(Integer, nullable=False, comment="0-100 risk score")

    # Timestamp
    validated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    document = relationship("Document", back_populates="validations")

    def __repr__(self):
        return f"<DocumentValidation(id={self.id}, doc={self.document_id})>"


class Image(Base):
    """
    Image analysis results for images extracted from documents or uploaded separately.

    Stores: AI detection, tampering detection, EXIF analysis, authenticity check
    """
    __tablename__ = "images"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Foreign Key (optional - standalone images don't have document)
    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        index=True
    )

    # Image Information
    image_path = Column(Text, nullable=False)
    image_hash = Column(String(64), index=True, comment="SHA-256 hash")
    image_type = Column(String(50), comment="PHOTO, SCAN, DIAGRAM, SIGNATURE")

    # Analysis Results (stored as JSONB)
    ai_generated_result = Column(JSONB, comment="AI detection result")
    tampering_result = Column(JSONB, comment="Tampering detection result")
    authenticity_result = Column(JSONB, comment="Reverse search result")
    forensic_result = Column(JSONB, comment="Forensic analysis result")
    exif_data = Column(JSONB, comment="EXIF metadata")

    # Overall Risk Score
    risk_score = Column(Integer, nullable=False, comment="0-100 risk score")

    # Timestamp
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    document = relationship("Document", back_populates="images")

    # Indexes
    __table_args__ = (
        Index('idx_image_risk', 'risk_score'),
        Index('idx_image_hash', 'image_hash'),
    )

    def __repr__(self):
        return f"<Image(id={self.id}, risk={self.risk_score})>"


class RiskScore(Base):
    """
    Risk score calculations for documents, transactions, or clients.

    Stores: Component scores, risk level, contributing factors
    """
    __tablename__ = "risk_scores"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Foreign Keys (polymorphic - can link to document, transaction, or client)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), index=True)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id", ondelete="CASCADE"), index=True)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), index=True)

    # Entity Type
    entity_type = Column(
        String(50),
        nullable=False,
        comment="DOCUMENT, TRANSACTION, CLIENT"
    )
    entity_id = Column(UUID(as_uuid=True), nullable=False)

    # Risk Score
    total_score = Column(Integer, nullable=False, comment="0-100 risk score")
    risk_level = Column(
        String(20),
        nullable=False,
        index=True,
        comment="LOW, MEDIUM, HIGH, CRITICAL"
    )

    # Component Breakdown
    component_scores = Column(JSONB, nullable=False, comment="Breakdown by component")
    component_weights = Column(JSONB, nullable=False, comment="Weights used")

    # Contributing Factors
    contributing_factors = Column(JSONB, nullable=False, comment="List of risk factors")

    # Recommendations
    recommendations = Column(JSONB, comment="Suggested actions")

    # Timestamp
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    document = relationship("Document", back_populates="risk_scores")

    # Indexes
    __table_args__ = (
        Index('idx_risk_entity', 'entity_type', 'entity_id'),
        Index('idx_risk_level', 'risk_level', 'calculated_at'),
    )

    def __repr__(self):
        return f"<RiskScore(id={self.id}, score={self.total_score}, level={self.risk_level})>"


class Alert(Base):
    """
    Alert entity for compliance alerts.

    Used for: Alert management, routing, remediation workflows
    """
    __tablename__ = "alerts"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Alert Classification
    alert_type = Column(
        String(100),
        nullable=False,
        index=True,
        comment="TRANSACTION_RISK, DOCUMENT_RISK, PATTERN_DETECTED, SANCTIONS_MATCH, etc."
    )
    severity = Column(
        String(20),
        nullable=False,
        index=True,
        comment="LOW, MEDIUM, HIGH, CRITICAL"
    )
    status = Column(
        String(50),
        nullable=False,
        default="NEW",
        index=True,
        comment="NEW, ACKNOWLEDGED, IN_REVIEW, ESCALATED, RESOLVED, FALSE_POSITIVE"
    )

    # Foreign Keys
    client_id = Column(
        UUID(as_uuid=True),
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id", ondelete="SET NULL"))
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="SET NULL"))

    # Alert Content
    title = Column(String(255), nullable=False)
    description = Column(Text)
    risk_score = Column(Integer, nullable=False)

    # Context
    triggered_rules = Column(JSONB, comment="Rules that triggered alert")
    context = Column(JSONB, comment="Additional context")
    recommended_actions = Column(JSONB, comment="Suggested remediation actions")

    # SLA
    due_date = Column(DateTime(timezone=True))

    # Assignment
    assigned_to = Column(UUID(as_uuid=True), nullable=True, comment="User ID assigned to handle alert")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Resolution
    resolved_at = Column(DateTime(timezone=True))
    resolved_by = Column(UUID(as_uuid=True), comment="User ID who resolved")
    resolution_type = Column(String(50), comment="APPROVED, BLOCKED, REPORTED, FALSE_POSITIVE")
    resolution_notes = Column(Text)

    # Relationships
    client = relationship("Client", back_populates="alerts")
    document = relationship("Document", back_populates="alerts")
    recipients = relationship("AlertRecipient", back_populates="alert", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="alert")

    # Indexes
    __table_args__ = (
        Index('idx_alert_status_severity', 'status', 'severity'),
        Index('idx_alert_client_status', 'client_id', 'status'),
        Index('idx_alert_created', 'created_at'),
    )

    def __repr__(self):
        return f"<Alert(id={self.id}, type={self.alert_type}, severity={self.severity}, status={self.status})>"


class AlertRecipient(Base):
    """
    Alert recipient for routing alerts to specific users.

    Tracks: Who was notified, when they acknowledged, when they viewed
    """
    __tablename__ = "alert_recipients"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Foreign Key
    alert_id = Column(
        UUID(as_uuid=True),
        ForeignKey("alerts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Recipient Information
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_role = Column(
        String(50),
        nullable=False,
        comment="RM, COMPLIANCE, LEGAL"
    )

    # Tracking
    notified_at = Column(DateTime(timezone=True))
    acknowledged_at = Column(DateTime(timezone=True))
    viewed_at = Column(DateTime(timezone=True))

    # Relationship
    alert = relationship("Alert", back_populates="recipients")

    # Indexes
    __table_args__ = (
        Index('idx_recipient_user', 'user_id', 'alert_id'),
    )

    def __repr__(self):
        return f"<AlertRecipient(id={self.id}, user={self.user_id}, role={self.user_role})>"


class Transaction(Base):
    """
    Transaction entity for AML transaction monitoring (Part 1).

    Placeholder for future implementation.
    """
    __tablename__ = "transactions"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Foreign Key
    client_id = Column(
        UUID(as_uuid=True),
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # External ID
    transaction_external_id = Column(String(255), unique=True, nullable=False)

    # Transaction Details
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    amount = Column(DECIMAL(20, 2), nullable=False, index=True)
    currency = Column(String(3), nullable=False, comment="ISO 4217 code")
    transaction_type = Column(
        String(50),
        nullable=False,
        comment="WIRE, CASH, TRADE, FX, OTHER"
    )

    # Accounts
    source_account = Column(String(255))
    destination_account = Column(String(255))

    # Counterparty
    counterparty_name = Column(String(255))
    counterparty_jurisdiction = Column(String(3), comment="ISO 3166 code")

    # Additional Details
    swift_code = Column(String(50))
    purpose = Column(Text)
    reference = Column(String(255))

    # Screening
    screening_flags = Column(JSONB, comment="PEP, SANCTIONS, ADVERSE_MEDIA, etc.")

    # Status
    status = Column(
        String(50),
        default="PENDING",
        comment="PENDING, PROCESSING, COMPLETED, BLOCKED"
    )

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    client = relationship("Client", back_populates="transactions")

    # Indexes
    __table_args__ = (
        Index('idx_transaction_client_timestamp', 'client_id', 'timestamp'),
        Index('idx_transaction_amount', 'amount'),
    )

    def __repr__(self):
        return f"<Transaction(id={self.id}, amount={self.amount} {self.currency})>"


class AuditLog(Base):
    """
    Audit log for compliance and debugging.

    Immutable log of all system activities.
    """
    __tablename__ = "audit_logs"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Timestamp (indexed for time-based queries)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Event Information
    event_type = Column(String(100), nullable=False, index=True)
    severity = Column(
        String(20),
        default="INFO",
        comment="INFO, WARNING, ERROR, AUDIT"
    )

    # User Context
    user_id = Column(UUID(as_uuid=True), index=True)
    user_role = Column(String(50))
    session_id = Column(String(255))
    ip_address = Column(INET)

    # Entity Context
    entity_type = Column(String(50), comment="CLIENT, DOCUMENT, ALERT, etc.")
    entity_id = Column(UUID(as_uuid=True), index=True)

    # Action
    action = Column(String(100), comment="CREATE, UPDATE, DELETE, ANALYZE, etc.")

    # State Changes (for audit trail)
    before_state = Column(JSONB, comment="State before action")
    after_state = Column(JSONB, comment="State after action")

    # Additional Data
    meta_data = Column(JSONB, comment="Flexible additional data")

    # Indexes
    __table_args__ = (
        Index('idx_audit_timestamp', 'timestamp'),
        Index('idx_audit_entity', 'entity_type', 'entity_id'),
        Index('idx_audit_user', 'user_id', 'timestamp'),
        Index('idx_audit_event', 'event_type', 'timestamp'),
    )

    def __repr__(self):
        return f"<AuditLog(id={self.id}, event={self.event_type}, timestamp={self.timestamp})>"


class Report(Base):
    """
    Generated reports for compliance and documentation.

    Stores: Report metadata, content, and export paths
    """
    __tablename__ = "reports"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Report Classification
    report_type = Column(
        String(100),
        nullable=False,
        index=True,
        comment="DOCUMENT_CORROBORATION, TRANSACTION_ANALYSIS, ALERT_SUMMARY, etc."
    )

    # Foreign Keys (optional - not all reports link to specific entities)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"))
    alert_id = Column(UUID(as_uuid=True), ForeignKey("alerts.id", ondelete="CASCADE"))
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"))

    # Generation
    generated_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    generated_by = Column(UUID(as_uuid=True), comment="User ID")

    # Content
    content = Column(JSONB, nullable=False, comment="Full report content as JSON")

    # Export Paths
    pdf_path = Column(Text, comment="Path to PDF export")
    markdown_path = Column(Text, comment="Path to Markdown export")
    json_path = Column(Text, comment="Path to JSON export")

    # Relationships
    document = relationship("Document", back_populates="reports")
    alert = relationship("Alert", back_populates="reports")

    # Indexes
    __table_args__ = (
        Index('idx_report_type_generated', 'report_type', 'generated_at'),
        Index('idx_report_document', 'document_id'),
        Index('idx_report_alert', 'alert_id'),
    )

    def __repr__(self):
        return f"<Report(id={self.id}, type={self.report_type})>"


# Export all models
__all__ = [
    "Base",
    "Client",
    "Document",
    "DocumentValidation",
    "Image",
    "RiskScore",
    "Alert",
    "AlertRecipient",
    "Transaction",
    "AuditLog",
    "Report",
]
