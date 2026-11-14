# Scheduler Application - Production Deployment Guide

## Overview

This project now has separate development and production Docker configurations for both UI and API services.

## Docker Configuration Changes

### File Structure

```
.
├── docker-compose.yml           # Development configuration
├── docker-compose.prod.yml      # Production configuration
├── api/
│   ├── Dockerfile              # Production Dockerfile
│   ├── Dockerfile.dev          # Development Dockerfile
│   ├── requirements-base.txt   # Production dependencies only
│   └── requirements-dev.txt    # Development tools
├── ui/
│   ├── Dockerfile              # Production Dockerfile
│   └── Dockerfile.dev          # Development Dockerfile
└── .env.example                # Environment variable template
```

### Key Changes

1. **Production Dockerfiles**
   - **API**: Multi-stage build with separated dev/prod dependencies
   - **UI**: Multi-stage build with Node.js static file serving

2. **Dependency Separation**
   - Production dependencies in `requirements-base.txt`
   - Development tools in `requirements-dev.txt`

3. **Environment Configuration**
   - `.env.example` template for production environment variables
   - Development configuration remains in `docker-compose.yml`

## Development vs Production

### Development

```bash
# Uses Dockerfile.dev files with hot reload
docker compose up
```

**Features:**

- Volume mounts for live code changes
- Auto-reload for API (`--reload` flag)
- Dev server for UI (`pnpm quasar dev`)
- Includes development dependencies

### Production

```bash
# Uses production Dockerfiles
docker compose -f docker-compose.prod.yml up -d
```

**Features:**

- Optimized multi-stage builds
- Static UI assets built at container build time
- API runs with 4 workers for production
- Health checks for UI container
- Only production dependencies included

## Production Dockerfile Details

### API Production Dockerfile

- Base: `python:3.12-slim`
- Non-root user: `appuser` (UID/GID 1000)
- Production dependencies only
- Runs uvicorn with 4 workers
- No auto-reload
- Port: 8000

### UI Production Dockerfile

- Builder stage: Node.js for building static assets
- Production stage: Node.js with `serve` package
- Builds Quasar/Vue application to `/dist/spa`
- Serves static files on port 9000
- Health check using wget
- Non-root user: `node`
- Port: 9000

## Building and Running

### Development

```bash
# Start development environment
docker compose up

# Build individual services
docker compose build ui
docker compose build api
```

### Production

```bash
# Build production images
docker compose -f docker-compose.prod.yml build

# Start production environment
docker compose -f docker-compose.prod.yml up -d

# Stop production environment
docker compose -f docker-compose.prod.yml down

# View logs
docker compose -f docker-compose.prod.yml logs -f
```

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
# Edit .env with your production values
```

## Health Checks

The UI container includes a health check:

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:9000 || exit 1
```

Check container health status:

```bash
docker ps --filter "name=scheduler" --format "table {{.Names}}\t{{.Status}}"
```

## CI/CD Integration

The GitHub Actions workflow has been updated to use production Dockerfiles:

- UI build job uses `./ui/Dockerfile`
- API build job uses `./api/Dockerfile`
- Images are built and pushed to GHCR

## Size Optimization

### API Image

- Uses slim Python base image
- Separates dev dependencies
- Multi-stage build to reduce final size

### UI Image

- Uses alpine Node.js base
- Builder stage separates build tools
- Production stage only includes built assets and serve package

## Troubleshooting

### Build Issues

1. **Node modules cache**: The UI Dockerfile uses Docker BuildKit cache mounts
2. **Python dependencies**: Ensure `requirements-base.txt` is up to date
3. **Asset permissions**: Non-root users ensure proper file ownership

### Runtime Issues

1. **Port conflicts**: Check ports 8000 and 9000 are available
2. **Database connectivity**: Verify PostgreSQL is accessible
3. **Health check failures**: Check UI container logs

### Logs

```bash
# All logs
docker compose -f docker-compose.prod.yml logs

# Specific service
docker compose -f docker-compose.prod.yml logs api
docker compose -f docker-compose.prod.yml logs ui

# Follow logs
docker compose -f docker-compose.prod.yml logs -f
```

## Security Considerations

1. **Non-root users**: Both containers run as non-root users
2. **Dependency scanning**: Regular updates of base images
3. **Environment secrets**: Use `.env` files (not committed to git)
4. **Network isolation**: Services use internal Docker network

## Performance

### API

- Uvicorn with 4 workers (adjust based on CPU cores)
- Connection pooling for database
- Redis cache for Celery results

### UI

- Static assets served with compression
- Browser caching enabled
- Health monitoring

## Monitoring

1. **Container health**: Docker health checks
2. **Application logs**: Container stdout/stderr
3. **Resource usage**: Docker stats
4. **API documentation**: Available at `http://localhost:8000/docs`
