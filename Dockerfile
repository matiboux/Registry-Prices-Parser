#syntax=docker/dockerfile:1

# This Dockerfile uses the service folder as context.


# --
# Global build arguments

ARG DOCKER_HUB_MIRROR='docker.io/'
ARG GHCR_MIRROR='ghcr.io/'
ARG UID=1001


# --
# Upstream images

# (see uv releases: https://github.com/astral-sh/uv/releases)

FROM ${DOCKER_HUB_MIRROR}alpine:3.22 AS alpine_upstream
FROM ${GHCR_MIRROR}astral-sh/uv:0.11 AS python_uv_upstream
FROM ${DOCKER_HUB_MIRROR}python:3.12-slim AS python_upstream


# --
# Alpine base stage

FROM alpine_upstream AS alpine_base

# Set app directory
WORKDIR /app


# --
# Python base stage

FROM python_upstream AS python_base

# Set app directory
WORKDIR /app
ENV PYTHONPATH=/app

# Set home directory for cache
ENV HOME=/tmp

# Set venv configuration
ENV UV_PROJECT_ENVIRONMENT=/app/.venv
ENV VIRTUAL_ENV="$UV_PROJECT_ENVIRONMENT"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"


# --
# Python build base stage

FROM python_base AS python_build_base

# Install uv (package manager)
COPY --from=python_uv_upstream --link --chmod=755 /uv /uvx /usr/local/bin/

# Install build dependencies
# (hadolint: Ignore non-pinned apt package version)
# hadolint ignore=DL3008
RUN --mount=type=cache,sharing=locked,id=apt-cache,target=/var/cache/apt \
	--mount=type=cache,sharing=locked,id=apt-lib,target=/var/lib/apt \
	apt-get update && \
	apt-get install -y --no-install-recommends build-essential

# Install curl
# (hadolint: Ignore non-pinned apt package version)
# hadolint ignore=DL3008
RUN --mount=type=cache,sharing=locked,id=apt-cache,target=/var/cache/apt \
	--mount=type=cache,sharing=locked,id=apt-lib,target=/var/lib/apt \
	apt-get update && \
	apt-get install -y --no-install-recommends curl


# --
# Python app base stage

FROM python_base AS python_app_base

# Install pg_dump
RUN --mount=type=cache,sharing=locked,id=apt-cache,target=/var/cache/apt \
	--mount=type=cache,sharing=locked,id=apt-lib,target=/var/lib/apt \
	apt-get update && \
	apt-get install -y --no-install-recommends postgresql-client-17


# --
# Deps base stage

FROM python_build_base AS deps_base

# Copy build configuration
COPY --link ./pyproject.toml ./uv.lock ./


# --
# Deps dev stage

FROM deps_base AS deps_dev

# Install dev Python dependencies
# (hadolint: Ignore pip cache usage, because cache is stored in a mount point)
# hadolint ignore=DL3042
RUN --mount=type=cache,id=uv,target=/tmp/uv-cache \
	export UV_CACHE_DIR=/tmp/uv-cache && \
	export UV_LINK_MODE=copy && \
	uv sync --frozen


# --
# Deps prod stage

FROM deps_base AS deps_prod

# Install prod Python dependencies
# (hadolint: Ignore pip cache usage, because cache is stored in a mount point)
# hadolint ignore=DL3042
RUN --mount=type=cache,id=uv,target=/tmp/uv-cache \
	export UV_CACHE_DIR=/tmp/uv-cache && \
	export UV_LINK_MODE=copy && \
	uv sync --frozen --no-dev


# --
# CLI base stage

FROM python_build_base AS app_cli_base

# Create command aliases (pip)
COPY --link --chmod=755 ./docker/pip-cli-alias.sh /usr/local/bin/aliases/pip
ENV PATH="/usr/local/bin/aliases:$PATH"


# --
# CLI image

FROM app_cli_base AS app_cli

# Build arguments
ARG UID

# Set uv configuration
ENV UV_LINK_MODE=copy

# Install sudo
# (hadolint: Ignore non-pinned apt package version)
# hadolint ignore=DL3008
RUN --mount=type=cache,sharing=locked,id=apt-cache,target=/var/cache/apt \
	--mount=type=cache,sharing=locked,id=apt-lib,target=/var/lib/apt \
	apt-get update && \
	apt-get install -y --no-install-recommends sudo && \
	echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# Create user 'user' in group 'root' & 'sudo'
# (hadolint: Ignore unchecked pipe failures)
# hadolint ignore=DL4006
RUN USERNAME="$(getent passwd "${UID}" 2>/dev/null | cut -d: -f1 || true)"; \
	if [ -z "${USERNAME}" ]; then \
		useradd -lm -u "${UID}" -U -G 0,sudo user; \
	else \
		usermod -a -G 0,sudo "${USERNAME}"; \
	fi

# Run as created non-root user
USER ${UID}

# Mount source code
VOLUME /app

# Run CLI command
COPY --link --chmod=755 ./docker/cli-entrypoint.sh /usr/local/bin/app-cli-entrypoint
ENTRYPOINT [ "app-cli-entrypoint" ]
CMD []
