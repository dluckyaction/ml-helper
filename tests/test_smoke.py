"""Smoke tests verifying the three layers are importable."""

import core
import entrypoints
import infrastructure


def test_layers_are_importable():
    assert core.__name__ == "core"
    assert infrastructure.__name__ == "infrastructure"
    assert entrypoints.__name__ == "entrypoints"