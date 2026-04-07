# ⚡ QUICK DEPLOY GUIDE

## 🎯 Deploy in 15 Minutes

### Prerequisites
- AWS account
- GitHub account
- SSH client

---

## Step 1: GitHub (2 minutes)

```bash
cd talking-bi
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/talking-bi.git
git push -u origin main
```

---

## Step 2: AWS EC2 (5 minutes)

1. **Launch EC2:**
   - Go to AWS Console → EC2 → Launch Instance
   - Name: `talking-bi-server`
   - AMI: Ubuntu 22.04 LTS
   - Type: t2.medium
   - Key pair: Create/download .pem file
   - Security: Allow ports 22, 80, 443, 8000
   - Storage: 20 GB
   - Launch!

2. **Get Public IP:**
   - Copy your EC2 Public IP address

---

## Step 3: Connect & Setup (3 minutes)

```bash
# Connect to EC2
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# Run setup (one command)
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/talking-bi/main/deploy/aws-setup.sh | bash

# Log out and back in
exit
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
```

---

## Step 4: Deploy (5 minutes)

```bash
# Clone repository
cd /opt
sudo git clone https://github.com/YOUR_USERNAME/talking-bi.git
sudo chown -R ubuntu:ubuntu talking-bi
cd talking-bi

# Configure
cp .env.example .env
nano .env  # Add your GROQ_API_KEY

# Deploy
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

---

## Step 5: Access (1 minute)

Open browser:
- **Frontend:** `http://YOUR_EC2_IP`
- **API Docs:** `http://YOUR_EC2_IP:8000/docs`

---

## ✅ Done!

Your Talking BI platform is live!

### Quick Commands

```bash
# View logs
docker-compose logs -f

# Restart
docker-compose restart

# Stop
docker-compose down

# Update
git pull && ./deploy/deploy.sh
```

---

## 🆘 Troubleshooting

**Can't access?**
- Check EC2 Security Group allows port 80
- Wait 2 minutes for services to start
- Check: `docker-compose ps`

**Services not running?**
```bash
docker-compose logs backend
docker-compose restart
```

**Need help?**
See full guide: `DEPLOYMENT_GUIDE.md`
