import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { config, getApiUrl } from '@/lib/config'

describe('Configuration Module', () => {
  const originalEnv = process.env

  beforeEach(() => {
    // Reset modules to ensure clean state
    process.env = { ...originalEnv }
  })

  afterEach(() => {
    // Restore original environment
    process.env = originalEnv
  })

  describe('API Configuration', () => {
    it('should have default backend URL', () => {
      expect(config.api.BACKEND_URL).toBeDefined()
      expect(typeof config.api.BACKEND_URL).toBe('string')
    })

    it('should have default API version', () => {
      expect(config.api.API_VERSION).toBeDefined()
      expect(typeof config.api.API_VERSION).toBe('string')
    })

    it('should construct correct BASE_URL', () => {
      const baseUrl = config.api.BASE_URL
      expect(baseUrl).toContain('/api/')
      expect(baseUrl).toContain(config.api.API_VERSION)
    })

    it('should have numeric timeout value', () => {
      expect(typeof config.api.TIMEOUT).toBe('number')
      expect(config.api.TIMEOUT).toBeGreaterThan(0)
    })

    it('should have numeric retry attempts', () => {
      expect(typeof config.api.RETRY_ATTEMPTS).toBe('number')
      expect(config.api.RETRY_ATTEMPTS).toBeGreaterThanOrEqual(0)
    })
  })

  describe('Feature Flags', () => {
    it('should have boolean feature flags', () => {
      expect(typeof config.features.USE_BACKEND_API).toBe('boolean')
      expect(typeof config.features.ENABLE_DOCUMENT_UPLOAD).toBe('boolean')
      expect(typeof config.features.ENABLE_AI_DETECTION).toBe('boolean')
    })
  })

  describe('UI Configuration', () => {
    it('should have valid app name', () => {
      expect(config.ui.APP_NAME).toBeDefined()
      expect(typeof config.ui.APP_NAME).toBe('string')
      expect(config.ui.APP_NAME.length).toBeGreaterThan(0)
    })

    it('should have numeric pagination settings', () => {
      expect(typeof config.ui.ITEMS_PER_PAGE).toBe('number')
      expect(config.ui.ITEMS_PER_PAGE).toBeGreaterThan(0)
    })

    it('should have numeric auto-refresh interval', () => {
      expect(typeof config.ui.AUTO_REFRESH_INTERVAL).toBe('number')
      expect(config.ui.AUTO_REFRESH_INTERVAL).toBeGreaterThanOrEqual(0)
    })
  })

  describe('Development Configuration', () => {
    it('should have boolean debug flag', () => {
      expect(typeof config.dev.DEBUG).toBe('boolean')
    })
  })

  describe('getApiUrl utility', () => {
    it('should construct correct URL without trailing slash', () => {
      const url = getApiUrl('/test')
      expect(url).toContain('/api/')
      expect(url).toContain('/test')
      expect(url).not.toMatch(/\/\/$/) // No double slashes
    })

    it('should construct correct URL with trailing slash', () => {
      const url = getApiUrl('test/')
      expect(url).toContain('/api/')
      expect(url).toContain('test')
    })

    it('should handle empty endpoint', () => {
      const url = getApiUrl('')
      expect(url).toContain('/api/')
    })

    it('should handle root endpoint', () => {
      const url = getApiUrl('/')
      expect(url).toContain('/api/')
    })
  })

  describe('Configuration Structure', () => {
    it('should have API config object', () => {
      expect(config.api).toBeDefined()
      expect(typeof config.api).toBe('object')
    })

    it('should have features config object', () => {
      expect(config.features).toBeDefined()
      expect(typeof config.features).toBe('object')
    })

    it('should have UI config object', () => {
      expect(config.ui).toBeDefined()
      expect(typeof config.ui).toBe('object')
    })
  })
})
