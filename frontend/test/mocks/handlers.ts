import { http, HttpResponse } from 'msw'

const API_BASE_URL = 'http://localhost:8000/api/v1'

export const handlers = [
  // Dashboard summary endpoint
  http.get(`${API_BASE_URL}/dashboard/summary`, () => {
    return HttpResponse.json({
      summary: {
        total_clients: 25,
        pending_reviews: 8,
        critical_alerts: 2,
        total_alerts: 7,
        total_red_flags: 12,
        avg_lead_time_hours: 3.2,
      },
    })
  }),

  // Active alerts endpoint
  http.get(`${API_BASE_URL}/alerts/`, () => {
    return HttpResponse.json({
      alerts: [
        {
          alert_id: 'ALT-001',
          client_id: 'CLI-456',
          client_name: 'Hans Müller',
          risk_score: 0.85,
          red_flags: ['tampered_document', 'high_risk_country', 'suspicious_activity'],
          status: 'flagged',
          severity: 'CRITICAL',
          created_at: '2025-11-01T10:00:00Z',
          updated_at: '2025-11-01T10:00:00Z',
        },
        {
          alert_id: 'ALT-002',
          client_id: 'CLI-789',
          client_name: 'Sophie Chen',
          risk_score: 0.65,
          red_flags: ['document_inconsistency'],
          status: 'review',
          severity: 'HIGH',
          created_at: '2025-11-01T08:00:00Z',
          updated_at: '2025-11-01T08:00:00Z',
        },
      ],
    })
  }),

  // Alert details endpoint
  http.get(`${API_BASE_URL}/alerts/:alertId`, ({ params }) => {
    const { alertId } = params
    return HttpResponse.json({
      alert_id: alertId,
      client_id: 'CLI-456',
      client_name: 'Hans Müller',
      risk_score: 0.85,
      red_flags: ['tampered_document', 'high_risk_country', 'suspicious_activity'],
      status: 'flagged',
      severity: 'CRITICAL',
      created_at: '2025-11-01T10:00:00Z',
      updated_at: '2025-11-01T10:00:00Z',
      details: {
        document_analysis: {
          authenticity_score: 0.45,
          tampered: true,
          ai_generated: false,
        },
      },
    })
  }),

  // Update alert status endpoint
  http.patch(`${API_BASE_URL}/alerts/:alertId/status`, async ({ request }) => {
    const body = await request.json()
    return HttpResponse.json({
      success: true,
      message: 'Alert status updated',
    })
  }),

  // Remediate alert endpoint
  http.post(`${API_BASE_URL}/alerts/:alertId/remediate`, () => {
    return HttpResponse.json({
      success: true,
      message: 'Alert remediated',
    })
  }),
]
