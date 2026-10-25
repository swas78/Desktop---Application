# For: Standalone engine entry point for PyInstaller executable bundling
# Must never: Bind to non-localhost network interfaces or disable CORS

import os
import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

import uvicorn
from engine.app.main import app
from engine.app.core.config import settings

if __name__ == "__main__":
    port = int(os.environ.get("ADVS_ENGINE_PORT", settings.port))
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")
