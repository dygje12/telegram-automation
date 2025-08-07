# Telegram Automation - Production-Ready

This repository contains a Telegram automation application, refactored and enhanced for production readiness. It includes a FastAPI backend, a React frontend with TypeScript, Docker support, and CI/CD pipelines.

## 🚀 Features

### Backend (FastAPI)
- **Clean Architecture**: Organized into API, services, CRUD, and database layers for maintainability and scalability.
- **Security**: Implemented rate limiting, input validation, secure error handling, JWT authentication, and password hashing.
- **Production Readiness**: Comprehensive logging, monitoring, and error tracking.
- **Database Optimization**: Efficient CRUD operations with eager loading, query optimization, and connection pooling.

### Frontend (React with TypeScript)
- **Feature-Based Structure**: Components organized by business domains for better modularity.
- **Performance Optimized**: Code splitting, bundle optimization, lazy loading, and runtime performance enhancements.
- **Error Resilient**: Error boundaries for graceful error handling and structured error reporting.
- **Type-Safe Validation**: Utilizes Zod schemas for robust form validation.
- **TypeScript Migration**: Full migration to TypeScript for improved code quality and maintainability.

### Infrastructure
- **Docker Support**: Multi-stage Dockerfiles for both backend and frontend, ensuring lightweight and secure images.
- **Docker Compose**: Simplified local development setup with `docker-compose.yml`.
- **CI/CD**: GitHub Actions workflows for automated linting, testing, and building, ensuring code quality and rapid deployment.

## 🛠️ Setup and Development

### Prerequisites
- Docker and Docker Compose
- Node.js (for frontend development, though Docker is preferred)
- Python (for backend development, though Docker is preferred)

### Local Development

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/dygje12/telegram-automation.git
    cd telegram-automation
    ```

2.  **Start the development environment:**
    Use the `make dev` command to build and run both backend and frontend services using Docker Compose.
    ```bash
    make dev
    ```
    The backend will be accessible at `http://localhost:8000` and the frontend at `http://localhost:80`.

### Building Docker Images

To build the Docker images without running them:

```bash
make build
```

### Running Tests

To run backend and frontend tests:

```bash
make test
```

### Linting

To run linting for both backend and frontend:

```bash
make lint
```

### Cleaning Up

To stop and remove Docker containers, volumes, and clean up local build artifacts:

```bash
make clean
```

## 📁 Project Structure

```
telegram-automation/
├── backend/                # FastAPI Backend
│   ├── app/                # Main application code
│   │   ├── api/            # API endpoints (versioned)
│   │   ├── core/           # Shared core logic (security, logging, exceptions)
│   │   ├── crud/           # Database access layer
│   │   ├── models/         # Database models and Pydantic schemas
│   │   ├── services/       # Business logic
│   │   ├── middleware/     # Custom FastAPI middleware
│   │   ├── utils/          # Utility functions
│   │   └── tests/          # Unit and Integration tests
│   ├── requirements/       # Python dependency files (base, dev, prod)
│   ├── pyproject.toml      # Poetry configuration for dependencies and tools
│   └── ...
├── frontend/               # React Frontend
│   ├── src/                # Source code
│   │   ├── features/       # Feature-specific components and logic
│   │   ├── components/     # Reusable UI components
│   │   ├── hooks/          # Custom React hooks
│   │   ├── api/            # API client and services
│   │   ├── utils/          # Utility functions
│   │   └── tests/          # Frontend tests
│   ├── public/             # Static assets
│   ├── tsconfig.json       # TypeScript configuration
│   ├── vite.config.ts      # Vite build configuration
│   ├── package.json        # Node.js dependencies
│   └── ...
├── infra/                  # Infrastructure related files
│   └── docker/             # Dockerfiles and Docker Compose
│       ├── backend.Dockerfile
│       ├── frontend.Dockerfile
│       └── docker-compose.yml
├── .github/                # GitHub Actions workflows
│   └── workflows/
│       └── main.yml        # CI/CD pipeline
├── docs/                   # Documentation (e.g., architecture diagrams)
├── Makefile                # Commands for development, build, test, lint
└── README_PRODUCTION.md    # This file
```

## 📊 CI/CD Pipeline (GitHub Actions)

The `main.yml` workflow automates the following:

-   **Backend**: Installs dependencies, runs linting (black, isort, mypy), and executes tests with coverage (minimum 80%).
-   **Frontend**: Installs dependencies, runs linting, and performs a production build.
-   **Docker**: Builds both backend and frontend Docker images.
-   **DevEx Check**: Briefly brings up Docker Compose services to ensure local development setup works.

## 🤝 Contributing

Contributions are welcome! Please ensure your code adheres to the established quality standards and passes all CI/CD checks.

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.


