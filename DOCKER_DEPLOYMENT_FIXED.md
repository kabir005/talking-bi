# Docker Deployment - Fixed Version

## Issue Fixed
The original Docker build was failing due to hash mismatch in requirements.txt. This has been resolved by:
- Changing from exact version pinning (`==`) to minimum version (`>=`)
- This allows pip to install compatible versions without strict hash checking

## Prerequisites
- Docker Desktop installed and running
- At least 10GB free disk space
- 8GB RAM minimum (16GB recommended)

## Quick Start

### 1. Set Environment Variables
Create a `.env` file in the `talking-bi` directory:

```bash
# Required
GROQ_API_KEY=your_groq_api_key_here

# Optional - Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password
SMTP_FROM=your_email@gmail.com

# Optional - Database
POSTGRES_PASSWORD=secure_password_here
```

### 2. Build and Start Services
```bash
cd talking-bi
docker-compose up -d
```

This will:
- Build backend (Python FastAPI) - ~10-15 minutes
- Build frontend (React + Nginx) - ~2-3 minutes
- Start PostgreSQL database
- Start Redis for caching
- Start Celery workers for background tasks

### 3. Check Status
```bash
# View running containers
docker-compose ps

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 4. Access Application
- Frontend: http://localhost
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Build Time Expectations
- **Backend**: 10-15 minutes (downloads ~2GB of ML/AI packages including PyTorch, CUDA libraries)
- **Frontend**: 2-3 minutes
- **Total**: ~15-20 minutes for first build

Subsequent builds will be faster due to Docker layer caching.

## Troubleshooting

### Build Fails with "hash mismatch"
This should be fixed now. If it still occurs:
```bash
docker-compose build --no-cache backend
```

### Out of Memory
If build fails with memory errors:
1. Increase Docker Desktop memory limit (Settings > Resources)
2. Close other applications
3. Try building services one at a time:
```bash
docker-compose build backend
docker-compose build frontend
docker-compose up -d
```

### Port Already in Use
If ports 80 or 8000 are in use:
1. Stop conflicting services
2. Or modify `docker-compose.yml` ports:
```yaml
frontend:
  ports:
    - "8080:80"  # Change 80 to 8080

backend:
  ports:
    - "8001:8000"  # Change 8000 to 8001
```

### Backend Won't Start
Check logs:
```bash
docker-compose logs backend
```

Common issues:
- Missing GROQ_API_KEY in .env
- Database connection issues (wait for postgres to be ready)

## Stopping Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

## Production Deployment

For production, add these to your `.env`:
```bash
# Security
CORS_ORIGINS=https://yourdomain.com

# Database (use external managed database)
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Redis (use external managed Redis)
REDIS_URL=redis://host:6379/0
```

Then deploy to cloud:
- AWS ECS/Fargate
- Azure Container Instances
- Google Cloud Run
- DigitalOcean App Platform

## Next Steps
1. Configure your GROQ API key
2. Upload your first dataset
3. Create dashboards
4. Set up morning briefings
5. Configure database connections

## Support
- Check logs: `docker-compose logs -f`
- Restart services: `docker-compose restart`
- Rebuild: `docker-compose build --no-cache`
