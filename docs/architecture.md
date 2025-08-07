# System Architecture

## Overview

Telegram Automation adalah aplikasi fullstack production-ready yang dibangun dengan arsitektur modern dan scalable. Aplikasi ini menggunakan clean architecture principles dengan separation of concerns yang jelas antara presentation layer, business logic, dan data access layer.

## High-Level Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        WEB[Web Browser]
        MOBILE[Mobile Browser]
    end
    
    subgraph "Load Balancer"
        NGINX[Nginx]
    end
    
    subgraph "Frontend"
        REACT[React + TypeScript]
        TAILWIND[Tailwind CSS]
        ROUTER[React Router]
    end
    
    subgraph "Backend API"
        FASTAPI[FastAPI]
        AUTH[Authentication]
        MIDDLEWARE[Middleware Layer]
    end
    
    subgraph "Business Logic"
        SERVICES[Service Layer]
        TELEGRAM[Telethon Client]
        SCHEDULER[APScheduler]
    end
    
    subgraph "Data Layer"
        DATABASE[(SQLite/PostgreSQL)]
        CACHE[(Redis Cache)]
    end
    
    subgraph "External Services"
        TELEGRAM_API[Telegram API]
        MONITORING[Monitoring Services]
    end
    
    WEB --> NGINX
    MOBILE --> NGINX
    NGINX --> REACT
    REACT --> FASTAPI
    FASTAPI --> AUTH
    FASTAPI --> MIDDLEWARE
    MIDDLEWARE --> SERVICES
    SERVICES --> TELEGRAM
    SERVICES --> SCHEDULER
    SERVICES --> DATABASE
    SERVICES --> CACHE
    TELEGRAM --> TELEGRAM_API
    FASTAPI --> MONITORING
```

## Component Architecture

### Frontend Architecture

```mermaid
graph LR
    subgraph "React Application"
        PAGES[Pages]
        FEATURES[Features]
        COMPONENTS[Components]
        HOOKS[Custom Hooks]
        STORE[State Management]
        API[API Client]
    end
    
    subgraph "Routing"
        ROUTER[React Router]
        GUARDS[Route Guards]
    end
    
    subgraph "Styling"
        TAILWIND[Tailwind CSS]
        THEMES[Theme System]
    end
    
    PAGES --> FEATURES
    FEATURES --> COMPONENTS
    FEATURES --> HOOKS
    HOOKS --> STORE
    HOOKS --> API
    ROUTER --> GUARDS
    GUARDS --> PAGES
    COMPONENTS --> TAILWIND
    TAILWIND --> THEMES
```

### Backend Architecture

```mermaid
graph TB
    subgraph "API Layer"
        ROUTES[API Routes]
        MIDDLEWARE[Middleware]
        VALIDATION[Request Validation]
    end
    
    subgraph "Service Layer"
        AUTH_SERVICE[Auth Service]
        MESSAGE_SERVICE[Message Service]
        GROUP_SERVICE[Group Service]
        SCHEDULER_SERVICE[Scheduler Service]
        TELEGRAM_SERVICE[Telegram Service]
    end
    
    subgraph "Data Access Layer"
        CRUD[CRUD Operations]
        MODELS[SQLAlchemy Models]
        SCHEMAS[Pydantic Schemas]
    end
    
    subgraph "Core Layer"
        CONFIG[Configuration]
        SECURITY[Security Utils]
        LOGGING[Logging]
        EXCEPTIONS[Exception Handling]
    end
    
    ROUTES --> MIDDLEWARE
    MIDDLEWARE --> VALIDATION
    VALIDATION --> AUTH_SERVICE
    VALIDATION --> MESSAGE_SERVICE
    VALIDATION --> GROUP_SERVICE
    VALIDATION --> SCHEDULER_SERVICE
    
    AUTH_SERVICE --> TELEGRAM_SERVICE
    MESSAGE_SERVICE --> TELEGRAM_SERVICE
    GROUP_SERVICE --> TELEGRAM_SERVICE
    SCHEDULER_SERVICE --> TELEGRAM_SERVICE
    
    AUTH_SERVICE --> CRUD
    MESSAGE_SERVICE --> CRUD
    GROUP_SERVICE --> CRUD
    SCHEDULER_SERVICE --> CRUD
    
    CRUD --> MODELS
    CRUD --> SCHEMAS
    
    AUTH_SERVICE --> CONFIG
    AUTH_SERVICE --> SECURITY
    AUTH_SERVICE --> LOGGING
    AUTH_SERVICE --> EXCEPTIONS
```

## Data Flow

### Authentication Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as Auth API
    participant T as Telegram Service
    participant TG as Telegram API
    participant DB as Database
    
    U->>F: Enter phone number
    F->>A: POST /auth/login
    A->>T: Initialize Telegram client
    T->>TG: Send code request
    TG-->>T: Code sent to phone
    T-->>A: Code request successful
    A-->>F: Code sent response
    
    U->>F: Enter verification code
    F->>A: POST /auth/verify-code
    A->>T: Verify code with Telegram
    T->>TG: Verify code
    TG-->>T: Authentication successful
    T-->>A: Session data
    A->>DB: Store encrypted session
    A-->>F: JWT token + user data
    F-->>U: Redirect to dashboard
```

### Message Sending Flow

```mermaid
sequenceDiagram
    participant S as Scheduler
    participant MS as Message Service
    participant GS as Group Service
    participant TS as Telegram Service
    participant TG as Telegram API
    participant DB as Database
    
    S->>MS: Get active messages
    MS->>DB: Query messages
    DB-->>MS: Message list
    
    S->>GS: Get active groups
    GS->>DB: Query groups
    DB-->>GS: Group list
    
    loop For each message-group pair
        S->>TS: Send message to group
        TS->>TG: Send message API call
        
        alt Success
            TG-->>TS: Message sent
            TS->>DB: Log success
        else Error
            TG-->>TS: Error response
            TS->>DB: Log error
            TS->>GS: Check if should blacklist
            GS->>DB: Add to blacklist if needed
        end
    end
```

## Security Architecture

### Authentication & Authorization

```mermaid
graph TB
    subgraph "Authentication Layer"
        JWT[JWT Tokens]
        REFRESH[Refresh Tokens]
        SESSION[Session Management]
    end
    
    subgraph "Authorization Layer"
        RBAC[Role-Based Access]
        PERMISSIONS[Permissions]
        GUARDS[Route Guards]
    end
    
    subgraph "Security Middleware"
        RATE_LIMIT[Rate Limiting]
        CORS[CORS Protection]
        VALIDATION[Input Validation]
        ENCRYPTION[Data Encryption]
    end
    
    subgraph "Data Protection"
        ENCRYPT_REST[Encryption at Rest]
        ENCRYPT_TRANSIT[Encryption in Transit]
        SECRETS[Secret Management]
    end
    
    JWT --> RBAC
    REFRESH --> SESSION
    RBAC --> PERMISSIONS
    PERMISSIONS --> GUARDS
    
    RATE_LIMIT --> CORS
    CORS --> VALIDATION
    VALIDATION --> ENCRYPTION
    
    ENCRYPTION --> ENCRYPT_REST
    ENCRYPTION --> ENCRYPT_TRANSIT
    ENCRYPT_REST --> SECRETS
```

## Database Schema

### Entity Relationship Diagram

```mermaid
erDiagram
    User ||--o{ Message : creates
    User ||--o{ Group : manages
    User ||--o{ Blacklist : maintains
    User ||--o{ Log : generates
    User ||--|| Settings : configures
    
    Message ||--o{ Log : references
    
    User {
        int id PK
        text api_id "encrypted"
        text api_hash "encrypted"
        text phone_number "encrypted"
        text session_data "encrypted"
        datetime created_at
        datetime updated_at
    }
    
    Message {
        int id PK
        int user_id FK
        string title
        text content
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    
    Group {
        int id PK
        int user_id FK
        string group_id
        string group_name
        string username
        text invite_link
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    
    Blacklist {
        int id PK
        int user_id FK
        string group_id
        string blacklist_type
        text reason
        datetime expires_at
        datetime created_at
    }
    
    Log {
        int id PK
        int user_id FK
        string group_id
        int message_id FK
        string status
        text error_message
        datetime created_at
    }
    
    Settings {
        int id PK
        int user_id FK
        int min_interval
        int max_interval
        int min_delay
        int max_delay
        datetime created_at
        datetime updated_at
    }
```

## Deployment Architecture

### Production Deployment

```mermaid
graph TB
    subgraph "Load Balancer"
        LB[Load Balancer/CDN]
    end
    
    subgraph "Web Tier"
        NGINX1[Nginx Instance 1]
        NGINX2[Nginx Instance 2]
    end
    
    subgraph "Application Tier"
        APP1[Backend Instance 1]
        APP2[Backend Instance 2]
        APP3[Backend Instance 3]
    end
    
    subgraph "Data Tier"
        DB_PRIMARY[(Primary Database)]
        DB_REPLICA[(Read Replica)]
        REDIS[(Redis Cache)]
    end
    
    subgraph "Monitoring"
        LOGS[Log Aggregation]
        METRICS[Metrics Collection]
        ALERTS[Alerting]
    end
    
    LB --> NGINX1
    LB --> NGINX2
    
    NGINX1 --> APP1
    NGINX1 --> APP2
    NGINX2 --> APP2
    NGINX2 --> APP3
    
    APP1 --> DB_PRIMARY
    APP2 --> DB_PRIMARY
    APP3 --> DB_PRIMARY
    
    APP1 --> DB_REPLICA
    APP2 --> DB_REPLICA
    APP3 --> DB_REPLICA
    
    APP1 --> REDIS
    APP2 --> REDIS
    APP3 --> REDIS
    
    APP1 --> LOGS
    APP2 --> LOGS
    APP3 --> LOGS
    
    LOGS --> METRICS
    METRICS --> ALERTS
```

### Container Architecture

```mermaid
graph TB
    subgraph "Docker Compose"
        subgraph "Frontend Container"
            REACT_APP[React App]
            NGINX_FRONTEND[Nginx]
        end
        
        subgraph "Backend Container"
            FASTAPI_APP[FastAPI App]
            PYTHON_RUNTIME[Python Runtime]
        end
        
        subgraph "Database Container"
            SQLITE[SQLite]
            POSTGRES[PostgreSQL]
        end
        
        subgraph "Cache Container"
            REDIS_CACHE[Redis]
        end
        
        subgraph "Reverse Proxy"
            NGINX_PROXY[Nginx Proxy]
        end
    end
    
    NGINX_PROXY --> REACT_APP
    NGINX_PROXY --> FASTAPI_APP
    FASTAPI_APP --> SQLITE
    FASTAPI_APP --> POSTGRES
    FASTAPI_APP --> REDIS_CACHE
```

## Performance Considerations

### Caching Strategy

```mermaid
graph LR
    subgraph "Client Side"
        BROWSER_CACHE[Browser Cache]
        LOCAL_STORAGE[Local Storage]
    end
    
    subgraph "CDN Layer"
        CDN[Content Delivery Network]
    end
    
    subgraph "Application Layer"
        REDIS_CACHE[Redis Cache]
        MEMORY_CACHE[In-Memory Cache]
    end
    
    subgraph "Database Layer"
        QUERY_CACHE[Query Cache]
        CONNECTION_POOL[Connection Pool]
    end
    
    BROWSER_CACHE --> CDN
    CDN --> REDIS_CACHE
    REDIS_CACHE --> MEMORY_CACHE
    MEMORY_CACHE --> QUERY_CACHE
    QUERY_CACHE --> CONNECTION_POOL
```

### Scaling Strategy

1. **Horizontal Scaling**: Multiple backend instances behind load balancer
2. **Database Scaling**: Read replicas for read-heavy operations
3. **Caching**: Redis for session storage and frequently accessed data
4. **CDN**: Static asset delivery through CDN
5. **Queue System**: Background job processing for heavy operations

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Telegram Client**: Telethon
- **Database**: SQLite (development) / PostgreSQL (production)
- **ORM**: SQLAlchemy
- **Validation**: Pydantic
- **Authentication**: JWT
- **Scheduling**: APScheduler
- **Testing**: Pytest
- **Code Quality**: Black, isort, mypy, Bandit

### Frontend
- **Framework**: React 18+ with TypeScript
- **Styling**: Tailwind CSS
- **Routing**: React Router
- **State Management**: React Query + Context API
- **UI Components**: Radix UI + Custom Components
- **Build Tool**: Vite
- **Testing**: Jest + React Testing Library
- **Code Quality**: ESLint + Prettier

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Reverse Proxy**: Nginx
- **CI/CD**: GitHub Actions
- **Monitoring**: Built-in health checks + logging
- **Security**: HTTPS, CORS, Rate limiting, Input validation

## Best Practices

### Code Organization
- **Clean Architecture**: Separation of concerns with clear layer boundaries
- **Feature-based Structure**: Frontend organized by features, not file types
- **Dependency Injection**: Loose coupling between components
- **Error Handling**: Comprehensive error handling at all layers

### Security
- **Data Encryption**: Sensitive data encrypted at rest and in transit
- **Input Validation**: All inputs validated and sanitized
- **Rate Limiting**: API rate limiting to prevent abuse
- **Secret Management**: No secrets in code, environment variables only

### Performance
- **Lazy Loading**: Components and routes loaded on demand
- **Caching**: Multi-layer caching strategy
- **Database Optimization**: Proper indexing and query optimization
- **Asset Optimization**: Minification and compression

### Monitoring
- **Health Checks**: Comprehensive health check endpoints
- **Logging**: Structured logging with appropriate log levels
- **Metrics**: Performance and business metrics collection
- **Alerting**: Automated alerting for critical issues

