"""Tests always run offline: ai.py loads .env on import, so blank the keys first (setdefault won't overwrite them).
Gemini behaviour is tested with fakes in test_ai_cards.py."""
import os

os.environ["GEMINI_API_KEY"] = ""
os.environ["GOOGLE_CLOUD_PROJECT"] = ""

import inspect
from pathlib import Path

import pytest

DATA = Path(os.environ.get("RUNWAY_DATA", Path(__file__).resolve().parent.parent / "data"))
HAS_DATA = (DATA / "monthly_summary.csv").exists()


def pytest_collection_modifyitems(config, items):
    """CI has no bank data (data/ is never committed): skip tests that need it, with a clear reason. Locally nothing changes."""
    if HAS_DATA:
        return
    skip = pytest.mark.skip(reason="needs the Tangerine data (never committed); runs locally before every merge")
    for it in items:
        src = inspect.getsource(it.function) if getattr(it, "function", None) else ""
        if ("d" in it.fixturenames or it.module.__name__ in ("test_api", "test_app_smoke")
                or any(k in src for k in ("E.load", "_facts(", "api.", "client."))):
            it.add_marker(skip)
