# 🚀 TALKING BI - COMPLETE DEPLOYMENT GUIDE

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [GitHub Setup](#github-setup)
3. [Docker Setup (Local Testing)](#docker-setup-local-testing)
4. [AWS EC2 Deployment](#aws-ec2-deployment)
5. [Post-Deployment](#post-deployment)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Accounts
- ✅ GitHub account
- ✅ AWS account (free tier eligible)
- ✅ Groq API key (optional, for LLM features)

### Local Requirements
- Git installed
- Docker & Docker Compose installed
- SSH client

---

## 1. GitHub Setup

### Step 1.1: Initialize Git Repository

```bash
cd "C:\Users\yoron\OneDrive\Desktop\Talking BI\talking-bi"

# Initialize git (if not already)
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Talking BI platform"
```

### Step 1.2: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `talking-bi`
3. Description: `Agentic AI Business Intelligence Platform`
4. Visibility: Private (recommended) or Public
5. DO NOT initialize with README (we already have files)
6. Click "Create repository"

### Step 1.3: Push to GitHub

```bash
# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/talking-bi.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 1.4: Verify Upload

Visit: `https://github.com/YOUR_USERNAME/talking-bi`

You should see all your files uploaded.

---

## 2. Docker Setup (Local Testing)

### Step 2.1: Create Environment File

```bash
cd talking-bi

# Copy example env file
cp .env.example .env

# Edit .env file and add your API key
# GROQ_API_KEY=your_actual_key_here
```

### Step 2.2: Build Docker Images

```bash
# Build all images
docker-compose build
```

This will take 5-10 minutes the first time.

### Step 2.3: Start Services

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Step 2.4: Test Locally

Open browser:
- Frontend: http://localhost
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Step 2.5: Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

---

## 3. AWS EC2 Deployment

### Step 3.1: Launch EC2 Instance

1. **Go to AWS Console** → EC2 → Launch Instance

2. **Configure Instance:**
   - Name: `talking-bi-server`
   - AMI: Ubuntu Server 22.04 LTS (Free tier eligible)
   - Instance type: `t2.medium` (recommended) or `t2.small` (minimum)
   - Key pair: Create new or use existing (download .pem file)

3. **Network Settings:**
   - Allow SSH (port 22) from your IP
   - Allow HTTP (port 80) from anywhere
   - Allow HTTPS (port 443) from anywhere
   - Allow Custom TCP (port 8000) from anywhere

4. **Storage:**
   - 20 GB gp3 (free tier: 30 GB)

5. **Click "Launch Instance"**

### Step 3.2: Connect to EC2

```bash
# Change permission of key file (Windows Git Bash or WSL)
chmod 400 your-key.pem

# Connect to EC2 (replace with your instance IP)
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

### Step 3.3: Setup EC2 Environment

On EC2 instance, run:

```bash
# Download and run setup script
curl -o setup.sh https://raw.githubusercontent.com/YOUR_USERNAME/talking-bi/main/deploy/aws-setup.sh

chmod +x setup.sh
./setup.sh
```

**Important:** Log out and log back in after setup completes!

```bash
exit
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

### Step 3.4: Clone Repository

```bash
# Clone your repository
cd /opt
sudo git clone https://github.com/YOUR_USERNAME/talking-bi.git
sudo chown -R ubuntu:ubuntu talking-bi
cd talking-bi
```

### Step 3.5: Configure Environment

```bash
# Create .env file
cp .env.example .env

# Edit .env file
nano .env
```

Add your configuration:
```env
GROQ_API_KEY=your_groq_api_key_here
CORS_ORIGINS=http://YOUR_EC2_PUBLIC_IP,http://YOUR_EC2_PUBLIC_IP:8000
```

Save: `Ctrl+X`, then `Y`, then `Enter`

### Step 3.6: Deploy Application

```bash
# Make deploy script executable
chmod +x deploy/deploy.sh

# Run deployment
./deploy/deploy.sh
```

Wait 2-3 minutes for all services to start.

### Step 3.7: Verify Deployment

```bash
# Check running containers
docker-compose ps

# Check logs
docker-compose logs -f backend

# Test health endpoint
curl http://localhost:8000/health
```

Should return: `{"status":"healthy"}`

---

## 4. Post-Deployment

### Step 4.1: Access Your Application

Open browser:
- **Frontend:** `http://YOUR_EC2_PUBLIC_IP`
- **Backend API:** `http://YOUR_EC2_PUBLIC_IP:8000`
- **API Docs:** `http://YOUR_EC2_PUBLIC_IP:8000/docs`

### Step 4.2: Test Upload

1. Go to frontend
2. Upload a CSV file
3. Generate dashboard
4. Verify charts appear

### Step 4.3: Setup Automatic Backups

```bash
# Make backup script executable
chmod +x deploy/backup.sh

# Create cron job for daily backups
crontab -e

# Add this line (daily backup at 2 AM)
0 2 * * * cd /opt/talking-bi && ./deploy/backup.sh
```

### Step 4.4: Monitor Services

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f celery

# Check resource usage
docker stats

# Check system resources
htop
```

---

## 5. Maintenance Commands

### Update Application

```bash
cd /opt/talking-bi

# Pull latest changes
git pull origin main

# Redeploy
./deploy/deploy.sh
```

### Restart Services

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### View Logs

```bash
# All logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Specific service
docker-compose logs -f backend
```

### Backup Data

```bash
# Manual backup
./deploy/backup.sh

# Backups are stored in ./backups/
```

### Restore Data

```bash
# Restore from backup
./deploy/restore.sh backups/talking-bi-backup-20260407_120000.tar.gz
```

### Clean Up

```bash
# Remove stopped containers
docker-compose down

# Remove all (including volumes)
docker-compose down -v

# Remove unused images
docker system prune -a
```

---

## 6. Troubleshooting

### Issue: Services Won't Start

```bash
# Check logs
docker-compose logs

# Check individual service
docker-compose logs backend

# Restart services
docker-compose restart
```

### Issue: Port Already in Use

```bash
# Check what's using port 8000
sudo lsof -i :8000

# Kill process
sudo kill -9 <PID>

# Or change port in docker-compose.yml
```

### Issue: Out of Memory

```bash
# Check memory usage
free -h

# Restart services
docker-compose restart

# Consider upgrading to t2.medium
```

### Issue: Can't Access from Browser

1. Check EC2 Security Group allows port 80 and 8000
2. Check services are running: `docker-compose ps`
3. Check firewall: `sudo ufw status`
4. Test locally: `curl http://localhost:8000/health`

### Issue: Frontend Shows 502 Error

```bash
# Backend might not be ready
docker-compose logs backend

# Wait 30 seconds and refresh
# Or restart backend
docker-compose restart backend
```

### Issue: Upload Fails

```bash
# Check backend logs
docker-compose logs backend

# Check disk space
df -h

# Check permissions
ls -la backend/data/
```

---

## 7. Cost Optimization (AWS Free Tier)

### Free Tier Limits
- **EC2:** 750 hours/month of t2.micro (1 year)
- **Storage:** 30 GB EBS
- **Data Transfer:** 15 GB out/month

### Recommendations
- Use t2.micro for testing (free tier)
- Use t2.small for light production
- Use t2.medium for full production
- Stop instance when not in use to save hours
- Use CloudWatch for monitoring (free tier: 10 metrics)

### Stop Instance When Not Needed

```bash
# From AWS Console
EC2 → Instances → Select instance → Instance State → Stop

# To restart
Instance State → Start
```

---

## 8. Security Best Practices

### 1. Update Security Group
- Restrict SSH (port 22) to your IP only
- Use HTTPS (port 443) with SSL certificate

### 2. Use Environment Variables
- Never commit .env file to GitHub
- Use AWS Secrets Manager for production

### 3. Regular Updates

```bash
# Update system packages
sudo apt-get update && sudo apt-get upgrade -y

# Update Docker images
docker-compose pull
docker-compose up -d
```

### 4. Enable HTTPS (Optional)

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get SSL certificate (requires domain name)
sudo certbot --nginx -d yourdomain.com
```

---

## 9. Monitoring & Logs

### Application Logs

```bash
# Real-time logs
docker-compose logs -f

# Save logs to file
docker-compose logs > logs.txt
```

### System Monitoring

```bash
# CPU and Memory
htop

# Disk usage
df -h

# Docker stats
docker stats
```

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Redis health
docker-compose exec redis redis-cli ping

# Check all services
docker-compose ps
```

---

## 10. Quick Reference

### Essential Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart service
docker-compose restart backend

# Update application
git pull && ./deploy/deploy.sh

# Backup data
./deploy/backup.sh

# Check status
docker-compose ps
```

### Important URLs

- Frontend: `http://YOUR_IP`
- Backend: `http://YOUR_IP:8000`
- API Docs: `http://YOUR_IP:8000/docs`
- Health: `http://YOUR_IP:8000/health`

### Important Files

- `docker-compose.yml` - Service configuration
- `.env` - Environment variables
- `deploy/deploy.sh` - Deployment script
- `deploy/backup.sh` - Backup script
- `nginx.conf` - Frontend proxy config

---

## 11. Next Steps

1. ✅ Setup custom domain (optional)
2. ✅ Enable HTTPS with Let's Encrypt
3. ✅ Setup CloudWatch monitoring
4. ✅ Configure automated backups to S3
5. ✅ Setup CI/CD with GitHub Actions
6. ✅ Add authentication layer
7. ✅ Scale with Load Balancer (if needed)

---

## Support

### Logs Location
- Application: `docker-compose logs`
- System: `/var/log/syslog`
- Docker: `/var/lib/docker/`

### Common Issues
- Check GitHub Issues: `https://github.com/YOUR_USERNAME/talking-bi/issues`
- AWS Documentation: https://docs.aws.amazon.com/
- Docker Documentation: https://docs.docker.com/

---

**🎉 Congratulations! Your Talking BI platform is now deployed!**

Access it at: `http://YOUR_EC2_PUBLIC_IP`
