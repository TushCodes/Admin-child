#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="${VENV_DIR:-.venv}"
POSTGRES_STARTED=0

if [[ ! -f .env.local ]]; then
  cp .env.example .env.local
  echo "Created .env.local from .env.example"
fi

if command -v docker >/dev/null 2>&1; then
  if docker compose version >/dev/null 2>&1; then
    docker compose up -d postgres
    POSTGRES_STARTED=1
  elif command -v docker-compose >/dev/null 2>&1; then
    docker-compose up -d postgres
    POSTGRES_STARTED=1
  else
    echo "Docker is installed, but Docker Compose is unavailable. Start PostgreSQL manually."
  fi
else
  echo "Docker is unavailable. Start PostgreSQL manually with the DATABASE_URL in .env.local."
fi

if [[ ! -x "$VENV_DIR/bin/python" ]] || ! "$VENV_DIR/bin/python" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' >/dev/null 2>&1; then
  rm -rf "$VENV_DIR"
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/python" -m pip install -r requirements.txt

set -a
# shellcheck disable=SC1091
source .env.local
set +a

if [[ "$POSTGRES_STARTED" == "1" ]]; then
  echo "Waiting for PostgreSQL to accept connections..."
  for _ in {1..30}; do
    if "$VENV_DIR/bin/python" - <<'PY' >/dev/null 2>&1
import os
import psycopg2
conn = psycopg2.connect(os.environ["DATABASE_URL"])
conn.close()
PY
    then
      break
    fi
    sleep 2
  done
fi

if ! "$VENV_DIR/bin/python" - <<'PY' >/dev/null 2>&1
import os
import psycopg2
conn = psycopg2.connect(os.environ["DATABASE_URL"])
conn.close()
PY
then
  echo "PostgreSQL is not reachable at DATABASE_URL=$DATABASE_URL"
  echo "Start Docker/Docker Compose or point DATABASE_URL in .env.local to a running local PostgreSQL database, then re-run this script."
  exit 1
fi

"$VENV_DIR/bin/python" - <<'PY'
from run_local import app
from app.admin.models import Consignment
with app.app_context():
    print(f"Local database is ready with {Consignment.query.count()} seeded consignments.")
PY

echo "Run locally with: source .venv/bin/activate && python run_local.py"
