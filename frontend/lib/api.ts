// ============================================
// Backend API Client for FastAPI
// ============================================

import { logger } from './logger'
import { config, getApiUrl } from './config'

const { BACKEND_URL, API_VERSION, BASE_URL: API_BASE } = config.api

// Log API configuration
logger.info('API', 'API client initialized', {
  backendUrl: BACKEND_URL,
  apiVersion: API_VERSION,
  useBackendApi: config.features.USE_BACKEND_API,
})

// ============================================
// Type Definitions
// ============================================

export interface Alert {
  alert_id: string
  priority: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW"
  client: string
  client_id: string
  type: string
  amount: number
  currency: string
  risk_score: number
  status: "pending" | "investigating" | "resolved"
  timestamp: string
  country?: string
  transaction_type?: string
  counterparty?: string
  purpose?: string
  date?: string
}

export interface DashboardSummary {
  total_active_alerts: number
  critical_alerts: number
  pending_cases: number
  avg_resolution_time: number
  resolution_time_change: number
  alerts_by_risk: {
    critical: number
    high: number
    medium: number
    low: number
  }
}

export interface TransactionVolume {
  month: string
  volume: number
}

export interface AgentFinding {
  agent_name: string
  agent_type: "Regulatory Watcher" | "Transaction Analyst" | "Document Forensics"
  priority: "critical" | "high" | "medium"
  finding: string
  regulation?: string
}

export interface DocumentIssue {
  type: "tampering" | "inconsistency" | "suspicious"
  description: string
  page: number
}

export interface TransactionHistory {
  month: string
  amount: number
}

export interface AlertDetails extends Alert {
  agent_findings: AgentFinding[]
  document_issues: DocumentIssue[]
  transaction_history: TransactionHistory[]
  document_url?: string
}

export interface AuditLogEntry {
  timestamp: string
  user: string
  action: string
  details: string
}

// ============================================
// Validation & Corroboration Types (Aligned with Backend)
// ============================================

export interface ValidationIssue {
  category: string
  severity: "low" | "medium" | "high" | "critical"
  description: string
  location?: string
  details?: Record<string, any>
}

export interface FormatValidationResult {
  has_double_spacing: boolean
  has_font_inconsistencies: boolean
  has_indentation_issues: boolean
  has_spelling_errors: boolean
  spelling_error_count: number
  issues: ValidationIssue[]
  has_formatting_issues: boolean
  double_spacing_count: number
  trailing_whitespace_count: number
  spelling_errors: string[]
}

export interface StructureValidationResult {
  is_complete: boolean
  missing_sections: string[]
  has_correct_headers: boolean
  template_match_score: number
  issues: ValidationIssue[]
}

export interface ContentValidationResult {
  has_sensitive_data: boolean
  quality_score: number
  readability_score: number
  word_count: number
  issues: ValidationIssue[]
}

export interface CompressionProfile {
  profile: string
  message: string
  confidence: string
  size_match: boolean
  ela_range: [number, number]
  typical_size: [number, number]
}

export interface ImageAnalysisResult {
  is_authentic: boolean
  is_ai_generated: boolean
  ai_detection_confidence: number
  is_tampered: boolean
  tampering_confidence: number
  reverse_image_matches: number
  metadata_issues: ValidationIssue[]
  forensic_findings: ValidationIssue[]
  compression_profiles?: CompressionProfile[]
  ela_variance?: number
}

export interface RiskScore {
  overall_score: number
  risk_level: "low" | "medium" | "high" | "critical"
  confidence: number
  contributing_factors: Array<{
    factor: string
    weight: number
    score: number
  }>
  recommendations: string[]
}

export interface CorroborationRequest {
  file: File
  client_id?: string
}

export interface CorroborationResponse {
  document_id: string
  file_name: string
  file_type: string
  analysis_timestamp: string

  // Validation results (separate properties, not "findings")
  format_validation?: FormatValidationResult
  structure_validation?: StructureValidationResult
  content_validation?: ContentValidationResult
  image_analysis?: ImageAnalysisResult

  // Risk assessment (nested object)
  risk_score: RiskScore

  // Processing metadata
  processing_time: number
  engines_used: string[]

  // Summary
  total_issues_found: number
  critical_issues_count: number
  requires_manual_review: boolean
}

// ============================================
// Utility Functions
// ============================================

async function fetchFromBackend(endpoint: string, options: RequestInit = {}) {
  const url = `${API_BASE}${endpoint}`
  const method = options.method || 'GET'

  try {
    logger.info('API', `→ ${method} ${endpoint}`)

    const startTime = Date.now()
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    })

    const duration = Date.now() - startTime

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      const errorMsg = errorData.detail || `API error: ${response.status}`
      logger.error('API', `← ${method} ${endpoint} → ${response.status} (${duration}ms)`, {
        status: response.status,
        error: errorMsg,
      })
      throw new Error(errorMsg)
    }

    const data = await response.json()
    logger.info('API', `← ${method} ${endpoint} → ${response.status} (${duration}ms)`)
    return data
  } catch (error) {
    logger.error('API', `✗ ${method} ${endpoint} failed`, { error })
    throw error
  }
}

async function uploadFile(endpoint: string, file: File, additionalData?: Record<string, any>) {
  const url = `${API_BASE}${endpoint}`
  const formData = new FormData()

  formData.append('file', file)

  if (additionalData) {
    Object.entries(additionalData).forEach(([key, value]) => {
      formData.append(key, String(value))
    })
  }

  try {
    const fileSizeMB = (file.size / 1024 / 1024).toFixed(2)
    logger.info('API', `→ POST ${endpoint} (uploading ${file.name}, ${fileSizeMB}MB)`)

    const startTime = Date.now()
    const response = await fetch(url, {
      method: 'POST',
      body: formData,
    })

    const duration = Date.now() - startTime

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      const errorMsg = errorData.detail || `API error: ${response.status}`
      logger.error('API', `← POST ${endpoint} → ${response.status} (${duration}ms)`, {
        status: response.status,
        error: errorMsg,
        fileName: file.name,
      })
      throw new Error(errorMsg)
    }

    const data = await response.json()
    logger.info('API', `← POST ${endpoint} → ${response.status} (${duration}ms, ${file.name} processed)`)
    return data
  } catch (error) {
    logger.error('API', `✗ POST ${endpoint} failed`, { error, fileName: file.name })
    throw error
  }
}

// ============================================
// API Functions
// ============================================

/**
 * Get dashboard summary statistics
 */
export async function getDashboardSummary(): Promise<DashboardSummary> {
  try {
    const data = await fetchFromBackend('/alerts/summary')
    return data
  } catch (error) {
    console.error('Error fetching dashboard summary:', error)
    // Return default values on error
    return {
      total_active_alerts: 0,
      critical_alerts: 0,
      pending_cases: 0,
      avg_resolution_time: 0,
      resolution_time_change: 0,
      alerts_by_risk: {
        critical: 0,
        high: 0,
        medium: 0,
        low: 0,
      },
    }
  }
}

/**
 * Get list of active alerts
 */
export async function getActiveAlerts(): Promise<Alert[]> {
  try {
    const data = await fetchFromBackend('/alerts/?status=active&limit=100')
    return data.alerts || []
  } catch (error) {
    console.error('Error fetching active alerts:', error)
    return []
  }
}

/**
 * Get transaction volume data
 */
export async function getTransactionVolume(): Promise<TransactionVolume[]> {
  // TODO: Implement backend endpoint
  // For now, return mock data
  return [
    { month: "Apr", volume: 1200 },
    { month: "May", volume: 1450 },
    { month: "Jun", volume: 1550 },
    { month: "Jul", volume: 1480 },
    { month: "Aug", volume: 1720 },
    { month: "Sep", volume: 1650 },
    { month: "Oct", volume: 1850 },
  ]
}

/**
 * Get detailed information about a specific alert
 */
export async function getAlertDetails(alertId: string): Promise<AlertDetails> {
  try {
    const data = await fetchFromBackend(`/alerts/${alertId}`)
    return {
      ...data,
      agent_findings: data.agent_findings || [],
      document_issues: data.document_issues || [],
      transaction_history: data.transaction_history || [],
    }
  } catch (error) {
    console.error(`Error fetching alert details for ${alertId}:`, error)
    throw error
  }
}

/**
 * Mark an alert as remediated
 */
export async function remediateAlert(alertId: string): Promise<{ success: boolean }> {
  try {
    await fetchFromBackend(`/alerts/${alertId}/status`, {
      method: 'PUT',
      body: JSON.stringify({ status: 'resolved' }),
    })
    return { success: true }
  } catch (error) {
    console.error(`Error remediating alert ${alertId}:`, error)
    throw error
  }
}

/**
 * Update alert status
 */
export async function updateAlertStatus(
  alertId: string,
  status: 'pending' | 'investigating' | 'resolved'
): Promise<{ success: boolean }> {
  try {
    await fetchFromBackend(`/alerts/${alertId}/status`, {
      method: 'PUT',
      body: JSON.stringify({ status }),
    })
    return { success: true }
  } catch (error) {
    console.error(`Error updating alert status for ${alertId}:`, error)
    throw error
  }
}

/**
 * Get audit trail for an alert
 */
export async function getAuditTrail(alertId: string): Promise<AuditLogEntry[]> {
  try {
    const data = await fetchFromBackend(`/alerts/${alertId}/audit-trail`)
    return data.audit_logs || []
  } catch (error) {
    console.error(`Error fetching audit trail for ${alertId}:`, error)
    // Return empty array on error
    return []
  }
}

/**
 * Upload and analyze a document
 */
export async function analyzeDocument(file: File, clientId?: string): Promise<CorroborationResponse> {
  try {
    const additionalData = clientId ? { client_id: clientId } : {}
    const data = await uploadFile('/corroboration/analyze', file, additionalData)
    return data
  } catch (error) {
    console.error('Error analyzing document:', error)
    throw error
  }
}

/**
 * Perform OCR on an image
 */
export async function performOCR(file: File): Promise<any> {
  try {
    const data = await uploadFile('/ocr/extract', file)
    return data
  } catch (error) {
    console.error('Error performing OCR:', error)
    throw error
  }
}

/**
 * Parse a document (PDF, DOCX, etc.)
 */
export async function parseDocument(file: File): Promise<any> {
  try {
    const data = await uploadFile('/documents/parse', file)
    return data
  } catch (error) {
    console.error('Error parsing document:', error)
    throw error
  }
}

/**
 * Check backend health
 */
export async function checkBackendHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${BACKEND_URL}/health`)
    return response.ok
  } catch (error) {
    console.error('Backend health check failed:', error)
    return false
  }
}
