import { Alert, DashboardSummary, TransactionVolume, AlertDetails, AgentFinding, DocumentIssue, TransactionHistory } from "./api";

export const mockDashboardSummary: DashboardSummary = {
  total_active_alerts: 127,
  critical_alerts: 8,
  pending_cases: 45,
  avg_resolution_time: 4.2,
  resolution_time_change: -12,
  alerts_by_risk: {
    critical: 8,
    high: 23,
    medium: 51,
    low: 45,
  },
};

export const mockTransactionVolume: TransactionVolume[] = [
  { month: "Apr", volume: 1200 },
  { month: "May", volume: 1450 },
  { month: "Jun", volume: 1550 },
  { month: "Jul", volume: 1480 },
  { month: "Aug", volume: 1720 },
  { month: "Sep", volume: 1650 },
  { month: "Oct", volume: 1850 },
];

export const mockActiveAlerts: Alert[] = [
  {
    alert_id: "ALT-789",
    priority: "CRITICAL",
    client: "ABC Trading Ltd",
    client_id: "CLI-456",
    type: "Integrated Alert: Transaction + Document Anomaly",
    amount: 150000,
    currency: "CHF",
    risk_score: 95,
    status: "pending",
    timestamp: "2025-10-30T09:15:00Z",
  },
  {
    alert_id: "ALT-788",
    priority: "HIGH",
    client: "Swiss Property Holdings",
    client_id: "CLI-203",
    type: "Transaction Pattern Anomaly",
    amount: 280000,
    currency: "CHF",
    risk_score: 87,
    status: "investigating",
    timestamp: "2025-10-30T08:45:00Z",
  },
  {
    alert_id: "ALT-787",
    priority: "HIGH",
    client: "Global Investments SA",
    client_id: "CLI-891",
    type: "Cross-Border Risk",
    amount: 95000,
    currency: "EUR",
    risk_score: 82,
    status: "pending",
    timestamp: "2025-10-30T07:30:00Z",
  },
  {
    alert_id: "ALT-786",
    priority: "MEDIUM",
    client: "Tech Ventures GmbH",
    client_id: "CLI-567",
    type: "Document Verification Required",
    amount: 45000,
    currency: "CHF",
    risk_score: 68,
    status: "pending",
    timestamp: "2025-10-30T04:20:00Z",
  },
  {
    alert_id: "ALT-785",
    priority: "MEDIUM",
    client: "Alpine Real Estate",
    client_id: "CLI-123",
    type: "Transaction Volume Spike",
    amount: 75000,
    currency: "CHF",
    risk_score: 55,
    status: "resolved",
    timestamp: "2025-10-30T02:10:00Z",
  },
];

export const mockAgentFindings: AgentFinding[] = [
  {
    agent_name: "Agent 1: Regulatory Watcher",
    agent_type: "Regulatory Watcher",
    priority: "critical",
    finding: "Transaction violates FINMA Circular 2025-04 regarding real estate transaction documentation requirements",
    regulation: "Regulation: FINMA Circular 2025-04",
  },
  {
    agent_name: "Agent 2: Transaction Analyst",
    agent_type: "Transaction Analyst",
    priority: "high",
    finding: "Amount is 250% above client's 6-month transaction average (CHF 60,000)",
  },
  {
    agent_name: "Agent 3: Document Forensics",
    agent_type: "Document Forensics",
    priority: "critical",
    finding: "Purchase agreement shows signs of digital tampering on page 8",
  },
];

export const mockDocumentIssues: DocumentIssue[] = [
  {
    type: "tampering",
    description: "Purchase price field shows metadata inconsistency - likely edited after signing",
    page: 8,
  },
  {
    type: "inconsistency",
    description: "Signature date conflicts with notary stamp date",
    page: 6,
  },
  {
    type: "suspicious",
    description: "Font mismatch detected in beneficiary name field",
    page: 3,
  },
];

export const mockTransactionHistory: TransactionHistory[] = [
  { month: "2025-04", amount: 45000 },
  { month: "2025-05", amount: 52000 },
  { month: "2025-06", amount: 61000 },
  { month: "2025-07", amount: 58000 },
  { month: "2025-08", amount: 68000 },
  { month: "2025-09", amount: 55000 },
  { month: "2025-10", amount: 150000 },
];

export const mockAlertDetails: AlertDetails = {
  alert_id: "ALT-788",
  priority: "HIGH",
  client: "ABC Trading Ltd",
  client_id: "CLI-456",
  type: "Integrated Alert: Transaction + Document Anomaly",
  amount: 150000,
  currency: "CHF",
  risk_score: 95,
  status: "pending",
  timestamp: "2025-10-30T09:15:00Z",
  date: "30/10/2025",
  country: "Switzerland",
  transaction_type: "Real Estate Purchase",
  counterparty: "Luxury Properties Zurich AG",
  purpose: "Purchase of residential property - Zurich",
  agent_findings: mockAgentFindings,
  document_issues: mockDocumentIssues,
  transaction_history: mockTransactionHistory,
  document_url: "/sample-document.pdf",
};

export const mockClients = [
  {
    client_id: "CLI-456",
    full_name: "Hans Müller",
    account_type: "Private Banking",
    risk_rating: "high",
    kyc_status: "under_review",
    last_updated: "2024-11-01",
    pending_documents: 2,
    alerts: 3,
    transactionHistory: [
      { date: "2024-10-28", description: "Incoming Wire", amount: 50000, risk: "low" },
      { date: "2024-10-25", description: "Outgoing Wire", amount: -200000, risk: "high" },
      { date: "2024-10-22", description: "Securities Purchase", amount: -75000, risk: "low" },
    ],
    adverseMedia: [
      { source: "News Daily", headline: "Müller's Company Faces Scrutiny Over New Allegations", date: "2024-10-29" },
    ],
    complianceStatus: {
      sanctions: "Clear",
      pep: "PEP Tier 3",
      aml: "High Risk",
    },
  },
  {
    client_id: "CLI-789",
    full_name: "Sophie Chen",
    account_type: "Wealth Management",
    risk_rating: "medium",
    kyc_status: "approved",
    last_updated: "2024-10-28",
    pending_documents: 0,
    alerts: 1,
    transactionHistory: [
        { date: "2024-10-27", description: "Dividend Payment", amount: 15000, risk: "low" },
    ],
    adverseMedia: [],
    complianceStatus: {
        sanctions: "Clear",
        pep: "Not a PEP",
        aml: "Medium Risk",
    },
  },
  {
    client_id: "CLI-234",
    full_name: "Mohammed Al-Rashid",
    account_type: "Private Banking",
    risk_rating: "high",
    kyc_status: "under_review",
    last_updated: "2024-10-30",
    pending_documents: 1,
    alerts: 2,
    transactionHistory: [
        { date: "2024-10-29", description: "Property Purchase", amount: -1500000, risk: "high" },
    ],
    adverseMedia: [
        { source: "Global Finance Times", headline: "Al-Rashid Linked to Offshore Investigation", date: "2024-10-28" },
    ],
    complianceStatus: {
        sanctions: "Potential Match",
        pep: "Not a PEP",
        aml: "High Risk",
    },
  },
  {
    client_id: "CLI-567",
    full_name: "Emma Thompson",
    account_type: "Investment Advisory",
    risk_rating: "low",
    kyc_status: "approved",
    last_updated: "2024-10-25",
    pending_documents: 0,
    alerts: 0,
    transactionHistory: [
        { date: "2024-10-24", description: "Mutual Fund Investment", amount: -50000, risk: "low" },
    ],
    adverseMedia: [],
    complianceStatus: {
        sanctions: "Clear",
        pep: "Not a PEP",
        aml: "Low Risk",
    },
  },
  {
    client_id: "CLI-890",
    full_name: "Carlos Mendoza",
    account_type: "Private Banking",
    risk_rating: "medium",
    kyc_status: "pending_documents",
    last_updated: "2024-10-29",
    pending_documents: 3,
    alerts: 1,
    transactionHistory: [
        { date: "2024-10-28", description: "Incoming International Transfer", amount: 250000, risk: "medium" },
    ],
    adverseMedia: [],
    complianceStatus: {
        sanctions: "Clear",
        pep: "Not a PEP",
        aml: "Medium Risk",
    },
  },
];

