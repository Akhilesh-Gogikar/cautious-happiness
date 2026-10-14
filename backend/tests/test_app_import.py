import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parents[1]
HEAVY_MODULES = ("torch", "transformers", "sentence_transformers")

# Runs in a fresh interpreter, as `uvicorn app.main:app` would import it, so module-level
# side effects in other tests cannot mask an import failure. A meta-path hook records
# attempts to import the ML stack, so the check also holds where it is not installed.
IMPORT_CHECK = """
import json, sys

attempted = []

class RecordHeavyImports:
    def find_spec(self, name, path=None, target=None):
        if name.split(".")[0] in {heavy!r}:
            attempted.append(name)
        return None

sys.meta_path.insert(0, RecordHeavyImports())
import app.main
from app.routers import demo
from app.domain.intelligence.sentiment import sentiment_analyzer
print(json.dumps({{
    "paths": sorted(app.main.app.openapi()["paths"].keys()),
    "heavy_import_attempts": sorted(set(attempted)),
    "orchestrator_built": demo._orchestrator is not None,
    "sentiment_load_attempted": sentiment_analyzer._load_attempted,
}}))
""".format(heavy=HEAVY_MODULES)


@pytest.fixture(scope="module")
def imported_app():
    env = {
        **os.environ,
        "PYTHONPATH": os.pathsep.join(filter(None, [str(BACKEND_DIR), os.environ.get("PYTHONPATH")])),
        # asyncpg ships in requirements.txt; no connection is opened at import.
        "DATABASE_URL": "postgresql+asyncpg://postgres:password@localhost:5432/polymarket",
        "HF_HUB_OFFLINE": "1",
        "TRANSFORMERS_OFFLINE": "1",
    }
    proc = subprocess.run(
        [sys.executable, "-W", "ignore", "-c", IMPORT_CHECK],
        cwd=BACKEND_DIR,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout.strip().splitlines()[-1])


def test_app_main_imports_and_registers_routes(imported_app):
    for path in ("/health", "/auth/token", "/intelligence/news", "/demo/analyze", "/prediction/predict"):
        assert path in imported_app["paths"]


def test_app_main_import_does_not_load_ml_models(imported_app):
    # FinBERT and bge-m3 load on first use; importing them at startup made boot
    # slow and network-dependent.
    assert imported_app["heavy_import_attempts"] == []
    assert imported_app["orchestrator_built"] is False
    assert imported_app["sentiment_load_attempted"] is False


def test_demo_orchestrator_is_built_once(monkeypatch):
    from app.routers import demo

    built = []

    def slow_orchestrator():
        time.sleep(0.05)
        built.append(object())
        return built[-1]

    monkeypatch.setattr(demo, "_orchestrator", None)
    monkeypatch.setattr(demo, "AgentOrchestrator", slow_orchestrator)
    results = []
    threads = [threading.Thread(target=lambda: results.append(demo.get_orchestrator())) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(built) == 1 and all(r is built[0] for r in results)
