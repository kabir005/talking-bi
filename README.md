# 🤖 Talking BI - Agentic AI Business Intelligence Platform

> Transform your data into actionable insights with AI-powered analysis

[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://www.docker.com/)
[![AWS](https://img.shields.io/badge/AWS-Deployable-orange)](https://aws.amazon.com/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## 🌟 Features

- **📊 Automated Dashboard Generation** - 15-20 charts per dataset
- **🤖 AI-Powered Insights** - LLM-driven analysis and recommendations
- **💬 Natural Language Queries** - Ask questions in plain English
- **📈 Advanced Analytics** - Forecasting, anomaly detection, root cause analysis
- **🔄 Real-time Processing** - Celery-based background tasks
- **📱 Modern UI** - React + TypeScript + TailwindCSS

## 🚀 Quick Start

### Local Development

```bash
# Backend
cd backend
pip install -r requirements.txt
python start_server.py

# Frontend
cd frontend
npm install
npm run dev
```

### Docker (Recommended)

```bash
# Start all services
docker-compose up -d

# Access
# Frontend: http://localhost
# Backend: http://localhost:8000
```

### AWS Deployment

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for complete instructions.

**Quick Deploy:**
```bash
# On EC2 instance
git clone https://github.com/YOUR_USERNAME/talking-bi.git
cd talking-bi
cp .env.example .env
# Edit .env with your config
docker-compose up -d
```

## 📋 Requirements

### Local Development
- Python 3.11+
- Node.js 18+
- Redis (optional, for background tasks)

### Docker Deployment
- Docker 20.10+
- Docker Compose 2.0+

### AWS Deployment
- EC2 instance (t2.medium recommended)
- 20 GB storage
- Ubuntu 22.04 LTS

## 🏗️ Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│   Backend   │────▶│    Redis    │
│  (React)    │     │  (FastAPI)  │     │  (Broker)   │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   Celery    │
                    │   Worker    │
                    └─────────────┘
```

## 📦 Tech Stack

### Backend
- FastAPI - Modern Python web framework
- SQLAlchemy - Database ORM
- Celery - Distributed task queue
- Pandas - Data processing
- FAISS - Vector similarity search
- ChromaDB - Vector database

### Frontend
- React 18 - UI framework
- TypeScript - Type safety
- Vite - Build tool
- TailwindCSS - Styling
- Recharts - Data visualization

### Infrastructure
- Docker - Containerization
- Nginx - Reverse proxy
- Redis - Message broker
- AWS EC2 - Hosting

## 🔧 Configuration

### Environment Variables

```env
# API Keys
GROQ_API_KEY=your_groq_api_key

# Backend
DATA_DIR=./data
MAX_FILE_SIZE_MB=100

# Redis
REDIS_URL=redis://localhost:6379/0

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:80
```

## 📚 Documentation

- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Complete deployment instructions
- [Quick Deploy](QUICK_DEPLOY.md) - 15-minute deployment guide
- [API Documentation](http://localhost:8000/docs) - Interactive API docs

## 🛠️ Development

### Project Structure

```
talking-bi/
├── backend/              # FastAPI backend
│   ├── agents/          # AI agents
│   ├── routers/         # API routes
│   ├── database/        # Database models
│   └── start_server.py  # Entry point
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # UI components
│   │   ├── pages/       # Page components
│   │   └── api/         # API client
│   └── package.json
├── deploy/              # Deployment scripts
│   ├── aws-setup.sh     # EC2 setup
│   ├── deploy.sh        # Deployment
│   └── backup.sh        # Backup script
├── docker-compose.yml   # Docker services
├── Dockerfile.backend   # Backend image
└── Dockerfile.frontend  # Frontend image
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 🔒 Security

- Environment variables for sensitive data
- CORS configuration
- Input validation
- SQL injection prevention
- XSS protection

## 📊 Performance

- Async/await for I/O operations
- Background task processing with Celery
- Redis caching
- Docker multi-stage builds
- Nginx gzip compression

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

- FastAPI for the amazing web framework
- React team for the UI library
- Docker for containerization
- AWS for cloud infrastructure

## 📧 Support

- GitHub Issues: [Create an issue](https://github.com/YOUR_USERNAME/talking-bi/issues)
- Documentation: [Full docs](DEPLOYMENT_GUIDE.md)

## 🗺️ Roadmap

- [ ] HTTPS/SSL support
- [ ] User authentication
- [ ] Multi-tenancy
- [ ] S3 storage integration
- [ ] Advanced ML models
- [ ] Real-time collaboration
- [ ] Mobile app

---

**Made with ❤️ by the Talking BI Team**

⭐ Star us on GitHub if you find this useful!
