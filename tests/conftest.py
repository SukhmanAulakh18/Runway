"""Tests always run offline: ai.py loads .env on import, so blank the keys first (setdefault won't overwrite them).
Gemini behaviour is tested with fakes in test_ai_cards.py."""
import os

os.environ["GEMINI_API_KEY"] = ""
os.environ["GOOGLE_CLOUD_PROJECT"] = ""
