# ✅ DEPLOYMENT CHECKLIST

Use this checklist to ensure successful deployment.

## Pre-Deployment

### Local Setup
- [ ] NumPy issue fixed (version < 2.0)
- [ ] All dependencies installed
- [ ] Backend runs locally without errors
- [ ] Frontend runs locally without errors
- [ ] Can upload files and generate dashboards locally

### GitHub
- [ ] GitHub account created
- [ ] Git installed locally
- [ ] Repository created on GitHub
- [ ] Code pushed to GitHub
- [ ] .gitignore configured (no .env files)

### AWS
- [ ] AWS account created
- [ ] Credit card added (for verification)
- [ ] Free tier eligible
- [ ] SSH key pair created and downloaded

### Configuration
- [ ] .env.example file reviewed
- [ ] GROQ_API_KEY obtained (if using LLM features)
- [ ] All sensitive data removed from code

---

## GitHub Deployment

### Step 1: Initialize Repository
```bash
cd talking-bi
git init
git add .
git commit -m "Initial commit: Talking BI platform"
```
- [ ] Git initialized
- [ ] Files added
- [ ] Initial commit created

### Step 2: Create GitHub Repository
- [ ] Logged into GitHub
- [ ] New repository created
- [ ] Repository name: `talking-bi`
- [ ] Visibility set (Private/Public)

### Step 3: Push to GitHub
```bash
git remote add origin https://github.com/YOUR_USERNAME/talking-bi.git
git branch -M main
git push -u origin main
```
- [ ] Remote added
- [ ] Code pushed
- [ ] Verified on GitHub website

---

## Docker Local Testing

### Step 1: Create .env File
```bash
cp .env.example .env
# Edit .env with your configuration
```
- [ ] .env file created
- [ ] GROQ_API_KEY added (if applicable)
- [ ] CORS_ORIGINS configured

### Step 2: Build Images
```bash
docker-compose build
```
- [ ] Backend image built successfully
- [ ] Frontend image built successfully
- [ ] No build errors

### Step 3: Start Services
```bash
docker-compose up -d
```
- [ ] Redis started
- [ ] Backend started
- [ ] Celery worker started
- [ ] Frontend started

### Step 4: Test Locally
- [ ] Frontend accessible: http://localhost
- [ ] Backend accessible: http://localhost:8000
- [ ] Health check passes: http://localhost:8000/health
- [ ] API docs accessible: http://localhost:8000/docs
- [ ] Can upload CSV file
- [ ] Can generate dashboard
- [ ] Charts display correctly

### Step 5: Stop Services
```bash
docker-compose down
```
- [ ] All services stopped cleanly

---

## AWS EC2 Deployment

### Step 1: Launch EC2 Instance
- [ ] Logged into AWS Console
- [ ] Navigated to EC2 Dashboard
- [ ] Clicked "Launch Instance"

**Instance Configuration:**
- [ ] Name: `talking-bi-server`
- [ ] AMI: Ubuntu Server 22.04 LTS
- [ ] Instance type: t2.medium (or t2.small minimum)
- [ ] Key pair: Created/selected and downloaded .pem file
- [ ] Storage: 20 GB gp3

**Security Group:**
- [ ] SSH (22) - Your IP only
- [ ] HTTP (80) - Anywhere (0.0.0.0/0)
- [ ] HTTPS (443) - Anywhere (0.0.0.0/0)
- [ ] Custom TCP (8000) - Anywhere (0.0.0.0/0)

- [ ] Instance launched successfully
- [ ] Public IP address noted

### Step 2: Connect to EC2
```bash
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
```
- [ ] SSH connection successful
- [ ] Can access EC2 terminal

### Step 3: Setup Environment
```bash
# Download setup script
curl -o setup.sh https://raw.githubusercontent.com/YOUR_USERNAME/talking-bi/main/deploy/aws-setup.sh
chmod +x setup.sh
./setup.sh
```
- [ ] Setup script downloaded
- [ ] Docker installed
- [ ] Docker Compose installed
- [ ] Git installed
- [ ] Firewall configured
- [ ] Logged out and back in

### Step 4: Clone Repository
```bash
cd /opt
sudo git clone https://github.com/YOUR_USERNAME/talking-bi.git
sudo chown -R ubuntu:ubuntu talking-bi
cd talking-bi
```
- [ ] Repository cloned
- [ ] Permissions set correctly
- [ ] In project directory

### Step 5: Configure Application
```bash
cp .env.example .env
nano .env
```
- [ ] .env file created
- [ ] GROQ_API_KEY added
- [ ] CORS_ORIGINS updated with EC2 IP
- [ ] File saved

### Step 6: Deploy
```bash
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```
- [ ] Deploy script executed
- [ ] Images built successfully
- [ ] Services started
- [ ] No errors in logs

### Step 7: Verify Deployment
```bash
docker-compose ps
curl http://localhost:8000/health
```
- [ ] All containers running
- [ ] Health check returns `{"status":"healthy"}`
- [ ] No error logs

---

## Post-Deployment Testing

### Frontend Testing
- [ ] Open: `http://YOUR_EC2_IP`
- [ ] Page loads correctly
- [ ] No console errors (F12)
- [ ] UI is responsive

### Backend Testing
- [ ] Open: `http://YOUR_EC2_IP:8000/docs`
- [ ] API documentation loads
- [ ] Can test endpoints

### Functionality Testing
- [ ] Upload CSV file
- [ ] File uploads successfully
- [ ] Generate dashboard
- [ ] Dashboard generates (10-15 seconds)
- [ ] Charts display correctly
- [ ] Can ask questions
- [ ] Insights generated

### Performance Testing
- [ ] Page load time < 3 seconds
- [ ] Upload time reasonable
- [ ] Dashboard generation < 30 seconds
- [ ] No timeout errors

---

## Monitoring Setup

### Logs
```bash
docker-compose logs -f
```
- [ ] Can view logs
- [ ] No critical errors
- [ ] Services responding

### Health Checks
- [ ] Backend health: `http://YOUR_EC2_IP:8000/health`
- [ ] Redis health: `docker-compose exec redis redis-cli ping`
- [ ] All services: `docker-compose ps`

### Backups
```bash
chmod +x deploy/backup.sh
./deploy/backup.sh
```
- [ ] Backup script works
- [ ] Backup file created
- [ ] Backup stored in ./backups/

### Cron Job (Optional)
```bash
crontab -e
# Add: 0 2 * * * cd /opt/talking-bi && ./deploy/backup.sh
```
- [ ] Cron job configured
- [ ] Daily backups scheduled

---

## Security Checklist

### AWS Security
- [ ] SSH restricted to your IP
- [ ] Key pair stored securely
- [ ] Security group properly configured
- [ ] No unnecessary ports open

### Application Security
- [ ] .env file not in GitHub
- [ ] API keys secure
- [ ] CORS properly configured
- [ ] No sensitive data in logs

### System Security
- [ ] System packages updated
- [ ] Firewall enabled
- [ ] Docker running as non-root
- [ ] Regular backups configured

---

## Troubleshooting Checklist

### If Services Won't Start
- [ ] Check logs: `docker-compose logs`
- [ ] Check disk space: `df -h`
- [ ] Check memory: `free -h`
- [ ] Restart: `docker-compose restart`

### If Can't Access from Browser
- [ ] Security group allows port 80
- [ ] Services running: `docker-compose ps`
- [ ] Firewall allows traffic: `sudo ufw status`
- [ ] Test locally: `curl http://localhost`

### If Upload Fails
- [ ] Backend logs: `docker-compose logs backend`
- [ ] Disk space: `df -h`
- [ ] Permissions: `ls -la backend/data/`
- [ ] File size within limits

---

## Final Verification

### Deployment Complete
- [ ] All services running
- [ ] Frontend accessible
- [ ] Backend accessible
- [ ] Can upload and analyze data
- [ ] No critical errors

### Documentation
- [ ] README.md updated with your info
- [ ] DEPLOYMENT_GUIDE.md reviewed
- [ ] Team members have access
- [ ] Credentials stored securely

### Maintenance Plan
- [ ] Backup schedule configured
- [ ] Monitoring in place
- [ ] Update procedure documented
- [ ] Support contacts listed

---

## Success Criteria

✅ **Deployment is successful when:**

1. Frontend loads at `http://YOUR_EC2_IP`
2. Backend API responds at `http://YOUR_EC2_IP:8000`
3. Health check returns healthy status
4. Can upload CSV file
5. Can generate dashboard with charts
6. Can ask questions and get insights
7. All Docker containers running
8. No critical errors in logs
9. Backups configured
10. Documentation complete

---

## Next Steps After Deployment

1. [ ] Setup custom domain (optional)
2. [ ] Enable HTTPS with Let's Encrypt
3. [ ] Configure CloudWatch monitoring
4. [ ] Setup automated backups to S3
5. [ ] Implement CI/CD with GitHub Actions
6. [ ] Add user authentication
7. [ ] Scale with Load Balancer (if needed)
8. [ ] Monitor costs and optimize

---

## Support Resources

- **Documentation:** DEPLOYMENT_GUIDE.md
- **Quick Start:** QUICK_DEPLOY.md
- **GitHub Issues:** https://github.com/YOUR_USERNAME/talking-bi/issues
- **AWS Docs:** https://docs.aws.amazon.com/
- **Docker Docs:** https://docs.docker.com/

---

**🎉 Congratulations on your deployment!**

Print this checklist and check off items as you complete them.
