#!/bin/bash
# Installs a minimal TeX Live with the packages needed for the PDF report into /usr/local/texlive.
#
# Configured through the environment (ARGs in the Dockerfile):
#   TEXLIVE_YEAR        expected TeX Live release, the installation fails if the repository serves a different one
#   TEXLIVE_REPOSITORY  TeX Live package repository (tlnet)
#
# TeX Live mirrors are occasionally unreachable or serve broken certificates. mirror.ctan.org redirects to a different
# mirror on each request, so network steps are retried and a retry usually reaches a working mirror.

set -euo pipefail

: "${TEXLIVE_YEAR:?TEXLIVE_YEAR must be set}"
: "${TEXLIVE_REPOSITORY:?TEXLIVE_REPOSITORY must be set}"

TEXDIR=/usr/local/texlive
INSTALLER_DIR=/tmp/install-tl
MAX_ATTEMPTS=5

PACKAGES=(
    latex latex-bin latexconfig l3kernel l3packages
    graphics graphics-cfg graphics-def graphics-pln
    clearsans fontaxes mweights
    lm
    pgf
    xcolor textpos ragged2e etoolbox ifmtarg parskip
    marvosym fontawesome geometry hyperref url
    xkeyval tools
    iftex infwarerr kvoptions kvsetkeys kvdefinekeys
    ltxcmds pdftexcmds hycolor letltxmacro bitset
    atbegshi atveryend refcount gettitlestring
    pdfescape stringenc etexcmds auxhook uniquecounter
    bigintcalc epstopdf-pkg psnfss
)

# Runs the given command and retries it with increasing delays if it fails.
# Returns the exit code of the last attempt.
retry() {
    local attempt exit_code
    for attempt in $(seq 1 "$MAX_ATTEMPTS"); do
        "$@" && return 0
        exit_code=$?
        echo "attempt ${attempt}/${MAX_ATTEMPTS} failed with exit code ${exit_code}: $*" >&2
        if [ "$attempt" -lt "$MAX_ATTEMPTS" ]; then
            sleep $((attempt * 10))
        fi
    done
    return "$exit_code"
}

download_installer() {
    retry wget -nv -O "${INSTALLER_DIR}.tar.gz" "${TEXLIVE_REPOSITORY}/install-tl-unx.tar.gz"
    mkdir -p "$INSTALLER_DIR"
    tar -xzf "${INSTALLER_DIR}.tar.gz" -C "$INSTALLER_DIR" --strip-components=1
}

check_release() {
    local release
    release=$(head -n1 "${INSTALLER_DIR}/release-texlive.txt")
    if [[ "$release" != *"version ${TEXLIVE_YEAR}" ]]; then
        echo "Expected TeX Live ${TEXLIVE_YEAR} but ${TEXLIVE_REPOSITORY} serves: ${release}" >&2
        echo "To keep building TeX Live ${TEXLIVE_YEAR}, set TEXLIVE_REPOSITORY to its frozen archive:" >&2
        echo "https://ftp.math.utah.edu/pub/tex/historic/systems/texlive/${TEXLIVE_YEAR}/tlnet-final" >&2
        exit 1
    fi
}

write_profile() {
    cat > "${INSTALLER_DIR}/texlive.profile" <<EOF
selected_scheme scheme-infraonly
TEXDIR ${TEXDIR}
TEXMFLOCAL ${TEXDIR}/texmf-local
TEXMFSYSCONFIG ${TEXDIR}/texmf-config
TEXMFSYSVAR ${TEXDIR}/texmf-var
tlpdbopt_install_docfiles 0
tlpdbopt_install_srcfiles 0
tlpdbopt_autobackup 0
EOF
}

install_base() {
    # start from an empty TEXDIR so that a retry does not build on a partial install left by a failed attempt
    rm -rf "$TEXDIR" && "${INSTALLER_DIR}/install-tl" --profile="${INSTALLER_DIR}/texlive.profile" \
        --repository "$TEXLIVE_REPOSITORY"
}

link_binaries() {
    # the binary directory is named after the platform (e.g. x86_64-linux), "current" gives it a fixed path for PATH
    local tlmgr
    tlmgr=$(find "${TEXDIR}/bin" -name tlmgr -print -quit)
    ln -sfn "$(dirname "$tlmgr")" "${TEXDIR}/bin/current"
    export PATH="${TEXDIR}/bin/current:${PATH}"
}

install_packages() {
    # install-tl stores the mirror it picked as tlmgr's repository, reset it so that tlmgr retries can switch mirrors
    tlmgr option repository "$TEXLIVE_REPOSITORY"
    retry tlmgr install "${PACKAGES[@]}"
    tlmgr path add
    fmtutil-sys --byengine pdftex
}

clean_up() {
    rm -rf "$INSTALLER_DIR" "${INSTALLER_DIR}.tar.gz" "${TEXDIR}/texmf-dist/doc" "${TEXDIR}/texmf-dist/source"
}

download_installer
check_release
write_profile
retry install_base
link_binaries
install_packages
clean_up
