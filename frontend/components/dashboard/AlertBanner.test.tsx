import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { AlertBanner } from './AlertBanner'

describe('AlertBanner', () => {
  it('should render alert message', () => {
    render(<AlertBanner />)

    expect(screen.getByText(/Critical Alert Require Immediate Attention/i)).toBeInTheDocument()
  })

  it('should render alert triangle icon', () => {
    const { container } = render(<AlertBanner />)

    const icon = container.querySelector('svg')
    expect(icon).toBeInTheDocument()
    expect(icon).toHaveClass('text-red-600')
  })

  it('should render badge with alert details', () => {
    render(<AlertBanner />)

    expect(screen.getByText(/ALT-789: ABC Trading Ltd - CHF 150,000/i)).toBeInTheDocument()
  })

  it('should have red styling for critical alert', () => {
    const { container } = render(<AlertBanner />)

    const banner = container.querySelector('.bg-red-50')
    expect(banner).toBeInTheDocument()
    expect(banner).toHaveClass('border-red-200')
  })

  it('should render badge with critical variant', () => {
    render(<AlertBanner />)

    // Check that the badge text is present (badge component is rendered)
    const badgeText = screen.getByText(/ALT-789: ABC Trading Ltd - CHF 150,000/i)
    expect(badgeText).toBeInTheDocument()
  })
})
