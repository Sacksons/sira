# SIRA Platform

**Shipping Intelligence & Risk Analytics Platform**

Sponsored by: Energie Partners (EP)

## Overview

SIRA is a comprehensive platform for managing shipping movements, tracking security events, and generating compliance reports. It provides:

- **Digital Control Tower**: Track cargo movements and logistics in real-time
- **Security Intelligence**: Monitor events, manage alerts, and investigate incidents
- **Case Management**: Handle security cases with evidence tracking
- **Playbook System**: Standardized incident response procedures
- **Real-time Notifications**: WebSocket and email alerts
- **Compliance Export**: Generate audit-ready documentation (PDF/JSON)

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens with bcrypt password hashing
- **Migrations**: Alembic
- **PDF Generation**: ReportLab / WeasyPrint

### Frontend
- **Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand + React Query
- **Charts**: Chart.js
- **Build Tool**: Vite

### DevOps
- **CI/CD**: GitHub Actions
- **Containerization**: Docker
- **Deployment**: PythonAnywhere

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL 12+

### Local Development Setup

1. **Clone the repository**
```bash
git clone https://github.com/your-username/sira.git
cd sira
```

2. **Run setup script**
```bash
chmod +x scripts/setup_local.sh
./scripts/setup_local.sh
```

3. **Configure environment**
```bash
cd backend
cp .env.example .env
# Edit .env with your database credentials
```

4. **Create database**
```bash
createdb sira_db
# Or using psql:
psql -U postgres -c "CREATE DATABASE sira_db;"
```

5. **Create admin user**
```bash
cd backend
source venv/bin/activate
python ../scripts/create_admin.py
```

6. **Start the backend**
```bash
uvicorn app.main:app --reload
```

7. **Start the frontend** (in a new terminal)
```bash
cd frontend
npm run dev
```

8. **Access the application**
- Frontend: http://localhost:3000
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## Project Structure

```
sira/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # API routes
│   │   ├── core/            # Config, database, security
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic
│   │   └── main.py          # FastAPI application
│   ├── tests/               # Test suite
│   ├── alembic/             # Database migrations
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API services
│   │   ├── stores/          # Zustand stores
│   │   └── types/           # TypeScript types
│   └── package.json
├── .github/workflows/       # CI/CD pipelines
└── scripts/                 # Utility scripts
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/token` - Login
- `POST /api/v1/auth/register` - Register
- `GET /api/v1/auth/me` - Current user

### Alerts
- `GET /api/v1/alerts/` - List alerts
- `POST /api/v1/alerts/` - Create alert
- `POST /api/v1/alerts/{id}/acknowledge` - Acknowledge alert
- `POST /api/v1/alerts/{id}/resolve` - Resolve alert

### Cases
- `GET /api/v1/cases/` - List cases
- `POST /api/v1/cases/` - Create case
- `GET /api/v1/cases/{id}/export` - Export compliance pack

### Movements
- `GET /api/v1/movements/` - List movements
- `POST /api/v1/movements/` - Create movement

See full API documentation at `/docs` when running the server.

## User Roles

| Role | Permissions |
|------|-------------|
| `admin` | Full access to all features |
| `supervisor` | Manage users, cases, alerts |
| `security_lead` | Manage alerts, cases, playbooks |
| `operator` | View and create movements, events |

## Running Tests

```bash
cd backend
source venv/bin/activate
pytest tests/ -v --cov=app
```

## Deployment

### PythonAnywhere

1. Create a PythonAnywhere account
2. Set up a PostgreSQL database
3. Clone repository to `/home/<username>/sira`
4. Configure WSGI file
5. Set environment variables
6. Reload web app

### Docker

```bash
cd backend
docker-compose up -d
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

Proprietary - Energie Partners (EP)

## Support

For issues and questions:
- Create an issue in the repository
- Contact: support@sira-platform.com
