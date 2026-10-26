FROM python:3.13-slim-trixie@sha256:6771159cd4fa5d9bba1258caf0b82e6b73458c694d178ad97c5e925c2d0e1a91

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

COPY --from=ghcr.io/astral-sh/uv:0.12.0@sha256:606e70c71c852d03f611b1e56a195d08648507018a7057fab82c4974c4eae105 /uv /uvx /usr/local/bin/

ARG DEBIAN_FRONTEND=noninteractive
# hadolint ignore=DL3008
RUN apt-get update && apt-get install -y --no-install-recommends \
        wget perl fontconfig git \
    && rm -rf /var/lib/apt/lists/*

# network steps for TeX Live are retried because the mirrors are sometimes flaky
COPY --chmod=755 docker/retry.sh /usr/local/bin/retry

# Pinned TeX Live release: mirror.ctan.org redirects to a random mirror (which is what makes retries useful) and always
# serves the latest release. Once TeX Live moves on to a newer release, the build fails on purpose. To keep building
# the old release, point the repository to the frozen archive:
# https://ftp.math.utah.edu/pub/tex/historic/systems/texlive/<year>/tlnet-final
# install-tl and tlmgr run in the same layer so that the release check also covers the packages installed with tlmgr.
# install-tl stores the mirror it picked as tlmgr's repository, so the repository is reset to let tlmgr retries switch
# mirrors as well.
ARG TEXLIVE_YEAR=2026
ARG TEXLIVE_REPOSITORY=https://mirror.ctan.org/systems/texlive/tlnet

ENV PATH="/usr/local/texlive/bin/current:${PATH}"
RUN retry wget -nv -O /tmp/install-tl.tar.gz "${TEXLIVE_REPOSITORY}/install-tl-unx.tar.gz" \
 && mkdir /tmp/install-tl && tar -xzf /tmp/install-tl.tar.gz -C /tmp/install-tl --strip-components=1 \
 && { head -n1 /tmp/install-tl/release-texlive.txt | grep -qE "version ${TEXLIVE_YEAR}\$" \
      || { echo "Expected TeX Live ${TEXLIVE_YEAR} but ${TEXLIVE_REPOSITORY} serves: $(head -n1 /tmp/install-tl/release-texlive.txt)" >&2; exit 1; }; } \
 && printf '%s\n' \
        'selected_scheme scheme-infraonly' \
        'TEXDIR /usr/local/texlive' \
        'TEXMFLOCAL /usr/local/texlive/texmf-local' \
        'TEXMFSYSCONFIG /usr/local/texlive/texmf-config' \
        'TEXMFSYSVAR /usr/local/texlive/texmf-var' \
        'tlpdbopt_install_docfiles 0' \
        'tlpdbopt_install_srcfiles 0' \
        'tlpdbopt_autobackup 0' \
        > /tmp/texlive.profile \
 && retry /tmp/install-tl/install-tl --profile=/tmp/texlive.profile --repository "${TEXLIVE_REPOSITORY}" \
 && ln -sfn "$(dirname "$(find /usr/local/texlive/bin -name tlmgr | head -n1)")" \
            /usr/local/texlive/bin/current \
 && rm -rf /tmp/install-tl /tmp/install-tl.tar.gz \
 && tlmgr option repository "${TEXLIVE_REPOSITORY}" \
 && retry tlmgr install \
        latex latex-bin latexconfig l3kernel l3packages \
        graphics graphics-cfg graphics-def graphics-pln \
        clearsans fontaxes mweights \
        lm \
        pgf \
        xcolor textpos ragged2e etoolbox ifmtarg parskip \
        marvosym fontawesome geometry hyperref url \
        xkeyval tools \
        iftex infwarerr kvoptions kvsetkeys kvdefinekeys \
        ltxcmds pdftexcmds hycolor letltxmacro bitset \
        atbegshi atveryend refcount gettitlestring \
        pdfescape stringenc etexcmds auxhook uniquecounter \
        bigintcalc epstopdf-pkg psnfss \
 && tlmgr path add && fmtutil-sys --byengine pdftex \
 && rm -rf /usr/local/texlive/texmf-dist/doc \
           /usr/local/texlive/texmf-dist/source

WORKDIR /opt/app
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-install-project --no-dev
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-dev --no-editable
ENV PATH="/opt/app/.venv/bin:${PATH}"

ENTRYPOINT ["./docker_entry.py"]