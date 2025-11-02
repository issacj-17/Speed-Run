import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { RiskScoreCard } from './RiskScoreCard'

describe('RiskScoreCard', () => {
  const mockBreakdown = {
    document_risk: 15,
    geographic_risk: 10,
    client_profile_risk: 8,
    transaction_risk: 5,
  }

  describe('Risk Level Classification', () => {
    it('should display Critical risk for score >= 86', () => {
      render(<RiskScoreCard score={90} breakdown={mockBreakdown} />)

      expect(screen.getByText('90')).toBeInTheDocument()
      expect(screen.getByText('Critical Risk')).toBeInTheDocument()
    })

    it('should display High risk for score 71-85', () => {
      render(<RiskScoreCard score={75} breakdown={mockBreakdown} />)

      expect(screen.getByText('75')).toBeInTheDocument()
      expect(screen.getByText('High Risk')).toBeInTheDocument()
    })

    it('should display Medium risk for score 41-70', () => {
      render(<RiskScoreCard score={55} breakdown={mockBreakdown} />)

      expect(screen.getByText('55')).toBeInTheDocument()
      expect(screen.getByText('Medium Risk')).toBeInTheDocument()
    })

    it('should display Low risk for score <= 40', () => {
      render(<RiskScoreCard score={30} breakdown={mockBreakdown} />)

      expect(screen.getByText('30')).toBeInTheDocument()
      expect(screen.getByText('Low Risk')).toBeInTheDocument()
    })
  })

  describe('Risk Breakdown Display', () => {
    it('should display document risk score', () => {
      render(<RiskScoreCard score={50} breakdown={mockBreakdown} />)

      expect(screen.getByText('Document Risk')).toBeInTheDocument()
      expect(screen.getByText('15/40')).toBeInTheDocument()
      expect(screen.getByText(/Tampering, missing fields/i)).toBeInTheDocument()
    })

    it('should display geographic risk score', () => {
      render(<RiskScoreCard score={50} breakdown={mockBreakdown} />)

      expect(screen.getByText('Geographic Risk')).toBeInTheDocument()
      expect(screen.getByText('10/30')).toBeInTheDocument()
      expect(screen.getByText(/High-risk jurisdictions/i)).toBeInTheDocument()
    })

    it('should display client profile risk score', () => {
      render(<RiskScoreCard score={50} breakdown={mockBreakdown} />)

      expect(screen.getByText('Client Profile Risk')).toBeInTheDocument()
      expect(screen.getByText('8/20')).toBeInTheDocument()
      expect(screen.getByText(/PEP status/i)).toBeInTheDocument()
    })

    it('should display transaction risk score', () => {
      render(<RiskScoreCard score={50} breakdown={mockBreakdown} />)

      expect(screen.getByText('Transaction Risk')).toBeInTheDocument()
      expect(screen.getByText('5/10')).toBeInTheDocument()
      expect(screen.getByText(/Large amounts/i)).toBeInTheDocument()
    })
  })

  describe('Visual Elements', () => {
    it('should render title with emoji', () => {
      render(<RiskScoreCard score={50} breakdown={mockBreakdown} />)

      expect(screen.getByText(/📊 Risk Score Assessment/)).toBeInTheDocument()
    })

    it('should display "out of 100" text', () => {
      render(<RiskScoreCard score={50} breakdown={mockBreakdown} />)

      expect(screen.getByText('out of 100')).toBeInTheDocument()
    })

    it('should render explanation section', () => {
      render(<RiskScoreCard score={50} breakdown={mockBreakdown} />)

      expect(screen.getByText(/How is this score assigned?/)).toBeInTheDocument()
      expect(screen.getByText(/calculated based on four key categories/i)).toBeInTheDocument()
    })

    it('should display risk level guide', () => {
      render(<RiskScoreCard score={50} breakdown={mockBreakdown} />)

      expect(screen.getByText('Risk Level Guide:')).toBeInTheDocument()
      expect(screen.getByText('0-40: Low Risk')).toBeInTheDocument()
      expect(screen.getByText('41-70: Medium Risk')).toBeInTheDocument()
      expect(screen.getByText('71-85: High Risk')).toBeInTheDocument()
      expect(screen.getByText('86-100: Critical Risk')).toBeInTheDocument()
    })
  })

  describe('Styling', () => {
    it('should apply critical styling for high scores', () => {
      const { container } = render(<RiskScoreCard score={90} breakdown={mockBreakdown} />)

      const card = container.querySelector('.border-red-300')
      expect(card).toBeInTheDocument()
      expect(card).toHaveClass('bg-red-50')
    })

    it('should apply medium styling for mid-range scores', () => {
      const { container } = render(<RiskScoreCard score={50} breakdown={mockBreakdown} />)

      const card = container.querySelector('.border-yellow-300')
      expect(card).toBeInTheDocument()
      expect(card).toHaveClass('bg-yellow-50')
    })

    it('should apply low risk styling for low scores', () => {
      const { container } = render(<RiskScoreCard score={25} breakdown={mockBreakdown} />)

      const card = container.querySelector('.border-green-300')
      expect(card).toBeInTheDocument()
      expect(card).toHaveClass('bg-green-50')
    })
  })

  describe('Progress Bars', () => {
    it('should render progress bars for all risk categories', () => {
      const { container } = render(<RiskScoreCard score={50} breakdown={mockBreakdown} />)

      // Should have 4 progress bars (one for each risk category)
      const progressBars = container.querySelectorAll('[role="progressbar"]')
      expect(progressBars.length).toBe(4)
    })
  })

  describe('Zero Risk Scores', () => {
    it('should handle zero risk scores correctly', () => {
      const zeroBreakdown = {
        document_risk: 0,
        geographic_risk: 0,
        client_profile_risk: 0,
        transaction_risk: 0,
      }

      render(<RiskScoreCard score={0} breakdown={zeroBreakdown} />)

      expect(screen.getByText('0')).toBeInTheDocument()
      expect(screen.getByText('Low Risk')).toBeInTheDocument()
      expect(screen.getByText('0/40')).toBeInTheDocument()
      expect(screen.getByText('0/30')).toBeInTheDocument()
      expect(screen.getByText('0/20')).toBeInTheDocument()
      expect(screen.getByText('0/10')).toBeInTheDocument()
    })
  })

  describe('Maximum Risk Scores', () => {
    it('should handle maximum risk scores correctly', () => {
      const maxBreakdown = {
        document_risk: 40,
        geographic_risk: 30,
        client_profile_risk: 20,
        transaction_risk: 10,
      }

      render(<RiskScoreCard score={100} breakdown={maxBreakdown} />)

      expect(screen.getByText('100')).toBeInTheDocument()
      expect(screen.getByText('Critical Risk')).toBeInTheDocument()
      expect(screen.getByText('40/40')).toBeInTheDocument()
      expect(screen.getByText('30/30')).toBeInTheDocument()
      expect(screen.getByText('20/20')).toBeInTheDocument()
      expect(screen.getByText('10/10')).toBeInTheDocument()
    })
  })
})
