import '@testing-library/jest-dom'
import { afterEach, beforeAll } from 'vitest'
import { cleanup } from '@testing-library/react'

// Mock localStorage for tests
const localStorageMock = (() => {
  let store: Record<string, string> = {}

  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value.toString()
    },
    removeItem: (key: string) => {
      delete store[key]
    },
    clear: () => {
      store = {}
    },
  }
})()

// Setup global mocks before all tests
beforeAll(() => {
  Object.defineProperty(global, 'localStorage', {
    value: localStorageMock,
    writable: true,
  })
})

// Reset any request handlers that we may add during the tests,
// so they don't affect other tests
afterEach(() => {
  cleanup()
  localStorageMock.clear()
})
