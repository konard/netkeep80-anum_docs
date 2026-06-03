# -*- coding: utf-8 -*-
"""Mark legacy parser/prover compatibility tests explicitly."""

from pathlib import Path

import pytest


LEGACY_DIR = Path(__file__).resolve().parent


def pytest_collection_modifyitems(config, items):
    for item in items:
        item_path = Path(str(item.path)).resolve()
        if LEGACY_DIR in item_path.parents:
            item.add_marker(pytest.mark.legacy)
