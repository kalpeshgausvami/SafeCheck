# Reel Truth Checker Backend 🚀🐍

The backend service is built using **FastAPI** (Python 3.11) and provides the core REST API endpoints, task orchestration using **Celery** and **Redis**, and transactional state storage using **PostgreSQL**.

---

## 📂 Backend Directory Structure

```directory
backend/
├── app/
│   ├── main.py              # Application entry point and lifespan setup
│   ├── api/                 # Endpoint controllers (Auth, Jobs, Billing, etc.)
│   ├── core/                # Configuration settings, exceptions, rate limits
│   ├── database/            # Database session, engine, and base metadata
│   ├── intelligence/        # Custom routes for claim analysis and verification
│   ├── trust_safety/        # Custom routes for account safety metrics
│   ├── workers/             # Celery application declaration and task functions
│   └── tests/               # Pytest unit tests for APIs and database integrations
├── Dockerfile               # Multi-stage production container build file
├── docker-compose.yml       # Dev service orchestrator (DB, Redis, Web, Worker, ML)
└── requirements.txt         # Core backend python dependencies
```

---

## ⚙️ Configuration

The application is configured using environment variables (or a local `.env` file). The settings class resides in `app/core/config.py`.

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | `postgresql+asyncpg://postgres:password123@localhost:5432/reel_truth_db` | Async database URL for FastAPI. |
| `DATABASE_SYNC_URL` | `postgresql://postgres:password123@localhost:5432/reel_truth_db` | Sync database URL for migrations. |
| `CELERY_BROKER_URL` | `redis://localhost:6379/0` | Redis message broker URL for Celery. |
| `CELERY_RESULT_BACKEND` | `redis://localhost:6379/0` | Redis result backend for Celery tasks. |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis URL for caching/rate-limiting. |
| `SECRET_KEY` | `rtc_jwt_secret_key_...` | JWT secret signing key. |
| `ALGORITHM` | `HS256` | JWT signing algorithm. |
| `ML_SERVICE_URL` | `http://localhost:8080` | URL endpoint for the ML Service. |

---

## 🛠️ Local Installation & Development

### 1. Set Up Virtual Environment
Ensure you have Python 3.11 installed.
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Set Up External Services
FastAPI expects PostgreSQL and Redis. If you don't want to run them on your system, launch them with Docker:
```bash
docker run -d --name rtc_postgres -e POSTGRES_PASSWORD=password123 -e POSTGRES_DB=reel_truth_db -p 5432:5432 postgres:15-alpine
docker run -d --name rtc_redis -p 6379:6379 redis:7-alpine
```

### 3. Run FastAPI Application
Start the Uvicorn reload server:
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation will be available at:
*   Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
*   ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### 4. Run Celery Worker
Launch a Celery worker instance to process background download and analysis jobs:
```bash
# Windows (eventlet is recommended on Windows)
pip install eventlet
celery -A app.workers.celery_app worker --loglevel=info -P eventlet

# Linux/macOS
celery -A app.workers.celery_app worker --loglevel=info
```

---

## 🧪 Testing

Unit tests are written using `pytest`. The database session is mocked or runs on a test database:
```bash
# Run pytest inside the backend/ folder
pytest app/tests/
```

---

## 🚢 Docker & Containerization

A multi-stage `Dockerfile` is provided for containerizing the API web service and the Celery worker.

*   **Build the API Image**:
    ```bash
    docker build -t rtc-api:latest .
    ```
*   **Run Web API Service**:
    ```bash
    docker run -d -p 8000:8000 --env-file=.env rtc-api:latest
    ```
*   **Run Celery Worker**:
    ```bash
    docker run -d --entrypoint celery rtc-api:latest -A app.workers.celery_app worker --loglevel=info
    ```
