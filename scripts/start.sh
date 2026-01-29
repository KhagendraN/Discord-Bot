#!/usr/bin/env bash
set -euo pipefail

# Run from project root (/app) and ensure Python path includes both project root and src
cd "$(dirname "$0")/.."
export PYTHONPATH="/app:/app/src"
cd /app/src
exec python main.py
