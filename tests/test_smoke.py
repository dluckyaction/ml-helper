"""Smoke tests verifying the three layers are importable."""

import ml_helper.core
import ml_helper.entrypoints
import ml_helper.infrastructure


def test_layers_are_importable():
    assert ml_helper.core.__name__ == "ml_helper.core"
    assert ml_helper.infrastructure.__name__ == "ml_helper.infrastructure"
    assert ml_helper.entrypoints.__name__ == "ml_helper.entrypoints"
