# Deployment Guide

This guide covers the deployment process for the Telegram Automation application.

## Prerequisites

- Docker and Docker Compose installed
- Git repository access
- Environment variables configured
- SSL certificates (for production)

## Environment Setup

### Development Environment

1. Clone the repository:
```bash
git clone https://github.com/dygje12/telegram-automation
cd telegram-automation
```

2. Copy environment files:
```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

3. Configure environment variables in both `.env` files

4. Start development environment:
```bash
make dev
```

### Production Environment

#### Using Docker Compose

1. Prepare production environment files:
```bash
cp backend/.env.example backend/.env.prod
cp frontend/.env.example frontend/.env.prod
```

2. Configure production environment variables

3. Deploy using Docker Compose:
```bash
make deploy
```

#### Manual Deployment

##### Backend Deployment

1. Install Python dependencies:
```bash
cd backend
pip install -r requirements/prod.txt
```

2. Run database migrations:
```bash
./infra/scripts/migrate.sh
```

3. Start the backend server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

##### Frontend Deployment

1. Install Node.js dependencies:
```bash
cd frontend
npm install
```

2. Build the frontend:
```bash
npm run build
```

3. Serve the built files using a web server (nginx, Apache, etc.)

## Docker Configuration

### Backend Dockerfile

The backend uses a multi-stage Docker build:

- **Build stage**: Installs dependencies and builds the application
- **Runtime stage**: Runs the application with a non-root user

### Frontend Dockerfile

The frontend uses a multi-stage Docker build:

- **Build stage**: Installs dependencies and builds the React application
- **Runtime stage**: Serves the built files using nginx

## Environment Variables

### Backend Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///./telegram_automation.db` |
| `TELEGRAM_API_ID` | Telegram API ID | Required |
| `TELEGRAM_API_HASH` | Telegram API Hash | Required |
| `SECRET_KEY` | JWT secret key | Required |
| `ENVIRONMENT` | Environment (development/production) | `development` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Frontend Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Backend API URL | `http://localhost:8000` |
| `VITE_API_VERSION` | API version | `v1` |
| `VITE_APP_NAME` | Application name | `Telegram Automation` |

## Health Checks

The application includes health check endpoints:

- Backend: `GET /health`
- Frontend: Served by nginx with health check configuration

## Monitoring

### Logs

- Backend logs are written to stdout/stderr and can be collected by Docker
- Frontend logs are handled by nginx
- Use `docker-compose logs` to view application logs

### Metrics

- Backend exposes metrics at `/metrics` (if enabled)
- Monitor application performance using the dashboard

## Security Considerations

### Production Security

1. **Environment Variables**: Never commit `.env` files to version control
2. **SSL/TLS**: Use HTTPS in production with valid SSL certificates
3. **Firewall**: Configure firewall rules to restrict access
4. **Updates**: Keep dependencies updated using Dependabot
5. **Secrets Management**: Use proper secrets management in production

### Network Security

- Backend and frontend communicate over internal Docker network
- Only necessary ports are exposed to the host
- CORS is configured to allow only trusted origins

## Backup and Recovery

### Database Backup

Use the provided backup script:
```bash
./infra/scripts/backup-db.sh
```

### Recovery

1. Stop the application
2. Restore the database from backup
3. Restart the application

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Check database URL in environment variables
   - Ensure database is accessible
   - Run migrations if needed

2. **API Connection Issues**
   - Verify backend is running and accessible
   - Check CORS configuration
   - Verify API endpoints

3. **Authentication Issues**
   - Check Telegram API credentials
   - Verify JWT secret key configuration
   - Check token expiration settings

### Debug Mode

Enable debug mode by setting:
- Backend: `DEBUG=True` in environment variables
- Frontend: `VITE_DEBUG=true` in environment variables

## Scaling

### Horizontal Scaling

- Backend can be scaled by running multiple instances behind a load balancer
- Frontend is stateless and can be served from CDN
- Database may need to be moved to a dedicated server for high load

### Performance Optimization

- Use Redis for caching (optional)
- Configure nginx for static file caching
- Optimize database queries
- Use connection pooling for database connections

## CI/CD Pipeline

The project includes GitHub Actions workflows for:

- **Continuous Integration**: Runs tests and linting on every push
- **Continuous Deployment**: Deploys to production on main branch updates

### Pipeline Stages

1. **Lint**: Code quality checks
2. **Test**: Unit and integration tests
3. **Build**: Docker image building
4. **Deploy**: Deployment to production environment

## Support

For deployment issues:

1. Check the logs using `docker-compose logs`
2. Verify environment configuration
3. Consult the troubleshooting section
4. Create an issue on GitHub if problems persist

