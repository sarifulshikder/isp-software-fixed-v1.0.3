# ─────────────────────────────────────────
# Stage 1: Build
# ─────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install --legacy-peer-deps

# Copy source and build
COPY . .
RUN npm run build

# ─────────────────────────────────────────
# Stage 2: Output stage
# The build output (/app/dist) is published to a shared Docker volume
# (`frontend_build`) and served by the main `nginx` service.
# This container only needs to keep `/app/dist` populated, so we use a
# minimal image that exits immediately after the volume mount copy.
# ─────────────────────────────────────────
FROM alpine:3.19 AS production

WORKDIR /app
COPY --from=builder /app/dist /app/dist

# Keep the container alive long enough for Docker to seed the named
# volume on first start, then idle. Nginx serves the files.
CMD ["sh", "-c", "echo 'Frontend build published to volume'; tail -f /dev/null"]
