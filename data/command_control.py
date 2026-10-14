"""Temporary Stage A compatibility shim for data.scaffolds.command_control; removed in Stage C."""
import importlib
import sys
from pathlib import Path

if __name__ == "__main__":
    import runpy
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    runpy.run_module("data.scaffolds.command_control", run_name="__main__")
else:
    sys.modules[__name__] = importlib.import_module("data.scaffolds.command_control")
