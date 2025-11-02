# Implementation Guide: Adding MongoDB and Groq API

This guide explains how to upgrade from mock data to production-ready MongoDB and Groq AI integration.

## Current Status ✅

The platform is **fully functional** with:
- ✅ Complete frontend UI (Next.js + TypeScript)
- ✅ Complete backend API (FastAPI + Python)
- ✅ Mock data for development
- ✅ Simulated AI agents
- ✅ WebSocket support (ready)
- ✅ All UI components and pages

## Phase 1: Add MongoDB Integration

### Step 1: Install MongoDB

**Option A: Local MongoDB**
```bash
# Download and install MongoDB Community Edition
# https://www.mongodb.com/try/download/community

# Start MongoDB service
# Windows: MongoDB starts automatically
# Mac: brew services start mongodb-community
# Linux: sudo systemctl start mongod
```

**Option B: MongoDB Atlas (Cloud)**
```bash
# Create free account at https://www.mongodb.com/cloud/atlas
# Create a cluster
# Get connection string
```

### Step 2: Update Backend Dependencies

```bash
cd backend
pip install motor==3.3.2 pymongo==4.6.1
```

### Step 3: Configure Environment

Create `backend/.env`:
```env
MONGODB_URL=mongodb://localhost:27017
# Or for Atlas:
# MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/

DATABASE_NAME=julius_baer_aml
CORS_ORIGINS=http://localhost:3000
```

### Step 4: Update Database Service

Replace `backend/services/database.py` with:

```python
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
from config import settings
import logging

logger = logging.getLogger(__name__)


class DatabaseService:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None

    @classmethod
    async def connect_db(cls):
        """Connect to MongoDB"""
        try:
            cls.client = AsyncIOMotorClient(settings.mongodb_url)
            cls.db = cls.client[settings.database_name]
            
            # Test connection
            await cls.client.admin.command('ping')
            logger.info(f"Connected to MongoDB: {settings.database_name}")
            
            # Create indexes
            await cls.create_indexes()
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    @classmethod
    async def close_db(cls):
        """Close MongoDB connection"""
        if cls.client:
            cls.client.close()
            logger.info("Closed MongoDB connection")

    @classmethod
    async def create_indexes(cls):
        """Create database indexes"""
        if cls.db is None:
            return
        
        # Alerts collection indexes
        await cls.db.alerts.create_index("alert_id", unique=True)
        await cls.db.alerts.create_index("risk_score")
        await cls.db.alerts.create_index("timestamp")
        await cls.db.alerts.create_index("status")
        
        logger.info("Database indexes created")

    @classmethod
    def get_db(cls) -> AsyncIOMotorDatabase:
        """Get database instance"""
        if cls.db is None:
            raise Exception("Database not connected")
        return cls.db


db_service = DatabaseService()
```

### Step 5: Update Config

Replace `backend/config.py` with:

```python
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "julius_baer_aml"
    cors_origins: str = "http://localhost:3000"
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
```

### Step 6: Seed Database

Create `backend/scripts/seed_database.py`:

```python
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import sys
sys.path.append('..')
from config import settings

async def seed_database():
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.database_name]
    
    # Clear existing data
    await db.alerts.delete_many({})
    
    # Insert mock alerts
    alerts = [
        {
            "alert_id": "ALT-789",
            "priority": "CRITICAL",
            "client": "ABC Trading Ltd",
            "client_id": "CLI-456",
            "type": "Integrated Alert: Transaction + Document Anomaly",
            "amount": 150000,
            "currency": "CHF",
            "risk_score": 95,
            "status": "pending",
            "timestamp": datetime.fromisoformat("2025-10-30T09:15:00"),
            "created_at": datetime.now(),
        },
        # Add more alerts...
    ]
    
    await db.alerts.insert_many(alerts)
    print(f"Seeded {len(alerts)} alerts")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_database())
```

Run: `python scripts/seed_database.py`

### Step 7: Update API Routes

Replace mock data calls with database queries in `backend/api/routes/alerts.py`:

```python
from services.database import db_service

@router.get("/active", response_model=list[Alert])
async def get_alerts():
    """Get list of active alerts from database"""
    db = db_service.get_db()
    alerts = await db.alerts.find({"status": {"$ne": "resolved"}}).to_list(100)
    return alerts
```

---

## Phase 2: Add Groq API Integration

### Step 1: Get Groq API Key

1. Visit https://console.groq.com
2. Sign up for free account
3. Generate API key
4. Copy the key

### Step 2: Install Groq SDK

```bash
cd backend
pip install groq==0.4.1
```

### Step 3: Update Environment

Add to `backend/.env`:
```env
GROQ_API_KEY=gsk_your_actual_api_key_here
```

### Step 4: Update Config

Add to `backend/config.py`:
```python
class Settings(BaseSettings):
    # ... existing fields ...
    groq_api_key: str = ""
```

### Step 5: Update Base Agent

Replace `backend/agents/base_agent.py`:

```python
from groq import Groq
from config import settings

class BaseAgent(ABC):
    def __init__(self, agent_name: str, agent_type: str):
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.groq_client = Groq(api_key=settings.groq_api_key) if settings.groq_api_key else None
    
    def _call_groq_api(self, prompt: str, model: str = "llama-3.1-70b-versatile") -> str:
        """Call Groq API for AI analysis"""
        if not self.groq_client:
            logger.warning("Groq API not configured, using mock response")
            return "Mock response"
        
        try:
            response = self.groq_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            return "Error calling AI service"
```

### Step 6: Update Agents to Use Groq

Example for `backend/agents/regulatory_watcher.py`:

```python
async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze with Groq AI"""
    
    prompt = f"""You are a Swiss banking regulatory compliance expert.

Analyze this transaction for FINMA compliance:
- Type: {data.get('transaction_type')}
- Amount: CHF {data.get('amount')}
- Client: {data.get('client')}
- Country: {data.get('country')}

Provide:
1. Priority level (critical/high/medium/low)
2. Specific finding
3. Relevant FINMA regulation if violated

Format as JSON:
{{"priority": "...", "finding": "...", "regulation": "..."}}
"""
    
    response = self._call_groq_api(prompt)
    
    # Parse JSON response
    try:
        result = json.loads(response)
        return {
            "agent_name": self.agent_name,
            "agent_type": self.agent_type,
            "priority": result.get("priority", "medium"),
            "finding": result.get("finding"),
            "regulation": result.get("regulation")
        }
    except:
        # Fallback to mock if parsing fails
        return await self.analyze_mock(data)
```

### Step 7: Test Groq Integration

```bash
cd backend
python -c "
from agents.regulatory_watcher import RegulatoryWatcherAgent
import asyncio

async def test():
    agent = RegulatoryWatcherAgent()
    result = await agent.analyze({
        'transaction_type': 'Real Estate Purchase',
        'amount': 150000,
        'client': 'ABC Trading Ltd',
        'country': 'Switzerland'
    })
    print(result)

asyncio.run(test())
"
```

---

## Phase 3: Connect Frontend to Backend

### Step 1: Update Frontend API Client

The frontend is already configured! Just ensure backend is running:

```bash
# Terminal 1: Start backend
cd backend
python main.py

# Terminal 2: Start frontend
cd frontend
npm run dev
```

### Step 2: Test Integration

1. Open http://localhost:3000
2. View dashboard (data from backend API)
3. Click "Investigate" on any alert
4. See detailed analysis

### Step 3: Enable Real-Time Updates

Add to `frontend/lib/websocket.ts`:

```typescript
export function connectWebSocket() {
  const ws = new WebSocket('ws://localhost:8000/ws/alerts');
  
  ws.onopen = () => {
    console.log('Connected to WebSocket');
  };
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
    // Handle real-time updates
  };
  
  return ws;
}
```

Use in dashboard:
```typescript
useEffect(() => {
  const ws = connectWebSocket();
  return () => ws.close();
}, []);
```

---

## Phase 4: Production Deployment

### Backend Deployment

**Option A: Docker**

Create `backend/Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Option B: Cloud Platform**
- AWS: Elastic Beanstalk or ECS
- Azure: App Service
- GCP: Cloud Run

### Frontend Deployment

```bash
cd frontend
npm run build

# Deploy to:
# - Vercel (recommended for Next.js)
# - Netlify
# - AWS Amplify
# - Azure Static Web Apps
```

### Environment Variables

**Production Backend:**
```env
MONGODB_URL=mongodb+srv://prod-cluster.mongodb.net/
DATABASE_NAME=julius_baer_aml_prod
GROQ_API_KEY=gsk_production_key
CORS_ORIGINS=https://your-domain.com
```

**Production Frontend:**
```env
NEXT_PUBLIC_API_URL=https://api.your-domain.com
NEXT_PUBLIC_WS_URL=wss://api.your-domain.com
```

---

## Testing Checklist

- [ ] MongoDB connection successful
- [ ] Database indexes created
- [ ] Mock data seeded
- [ ] API endpoints return data from MongoDB
- [ ] Groq API key configured
- [ ] AI agents return intelligent responses
- [ ] Frontend connects to backend
- [ ] Dashboard displays real data
- [ ] Investigation page works
- [ ] WebSocket connection established
- [ ] Real-time updates working

---

## Troubleshooting

### MongoDB Connection Issues
```bash
# Check MongoDB is running
mongosh

# Check connection string
echo $MONGODB_URL
```

### Groq API Issues
```bash
# Test API key
curl https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer $GROQ_API_KEY"
```

### CORS Issues
- Ensure backend CORS_ORIGINS includes frontend URL
- Check browser console for CORS errors
- Verify both services are running

---

## Support

For issues or questions:
1. Check logs: `backend/logs/` and browser console
2. Review API docs: http://localhost:8000/docs
3. Contact development team

---

**Current Status: Ready for MongoDB and Groq Integration** 🚀

