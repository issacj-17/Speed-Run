# Frontend Testing Documentation

## Overview

This document provides comprehensive information about the testing infrastructure for the Speed-Run frontend application.

## Testing Stack

- **Test Runner**: Vitest (fast, modern test runner with excellent TypeScript support)
- **Testing Library**: React Testing Library (for component testing)
- **Assertion Library**: Vitest's built-in assertions + @testing-library/jest-dom
- **Mocking**: MSW (Mock Service Worker) for API mocking
- **Coverage**: v8 coverage provider

## Test Structure

```
frontend/
├── __tests__/
│   └── integration/           # Integration and E2E tests
│       ├── compliance-flow.test.tsx
│       └── document-analysis-flow.test.tsx
├── components/
│   ├── dashboard/
│   │   ├── KPICard.test.tsx
│   │   ├── LoadingState.test.tsx
│   │   └── AlertBanner.test.tsx
│   ├── compliance/
│   │   └── RiskScoreCard.test.tsx
│   └── ErrorBoundary.test.tsx
├── lib/
│   └── logger.test.ts         # Utility tests
└── test/
    └── setup.ts               # Global test setup
```

## Running Tests

### All Tests
```bash
npm test
# or
npm run test:watch  # Watch mode
```

### Specific Test File
```bash
npm test -- logger.test.ts
```

### With Coverage
```bash
npm run test:coverage
```

### UI Mode (Interactive)
```bash
npm run test:ui
```

### Run Once (CI/CD)
```bash
npm run test:run
```

## Test Categories

### 1. Unit Tests

Test individual components and utilities in isolation.

**Examples:**
- `lib/logger.test.ts` - Logger utility tests
- `components/ui/*.test.tsx` - UI component tests
- `components/dashboard/*.test.tsx` - Dashboard component tests

**What they test:**
- Component rendering
- Props handling
- State management
- User interactions
- Edge cases

### 2. Integration Tests

Test multiple components working together and complete user flows.

**Examples:**
- `__tests__/integration/compliance-flow.test.tsx`
- `__tests__/integration/document-analysis-flow.test.tsx`

**What they test:**
- Complete user workflows
- Component interactions
- API integration
- Navigation flows
- Error handling across components

## Test Coverage Goals

- **Statements**: > 80%
- **Branches**: > 75%
- **Functions**: > 80%
- **Lines**: > 80%

## Writing Tests

### Test Naming Convention

```typescript
describe('ComponentName', () => {
  it('should do something specific', () => {
    // Test implementation
  })
})
```

### Component Test Template

```typescript
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { YourComponent } from './YourComponent'

describe('YourComponent', () => {
  it('should render correctly', () => {
    render(<YourComponent prop="value" />)

    expect(screen.getByText('Expected Text')).toBeInTheDocument()
  })

  it('should handle user interactions', async () => {
    const user = userEvent.setup()
    render(<YourComponent />)

    const button = screen.getByRole('button', { name: /click me/i })
    await user.click(button)

    expect(screen.getByText('Result')).toBeInTheDocument()
  })
})
```

### Integration Test Template

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'

describe('User Flow Name', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should complete the workflow', async () => {
    // Setup
    // Action
    // Assert
  })
})
```

## Best Practices

### 1. Test User Behavior, Not Implementation

❌ Bad:
```typescript
expect(component.state.count).toBe(1)
```

✅ Good:
```typescript
expect(screen.getByText('Count: 1')).toBeInTheDocument()
```

### 2. Use Semantic Queries

Priority order:
1. `getByRole` (most accessible)
2. `getByLabelText`
3. `getByPlaceholderText`
4. `getByText`
5. `getByTestId` (last resort)

### 3. Async Testing

Always use `waitFor` or `findBy*` queries for async operations:

```typescript
await waitFor(() => {
  expect(screen.getByText('Loaded')).toBeInTheDocument()
})
```

### 4. Mock External Dependencies

```typescript
import { vi } from 'vitest'

vi.mock('@/lib/api', () => ({
  fetchData: vi.fn(() => Promise.resolve({ data: 'mock' }))
}))
```

### 5. Clean Up After Tests

```typescript
afterEach(() => {
  vi.restoreAllMocks()
  cleanup() // Automatically called by testing-library
})
```

## Test Utilities

### Custom Render Function

For tests that need providers:

```typescript
import { render } from '@testing-library/react'
import { QueryClientProvider } from '@tanstack/react-query'

const AllTheProviders = ({ children }) => {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}

const customRender = (ui, options) =>
  render(ui, { wrapper: AllTheProviders, ...options })

export * from '@testing-library/react'
export { customRender as render }
```

## Continuous Integration

Tests run automatically on:
- Pull requests
- Pushes to main branch
- Pre-commit hooks (via pre-commit script)

## Debugging Tests

### 1. Debug Output
```typescript
import { screen } from '@testing-library/react'

// Print the DOM
screen.debug()

// Print specific element
screen.debug(screen.getByRole('button'))
```

### 2. Run in VS Code Debugger
Add breakpoints and run tests in debug mode.

### 3. Test Only Mode
```typescript
it.only('should run only this test', () => {
  // Test implementation
})
```

## Common Issues and Solutions

### Issue: "Unable to find element"

**Solution**: Use `screen.debug()` to see the actual DOM and adjust your query.

### Issue: "Act warning"

**Solution**: Wrap state updates in `act()` or use `waitFor()` for async operations.

### Issue: "Tests timeout"

**Solution**: Increase timeout or check for missing `await` statements.

```typescript
it('long running test', async () => {
  // test
}, 10000) // 10 second timeout
```

## UTF-8 Testing

The logger has special UTF-8 handling. When testing UTF-8:

```typescript
it('should handle UTF-8 characters', () => {
  logger.info('Test', 'Message with emoji 🎉 and special chars é, ñ')
  const logs = logger.getLogs()
  expect(logs[0].message).toContain('🎉')
})
```

## Resources

- [Vitest Documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/react)
- [Jest DOM Matchers](https://github.com/testing-library/jest-dom)
- [MSW Documentation](https://mswjs.io/)

## Contributing

When adding new features:
1. Write tests for new components
2. Update existing tests if behavior changes
3. Maintain test coverage above 80%
4. Run tests before committing: `npm run validate`

## Test File Checklist

- [ ] Component renders correctly
- [ ] Props are handled properly
- [ ] User interactions work as expected
- [ ] Edge cases are covered
- [ ] Error states are tested
- [ ] Loading states are tested
- [ ] Accessibility is considered
- [ ] UTF-8 characters are handled correctly
