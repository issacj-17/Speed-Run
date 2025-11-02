import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { KPICard } from './KPICard'
import { AlertTriangle } from 'lucide-react'

describe('KPICard', () => {
  const mockIcon = AlertTriangle

  it('should render title, value, and subtitle', () => {
    render(
      <KPICard
        title="Total Alerts"
        value={42}
        subtitle="Active this month"
        icon={mockIcon}
      />
    )

    expect(screen.getByText('Total Alerts')).toBeInTheDocument()
    expect(screen.getByText('42')).toBeInTheDocument()
    expect(screen.getByText('Active this month')).toBeInTheDocument()
  })

  it('should render string values correctly', () => {
    render(
      <KPICard
        title="Status"
        value="Completed"
        subtitle="Current state"
        icon={mockIcon}
      />
    )

    expect(screen.getByText('Completed')).toBeInTheDocument()
  })

  it('should render trend indicator when provided', () => {
    render(
      <KPICard
        title="Risk Score"
        value={75}
        subtitle="Average score"
        icon={mockIcon}
        trend={{ value: 12, isPositive: true }}
      />
    )

    expect(screen.getByText(/12% from last month/)).toBeInTheDocument()
  })

  it('should show down arrow for positive trend', () => {
    render(
      <KPICard
        title="Alerts"
        value={100}
        subtitle="Total"
        icon={mockIcon}
        trend={{ value: 15, isPositive: true }}
      />
    )

    const trendElement = screen.getByText(/15% from last month/)
    expect(trendElement).toHaveClass('text-green-600')
    expect(trendElement.textContent).toContain('↓')
  })

  it('should show up arrow for negative trend', () => {
    render(
      <KPICard
        title="Alerts"
        value={150}
        subtitle="Total"
        icon={mockIcon}
        trend={{ value: -20, isPositive: false }}
      />
    )

    const trendElement = screen.getByText(/20% from last month/)
    expect(trendElement).toHaveClass('text-red-600')
    expect(trendElement.textContent).toContain('↑')
  })

  it('should apply custom icon color', () => {
    const { container } = render(
      <KPICard
        title="Test"
        value={10}
        subtitle="Test subtitle"
        icon={mockIcon}
        iconColor="text-red-600"
      />
    )

    const iconContainer = container.querySelector('.text-red-600')
    expect(iconContainer).toBeInTheDocument()
  })

  it('should use default icon color when not provided', () => {
    const { container } = render(
      <KPICard
        title="Test"
        value={10}
        subtitle="Test subtitle"
        icon={mockIcon}
      />
    )

    const iconContainer = container.querySelector('.text-blue-600')
    expect(iconContainer).toBeInTheDocument()
  })

  it('should not render trend when not provided', () => {
    const { container } = render(
      <KPICard
        title="Test"
        value={10}
        subtitle="Test subtitle"
        icon={mockIcon}
      />
    )

    const trendText = container.textContent
    expect(trendText).not.toContain('from last month')
  })

  it('should render icon component', () => {
    const { container } = render(
      <KPICard
        title="Test"
        value={10}
        subtitle="Test subtitle"
        icon={mockIcon}
      />
    )

    const icon = container.querySelector('svg')
    expect(icon).toBeInTheDocument()
  })
})
