FROM python:3.11-slim AS base

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# Create data/logs directories
RUN mkdir -p data logs

EXPOSE 8000

# FastAPI server
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ── Streamlit target ────────────────────────────────────────────
FROM base AS streamlit

EXPOSE 8501

CMD ["streamlit", "run", "frontend/app.py", \
     "--server.port=8501", \
     "--server.headless=true", \
     "--server.address=0.0.0.0"]

# ── Rust engine builder ─────────────────────────────────────────
FROM rust:1.75-slim AS rust-builder

RUN apt-get update && apt-get install -y python3-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /build
COPY rust_engine/ .

RUN cargo build --release

# ── Production with Rust engine ─────────────────────────────────
FROM base AS production

# Copy Rust shared library if built
# COPY --from=rust-builder /build/target/release/libsatellite_rs.so /app/satellite_rs.so

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
