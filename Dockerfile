FROM python:3.13-slim-trixie@sha256:6771159cd4fa5d9bba1258caf0b82e6b73458c694d178ad97c5e925c2d0e1a91

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

COPY --from=ghcr.io/astral-sh/uv:0.12.0@sha256:606e70c71c852d03f611b1e56a195d08648507018a7057fab82c4974c4eae105 /uv /uvx /usr/local/bin/

ARG DEBIAN_FRONTEND=noninteractive
# hadolint ignore=DL3008
RUN apt-get update && apt-get install -y --no-install-recommends \
        wget perl fontconfig git \
    && rm -rf /var/lib/apt/lists/*

# TeX Live is installed by docker/install-texlive.sh, see there for details.
# TEXLIVE_YEAR pins the release: mirror.ctan.org always serves the latest release, so the build fails on purpose once
# TeX Live moves on to a newer release. To keep building the old release, point TEXLIVE_REPOSITORY to the frozen
# archive: https://ftp.math.utah.edu/pub/tex/historic/systems/texlive/<year>/tlnet-final
ARG TEXLIVE_YEAR=2026
ARG TEXLIVE_REPOSITORY=https://mirror.ctan.org/systems/texlive/tlnet

ENV PATH="/usr/local/texlive/bin/current:${PATH}"
RUN --mount=type=bind,source=docker/install-texlive.sh,target=/tmp/install-texlive.sh \
    bash /tmp/install-texlive.sh

WORKDIR /opt/app
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-install-project --no-dev
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-dev --no-editable
ENV PATH="/opt/app/.venv/bin:${PATH}"

ENTRYPOINT ["./docker_entry.py"]