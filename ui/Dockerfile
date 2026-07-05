FROM node:24.6 AS base

ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"

RUN corepack enable

# ------------------------
# Dependencies
# ------------------------
FROM base AS deps

WORKDIR /app

COPY scheduler_ui/package.json scheduler_ui/pnpm-*.yaml ./

RUN --mount=type=cache,id=pnpm-store,target=/pnpm/store \
    pnpm install --frozen-lockfile

# ------------------------
# Dev stage
# ------------------------
FROM base AS dev

WORKDIR /app

USER 1000:1000

COPY --from=deps /app/node_modules ./node_modules
COPY scheduler_ui ./

EXPOSE 3000

CMD ["pnpm", "dev"]
