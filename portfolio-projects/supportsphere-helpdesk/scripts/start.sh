#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
"$ROOT/backend/.venv/bin/python" -m uvicorn main:app --app-dir "$ROOT/backend" --host 127.0.0.1 --port 8000 &
API_PID=$!
trap 'kill "$API_PID" 2>/dev/null || true' EXIT
cd "$ROOT/frontend"
npm run dev -- --host 0.0.0.0
