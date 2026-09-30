"""Tests for the marimo notebook.

The import smoke test alone cannot catch a call to a marimo API that does not
exist, because the cell bodies never run. These tests execute the cells against
a stubbed form value so that every branch is actually exercised.
"""

import marimo as mo
import pytest
from core.syntetos import classify_series
from entrypoints.syntetos_classifier import notebook
from infrastructure.syntetos_metrics import PolarsSyntetosMetrics
from infrastructure.time_series_reader import TimeSeriesReadError, load_time_series

CELLS = list(notebook.app._cell_manager.cells())


def _cell(*defs):
    wanted = set(defs)
    for cell in CELLS:
        if wanted <= cell.defs:
            return cell
    raise AssertionError(f"no cell defines {defs}")


def _pipeline(form_value):
    class Form:
        value = form_value

    return _cell("error").run(
        mo=mo,
        form=Form(),
        load_time_series=load_time_series,
        classify_series=classify_series,
        PolarsSyntetosMetrics=PolarsSyntetosMetrics,
        TimeSeriesReadError=TimeSeriesReadError,
    )[1]


def _outputs(form_value):
    """Run the pipeline cell, then the chart cell when the pipeline produced a result.

    ``mo.stop(True)`` halts the pipeline cell on error and the marimo runtime
    skips its dependents, so the chart cell only runs when a result exists.
    """
    namespace = _pipeline(form_value)
    if namespace["result"] is None:
        return namespace, None
    chart = _cell("not_classifiable")
    return namespace, chart.run(mo=mo, alt=_altair(), result=namespace["result"])[1]


def _altair():
    import altair

    return altair


def _base(source="", upload=()):
    return {
        "date_column": "date",
        "value_column": "value",
        "source": source,
        "upload": upload,
    }


def test_notebook_module_imports():
    assert notebook.app is not None


def test_every_marimo_api_used_exists():
    """Catches calls to marimo APIs removed or renamed in an upgrade."""
    import ast
    from pathlib import Path

    import marimo

    path = Path(notebook.__file__)
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    for node in ast.walk(tree):
        if not isinstance(node, ast.Attribute):
            continue
        if isinstance(node.value, ast.Name) and node.value.id == "mo":
            assert hasattr(marimo, node.attr), f"mo.{node.attr} does not exist"
        if (
            isinstance(node.value, ast.Attribute)
            and isinstance(node.value.value, ast.Name)
            and node.value.value.id == "mo"
            and node.value.attr == "ui"
        ):
            assert hasattr(marimo.ui, node.attr), f"mo.ui.{node.attr} does not exist"


def test_valid_path_is_classified(tmp_path):
    path = tmp_path / "series.csv"
    path.write_text("date,value\n2026-01-01,10\n2026-01-02,0\n2026-01-03,12\n", encoding="utf-8")
    namespace, outputs = _outputs(_base(source=str(path)))
    assert namespace["result"][1] is not None
    assert outputs is not None


def test_invalid_path_reports_an_error(tmp_path):
    namespace, _ = _outputs(_base(source=str(tmp_path / "missing.csv")))
    assert namespace["result"] is None
    assert "No such file" in namespace["error"]


def test_missing_source_reports_an_error():
    namespace, _ = _outputs(_base())
    assert namespace["result"] is None
    assert namespace["error"]


def test_source_and_upload_together_report_an_error():
    class Upload:
        contents = b"date,value\n2026-01-01,10\n"
        name = "series.csv"

    namespace, _ = _outputs(_base(source="series.csv", upload=(Upload(),)))
    assert namespace["result"] is None
    assert "not both" in namespace["error"]


def test_upload_is_classified():
    class Upload:
        contents = b"date,value\n2026-01-01,10\n2026-01-02,0\n2026-01-03,12\n"
        name = "series.csv"

    namespace, outputs = _outputs(_base(upload=(Upload(),)))
    assert namespace["result"] is not None
    assert outputs is not None
