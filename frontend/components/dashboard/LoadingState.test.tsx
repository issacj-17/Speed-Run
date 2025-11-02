import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { DashboardLoadingState } from './LoadingState'

describe('DashboardLoadingState', () => {
  it('should render loading skeletons', () => {
    const { container } = render(<DashboardLoadingState />)

    // Check for skeleton elements (using data-testid or text content matching)
    const hasSkeletons = container.innerHTML.includes('space-y-6')
    expect(hasSkeletons).toBe(true)
  })

  it('should render 4 KPI card skeletons', () => {
    const { container } = render(<DashboardLoadingState />)

    // Count cards in the first grid (KPI cards)
    const kpiGrid = container.querySelector('.grid')
    const cards = kpiGrid?.querySelectorAll('[class*="card"]') || []
    expect(cards.length).toBe(4)
  })

  it('should render chart loading placeholders', () => {
    const { container } = render(<DashboardLoadingState />)

    // Check that the component renders multiple grids (KPIs + Charts)
    const grids = container.querySelectorAll('.grid')
    expect(grids.length).toBeGreaterThanOrEqual(2)
  })

  it('should render table loading placeholder with rows', () => {
    const { container } = render(<DashboardLoadingState />)

    // Verify multiple card sections are rendered (KPIs, charts, table)
    const cards = container.querySelectorAll('[class*="card"]')
    expect(cards.length).toBeGreaterThan(5)
  })

  it('should have proper grid layout structure', () => {
    const { container } = render(<DashboardLoadingState />)

    // Check for grid containers
    const grids = container.querySelectorAll('.grid')
    expect(grids.length).toBeGreaterThan(0)
  })

  it('should render with proper spacing', () => {
    const { container } = render(<DashboardLoadingState />)

    const mainContainer = container.querySelector('.space-y-6')
    expect(mainContainer).toBeInTheDocument()
  })
})
