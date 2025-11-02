/**
 * Custom hooks for document and alert data fetching
 * Uses TanStack Query for efficient data management
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  getDashboardSummary,
  getActiveAlerts,
  getAlertDetails,
  updateAlertStatus,
  remediateAlert,
  analyzeDocument,
  performOCR,
  parseDocument
} from '../api'
import { config } from '../config'

// Query keys for cache management
export const queryKeys = {
  dashboardSummary: ['dashboardSummary'] as const,
  activeAlerts: ['activeAlerts'] as const,
  alertDetails: (id: string) => ['alertDetails', id] as const,
  auditTrail: (id: string) => ['auditTrail', id] as const,
}

/**
 * Fetch dashboard summary statistics
 */
export function useDashboardSummary() {
  return useQuery({
    queryKey: queryKeys.dashboardSummary,
    queryFn: getDashboardSummary,
    staleTime: config.ui.AUTO_REFRESH_INTERVAL,
    refetchInterval: config.ui.AUTO_REFRESH_INTERVAL > 0 ? config.ui.AUTO_REFRESH_INTERVAL : undefined,
    enabled: config.features.USE_BACKEND_API,
  })
}

/**
 * Fetch active alerts/reviews
 */
export function useActiveAlerts() {
  return useQuery({
    queryKey: queryKeys.activeAlerts,
    queryFn: getActiveAlerts,
    staleTime: config.ui.AUTO_REFRESH_INTERVAL,
    refetchInterval: config.ui.AUTO_REFRESH_INTERVAL > 0 ? config.ui.AUTO_REFRESH_INTERVAL : undefined,
    enabled: config.features.USE_BACKEND_API,
  })
}

/**
 * Fetch detailed information about a specific alert
 */
export function useAlertDetails(alertId: string) {
  return useQuery({
    queryKey: queryKeys.alertDetails(alertId),
    queryFn: () => getAlertDetails(alertId),
    enabled: !!alertId && config.features.USE_BACKEND_API,
  })
}

/**
 * Update alert status (mutation)
 */
export function useUpdateAlertStatus() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ alertId, status }: { alertId: string; status: 'pending' | 'investigating' | 'resolved' }) =>
      updateAlertStatus(alertId, status),
    onSuccess: () => {
      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: queryKeys.activeAlerts })
      queryClient.invalidateQueries({ queryKey: queryKeys.dashboardSummary })
    },
  })
}

/**
 * Remediate alert (mutation)
 */
export function useRemediateAlert() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (alertId: string) => remediateAlert(alertId),
    onSuccess: () => {
      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: queryKeys.activeAlerts })
      queryClient.invalidateQueries({ queryKey: queryKeys.dashboardSummary })
    },
  })
}

/**
 * Analyze document (mutation)
 */
export function useAnalyzeDocument() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ file, clientId }: { file: File; clientId?: string }) =>
      analyzeDocument(file, clientId),
    onSuccess: () => {
      // Optionally invalidate relevant queries
      queryClient.invalidateQueries({ queryKey: queryKeys.activeAlerts })
    },
  })
}

/**
 * Perform OCR (mutation)
 */
export function usePerformOCR() {
  return useMutation({
    mutationFn: (file: File) => performOCR(file),
  })
}

/**
 * Parse document (mutation)
 */
export function useParseDocument() {
  return useMutation({
    mutationFn: (file: File) => parseDocument(file),
  })
}
