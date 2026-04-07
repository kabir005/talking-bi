# Talking BI - Deployment Guide

**Version:** 1.0.0  
**Last Updated:** March 22, 2026

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Production Deployment](#production-deployment)
4. [Backend Deployment (Render.com)](#backend-deployment-rendercom)
5. [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
6. [Environment Variables](#environment-variables)
7. [Database Setup](#database-setup)
8. [Performance Optimization](#performance-optimization)
9. [Security](#security)
10. [Monitoring](#monitoring)
11. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

**Minimum:**
- CPU: 2 cores
- RAM: 2GB
- Storage: 5GB
- OS: Linux, macOS, or Windows

**Recommended:**
- CPU: 4+ cores
- RAM: 4GB+
- Storage: 10GB+
- OS: Linux (Ubuntu 20.04+)

### Software Requirements

**Backend:**
- Python 3.11 or higher
- pip (Python package manager)
- Virtual environment tool (venv or virtualenv)

**Frontend:**
- Node.js 18 or higher
- npm or yarn

**Optional:**
- Docker (for containerized deployment)
- Git (for version control)

---

## Local Development

### Backend Setup

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd talking-bi/backend
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   
   # Activate (Linux/Mac)
   source venv/bin/activate
   
   # Activate (Windows)
   venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your GROQ_API_KEY
   ```

5. **Run Backend**
   ```bash
   python main.py
   ```

   Backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to Frontend**
   ```bash
   cd talking-bi/frontend
   ```

2. **Install Dependencies**
   ```bash
   npm install
   ```

3. **Set Environment Variables**
   ```bash
   # Create .env file
   echo "VITE_API_URL=http://localhost:8000/api" > .env
   ```

4. **Run Frontend**
   ```bash
   npm run dev
   ```

   Frontend will be available at `http://localhost:5173`

---

## Production Deployment

### Architecture Overview

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Vercel    │─────▶│  Render.com  │─────▶│   SQLite    │
│  (Frontend) │      │   (Backend)  │      │  (Database) │
└─────────────┘      └──────────────┘      └─────────────┘
```

### Deployment Checklist

- [ ] Set up Groq API key
- [ ] Configure environment variables
- [ ] Deploy backend to Render.com
- [ ] Deploy frontend to Vercel
- [ ] Test all endpoints
- [ ] Set up monitoring
- [ ] Configure custom domain (optional)

---

## Backend Deployment (Render.com)

### Step 1: Prepare Backend

1. **Create `render.yaml`**
   ```yaml
   services:
     - type: web
       name: talking-bi-backend
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
       envVars:
         - key: PYTHON_VERSION
           value: 3.11.0
         - key: GROQ_API_KEY
           sync: false
   ```

2. **Update `requirements.txt`**
   ```txt
   fastapi==0.104.1
   uvicorn[standard]==0.24.0
   sqlalchemy==2.0.23
   pandas==2.1.3
   numpy==1.26.2
   scikit-learn==1.3.2
   httpx==0.25.1
   python-dotenv==1.0.0
   aiosqlite==0.19.0
   # ... other dependencies
   ```

### Step 2: Deploy to Render

1. **Sign Up / Log In**
   - Go to [render.com](https://render.com)
   - Create account or log in

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your Git repository
   - Or use "Deploy from GitHub"

3. **Configure Service**
   - **Name:** `talking-bi-backend`
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free (or paid for better performance)

4. **Set Environment Variables**
   - Go to "Environment" tab
   - Add `GROQ_API_KEY` with your API key
   - Add `CORS_ORIGINS` with your frontend URL

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (5-10 minutes)
   - Note your backend URL: `https://talking-bi-backend.onrender.com`

### Step 3: Verify Backend

```bash
curl https://talking-bi-backend.onrender.com/health
# Should return: {"status": "healthy"}
```

---

## Frontend Deployment (Vercel)

### Step 1: Prepare Frontend

1. **Update API URL**
   ```bash
   # In .env.production
   VITE_API_URL=https://talking-bi-backend.onrender.com/api
   ```

2. **Create `vercel.json`**
   ```json
   {
     "buildCommand": "npm run build",
     "outputDirectory": "dist",
     "framework": "vite",
     "rewrites": [
       {
         "source": "/(.*)",
         "destination": "/index.html"
       }
     ]
   }
   ```

### Step 2: Deploy to Vercel

1. **Sign Up / Log In**
   - Go to [vercel.com](https://vercel.com)
   - Create account or log in

2. **Import Project**
   - Click "Add New..." → "Project"
   - Import from Git repository
   - Select `talking-bi/frontend` directory

3. **Configure Project**
   - **Framework Preset:** Vite
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
   - **Install Command:** `npm install`

4. **Set Environment Variables**
   - Add `VITE_API_URL` with your backend URL
   - Example: `https://talking-bi-backend.onrender.com/api`

5. **Deploy**
   - Click "Deploy"
   - Wait for deployment (2-5 minutes)
   - Note your frontend URL: `https://talking-bi.vercel.app`

### Step 3: Verify Frontend

- Open your frontend URL in browser
- Try uploading a file
- Check if API calls work

---

## Environment Variables

### Backend (.env)

```bash
# Required
GROQ_API_KEY=your_groq_api_key_here

# Optional
CORS_ORIGINS=https://talking-bi.vercel.app,http://localhost:5173
DATABASE_URL=sqlite:///./data/talking.db
FAISS_INDEX_PATH=./data/faiss.index
CHROMA_PATH=./data/chroma
MODELS_PATH=./models
```

### Frontend (.env.production)

```bash
# Required
VITE_API_URL=https://talking-bi-backend.onrender.com/api

# Optional
VITE_APP_NAME=Talking BI
VITE_APP_VERSION=1.0.0
```

---

## Database Setup

### SQLite (Default)

SQLite is used by default. No setup required.

**Location:** `backend/data/talking.db`

**Backup:**
```bash
# Backup database
cp backend/data/talking.db backend/data/talking.db.backup

# Restore database
cp backend/data/talking.db.backup backend/data/talking.db
```

### PostgreSQL (Optional)

For production with high traffic:

1. **Install PostgreSQL**
   ```bash
   # Ubuntu
   sudo apt install postgresql postgresql-contrib
   ```

2. **Create Database**
   ```sql
   CREATE DATABASE talking_bi;
   CREATE USER talking_bi_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE talking_bi TO talking_bi_user;
   ```

3. **Update Connection String**
   ```bash
   DATABASE_URL=postgresql://talking_bi_user:your_password@localhost/talking_bi
   ```

4. **Install PostgreSQL Driver**
   ```bash
   pip install asyncpg
   ```

---

## Performance Optimization

### Backend Optimization

1. **Enable Caching**
   ```python
   # Add to main.py
   from fastapi_cache import FastAPICache
   from fastapi_cache.backends.inmemory import InMemoryBackend
   
   @app.on_event("startup")
   async def startup():
       FastAPICache.init(InMemoryBackend())
   ```

2. **Use Connection Pooling**
   ```python
   # In database/db.py
   engine = create_async_engine(
       DATABASE_URL,
       pool_size=20,
       max_overflow=0
   )
   ```

3. **Optimize Queries**
   - Use indexes on frequently queried columns
   - Limit result sets
   - Use pagination

4. **Enable Compression**
   ```python
   # Add to main.py
   from fastapi.middleware.gzip import GZipMiddleware
   
   app.add_middleware(GZipMiddleware, minimum_size=1000)
   ```

### Frontend Optimization

1. **Code Splitting**
   ```typescript
   // Use lazy loading
   const Dashboard = lazy(() => import('./components/Dashboard'));
   ```

2. **Optimize Bundle**
   ```bash
   # Build with optimization
   npm run build -- --mode production
   ```

3. **Enable Caching**
   ```json
   // In vercel.json
   {
     "headers": [
       {
         "source": "/assets/(.*)",
         "headers": [
           {
             "key": "Cache-Control",
             "value": "public, max-age=31536000, immutable"
           }
         ]
       }
     ]
   }
   ```

4. **Use CDN**
   - Vercel automatically uses CDN
   - For custom deployment, use Cloudflare

---

## Security

### Backend Security

1. **Enable CORS Properly**
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://talking-bi.vercel.app"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. **Add Rate Limiting**
   ```python
   from slowapi import Limiter
   from slowapi.util import get_remote_address
   
   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter
   
   @app.get("/api/datasets")
   @limiter.limit("100/minute")
   async def list_datasets():
       ...
   ```

3. **Validate Input**
   - Use Pydantic models
   - Sanitize file uploads
   - Validate SQL queries

4. **Secure API Keys**
   - Never commit .env files
   - Use environment variables
   - Rotate keys regularly

### Frontend Security

1. **Sanitize User Input**
   ```typescript
   import DOMPurify from 'dompurify';
   
   const clean = DOMPurify.sanitize(userInput);
   ```

2. **Use HTTPS Only**
   - Vercel provides HTTPS by default
   - Enforce HTTPS redirects

3. **Set Security Headers**
   ```json
   // In vercel.json
   {
     "headers": [
       {
         "source": "/(.*)",
         "headers": [
           {
             "key": "X-Content-Type-Options",
             "value": "nosniff"
           },
           {
             "key": "X-Frame-Options",
             "value": "DENY"
           },
           {
             "key": "X-XSS-Protection",
             "value": "1; mode=block"
           }
         ]
       }
     ]
   }
   ```

---

## Monitoring

### Backend Monitoring

1. **Health Check Endpoint**
   ```python
   @app.get("/health")
   async def health_check():
       return {
           "status": "healthy",
           "timestamp": datetime.utcnow().isoformat()
       }
   ```

2. **Logging**
   ```python
   import logging
   
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
   )
   ```

3. **Error Tracking**
   - Use Sentry for error tracking
   - Set up alerts for critical errors

### Frontend Monitoring

1. **Analytics**
   - Use Google Analytics or Plausible
   - Track user interactions

2. **Performance Monitoring**
   - Use Vercel Analytics
   - Monitor Core Web Vitals

3. **Error Tracking**
   - Use Sentry or LogRocket
   - Track JavaScript errors

---

## Troubleshooting

### Common Issues

**Backend won't start**
```bash
# Check Python version
python --version  # Should be 3.11+

# Check dependencies
pip list

# Check logs
tail -f logs/app.log
```

**Frontend build fails**
```bash
# Clear cache
rm -rf node_modules package-lock.json
npm install

# Check Node version
node --version  # Should be 18+
```

**API calls fail**
```bash
# Check CORS settings
# Check API URL in frontend .env
# Check backend is running
curl http://localhost:8000/health
```

**Database errors**
```bash
# Reset database
rm backend/data/talking.db
python main.py  # Will recreate database
```

### Performance Issues

**Slow API responses**
- Check database indexes
- Enable caching
- Optimize queries
- Increase server resources

**High memory usage**
- Limit dataset size
- Use pagination
- Clear old data
- Restart services

---

## Backup & Recovery

### Backup Strategy

1. **Database Backup**
   ```bash
   # Daily backup
   0 2 * * * cp /path/to/talking.db /path/to/backups/talking-$(date +\%Y\%m\%d).db
   ```

2. **File Backup**
   ```bash
   # Backup uploaded files
   tar -czf data-backup.tar.gz backend/data/
   ```

3. **Configuration Backup**
   ```bash
   # Backup environment variables
   cp .env .env.backup
   ```

### Recovery

1. **Restore Database**
   ```bash
   cp backups/talking-20240322.db backend/data/talking.db
   ```

2. **Restore Files**
   ```bash
   tar -xzf data-backup.tar.gz
   ```

---

## Scaling

### Horizontal Scaling

1. **Load Balancer**
   - Use Nginx or Cloudflare
   - Distribute traffic across instances

2. **Multiple Backend Instances**
   - Deploy multiple Render services
   - Use shared database

3. **CDN**
   - Use Cloudflare for static assets
   - Cache API responses

### Vertical Scaling

1. **Upgrade Server**
   - Increase CPU/RAM on Render
   - Use paid plans for better performance

2. **Optimize Code**
   - Profile slow endpoints
   - Optimize database queries
   - Use async operations

---

## Cost Estimation

### Free Tier (Recommended for Testing)

- **Backend (Render):** Free
  - 750 hours/month
  - Sleeps after 15 min inactivity
  - 512MB RAM

- **Frontend (Vercel):** Free
  - Unlimited bandwidth
  - 100GB bandwidth/month
  - Automatic HTTPS

- **Total:** $0/month

### Paid Tier (Recommended for Production)

- **Backend (Render):** $7/month
  - Always on
  - 512MB RAM
  - No sleep

- **Frontend (Vercel):** $20/month (Pro)
  - Priority support
  - Advanced analytics
  - More bandwidth

- **Total:** $27/month

---

## Next Steps

1. ✅ Deploy backend to Render
2. ✅ Deploy frontend to Vercel
3. ✅ Test all features
4. ✅ Set up monitoring
5. ✅ Configure custom domain
6. ✅ Set up backups
7. ✅ Enable security features
8. ✅ Monitor performance

---

**Version:** 1.0.0  
**Last Updated:** March 22, 2026  
**Platform:** Talking BI - Agentic AI Business Intelligence

