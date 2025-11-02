import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { Logger, LogLevel } from './logger'

describe('Logger', () => {
  let logger: Logger
  let consoleDebugSpy: any
  let consoleLogSpy: any
  let consoleWarnSpy: any
  let consoleErrorSpy: any

  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear()

    // Reset the singleton instance
    // @ts-expect-error - accessing private static field for testing
    Logger.instance = undefined

    // Spy on console methods
    consoleDebugSpy = vi.spyOn(console, 'debug').mockImplementation(() => {})
    consoleLogSpy = vi.spyOn(console, 'log').mockImplementation(() => {})
    consoleWarnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})
    consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

    logger = Logger.getInstance()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('Singleton Pattern', () => {
    it('should return the same instance', () => {
      const instance1 = Logger.getInstance()
      const instance2 = Logger.getInstance()
      expect(instance1).toBe(instance2)
    })

    it('should have a unique session ID', () => {
      const sessionId = logger.getSessionId()
      expect(sessionId).toMatch(/^session_\d+_[a-z0-9]+$/)
    })
  })

  describe('Logging Methods', () => {
    it('should log debug messages', () => {
      logger.debug('TestComponent', 'Debug message', { foo: 'bar' })
      expect(consoleDebugSpy).toHaveBeenCalled()

      const logs = logger.getLogs()
      expect(logs).toHaveLength(2) // 1 from constructor + 1 from debug call

      const lastLog = logs[logs.length - 1]
      expect(lastLog.level).toBe('DEBUG')
      expect(lastLog.component).toBe('TestComponent')
      expect(lastLog.message).toBe('Debug message')
      expect(lastLog.data).toEqual({ foo: 'bar' })
    })

    it('should log info messages', () => {
      logger.info('TestComponent', 'Info message')
      expect(consoleLogSpy).toHaveBeenCalled()

      const logs = logger.getLogs('INFO')
      expect(logs.length).toBeGreaterThan(0)

      const lastInfoLog = logs[logs.length - 1]
      expect(lastInfoLog.level).toBe('INFO')
      expect(lastInfoLog.message).toBe('Info message')
    })

    it('should log warning messages', () => {
      logger.warn('TestComponent', 'Warning message')
      expect(consoleWarnSpy).toHaveBeenCalled()

      const logs = logger.getLogs('WARN')
      expect(logs.length).toBeGreaterThan(0)
      expect(logs[logs.length - 1].level).toBe('WARN')
    })

    it('should log error messages', () => {
      logger.error('TestComponent', 'Error message', new Error('Test error'))
      expect(consoleErrorSpy).toHaveBeenCalled()

      const logs = logger.getLogs('ERROR')
      expect(logs.length).toBeGreaterThan(0)
      expect(logs[logs.length - 1].level).toBe('ERROR')
    })
  })

  describe('UTF-8 Handling', () => {
    it('should handle UTF-8 emojis correctly', () => {
      logger.info('TestComponent', 'Message with emoji 🎉')
      const logs = logger.getLogs()
      const lastLog = logs[logs.length - 1]
      expect(lastLog.message).toBe('Message with emoji 🎉')
    })

    it('should sanitize strings correctly', () => {
      // Test with various special characters
      logger.info('TestComponent', 'Special chars: ñ, é, 中文, العربية')
      const logs = logger.getLogs()
      const lastLog = logs[logs.length - 1]
      expect(lastLog.message).toContain('Special chars')
    })
  })

  describe('Log Storage', () => {
    it('should persist logs to localStorage', () => {
      logger.info('TestComponent', 'Persistent message')

      const stored = localStorage.getItem('speedrun_frontend_logs')
      expect(stored).not.toBeNull()

      const parsedLogs = JSON.parse(stored!)
      expect(Array.isArray(parsedLogs)).toBe(true)
      expect(parsedLogs.length).toBeGreaterThan(0)
    })

    it('should load logs from localStorage on initialization', () => {
      // Store some logs
      logger.info('TestComponent', 'Message 1')
      logger.info('TestComponent', 'Message 2')

      // Create a new logger instance
      // @ts-expect-error - accessing private static field for testing
      Logger.instance = undefined
      const newLogger = Logger.getInstance()

      const logs = newLogger.getLogs()
      // Should have logs from previous instance plus constructor log from new instance
      expect(logs.length).toBeGreaterThanOrEqual(2)
    })

    it('should limit stored logs to MAX_LOGS', () => {
      // Add many logs
      for (let i = 0; i < 1500; i++) {
        logger.info('TestComponent', `Message ${i}`)
      }

      const stored = localStorage.getItem('speedrun_frontend_logs')
      const parsedLogs = JSON.parse(stored!)

      // Should not exceed MAX_LOGS (1000)
      expect(parsedLogs.length).toBeLessThanOrEqual(1000)
    })
  })

  describe('Log Filtering', () => {
    it('should filter logs by level', () => {
      logger.debug('TestComponent', 'Debug message')
      logger.info('TestComponent', 'Info message')
      logger.warn('TestComponent', 'Warn message')
      logger.error('TestComponent', 'Error message')

      expect(logger.getLogs('DEBUG').length).toBeGreaterThanOrEqual(1)
      expect(logger.getLogs('INFO').length).toBeGreaterThanOrEqual(1)
      expect(logger.getLogs('WARN').length).toBe(1)
      expect(logger.getLogs('ERROR').length).toBe(1)
    })

    it('should return all logs when no filter is specified', () => {
      logger.info('TestComponent', 'Message 1')
      logger.warn('TestComponent', 'Message 2')

      const allLogs = logger.getLogs()
      expect(allLogs.length).toBeGreaterThanOrEqual(2)
    })
  })

  describe('Clear Logs', () => {
    it('should clear all logs', () => {
      logger.info('TestComponent', 'Message 1')
      logger.info('TestComponent', 'Message 2')

      logger.clearLogs()

      const logs = logger.getLogs()
      // Should only have the "Logs cleared" message
      expect(logs.length).toBe(1)
      expect(logs[0].message).toBe('Logs cleared')
    })

    it('should remove logs from localStorage', () => {
      logger.info('TestComponent', 'Message')
      expect(localStorage.getItem('speedrun_frontend_logs')).not.toBeNull()

      logger.clearLogs()

      // After clear, there should be a new log entry with "Logs cleared"
      const stored = localStorage.getItem('speedrun_frontend_logs')
      expect(stored).not.toBeNull()
      const parsedLogs = JSON.parse(stored!)
      expect(parsedLogs[0].message).toBe('Logs cleared')
    })
  })

  describe('Download Logs', () => {
    it('should create a download link with UTF-8 encoding', () => {
      logger.info('TestComponent', 'Message with emoji 🎉')

      // Mock document.createElement and URL methods
      const createElementSpy = vi.spyOn(document, 'createElement')
      const createObjectURLSpy = vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:mock-url')
      const revokeObjectURLSpy = vi.spyOn(URL, 'revokeObjectURL').mockImplementation(() => {})

      logger.downloadLogs()

      expect(createElementSpy).toHaveBeenCalledWith('a')
      expect(createObjectURLSpy).toHaveBeenCalled()

      // Check that the blob was created with UTF-8 charset
      const blobCall = createObjectURLSpy.mock.calls[0][0] as Blob
      expect(blobCall.type).toBe('text/plain;charset=utf-8')

      createElementSpy.mockRestore()
      createObjectURLSpy.mockRestore()
      revokeObjectURLSpy.mockRestore()
    })
  })

  describe('Console Output', () => {
    it('should include emoji, level, time, component, and message in console output', () => {
      logger.info('TestComponent', 'Test message')

      expect(consoleLogSpy).toHaveBeenCalled()
      const call = consoleLogSpy.mock.calls[consoleLogSpy.mock.calls.length - 1]
      const message = call[0]

      expect(message).toContain('ℹ️')
      expect(message).toContain('[INFO]')
      expect(message).toContain('[TestComponent]')
      expect(message).toContain('Test message')
    })

    it('should use correct console methods for each log level', () => {
      logger.debug('Test', 'Debug')
      expect(consoleDebugSpy).toHaveBeenCalled()

      logger.info('Test', 'Info')
      expect(consoleLogSpy).toHaveBeenCalled()

      logger.warn('Test', 'Warn')
      expect(consoleWarnSpy).toHaveBeenCalled()

      logger.error('Test', 'Error')
      expect(consoleErrorSpy).toHaveBeenCalled()
    })
  })

  describe('Timestamp', () => {
    it('should include ISO timestamp in log entries', () => {
      logger.info('TestComponent', 'Message')
      const logs = logger.getLogs()
      const lastLog = logs[logs.length - 1]

      expect(lastLog.timestamp).toBeDefined()
      expect(() => new Date(lastLog.timestamp)).not.toThrow()

      const timestamp = new Date(lastLog.timestamp)
      expect(timestamp.toISOString()).toBe(lastLog.timestamp)
    })
  })
})
