# ─────────────────────────────────────────
# Stage 1: Builder
# ─────────────────────────────────────────
FROM python:3.12-alpine AS builder

# Install build dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev \
    libffi-dev \
    openssl-dev \
    cargo \
    rust \
    jpeg-dev \
    zlib-dev \
    freetype-dev \
    libpng-dev \
    build-base

WORKDIR /build

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements.txt

# ─────────────────────────────────────────
# Stage 2: Production
# ─────────────────────────────────────────
FROM python:3.12-alpine AS production

LABEL maintainer="ISP Software Team"
LABEL version="1.0.1"

# Install runtime dependencies only
RUN apk add --no-cache \
    postgresql-client \
    libpq \
    jpeg \
    zlib \
    freetype \
    libpng \
    tzdata \
    curl \
    && cp /usr/share/zoneinfo/Asia/Dhaka /etc/localtime \
    && echo "Asia/Dhaka" > /etc/timezone \
    && apk del tzdata

# Create non-root user for security
RUN addgroup -g 1001 -S ispgroup && \
    adduser -u 1001 -S ispuser -G ispgroup

WORKDIR /app

# Copy wheels from builder and install
COPY --from=builder /build/wheels /wheels
RUN pip install --no-cache /wheels/* && rm -rf /wheels

# Copy application code
COPY --chown=ispuser:ispgroup . .

# Create necessary directories
RUN mkdir -p /app/staticfiles /app/media /app/logs && \
    chown -R ispuser:ispgroup /app

USER ispuser

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/api/health/ || exit 1

# Default ASGI server (daphne) so WebSocket / Channels work.
# Override the command in docker-compose for celery/beat/flower services.
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]
