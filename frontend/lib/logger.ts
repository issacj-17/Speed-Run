/**
 * Frontend logging utility for Speed-Run application.
 * Provides console logging with colors and file-based logging to localStorage.
 */

type LogLevel = 'DEBUG' | 'INFO' | 'WARN' | 'ERROR'

interface LogEntry {
  timestamp: string
  level: LogLevel
  component: string
  message: string
  data?: any
}

class Logger {
  private static instance: Logger
  private logs: LogEntry[] = []
  private readonly MAX_LOGS = 1000
  private readonly STORAGE_KEY = 'speedrun_frontend_logs'
  private sessionId: string

  // Color codes for console
  private readonly colors = {
    DEBUG: '#6B7280',    // Gray
    INFO: '#10B981',     // Green
    WARN: '#F59E0B',     // Orange
    ERROR: '#EF4444',    // Red
  }

  private readonly emojis = {
    DEBUG: '🔍',
    INFO: 'ℹ️',
    WARN: '⚠️',
    ERROR: '❌',
  }

  private constructor() {
    this.sessionId = this.generateSessionId()
    this.loadLogsFromStorage()

    // Log session start
    this.info('Logger', 'Frontend logging session started', { sessionId: this.sessionId })
  }

  public static getInstance(): Logger {
    if (!Logger.instance) {
      Logger.instance = new Logger()
    }
    return Logger.instance
  }

  private generateSessionId(): string {
    const timestamp = Date.now()
    const random = Math.random().toString(36).substring(7)
    return `session_${timestamp}_${random}`
  }

  private loadLogsFromStorage(): void {
    if (typeof window === 'undefined') return

    try {
      const stored = localStorage.getItem(this.STORAGE_KEY)
      if (stored) {
        this.logs = JSON.parse(stored)
      }
    } catch (error) {
      console.warn('Failed to load logs from storage:', error)
    }
  }

  private saveLogsToStorage(): void {
    if (typeof window === 'undefined') return

    try {
      // Keep only the most recent logs
      const recentLogs = this.logs.slice(-this.MAX_LOGS)
      // Ensure proper UTF-8 encoding when stringifying
      const jsonString = JSON.stringify(recentLogs)
      localStorage.setItem(this.STORAGE_KEY, jsonString)
    } catch (error) {
      console.warn('Failed to save logs to storage:', error)
    }
  }

  private log(level: LogLevel, component: string, message: string, data?: any): void {
    const timestamp = new Date().toISOString()

    // Ensure all strings are valid UTF-8 by sanitizing
    const sanitizedMessage = this.sanitizeString(message)
    const sanitizedComponent = this.sanitizeString(component)

    // Sanitize data field to ensure UTF-8 compatibility
    const sanitizedData = data ? this.sanitizeData(data) : undefined

    const entry: LogEntry = {
      timestamp,
      level,
      component: sanitizedComponent,
      message: sanitizedMessage,
      data: sanitizedData,
    }

    // Add to logs array
    this.logs.push(entry)

    // Save to localStorage
    this.saveLogsToStorage()

    // Console output with colors
    this.consoleLog(entry)
  }

  private sanitizeString(str: string): string {
    // Ensure string is valid UTF-8 by encoding/decoding
    try {
      const encoder = new TextEncoder()
      const decoder = new TextDecoder('utf-8', { fatal: false })
      const bytes = encoder.encode(str)
      return decoder.decode(bytes)
    } catch (error) {
      // If sanitization fails, return original string
      return str
    }
  }

  private sanitizeData(data: any): any {
    // Recursively sanitize data to ensure UTF-8 compatibility
    try {
      if (typeof data === 'string') {
        return this.sanitizeString(data)
      } else if (Array.isArray(data)) {
        return data.map(item => this.sanitizeData(item))
      } else if (data !== null && typeof data === 'object') {
        const sanitized: Record<string, any> = {}
        for (const [key, value] of Object.entries(data)) {
          sanitized[this.sanitizeString(key)] = this.sanitizeData(value)
        }
        return sanitized
      }
      return data
    } catch (error) {
      // If sanitization fails, return string representation
      return String(data)
    }
  }

  private consoleLog(entry: LogEntry): void {
    const emoji = this.emojis[entry.level]
    const color = this.colors[entry.level]
    const time = new Date(entry.timestamp).toLocaleTimeString()

    const message = `${emoji} [${entry.level}] ${time} [${entry.component}] ${entry.message}`

    // Use appropriate console method
    switch (entry.level) {
      case 'DEBUG':
        console.debug(`%c${message}`, `color: ${color}`, entry.data || '')
        break
      case 'INFO':
        console.log(`%c${message}`, `color: ${color}`, entry.data || '')
        break
      case 'WARN':
        console.warn(`%c${message}`, `color: ${color}`, entry.data || '')
        break
      case 'ERROR':
        console.error(`%c${message}`, `color: ${color}`, entry.data || '')
        break
    }
  }

  // Public logging methods
  public debug(component: string, message: string, data?: any): void {
    this.log('DEBUG', component, message, data)
  }

  public info(component: string, message: string, data?: any): void {
    this.log('INFO', component, message, data)
  }

  public warn(component: string, message: string, data?: any): void {
    this.log('WARN', component, message, data)
  }

  public error(component: string, message: string, data?: any): void {
    this.log('ERROR', component, message, data)
  }

  // Utility methods
  public getLogs(level?: LogLevel): LogEntry[] {
    if (level) {
      return this.logs.filter(log => log.level === level)
    }
    return this.logs
  }

  public clearLogs(): void {
    this.logs = []
    if (typeof window !== 'undefined') {
      localStorage.removeItem(this.STORAGE_KEY)
    }
    this.info('Logger', 'Logs cleared')
  }

  public downloadLogs(): void {
    if (typeof window === 'undefined') return

    const timestamp = Date.now()

    // Ensure all log entries are properly sanitized before stringifying
    const logsText = this.logs.map(log => {
      const dataStr = log.data
        ? ' | Data: ' + JSON.stringify(log.data, null, 2)
        : ''
      return `[${log.timestamp}] [${log.level}] [${log.component}] ${log.message}${dataStr}`
    }).join('\n')

    // Add UTF-8 BOM (Byte Order Mark) to ensure proper encoding detection
    const BOM = '\uFEFF'
    const content = BOM + logsText

    // Explicitly specify UTF-8 encoding for the blob
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `speedrun-frontend-logs-${timestamp}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)

    this.info('Logger', 'Logs downloaded')
  }

  public getSessionId(): string {
    return this.sessionId
  }
}

// Export singleton instance
export const logger = Logger.getInstance()

// Export class for testing
export { Logger }
export type { LogLevel, LogEntry }
