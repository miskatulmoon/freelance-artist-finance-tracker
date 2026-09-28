import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_openapi_matches_exported_file(client):
    root = Path(__file__).resolve().parents[2]
    exported_path = root / "openapi.json"
    assert exported_path.exists(), "Root openapi.json must exist"

    live = client.get("/openapi.json")
    assert live.status_code == 200
    live_schema = live.json()
    exported_schema = json.loads(exported_path.read_text(encoding="utf-8"))

    # Compare structural equality ignoring server URLs/timestamps
    def normalize(s):
        # Remove fields that change per run
        d = dict(s)
        d.pop("servers", None)
        return d

    assert normalize(live_schema) == normalize(exported_schema), "Live OpenAPI schema differs from exported openapi.json"
