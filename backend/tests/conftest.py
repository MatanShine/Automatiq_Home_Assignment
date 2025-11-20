import sys
from pathlib import Path
import os
import pytest

# Ensure the backend package is importable when running tests
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# Provide a dummy OpenAI key for modules that require it at import time
os.environ.setdefault("OPENAI_API_KEY", "test-key")


def pytest_configure(config):
    config.addinivalue_line("markers", "asyncio: mark test as async")


@pytest.fixture
def anyio_backend():
    return "asyncio"
