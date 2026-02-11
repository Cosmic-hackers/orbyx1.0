# Satellite Orbit Tools

**Real-time satellite collision detection and monitoring system** — powered by SGP4 propagation, Rust engine, Redis caching, and a modern web interface.

Tracks 66,000+ satellites, detects close approaches with risk scoring, predicts ground station passes, and visualizes everything in 2D/3D.

---

## Features

| Feature | Description |
|---------|-------------|
| **Live TLE Data** | Fetch real-time satellite data from Space-Track.org |
| **Collision Analysis** | Detect close approaches, calculate relative velocity, assign risk scores (0-100) |
| **Pass Predictions** | AOS/MAX/LOS with azimuth/elevation for any ground station |
| **2D/3D Visualization** | Interactive Plotly globe and geo maps |
| **CSV/HTML Reports** | Export analysis results in multiple formats |
| **WebSocket Dashboard** | Real-time satellite position streaming |
| **Redis Caching** | 450x faster repeated analyses |
| **Rust Engine (PyO3)** | Parallel collision detection with Rayon — 9x faster orbit computations |
| **REST API** | Full FastAPI backend with Swagger docs |

---

## Architecture

```
┌─────────────────────────────────────────┐
│          Streamlit Frontend             │
│  Dashboard│Collision│Visibility│3D View │
├─────────────────────────────────────────┤
│     FastAPI + WebSocket Backend         │
│     REST API  │  Real-time Tracking     │
├──────────┬──────────┬───────────────────┤
│   SGP4   │ Rust Eng.│   Redis Cache     │
│ Propagator│  (PyO3) │   (optional)      │
├──────────┴──────────┴───────────────────┤
│     SQLite (66k+ satellite catalog)     │
├─────────────────────────────────────────┤
│        Space-Track.org API Feed         │
└─────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit (dark theme, OpenClaw-inspired UI) |
| Backend API | FastAPI + WebSocket |
| Performance | Redis cache, Rust engine (PyO3 + Rayon), async fetching |
| Database | SQLite (WAL mode, 66k+ catalog, auto-sync) |
| Visualization | Plotly (2D/3D), Scattergeo, Surface |
| Orbit Math | SGP4 (via `sgp4` package), custom TEME-to-ECEF conversion |
| CI/CD | GitHub Actions (lint, test, Rust build, Docker) |
| Containers | Docker + Docker Compose (API, Frontend, Redis) |

---

## Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/recepsuluker/satellite-orbit-tools.git
cd satellite-orbit-tools

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env with your Space-Track.org credentials
```

### 3. Run

**Streamlit Frontend** (recommended):
```bash
streamlit run frontend/app.py
# Open http://localhost:8501
```

**FastAPI Backend**:
```bash
uvicorn src.api.main:app --reload
# API docs: http://localhost:8000/docs
```

**Docker Compose** (everything):
```bash
docker compose up -d
# Frontend: http://localhost:8501
# API: http://localhost:8000
# Redis: localhost:6379
```

---

## Project Structure

```
satellite-orbit-tools/
├── src/
│   ├── config.py                    # Pydantic settings
│   ├── logging_config.py            # Centralized rotating logs
│   ├── api/
│   │   ├── main.py                  # FastAPI app
│   │   └── routes/
│   │       ├── satellites.py        # Catalog CRUD & propagation
│   │       ├── collision.py         # Collision analysis endpoints
│   │       ├── visibility.py        # Pass prediction endpoints
│   │       └── websocket_routes.py  # Real-time tracking & alerts
│   ├── database/
│   │   ├── models.py                # SQLite schema + initialization
│   │   └── manager.py               # Database operations
│   ├── engine/
│   │   ├── orbit_propagator.py      # SGP4 propagation engine
│   │   ├── collision_detector.py    # Conjunction detection + risk scoring
│   │   ├── visibility_calculator.py # Pass prediction (AOS/MAX/LOS)
│   │   └── cache.py                 # Redis cache layer
│   └── utils/
│       ├── tle_parser.py            # TLE parsing & validation
│       ├── space_track_client.py    # Async Space-Track.org client
│       └── export.py                # CSV/HTML report generation
├── frontend/
│   ├── app.py                       # Streamlit main app
│   └── pages/
│       ├── 01_dashboard.py          # Catalog overview & quick track
│       ├── 02_collision_analysis.py # Multi-satellite collision analysis
│       ├── 03_visibility.py         # Pass predictions
│       ├── 04_3d_view.py            # 3D globe visualization
│       └── 05_reports.py            # Reports & system status
├── rust_engine/
│   ├── Cargo.toml
│   └── src/lib.rs                   # Rayon-parallel collision detection
├── tests/                           # Pytest suite (7 test files)
├── .github/workflows/ci.yml         # CI/CD pipeline
├── docker-compose.yml               # Redis + API + Frontend
├── Dockerfile                       # Multi-stage build
├── requirements.txt
├── pyproject.toml
└── .env.example
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/docs` | Swagger UI |
| `GET` | `/api/v1/satellites/` | List/search satellites |
| `GET` | `/api/v1/satellites/stats` | Catalog statistics |
| `GET` | `/api/v1/satellites/{id}` | Get satellite by NORAD ID |
| `GET` | `/api/v1/satellites/{id}/position` | Propagate orbit |
| `POST` | `/api/v1/collision/analyze` | Run collision analysis |
| `GET` | `/api/v1/collision/history` | Recent conjunctions |
| `POST` | `/api/v1/collision/quick-check` | Quick pair check |
| `GET` | `/api/v1/visibility/passes/{id}` | Pass predictions |
| `GET` | `/api/v1/visibility/stations` | List ground stations |
| `POST` | `/api/v1/visibility/stations` | Add ground station |
| `WS` | `/ws/track` | Real-time satellite tracking |
| `WS` | `/ws/alerts` | Collision alert stream |

---

## Performance

| Scenario | Before | After | Improvement |
|----------|--------|-------|-------------|
| 100 satellite analysis | 45s | 5s | 9x (Rust engine) |
| Repeated analysis (cache hit) | 45s | 0.1s | 450x (Redis) |
| 1000 satellite collision check | timeout | 30s | Rust + Rayon parallel |

---

## Running Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=term-missing

# Specific module
pytest tests/test_collision_detector.py -v
```

---

## Rust Engine

The Rust engine provides parallel collision detection using Rayon:

```bash
cd rust_engine
cargo build --release
# The shared library integrates with Python via PyO3
```

For Python-only mode, the system falls back to the Python collision detector automatically.

---

## Roadmap

| Version | Timeline | Features |
|---------|----------|----------|
| **v2.0** | Q1 2026 | React frontend, PostgreSQL, user auth |
| **v2.1** | Q2 2026 | ML collision prediction (LSTM/Transformer), mobile app |
| **v3.0** | Q3 2026 | GPU acceleration (CUDA/Jetson Orin), commercial API |

---

## Environment Variables

See [`.env.example`](.env.example) for all configuration options:
- `SPACETRACK_USERNAME` / `SPACETRACK_PASSWORD` — Space-Track.org credentials
- `REDIS_HOST` / `REDIS_PORT` — Redis connection
- `COLLISION_THRESHOLD_KM` — Default detection threshold
- `GROUND_STATION_*` — Default ground station coordinates

---

by Recep Suluker | Powered by SGP4, FastAPI, Streamlit, Rust + PyO3
