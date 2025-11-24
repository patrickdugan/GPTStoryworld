# 🚀 Vercel Postgres Backend - Complete Setup Guide
## Production-Ready PostgreSQL Backend for Job Applications

## Why This Setup is Perfect for Job Applications

### ✅ Shows Professional Skills
- **Full-stack competency**: Frontend + Backend + Database
- **Modern serverless architecture**: Edge Functions + Postgres
- **Production deployment**: Actually deployed and working
- **RESTful API design**: Industry-standard patterns
- **SQL proficiency**: Complex queries, indexes, views

### ✅ Easy for Recruiters to Evaluate
- One-click deploy from your GitHub
- Live demo URL they can test immediately
- Clean, documented API endpoints
- Professional README with architecture diagram

### ✅ Technical Depth
- Database schema design
- API route handlers
- Edge compute optimization
- Performance indexes
- ACID compliance

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────┐
│   React Frontend (Vercel Edge)          │
│   - UI for generating storyworlds       │
│   - Browse/gallery pages                │
│   - Real-time updates                   │
└───────────┬─────────────────────────────┘
            │
            │ HTTPS/JSON
            │
┌───────────▼─────────────────────────────┐
│   Vercel Edge Functions (API Routes)    │
│                                          │
│   POST   /api/storyworlds               │
│   GET    /api/storyworlds               │
│   GET    /api/storyworlds/[id]          │
│   PATCH  /api/storyworlds/[id]          │
│   DELETE /api/storyworlds/[id]          │
│   POST   /api/storyworlds/[id]/like     │
│   GET    /api/stats                     │
└───────────┬─────────────────────────────┘
            │
            │ Vercel Postgres SDK (@vercel/postgres)
            │
┌───────────▼─────────────────────────────┐
│   Vercel Postgres (Neon-powered)        │
│                                          │
│   ┌────────────────────────────────┐    │
│   │ storyworlds table              │    │
│   │ - Full JSONB support           │    │
│   │ - Indexes for performance      │    │
│   │ - Triggers for timestamps      │    │
│   └────────────────────────────────┘    │
│                                          │
│   ┌────────────────────────────────┐    │
│   │ Views & Analytics              │    │
│   │ - public_storyworlds           │    │
│   │ - storyworld_analytics         │    │
│   └────────────────────────────────┘    │
└──────────────────────────────────────────┘
```

---

## 📦 Step 1: Setup Vercel Postgres (5 minutes)

### 1.1 Create Vercel Account
```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login
```

### 1.2 Create Postgres Database

**Option A: Via Vercel Dashboard**
1. Go to https://vercel.com/dashboard
2. Select your project (or create new)
3. Go to "Storage" tab
4. Click "Create Database"
5. Select "Postgres"
6. Choose region (same as your project)
7. Click "Create"

**Option B: Via CLI**
```bash
vercel postgres create gpt-storyworld-db
```

### 1.3 Get Connection Details

The Vercel CLI will automatically set these environment variables:
- `POSTGRES_URL` - Full connection string
- `POSTGRES_PRISMA_URL` - For Prisma (if using)
- `POSTGRES_URL_NON_POOLING` - Direct connection
- `POSTGRES_USER`, `POSTGRES_HOST`, `POSTGRES_PASSWORD`, `POSTGRES_DATABASE`

---

## 📊 Step 2: Initialize Database Schema (3 minutes)

### 2.1 Connect to Your Database

**Via Vercel Dashboard:**
1. Go to Storage → Your Postgres DB
2. Click "Query" tab
3. Paste the contents of `schema.sql`
4. Click "Run Query"

**Via CLI:**
```bash
# Connect
vercel postgres connect gpt-storyworld-db

# Or use psql directly
psql $(vercel env pull | grep POSTGRES_URL | cut -d '=' -f2)
```

### 2.2 Run Schema

```bash
# Copy the schema.sql to your project
# Then run it via psql
psql $POSTGRES_URL -f schema.sql
```

### 2.3 Verify Setup

```sql
-- Run in Vercel Postgres console
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';

-- Should show: storyworlds, storyworld_analytics
```

---

## 💻 Step 3: Project Structure (2 minutes)

```
gpt-storyworld/
├── api/                          # Vercel API Routes
│   ├── storyworlds/
│   │   ├── route.js             # GET/POST /api/storyworlds
│   │   └── [id]/
│   │       ├── route.js         # GET/PATCH/DELETE /api/storyworlds/[id]
│   │       └── like/
│   │           └── route.js     # POST /api/storyworlds/[id]/like
│   └── stats/
│       └── route.js              # GET /api/stats
├── src/                          # Frontend (React)
│   ├── components/
│   ├── pages/
│   └── lib/
│       └── api.js               # API client
├── schema.sql                    # Database schema
├── vercel.json                   # Vercel configuration
├── package.json
└── README.md
```

---

## 🔧 Step 4: Create API Client (5 minutes)

Create `src/lib/api.js`:

```javascript
const API_BASE = process.env.NODE_ENV === 'production' 
  ? 'https://your-app.vercel.app/api'
  : 'http://localhost:3000/api';

export const storyworldAPI = {
  // Create a storyworld
  async create(data) {
    const res = await fetch(`${API_BASE}/storyworlds`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to create storyworld');
    return res.json();
  },

  // Get all storyworlds (paginated)
  async list({ limit = 20, offset = 0, sort = 'created_at', order = 'desc' } = {}) {
    const params = new URLSearchParams({ limit, offset, sort, order });
    const res = await fetch(`${API_BASE}/storyworlds?${params}`);
    if (!res.ok) throw new Error('Failed to fetch storyworlds');
    return res.json();
  },

  // Get a single storyworld
  async get(id) {
    const res = await fetch(`${API_BASE}/storyworlds/${id}`);
    if (!res.ok) throw new Error('Storyworld not found');
    return res.json();
  },

  // Update a storyworld
  async update(id, data) {
    const res = await fetch(`${API_BASE}/storyworlds/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to update storyworld');
    return res.json();
  },

  // Delete a storyworld
  async delete(id) {
    const res = await fetch(`${API_BASE}/storyworlds/${id}`, {
      method: 'DELETE'
    });
    if (!res.ok) throw new Error('Failed to delete storyworld');
    return res.json();
  },

  // Like/unlike a storyworld
  async toggleLike(id, action = 'like') {
    const res = await fetch(`${API_BASE}/storyworlds/${id}/like?action=${action}`, {
      method: 'POST'
    });
    if (!res.ok) throw new Error('Failed to toggle like');
    return res.json();
  },

  // Get stats
  async getStats() {
    const res = await fetch(`${API_BASE}/stats`);
    if (!res.ok) throw new Error('Failed to fetch stats');
    return res.json();
  }
};
```

---

## 🎨 Step 5: Update Frontend to Use Backend (10 minutes)

### Update `App.jsx` to save to database:

```javascript
import { storyworldAPI } from './lib/api';

const handleGenerate = async () => {
  setIsGenerating(true);
  
  try {
    // Call OpenAI GPT API (existing code)
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      // ... your existing GPT call
    });
    
    const data = await response.json();
    const encounterText = data.choices[0].message.content;
    const encounter = JSON.parse(encounterText);
    
    // Save to your Postgres backend
    const saved = await storyworldAPI.create({
      title: customPrompt.slice(0, 100) || 'Untitled Storyworld',
      description: customPrompt,
      num_characters: config.numCharacters,
      num_themes: config.numThemes,
      num_variables: config.numVariables,
      encounter_length: config.encounterLength,
      custom_prompt: customPrompt,
      encounter: encounter,
      system_prompt: generateSystemPrompt(),
      is_public: true,
      model_used: 'gpt-4',
      temperature: 0.8
    });
    
    console.log('Saved to database!', saved.storyworld.id);
    
    // Still download JSON for local copy
    const blob = new Blob([encounterText], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `storyworld_${saved.storyworld.id}.json`;
    a.click();
    
    // Show success with link to view
    alert(`Storyworld created! View at: /storyworld/${saved.storyworld.id}`);
    
  } catch (error) {
    console.error('Error:', error);
    alert('Failed to generate storyworld');
  } finally {
    setIsGenerating(false);
  }
};
```

### Create Browse Page (`src/pages/Browse.jsx`):

```javascript
import { useState, useEffect } from 'react';
import { storyworldAPI } from '../lib/api';

export default function Browse() {
  const [storyworlds, setStoryworlds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sort, setSort] = useState('created_at');
  
  useEffect(() => {
    loadStoryworlds();
  }, [sort]);
  
  const loadStoryworlds = async () => {
    try {
      const data = await storyworldAPI.list({ sort, limit: 20 });
      setStoryworlds(data.storyworlds);
    } catch (error) {
      console.error('Error loading storyworlds:', error);
    } finally {
      setLoading(false);
    }
  };
  
  if (loading) return <div>Loading...</div>;
  
  return (
    <div className="browse-page">
      <h1>Browse Storyworlds</h1>
      
      <div className="sort-controls">
        <button onClick={() => setSort('created_at')}>Newest</button>
        <button onClick={() => setSort('likes')}>Most Liked</button>
        <button onClick={() => setSort('views')}>Most Viewed</button>
      </div>
      
      <div className="storyworld-grid">
        {storyworlds.map(sw => (
          <StoryworldCard key={sw.id} storyworld={sw} />
        ))}
      </div>
    </div>
  );
}
```

---

## 🚀 Step 6: Deploy to Vercel (2 minutes)

### 6.1 Configure `vercel.json`

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "/api/$1"
    }
  ]
}
```

### 6.2 Deploy

```bash
# First deployment
vercel

# Production deployment
vercel --prod
```

The database connection is automatically configured via environment variables!

---

## 📊 API Documentation for Your README

### Endpoints

#### `POST /api/storyworlds`
Create a new storyworld.

**Request Body:**
```json
{
  "title": "string",
  "description": "string",
  "num_characters": "integer (1-10)",
  "num_themes": "integer (1-5)",
  "num_variables": "integer (3-20)",
  "encounter_length": "integer (200-1500)",
  "custom_prompt": "string",
  "encounter": {
    "encounter": "string",
    "choices": ["string"],
    "variables_affected": {},
    "metadata": {}
  },
  "system_prompt": "string",
  "is_public": "boolean",
  "model_used": "string",
  "temperature": "float"
}
```

**Response:**
```json
{
  "success": true,
  "storyworld": { ... }
}
```

#### `GET /api/storyworlds`
List all public storyworlds (paginated).

**Query Parameters:**
- `limit` (default: 20)
- `offset` (default: 0)
- `sort` (options: created_at, likes, views, fork_count)
- `order` (options: asc, desc)

**Response:**
```json
{
  "storyworlds": [...],
  "total": 150,
  "limit": 20,
  "offset": 0
}
```

#### `GET /api/storyworlds/[id]`
Get a specific storyworld (increments view count).

#### `PATCH /api/storyworlds/[id]`
Update a storyworld.

#### `DELETE /api/storyworlds/[id]`
Delete a storyworld.

#### `POST /api/storyworlds/[id]/like?action=like|unlike`
Toggle like on a storyworld.

#### `GET /api/stats`
Get platform statistics (trending, recent, popular).

---

## 🎯 For Your Job Application

### Include in Your README:

```markdown
## 🏗️ Backend Architecture

This project uses a modern serverless architecture:

- **Frontend**: React + Vite deployed on Vercel Edge
- **Backend**: Vercel Edge Functions (Node.js 20)
- **Database**: Vercel Postgres (Neon-powered, 512MB)
- **API**: RESTful endpoints with JSON responses
- **Deployment**: Continuous deployment via GitHub integration

### Technical Highlights

- **Edge Functions**: Low-latency API responses globally distributed
- **PostgreSQL**: ACID-compliant relational database with JSONB support
- **Indexing Strategy**: Optimized B-tree and GIN indexes for performance
- **Computed Fields**: Engagement scores and analytics via SQL views
- **Error Handling**: Comprehensive error responses with status codes
- **Type Safety**: Input validation and SQL injection prevention
- **Scalability**: Serverless auto-scaling to handle traffic spikes

### Database Schema

[Link to schema.sql]

- Complex JSONB structure for flexible encounter storage
- Referential integrity with foreign keys
- Materialized views for analytics
- Automated timestamp management via triggers

### API Design Patterns

- RESTful resource naming
- HTTP status codes (200, 201, 400, 404, 500)
- Pagination support
- Filtering and sorting
- Atomic operations (likes, views)
```

---

## 💰 Cost Breakdown

**Vercel Hobby (Free)**
- 100 GB bandwidth
- 60 compute hours
- 512 MB Postgres database
- Unlimited API requests

**When you need to upgrade ($20/month Pro):**
- 1 TB bandwidth
- 1,000 compute hours  
- Still 512 MB DB (or add more storage)

---

## ✅ Pre-Interview Checklist

- [ ] Database schema deployed
- [ ] All API endpoints working
- [ ] Error handling tested
- [ ] README with architecture diagram
- [ ] Live demo URL working
- [ ] GitHub repo clean and documented
- [ ] Can explain design decisions
- [ ] Know SQL queries by heart
- [ ] Understand Edge Function benefits
- [ ] Can discuss scalability trade-offs

---

## 🎤 Interview Talking Points

**"Why Vercel Postgres?"**
> "I chose Vercel Postgres for its seamless integration with Edge Functions, low-latency global distribution, and serverless architecture. It's built on Neon, which offers modern features like branching and autoscaling while maintaining PostgreSQL compatibility."

**"How did you design the schema?"**
> "I normalized the data to third normal form while using JSONB for the encounter field to balance structure and flexibility. The indexing strategy prioritizes common query patterns - B-tree indexes for sorting by likes/views, and GIN indexes for JSONB searches."

**"How does this scale?"**
> "The Edge Functions run globally distributed, so API latency is <50ms worldwide. The database uses connection pooling to handle concurrent requests. For scaling beyond the free tier, I'd implement caching with Vercel KV and could shard by user geography."

**"What about security?"**
> "Input validation prevents SQL injection, rate limiting protects against abuse, and the Postgres connection uses SSL. For production, I'd add authentication (likely Vercel's Auth.js) and implement row-level security policies."

---

## 🚀 Ready to Impress!

Your portfolio now shows:
- Full-stack capability
- Modern cloud architecture
- Database design skills
- API development
- Production deployment experience

All deployed and working, not just localhost! 🎉
