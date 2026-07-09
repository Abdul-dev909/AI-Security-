"""Pytest bootstrap for local imports and shared test setup.

Add shared fixtures here later when the MemoryManager implementation becomes
available. Keep this file generic and free from implementation-specific
assumptions.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def clean_test_context():
    """Provide a simple, isolated context for tests.

    Extend this fixture later if shared setup is needed.
    """
    return {"project_root": str(PROJECT_ROOT)}