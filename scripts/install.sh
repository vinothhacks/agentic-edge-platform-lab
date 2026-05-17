#!/usr/bin/env bash
# Agentic Edge Platform Lab - one-line installer (macOS / Linux)
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/vinothhacks/agentic-edge-platform-lab/main/scripts/install.sh | bash
#
# Optional env vars:
#   AEPL_DIR    target directory (default: ./agentic-edge-platform-lab)
#   AEPL_BRANCH branch to clone (default: main)
#   AEPL_SKIP_UP skip `docker compose up` if set

set -euo pipefail

REPO="https://github.com/vinothhacks/agentic-edge-platform-lab.git"
DIR="${AEPL_DIR:-agentic-edge-platform-lab}"
BRANCH="${AEPL_BRANCH:-main}"

CYAN='\033[0;36m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'

say()  { printf "${CYAN}==>${NC} %s\n" "$*"; }
ok()   { printf "${GREEN}\u2713${NC} %s\n" "$*"; }
warn() { printf "${YELLOW}!${NC} %s\n" "$*"; }
die()  { printf "${RED}\u2717${NC} %s\n" "$*" >&2; exit 1; }

need() { command -v "$1" >/dev/null 2>&1 || die "Missing required tool: $1"; }

say "Checking prerequisites"
need git
need docker
if ! docker compose version >/dev/null 2>&1; then
  die "docker compose v2 plugin is required (try: docker compose version)"
fi
ok "git + docker compose present"

if [ -d "$DIR/.git" ]; then
  say "Repo already exists at $DIR - pulling latest"
  git -C "$DIR" fetch --depth=1 origin "$BRANCH"
  git -C "$DIR" reset --hard "origin/$BRANCH"
else
  say "Cloning $REPO into $DIR"
  git clone --depth=1 --branch "$BRANCH" "$REPO" "$DIR"
fi
ok "Source ready"

cd "$DIR"

if [ -n "${AEPL_SKIP_UP:-}" ]; then
  warn "AEPL_SKIP_UP set - not booting the stack"
else
  say "Building and starting the stack (this is a one-time cost)"
  docker compose up -d --build
  ok "Stack is up"

  printf "\n${GREEN}Done.${NC}\n"
  echo
  echo "  Broker API:    http://localhost:8000/docs"
  echo "  Edge (Envoy):  http://localhost:10000"
  echo
  echo "Try the agent:"
  echo "  curl -s -X POST http://localhost:8000/api/agent/chat \\"
  echo "    -H 'Content-Type: application/json' \\"
  echo "    -d '{\"message\":\"Expose orders on orders.localhost with 100 req/min\"}' | jq"
fi
