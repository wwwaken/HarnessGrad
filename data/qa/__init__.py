"""Temporary Stage A re-export package; removed in Stage C.

Python modules alias their canonical data.scaffolds.qa implementations. The CLI
and prediction files use links because existing callers copy standalone files;
copying an import shim would change that contract.
"""
