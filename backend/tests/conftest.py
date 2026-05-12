import os
import sys
import tempfile
from pathlib import Path

# Make sure tests use an isolated SQLite DB regardless of any .env on disk.
_TMP_DIR = Path(tempfile.mkdtemp(prefix="tours-test-"))
os.environ["DATABASE_URL"] = f"sqlite:///{_TMP_DIR / 'test.db'}"

# Point seeder at the real contracts file relative to the repo.
_BACKEND_ROOT = Path(__file__).resolve().parents[1]
_SEED_FILE = _BACKEND_ROOT.parent / "contracts" / "tours_seed.json"
os.environ["SEED_PATH"] = str(_SEED_FILE)

# Ensure the backend package is importable when running pytest from any cwd.
sys.path.insert(0, str(_BACKEND_ROOT))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c
