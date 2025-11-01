import { supabase } from './supabase'

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
// SUPABASE API FUNCTIONS
// ============================================

export async function getDashboardSummary(): Promise<DashboardSummary> {
  try {
    // Get all alerts
    const { data: alerts, error } = await supabase
      .from('alerts')
      .select('priority, status, risk_score')

    if (error) {
      console.error('Supabase error:', error)
      throw error
    }

    // Calculate statistics
    const activeAlerts = alerts?.filter(a => a.status !== 'resolved') || []
    const totalAlerts = activeAlerts.length
    const criticalAlerts = activeAlerts.filter(a => a.priority === 'CRITICAL').length
    const pendingCases = activeAlerts.filter(a => a.status === 'pending').length

    const alertsByRisk = {
      critical: activeAlerts.filter(a => a.priority === 'CRITICAL').length,
      high: activeAlerts.filter(a => a.priority === 'HIGH').length,
      medium: activeAlerts.filter(a => a.priority === 'MEDIUM').length,
      low: activeAlerts.filter(a => a.priority === 'LOW').length,
    }

    return {
      total_active_alerts: totalAlerts,
      critical_alerts: criticalAlerts,
      pending_cases: pendingCases,
      avg_resolution_time: 4.2,
      resolution_time_change: -12,
      alerts_by_risk: alertsByRisk,
    }
  } catch (error) {
    console.error('Error in getDashboardSummary:', error)
    throw error
  }
}

export async function getActiveAlerts(): Promise<Alert[]> {
  try {
    const { data, error } = await supabase
      .from('alerts')
      .select('*')
      .neq('status', 'resolved')
      .order('timestamp', { ascending: false })
      .limit(100)

    if (error) {
      console.error('Supabase error:', error)
      throw error
    }

    return data || []
  } catch (error) {
    console.error('Error in getActiveAlerts:', error)
    throw error
  }
}

export async function getTransactionVolume(): Promise<TransactionVolume[]> {
  // Mock data for now - TODO: Calculate from transactions table
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

export async function getAlertDetails(alertId: string): Promise<AlertDetails> {
  try {
    const { data, error } = await supabase
      .from('alerts')
      .select('*')
      .eq('alert_id', alertId)
      .single()

    if (error) {
      console.error('Supabase error:', error)
      throw error
    }

    if (!data) {
      throw new Error('Alert not found')
    }

    return {
      ...data,
      agent_findings: data.agent_findings || [],
      document_issues: data.document_issues || [],
      transaction_history: data.transaction_history || [],
    }
  } catch (error) {
    console.error('Error in getAlertDetails:', error)
    throw error
  }
}

export async function remediateAlert(alertId: string): Promise<{ success: boolean }> {
  try {
    const { error } = await supabase
      .from('alerts')
      .update({ 
        status: 'resolved', 
        updated_at: new Date().toISOString() 
      })
      .eq('alert_id', alertId)

    if (error) {
      console.error('Supabase error:', error)
      throw error
    }

    return { success: true }
  } catch (error) {
    console.error('Error in remediateAlert:', error)
    throw error
  }
}

export async function getAuditTrail(alertId: string): Promise<AuditLogEntry[]> {
  // Mock data for now
  return [
    {
      timestamp: "2025-10-30T09:15:00Z",
      user: "Ana Rodriguez",
      action: "Alert Created",
      details: "Alert automatically generated by Transaction Monitor Agent",
    },
    {
      timestamp: "2025-10-30T09:20:00Z",
      user: "Ana Rodriguez",
      action: "Alert Viewed",
      details: "Compliance officer viewed alert details",
    },
  ]
}