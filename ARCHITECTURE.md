# 🏗️ TALKING BI - SYSTEM ARCHITECTURE

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                             │
│                    http://YOUR_EC2_IP                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AWS EC2 INSTANCE                            │
│                    (Ubuntu 22.04 LTS)                            │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    DOCKER NETWORK                           │ │
│  │                                                              │ │
│  │  ┌──────────────┐         ┌──────────────┐                │ │
│  │  │   FRONTEND   │         │   BACKEND    │                │ │
│  │  │              │         │              │                │ │
│  │  │  React App   │────────▶│   FastAPI    │                │ │
│  │  │  + Nginx     │  API    │   Server     │                │ │
│  │  │              │ Proxy   │              │                │ │
│  │  │  Port: 80    │         │  Port: 8000  │                │ │
│  │  └──────────────┘         └──────┬───────┘                │ │
│  │                                   │                         │ │
│  │                                   │                         │ │
│  │                          ┌────────┴────────┐               │ │
│  │                          │                 │               │ │
│  │                          ▼                 ▼               │ │
│  │                   ┌──────────┐      ┌──────────┐          │ │
│  │                   │  REDIS   │      │  CELERY  │          │ │
│  │                   │          │      │  WORKER  │          │ │
│  │                   │  Broker  │◀─────│          │          │ │
│  │                   │          │      │ BG Tasks │          │ │
│  │                   │ Port:6379│      │          │          │ │
│  │                   └──────────┘      └──────────┘          │ │
│  │                                                              │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                   PERSISTENT STORAGE                        │ │
│  │                    (Docker Volumes)                         │ │
│  │                                                              │ │
│  │  • SQLite Database (talking_bi.db)                         │ │
│  │  • Uploaded CSV Files                                       │ │
│  │  • FAISS Vector Store                                       │ │
│  │  • ChromaDB Data                                            │ │
│  │  • Generated Dashboards                                     │ │
│  │  • Application Logs                                         │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. Frontend Container
**Technology:** React 18 + TypeScript + Vite + Nginx

**Responsibilities:**
- Serve static React application
- Reverse proxy API requests to backend
- Handle SPA routing
- Gzip compression

**Endpoints:**
- `/` - React application
- `/api/*` - Proxied to backend:8000
- `/docs` - Proxied to backend:8000/docs

**Configuration:**
- Base Image: `node:18-alpine` (build) + `nginx:alpine` (serve)
- Port: 80
- Volume: None (stateless)

---

### 2. Backend Container
**Technology:** FastAPI + Python 3.11 + Uvicorn

**Responsibilities:**
- REST API endpoints
- File upload handling
- Data processing with Pandas
- Dashboard generation
- Query processing
- AI agent orchestration

**Key Features:**
- Async/await for I/O operations
- SQLAlchemy ORM for database
- FAISS for vector similarity
- ChromaDB for embeddings
- Background task delegation to Celery

**Endpoints:**
- `/health` - Health check
- `/api/upload/*` - File upload
- `/api/datasets/*` - Dataset management
- `/api/dashboards/*` - Dashboard operations
- `/api/query` - Natural language queries
- `/api/ml/*` - ML operations
- `/docs` - Interactive API documentation

**Configuration:**
- Base Image: `python:3.11-slim`
- Port: 8000
- Volumes: 
  - `backend_data:/app/data` (persistent)
  - `backend_logs:/app/logs` (persistent)

---

### 3. Redis Container
**Technology:** Redis 7 Alpine

**Responsibilities:**
- Message broker for Celery
- Task queue management
- Result backend
- Caching (optional)

**Configuration:**
- Base Image: `redis:7-alpine`
- Port: 6379
- Volume: `redis_data:/data` (persistent)
- Health Check: `redis-cli ping`

---

### 4. Celery Worker Container
**Technology:** Celery + Python 3.11

**Responsibilities:**
- Background task processing
- Dashboard generation (async)
- Long-running analytics
- Scheduled tasks
- Report generation

**Task Types:**
- Dashboard generation
- Data cleaning
- ML model training
- Report exports
- Scheduled briefings

**Configuration:**
- Base Image: Same as backend
- Command: `celery -A celery_app worker`
- Concurrency: 2 workers
- Volumes: Same as backend (shared data)

---

## Data Flow

### 1. File Upload Flow
```
User Browser
    │
    ▼
Frontend (React)
    │ POST /api/upload/file
    ▼
Nginx Proxy
    │
    ▼
Backend (FastAPI)
    │
    ├─▶ Validate file
    ├─▶ Save to disk
    ├─▶ Create database record
    └─▶ Return dataset_id
```

### 2. Dashboard Generation Flow
```
User Browser
    │
    ▼
Frontend (React)
    │ POST /api/dashboards/generate
    ▼
Backend (FastAPI)
    │
    ├─▶ Create Celery task
    │   │
    │   ▼
    │   Redis (Queue task)
    │   │
    │   ▼
    │   Celery Worker
    │   │
    │   ├─▶ Load dataset
    │   ├─▶ Run analysis
    │   ├─▶ Generate charts
    │   ├─▶ Save dashboard
    │   └─▶ Update status
    │
    └─▶ Return task_id
```

### 3. Query Processing Flow
```
User Browser
    │
    ▼
Frontend (React)
    │ POST /api/query
    ▼
Backend (FastAPI)
    │
    ├─▶ Load dataset
    ├─▶ Orchestrator Agent
    │   │
    │   ├─▶ Analyst Agent
    │   ├─▶ Insight Agent
    │   ├─▶ Chart Agent
    │   └─▶ Strategist Agent
    │
    ├─▶ Generate response
    └─▶ Return insights
```

---

## Network Architecture

### Internal Docker Network
```
talking-bi-network (bridge)
├── frontend:80
├── backend:8000
├── redis:6379
└── celery (no exposed ports)
```

### External Access
```
Internet
    │
    ▼
AWS Security Group
    │
    ├─▶ Port 22 (SSH) → EC2 Instance
    ├─▶ Port 80 (HTTP) → Frontend Container
    ├─▶ Port 443 (HTTPS) → Frontend Container (if SSL)
    └─▶ Port 8000 (API) → Backend Container
```

---

## Storage Architecture

### Docker Volumes
```
/var/lib/docker/volumes/
├── talking-bi_redis_data/
│   └── dump.rdb (Redis persistence)
├── talking-bi_backend_data/
│   ├── talking_bi.db (SQLite)
│   ├── *.csv (Uploaded files)
│   ├── chroma/ (Vector DB)
│   └── exports/ (Generated reports)
└── talking-bi_backend_logs/
    └── *.log (Application logs)
```

### File System Layout
```
/opt/talking-bi/
├── backend/
│   ├── agents/ (AI agents)
│   ├── routers/ (API routes)
│   ├── database/ (Models)
│   ├── memory/ (FAISS/ChromaDB)
│   └── start_server.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── api/
│   └── dist/ (Built files)
├── deploy/
│   ├── aws-setup.sh
│   ├── deploy.sh
│   └── backup.sh
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
└── .env
```

---

## Security Architecture

### Network Security
```
┌─────────────────────────────────────┐
│      AWS Security Group             │
│                                      │
│  ┌────────────────────────────────┐ │
│  │  Inbound Rules                 │ │
│  │  • SSH (22) ← Your IP only     │ │
│  │  • HTTP (80) ← 0.0.0.0/0       │ │
│  │  • HTTPS (443) ← 0.0.0.0/0     │ │
│  │  • API (8000) ← 0.0.0.0/0      │ │
│  └────────────────────────────────┘ │
│                                      │
│  ┌────────────────────────────────┐ │
│  │  Outbound Rules                │ │
│  │  • All traffic → 0.0.0.0/0     │ │
│  └────────────────────────────────┘ │
└─────────────────────────────────────┘
```

### Application Security
- CORS configuration
- Input validation
- SQL injection prevention
- XSS protection
- Environment variable isolation
- No sensitive data in logs

---

## Scalability Considerations

### Current Architecture (Single Instance)
- **Capacity:** 15-50 concurrent users
- **Bottleneck:** Single EC2 instance
- **Storage:** Local volumes

### Scaling Options

#### Vertical Scaling (Easier)
```
t2.medium → t2.large → t2.xlarge
2 vCPU, 4GB → 2 vCPU, 8GB → 4 vCPU, 16GB
```

#### Horizontal Scaling (Advanced)
```
┌─────────────────────────────────────┐
│      Application Load Balancer      │
└──────────┬──────────────┬───────────┘
           │              │
    ┌──────▼─────┐ ┌─────▼──────┐
    │  EC2 #1    │ │  EC2 #2    │
    │  (App)     │ │  (App)     │
    └──────┬─────┘ └─────┬──────┘
           │              │
    ┌──────▼──────────────▼───────┐
    │      RDS PostgreSQL          │
    │      (Shared Database)       │
    └──────────────────────────────┘
    ┌──────────────────────────────┐
    │      ElastiCache Redis       │
    │      (Shared Cache)          │
    └──────────────────────────────┘
    ┌──────────────────────────────┐
    │      S3 Bucket               │
    │      (File Storage)          │
    └──────────────────────────────┘
```

---

## Monitoring Architecture

### Health Checks
```
┌─────────────────────────────────────┐
│      Health Check Endpoints         │
│                                      │
│  • Frontend: GET /                  │
│  • Backend: GET /health             │
│  • Redis: redis-cli ping            │
│  • Celery: celery inspect ping      │
└─────────────────────────────────────┘
```

### Logging
```
Application Logs
    │
    ├─▶ Backend: /app/logs/*.log
    ├─▶ Frontend: Nginx access/error logs
    ├─▶ Celery: Worker logs
    └─▶ Redis: Redis logs

Docker Logs
    │
    └─▶ docker-compose logs -f
```

### Metrics (Optional - CloudWatch)
- CPU utilization
- Memory usage
- Disk I/O
- Network traffic
- Request count
- Response time
- Error rate

---

## Backup Architecture

### Backup Strategy
```
┌─────────────────────────────────────┐
│      Automated Backup (Cron)        │
│      Daily at 2 AM                  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      Backup Script                  │
│      (deploy/backup.sh)             │
└──────────────┬──────────────────────┘
               │
               ├─▶ Stop services
               ├─▶ Tar backend/data/
               ├─▶ Include .env
               ├─▶ Save to ./backups/
               └─▶ Restart services
```

### Backup Contents
- SQLite database
- Uploaded CSV files
- FAISS indices
- ChromaDB data
- Environment configuration

### Restore Process
```
Backup File (.tar.gz)
    │
    ▼
Restore Script
    │
    ├─▶ Stop services
    ├─▶ Extract backup
    ├─▶ Replace data/
    └─▶ Start services
```

---

## Deployment Pipeline

### CI/CD Flow (GitHub Actions)
```
Developer
    │ git push
    ▼
GitHub Repository
    │
    ▼
GitHub Actions
    │
    ├─▶ Build Docker images
    ├─▶ Run tests
    ├─▶ Push to registry (optional)
    └─▶ Deploy to EC2 (optional)
```

### Manual Deployment Flow
```
Local Machine
    │ git push
    ▼
GitHub Repository
    │
    ▼
EC2 Instance
    │ git pull
    ▼
Deploy Script
    │
    ├─▶ Stop containers
    ├─▶ Build new images
    ├─▶ Start containers
    └─▶ Verify health
```

---

## Technology Stack Summary

### Frontend
- **Framework:** React 18
- **Language:** TypeScript
- **Build Tool:** Vite
- **Styling:** TailwindCSS
- **Charts:** Recharts
- **HTTP Client:** Axios
- **State:** Zustand
- **Server:** Nginx

### Backend
- **Framework:** FastAPI
- **Language:** Python 3.11
- **Server:** Uvicorn
- **ORM:** SQLAlchemy
- **Database:** SQLite
- **Task Queue:** Celery
- **Broker:** Redis
- **Data:** Pandas, NumPy
- **ML:** scikit-learn, SHAP
- **Vector:** FAISS, ChromaDB
- **LLM:** Groq API

### Infrastructure
- **Containerization:** Docker
- **Orchestration:** Docker Compose
- **Cloud:** AWS EC2
- **OS:** Ubuntu 22.04 LTS
- **Proxy:** Nginx
- **CI/CD:** GitHub Actions

---

## Performance Characteristics

### Response Times (t2.medium)
- **Page Load:** < 2 seconds
- **File Upload:** 2-10 seconds (depends on size)
- **Dashboard Generation:** 5-15 seconds
- **Query Response:** 2-5 seconds
- **Health Check:** < 100ms

### Resource Usage
- **CPU:** 20-40% average, 80% peak
- **Memory:** 2-3 GB average, 4 GB peak
- **Disk:** 5-10 GB (depends on data)
- **Network:** < 1 GB/day typical

### Capacity
- **Concurrent Users:** 15-50
- **Datasets:** Unlimited (storage limited)
- **Dashboard Size:** Up to 100 MB
- **File Upload:** Up to 100 MB

---

This architecture provides a solid foundation for production deployment while maintaining simplicity and cost-effectiveness.
