import { describe, it, expect } from 'vitest'
import { renderHook } from '@/test/test-utils'
import {
  useDashboardSummary,
  useActiveAlerts,
  useUpdateAlertStatus,
} from '@/lib/hooks/useDocuments'

describe('useDocuments Hooks (Integration)', () => {
  describe('useDashboardSummary', () => {
    it('should initialize with correct query structure', () => {
      const { result } = renderHook(() => useDashboardSummary())

      // Hook should return expected properties
      expect(result.current).toHaveProperty('isLoading')
      expect(result.current).toHaveProperty('isSuccess')
      expect(result.current).toHaveProperty('isError')
      expect(result.current).toHaveProperty('data')
      expect(result.current).toHaveProperty('error')
    })

    it('should have correct initial state', () => {
      const { result } = renderHook(() => useDashboardSummary())

      // Initially should not have data
      expect(result.current.data).toBeUndefined()
    })
  })

  describe('useActiveAlerts', () => {
    it('should initialize with correct query structure', () => {
      const { result } = renderHook(() => useActiveAlerts())

      // Hook should return expected properties
      expect(result.current).toHaveProperty('isLoading')
      expect(result.current).toHaveProperty('isSuccess')
      expect(result.current).toHaveProperty('isError')
      expect(result.current).toHaveProperty('data')
      expect(result.current).toHaveProperty('error')
    })

    it('should have correct initial state', () => {
      const { result } = renderHook(() => useActiveAlerts())

      // Initially should not have data
      expect(result.current.data).toBeUndefined()
    })
  })

  describe('useUpdateAlertStatus', () => {
    it('should initialize with correct mutation structure', () => {
      const { result } = renderHook(() => useUpdateAlertStatus())

      // Mutation should have expected properties
      expect(result.current).toHaveProperty('mutate')
      expect(result.current).toHaveProperty('mutateAsync')
      expect(result.current).toHaveProperty('isPending')
      expect(result.current).toHaveProperty('isSuccess')
      expect(result.current).toHaveProperty('isError')
      expect(result.current).toHaveProperty('data')
      expect(result.current).toHaveProperty('error')
    })

    it('should have mutation function', () => {
      const { result } = renderHook(() => useUpdateAlertStatus())

      // Mutation functions should exist
      expect(result.current.mutate).toBeDefined()
      expect(typeof result.current.mutate).toBe('function')
      expect(typeof result.current.mutateAsync).toBe('function')
    })

    it('should have correct initial state', () => {
      const { result } = renderHook(() => useUpdateAlertStatus())

      // Initially should not be pending
      expect(result.current.isPending).toBe(false)
      expect(result.current.isSuccess).toBe(false)
      expect(result.current.isError).toBe(false)
      expect(result.current.data).toBeUndefined()
    })
  })

  describe('Hook Types and Interfaces', () => {
    it('should have properly typed query hooks', () => {
      const { result: summaryResult } = renderHook(() => useDashboardSummary())
      const { result: alertsResult } = renderHook(() => useActiveAlerts())

      // Verify both hooks return query-like objects
      expect('isLoading' in summaryResult.current).toBe(true)
      expect('isLoading' in alertsResult.current).toBe(true)
    })

    it('should have properly typed mutation hooks', () => {
      const { result } = renderHook(() => useUpdateAlertStatus())

      // Verify mutation object structure
      expect('mutate' in result.current).toBe(true)
      expect('isPending' in result.current).toBe(true)
    })
  })
})
