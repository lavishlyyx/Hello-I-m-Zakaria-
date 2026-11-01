#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python -m venv "$ROOT/backend/.venv"
"$ROOT/backend/.venv/bin/python" -m pip install -r "$ROOT/backend/requirements.txt"
cd "$ROOT/frontend"
npm install
echo "Dependencies installed. Run: bash portfolio-projects/supportsphere-helpdesk/scripts/start.sh"
