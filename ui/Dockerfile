FROM node:24.6@sha256:d2b6b5aedb5b729f68ee1129e0f5a5d4713d93f82448249e82241876d8e8d86e AS base 
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

FROM base AS build 

USER 1000:1000

WORKDIR /app

# FIXME: Quasar wants to run from the project, but this means the code is in a docker layer.
# COPY --chown=node ./scheduler_ui/package.json ./scheduler_ui/pnpm-lock.yaml ./
COPY --chown=node ./scheduler_ui ./

RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm install --frozen-lockfile --config.confirmModulesPurge=false

CMD ["pnpm", "quasar", "dev"]
