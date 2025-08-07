# Telegram Automation - Production-Ready Fullstack Application

[![Backend CI](https://github.com/dygje12/telegram-automation/workflows/Backend%20CI/badge.svg)](https://github.com/dygje12/telegram-automation/actions)
[![Frontend CI](https://github.com/dygje12/telegram-automation/workflows/Frontend%20CI/badge.svg)](https://github.com/dygje12/telegram-automation/actions)
[![Production Deployment](https://github.com/dygje12/telegram-automation/workflows/Production%20Deployment/badge.svg)](https://github.com/dygje12/telegram-automation/actions)

Aplikasi fullstack production-ready untuk otomasi pengiriman pesan Telegram menggunakan user account dengan fitur-fitur canggih seperti smart blacklist, scheduler otomatis, dan monitoring real-time.

## 🚀 Fitur Utama

- **Autentikasi Telegram**: Login menggunakan nomor telepon dengan dukungan 2FA
- **Manajemen Pesan**: Template pesan dengan variabel dinamis
- **Manajemen Grup**: Validasi dan monitoring grup Telegram
- **Smart Blacklist**: Sistem blacklist otomatis dan manual
- **Scheduler Otomatis**: Penjadwalan pengiriman pesan dengan interval yang dapat dikonfigurasi
- **Monitoring Real-time**: Dashboard dengan statistik dan log pengiriman
- **Keamanan Tingkat Produksi**: Enkripsi data, rate limiting, dan validasi input
- **Arsitektur Scalable**: Clean architecture dengan separation of concerns

## 📋 Persyaratan Sistem

### Development
- Python 3.11+
- Node.js 18+ atau 20+
- Docker & Docker Compose
- Git

### Production
- Docker & Docker Compose
- SSL Certificate (untuk HTTPS)
- Domain name (opsional)

## 🛠️ Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/dygje12/telegram-automation
cd telegram-automation
```

### 2. Setup Environment
```bash
# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Edit environment variables
nano backend/.env  # Configure your Telegram API credentials
nano frontend/.env # Configure frontend settings
```

### 3. Start Development Environment
```bash
# Using Make (recommended)
make dev

# Or using Docker Compose directly
docker-compose -f infra/docker/docker-compose.yml up --build
```

### 4. Access Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 🔧 Development Setup

### Backend Development
```bash
cd backend

# Install dependencies
pip install -r requirements/dev.txt

# Run database migrations
../infra/scripts/migrate.sh

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## 🧪 Testing

### Run All Tests
```bash
make test
```

### Backend Tests
```bash
cd backend
python -m pytest app/tests/ --cov=app --cov-report=term-missing --cov-fail-under=80
```

### Frontend Tests
```bash
cd frontend
npm run test:coverage
```

## 🏗️ Build & Deploy

### Development Build
```bash
make build
```

### Production Deployment
```bash
# Deploy to production
make deploy

# Or using Docker Compose
docker-compose -f infra/docker/docker-compose.yml -f infra/docker/docker-compose.prod.yml up -d
```

### Manual Deployment

#### Backend
```bash
cd backend
pip install -r requirements/prod.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Frontend
```bash
cd frontend
npm install
npm run build
# Serve dist/ folder using nginx or any web server
```

## 📁 Project Structure

```
telegram-automation/
├── .github/                 # GitHub workflows and templates
│   ├── workflows/          # CI/CD pipelines
│   ├── ISSUE_TEMPLATE/     # Issue templates
│   ├── pull_request_template.md
│   └── dependabot.yml      # Dependency updates
├── backend/                # FastAPI + Telethon backend
│   ├── app/
│   │   ├── api/v1/         # API routes grouped by domain
│   │   ├── core/           # Shared core logic
│   │   ├── crud/           # Database access layer
│   │   ├── models/         # Pydantic & SQLAlchemy models
│   │   ├── services/       # Business logic
│   │   ├── utils/          # Helper utilities
│   │   └── tests/          # Pytest test suite
│   ├── alembic/            # Database migrations
│   ├── requirements/       # Python dependencies
│   └── .env.example        # Environment template
├── frontend/               # React + TypeScript + Tailwind
│   ├── src/
│   │   ├── api/            # API client
│   │   ├── components/     # Reusable UI components
│   │   ├── features/       # Feature-based modules
│   │   ├── hooks/          # Custom React hooks
│   │   ├── pages/          # Route-level components
│   │   ├── routes/         # React Router configuration
│   │   ├── styles/         # Global styles & Tailwind config
│   │   └── tests/          # Jest + React Testing Library
│   └── .env.example        # Environment template
├── infra/                  # Infrastructure & deployment
│   ├── docker/             # Docker configurations
│   ├── nginx/              # Nginx configuration
│   ├── scripts/            # Utility scripts
│   ├── k8s/                # Kubernetes manifests (optional)
│   └── terraform/          # Infrastructure as Code (optional)
├── docs/                   # Documentation
│   ├── architecture.md     # System architecture
│   ├── deployment.md       # Deployment guide
│   └── openapi.json        # API specification
├── Makefile                # Development commands
└── README.md               # This file
```

## 🔒 Security

- **Data Encryption**: Sensitive data encrypted at rest
- **JWT Authentication**: Secure token-based authentication
- **Rate Limiting**: API rate limiting to prevent abuse
- **Input Validation**: Comprehensive input validation and sanitization
- **CORS Configuration**: Proper CORS setup for production
- **Environment Variables**: No secrets in code, all via environment variables

## 📊 Monitoring & Logging

- **Health Checks**: Built-in health check endpoints
- **Structured Logging**: JSON-formatted logs for production
- **Error Tracking**: Comprehensive error handling and reporting
- **Performance Metrics**: Built-in performance monitoring
- **Dashboard**: Real-time monitoring dashboard

## 🔄 CI/CD Pipeline

### Continuous Integration
- **Code Quality**: Black, isort, mypy, ESLint
- **Testing**: Unit and integration tests with coverage reports
- **Security**: Bandit security scanning, dependency auditing
- **Build**: Docker image building and testing

### Continuous Deployment
- **Staging**: Automatic deployment to staging on main branch
- **Production**: Manual deployment with approval gates
- **Rollback**: Easy rollback capabilities
- **Monitoring**: Post-deployment health checks

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow the existing code style and conventions
- Write tests for new features
- Update documentation as needed
- Ensure all CI checks pass

## 📖 Documentation

- [Architecture Documentation](docs/architecture.md)
- [Deployment Guide](docs/deployment.md)
- [API Documentation](http://localhost:8000/docs) (when running locally)
- [Frontend Components](docs/frontend_jsdoc/index.html)

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Issues**
   ```bash
   # Reset database
   rm backend/telegram_automation.db
   ./infra/scripts/migrate.sh
   ```

2. **Port Already in Use**
   ```bash
   # Kill processes on ports
   sudo lsof -ti:8000 | xargs kill -9
   sudo lsof -ti:3000 | xargs kill -9
   ```

3. **Docker Issues**
   ```bash
   # Clean Docker cache
   make clean
   docker system prune -a
   ```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

Aplikasi ini dibuat untuk tujuan edukasi dan otomasi personal. Pengguna bertanggung jawab penuh untuk mematuhi Terms of Service Telegram dan tidak melakukan spam. Penggunaan yang tidak bertanggung jawab dapat menyebabkan akun Telegram diblokir atau dibanned.

## 📞 Support

- 📧 Email: team@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/dygje12/telegram-automation/issues)
- 📖 Documentation: [Project Wiki](https://github.com/dygje12/telegram-automation/wiki)

---

**Dibuat dengan ❤️ menggunakan FastAPI, Telethon, React, TypeScript, dan Tailwind CSS**

