"""Export the OpenAPI schema so the frontend can generate its API types.

Run from the backend directory:
    python export_openapi.py
"""

import json
from pathlib import Path

from app.main import app

ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = ROOT / "openapi.json"

schema = app.openapi()
OUT_PATH.write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")
print(f"OpenAPI schema written to {OUT_PATH}")
