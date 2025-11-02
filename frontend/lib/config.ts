/**
 * Centralized Frontend Configuration
 *
 * All application configuration should be managed through environment variables.
 * This file provides typed access to configuration with sensible defaults.
 */

// ============================================================================
// API Configuration
// ============================================================================

export const API_CONFIG = {
  /**
   * Backend API base URL
   * @default "http://localhost:8000"
   */
  BACKEND_URL: process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000',

  /**
   * API version
   * @default "v1"
   */
  API_VERSION: process.env.NEXT_PUBLIC_API_VERSION || 'v1',

  /**
   * Complete API base URL (constructed from BACKEND_URL and API_VERSION)
   */
  get BASE_URL() {
    return `${this.BACKEND_URL}/api/${this.API_VERSION}`
  },

  /**
   * Request timeout in milliseconds
   * @default 30000 (30 seconds)
   */
  TIMEOUT: parseInt(process.env.NEXT_PUBLIC_API_TIMEOUT || '30000', 10),

  /**
   * Number of retry attempts for failed requests
   * @default 3
   */
  RETRY_ATTEMPTS: parseInt(process.env.NEXT_PUBLIC_API_RETRY_ATTEMPTS || '3', 10),
} as const

// ============================================================================
// Feature Flags
// ============================================================================

export const FEATURES = {
  /**
   * Enable backend API integration
   * When false, uses mock data
   * @default true
   */
  USE_BACKEND_API: process.env.NEXT_PUBLIC_USE_BACKEND_API === 'true',

  /**
   * Enable document upload functionality
   * @default true
   */
  ENABLE_DOCUMENT_UPLOAD: process.env.NEXT_PUBLIC_ENABLE_DOCUMENT_UPLOAD !== 'false',

  /**
   * Enable AI-generated image detection
   * @default true
   */
  ENABLE_AI_DETECTION: process.env.NEXT_PUBLIC_ENABLE_AI_DETECTION !== 'false',

  /**
   * Enable advanced forensic analysis
   * @default true
   */
  ENABLE_FORENSIC_ANALYSIS: process.env.NEXT_PUBLIC_ENABLE_FORENSIC_ANALYSIS !== 'false',

  /**
   * Enable reverse image search
   * @default false (requires API keys)
   */
  ENABLE_REVERSE_IMAGE_SEARCH: process.env.NEXT_PUBLIC_ENABLE_REVERSE_IMAGE_SEARCH === 'true',

  /**
   * Enable real-time alerts
   * @default true
   */
  ENABLE_REALTIME_ALERTS: process.env.NEXT_PUBLIC_ENABLE_REALTIME_ALERTS !== 'false',

  /**
   * Enable drag-and-drop Kanban board
   * @default true
   */
  ENABLE_KANBAN_BOARD: process.env.NEXT_PUBLIC_ENABLE_KANBAN_BOARD !== 'false',
} as const

// ============================================================================
// UI Configuration
// ============================================================================

export const UI_CONFIG = {
  /**
   * Application name
   * @default "Speed-Run AML Platform"
   */
  APP_NAME: process.env.NEXT_PUBLIC_APP_NAME || 'Speed-Run AML Platform',

  /**
   * Application version
   * @default "1.0.0"
   */
  APP_VERSION: process.env.NEXT_PUBLIC_APP_VERSION || '1.0.0',

  /**
   * Items per page for pagination
   * @default 10
   */
  ITEMS_PER_PAGE: parseInt(process.env.NEXT_PUBLIC_ITEMS_PER_PAGE || '10', 10),

  /**
   * Auto-refresh interval for dashboards (in milliseconds)
   * @default 30000 (30 seconds)
   * Set to 0 to disable auto-refresh
   */
  AUTO_REFRESH_INTERVAL: parseInt(process.env.NEXT_PUBLIC_AUTO_REFRESH_INTERVAL || '30000', 10),

  /**
   * Maximum file size for uploads (in bytes)
   * @default 10485760 (10MB)
   */
  MAX_FILE_SIZE: parseInt(process.env.NEXT_PUBLIC_MAX_FILE_SIZE || '10485760', 10),

  /**
   * Allowed file extensions for document upload
   * @default [".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".docx"]
   */
  ALLOWED_FILE_TYPES: (process.env.NEXT_PUBLIC_ALLOWED_FILE_TYPES || '.pdf,.png,.jpg,.jpeg,.tiff,.bmp,.docx').split(','),
} as const

// ============================================================================
// Development & Debugging
// ============================================================================

export const DEV_CONFIG = {
  /**
   * Enable debug mode (more verbose logging)
   * @default false
   */
  DEBUG: process.env.NEXT_PUBLIC_DEBUG === 'true',

  /**
   * Enable development tools in production
   * @default false
   */
  ENABLE_DEV_TOOLS: process.env.NEXT_PUBLIC_ENABLE_DEV_TOOLS === 'true',

  /**
   * Log API requests and responses
   * @default false in production, true in development
   */
  LOG_API_CALLS: process.env.NEXT_PUBLIC_LOG_API_CALLS === 'true' || process.env.NODE_ENV === 'development',

  /**
   * Show performance metrics
   * @default false
   */
  SHOW_PERFORMANCE_METRICS: process.env.NEXT_PUBLIC_SHOW_PERFORMANCE_METRICS === 'true',
} as const

// ============================================================================
// Authentication (Placeholder for future implementation)
// ============================================================================

export const AUTH_CONFIG = {
  /**
   * Enable authentication
   * @default false (not implemented yet)
   */
  ENABLE_AUTH: process.env.NEXT_PUBLIC_ENABLE_AUTH === 'true',

  /**
   * Session timeout in minutes
   * @default 30
   */
  SESSION_TIMEOUT: parseInt(process.env.NEXT_PUBLIC_SESSION_TIMEOUT || '30', 10),
} as const

// ============================================================================
// Export all config
// ============================================================================

export const config = {
  api: API_CONFIG,
  features: FEATURES,
  ui: UI_CONFIG,
  dev: DEV_CONFIG,
  auth: AUTH_CONFIG,
} as const

export default config

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Check if the application is running in development mode
 */
export const isDevelopment = () => process.env.NODE_ENV === 'development'

/**
 * Check if the application is running in production mode
 */
export const isProduction = () => process.env.NODE_ENV === 'production'

/**
 * Get the full API endpoint URL
 */
export const getApiUrl = (endpoint: string) => {
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint
  return `${API_CONFIG.BASE_URL}/${cleanEndpoint}`
}

/**
 * Validate configuration on startup
 */
export const validateConfig = () => {
  const errors: string[] = []

  // Validate API URL
  try {
    new URL(API_CONFIG.BACKEND_URL)
  } catch {
    errors.push(`Invalid NEXT_PUBLIC_BACKEND_URL: ${API_CONFIG.BACKEND_URL}`)
  }

  // Validate numeric values
  if (API_CONFIG.TIMEOUT <= 0) {
    errors.push('NEXT_PUBLIC_API_TIMEOUT must be a positive number')
  }

  if (UI_CONFIG.MAX_FILE_SIZE <= 0) {
    errors.push('NEXT_PUBLIC_MAX_FILE_SIZE must be a positive number')
  }

  // Log errors if in development
  if (errors.length > 0 && isDevelopment()) {
    console.error('Configuration validation errors:', errors)
  }

  return errors.length === 0
}

// Validate config on module load
if (typeof window !== 'undefined' && DEV_CONFIG.DEBUG) {
  console.log('Frontend Configuration:', config)
  validateConfig()
}
