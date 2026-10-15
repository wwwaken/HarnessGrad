"""Invoke pytest beneath the existing socket-denying fixture wrapper."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
import pytest
raise SystemExit(pytest.main(sys.argv[1:]))
