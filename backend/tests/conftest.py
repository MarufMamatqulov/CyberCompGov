import os
import tempfile
from pathlib import Path

_db = Path(tempfile.mkdtemp()) / "test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{_db.as_posix()}"
os.environ["SEED_ON_STARTUP"] = "true"
os.environ["DEMO_MODE"] = "true"
