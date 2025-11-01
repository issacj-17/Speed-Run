import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Database types
export type SupabaseAlert = {
  id: string
  alert_id: string
  priority: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW'
  client: string
  client_id: string
  type: string
  amount: number
  currency: string
  risk_score: number
  status: 'pending' | 'investigating' | 'resolved'
  timestamp: string
  country?: string
  transaction_type?: string
  counterparty?: string
  purpose?: string
  date?: string
  agent_findings: any[]
  document_issues: any[]
  transaction_history: any[]
  document_url?: string
  created_at: string
  updated_at: string
}