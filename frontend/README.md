# Julius Baer Agentic AI AML Platform - Frontend

A modern Next.js application for real-time AML monitoring and document corroboration with AI-powered analysis.

## Features

- **Real-Time AML Monitoring Dashboard**
  - KPI cards showing active alerts, critical cases, and resolution times
  - Interactive charts for risk visualization
  - Alert triage queue with detailed information

- **Investigation Cockpit**
  - Detailed transaction analysis
  - AI-powered document forensics
  - Multi-agent findings (Regulatory Watcher, Transaction Analyst, Document Forensics)
  - Historical transaction context
  - Audit trail management

## Tech Stack

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **TailwindCSS** - Utility-first styling
- **shadcn/ui** - High-quality React components
- **Recharts** - Data visualization
- **React Query** - Data fetching and caching

## Getting Started

### Prerequisites

- Node.js 18+ installed
- npm or yarn package manager

### Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create environment variables:
```bash
# .env.local is already created with default values
# Update if needed:
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

4. Run the development server:
```bash
npm run dev
```

5. Open your browser and navigate to:
```
http://localhost:3000
```

### Build for Production

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── app/
│   ├── page.tsx                          # Main dashboard
│   ├── investigation/[alertId]/page.tsx  # Investigation cockpit
│   ├── layout.tsx                        # Root layout
│   ├── providers.tsx                     # React Query provider
│   └── globals.css                       # Global styles
├── components/
│   ├── dashboard/
│   │   ├── AlertBanner.tsx              # Critical alert banner
│   │   ├── KPICard.tsx                  # KPI metric cards
│   │   └── AlertTriageTable.tsx         # Alert table
│   ├── investigation/
│   │   ├── TransactionDetails.tsx       # Transaction info panel
│   │   ├── DocumentViewer.tsx           # Document forensics viewer
│   │   ├── AgentFindings.tsx            # AI agent findings
│   │   └── HistoricalContext.tsx        # Transaction history chart
│   ├── charts/
│   │   ├── PieChart.tsx                 # Pie chart component
│   │   └── LineChart.tsx                # Line chart component
│   └── ui/                              # shadcn/ui components
├── lib/
│   ├── api.ts                           # API client and types
│   ├── mock-data.ts                     # Mock data for development
│   └── utils.ts                         # Utility functions
└── types/
    └── index.ts                         # TypeScript type definitions
```

## Key Pages

### Dashboard (`/`)
- Overview of all active AML alerts
- KPI metrics and trends
- Risk level distribution
- Transaction volume trends
- Alert triage queue

### Investigation Cockpit (`/investigation/[alertId]`)
- Detailed alert investigation
- Transaction details and risk scoring
- AI-powered document analysis
- Multi-agent findings
- Historical transaction context
- Remediation actions

## Mock Data

The application currently uses mock data for development. When the backend is ready:

1. Update the API client in `lib/api.ts` to use real endpoints
2. Replace mock data imports with actual API calls using React Query
3. Configure WebSocket connections for real-time updates

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |
| `NEXT_PUBLIC_WS_URL` | WebSocket URL | `ws://localhost:8000` |

## Development Notes

- The application uses mock data by default
- All components are built with TypeScript for type safety
- Charts are responsive and interactive
- The UI follows Julius Baer's professional banking aesthetic
- Components are modular and reusable

## Next Steps

1. **Backend Integration**: Connect to FastAPI backend when ready
2. **Real-Time Features**: Implement WebSocket connections for live updates
3. **Authentication**: Add user authentication and role-based access
4. **Testing**: Add unit and integration tests
5. **Performance**: Optimize with React Server Components where applicable

## License

Proprietary - Julius Baer
