#!/usr/bin/env bash
# For: Single-command startup launcher running the Python engine and desktop shell together
# Must never: Leave background engine processes orphaned after shell exit

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "=== Automated Document Verification System (ADVS) ==="
echo "Starting local offline verification engine and desktop desk..."

# 1. Ensure Python virtualenv exists
if [ ! -f "engine/.venv/bin/python" ]; then
    echo "Initializing Python environment..."
    uv venv engine/.venv --python 3.14
    uv pip install --python engine/.venv/bin/python fastapi uvicorn pydantic python-multipart bcrypt pyjwt cryptography pillow rapidfuzz reportlab openpyxl pypdf pytest
fi

# 2. Ensure sample test documents exist
if [ ! -f "sample_data/sample_clean_marksheet.pdf" ]; then
    echo "Generating verification test samples..."
    PYTHONPATH=. engine/.venv/bin/python tools/synthetic_data.py
fi

# 3. Start Python Engine in background
export PYTHONPATH=.
engine/.venv/bin/python -m uvicorn engine.app.main:app --host 127.0.0.1 --port 8000 &
ENGINE_PID=$!

# Trap signals to cleanly kill engine on exit
cleanup() {
    echo ""
    echo "Shutting down ADVS engine (PID: $ENGINE_PID)..."
    kill "$ENGINE_PID" 2>/dev/null || true
    wait "$ENGINE_PID" 2>/dev/null || true
    echo "ADVS stopped cleanly."
}
trap cleanup EXIT INT TERM

# 4. Wait for engine to respond to health check
echo "Waiting for engine health check on 127.0.0.1:8000..."
for i in {1..15}; do
    if curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
        echo "Engine healthy and operational."
        break
    fi
    sleep 0.5
done

# 5. Launch desktop UI
cd apps/desktop
npm run dev
