"""Smoke test: the marimo notebook imports without executing its cells."""

from entrypoints.syntetos_classifier import notebook


def test_notebook_module_imports():
    assert notebook.app is not None
