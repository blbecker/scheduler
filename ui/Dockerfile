FROM node:24.6-alpine@sha256:d2b6b5aedb5b729f68ee1129e0f5a5d4713d93f82448249e82241876d8e8d86e AS builder

ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

USER node

WORKDIR /app

# Copy package files and source code
COPY --chown=node:node scheduler_ui/ ./

# Install dependencies with cache
RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm install --frozen-lockfile --config.confirmModulesPurge=false

# Build the application
RUN pnpm run build

FROM node:24.6-alpine@sha256:d2b6b5aedb5b729f68ee1129e0f5a5d4713d93f82448249e82241876d8e8d86e AS production

WORKDIR /app

# Copy built assets from builder
COPY --from=builder --chown=node:node /app/dist/spa ./dist

# Install serve (simple static server) as root, then switch to node
USER root
RUN npm install -g serve@14
USER node

# Expose port
EXPOSE 9000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:9000 || exit 1

# Run the static server
CMD ["serve", "-s", "dist", "-l", "9000"]