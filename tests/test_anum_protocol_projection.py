# -*- coding: utf-8 -*-
"""Tests for issue #61 two-abit protocol projection."""

from core.anum_model import Abit
from core.anum_projector import project_two_abit_form


def test_projects_container_form_to_protocol_zero():
    projection = project_two_abit_form(Abit.OPEN, Abit.CLOSE)

    assert projection.source == "[]"
    assert projection.arrow_form == "α ⟼ β"
    assert projection.protocol_value == "0"
    assert "container" in projection.meaning


def test_projects_bridge_form_to_protocol_one():
    projection = project_two_abit_form(Abit.CLOSE, Abit.OPEN)

    assert projection.source == "]["
    assert projection.arrow_form == "β ⟼ α"
    assert projection.protocol_value == "1"
    assert "bridge" in projection.meaning


def test_open_open_and_close_close_are_existing_forms():
    open_open = project_two_abit_form(Abit.OPEN, Abit.OPEN)
    close_close = project_two_abit_form(Abit.CLOSE, Abit.CLOSE)

    assert open_open.source == "[["
    assert open_open.arrow_form == "α ⟼ α"
    assert open_open.protocol_value is None

    assert close_close.source == "]]"
    assert close_close.arrow_form == "β ⟼ β"
    assert close_close.protocol_value is None
