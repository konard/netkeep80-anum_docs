# -*- coding: utf-8 -*-
"""Tests that string and strict quaternary *.anum modes stay separate."""

import pytest

from core.anum_model import AnumForm, AnumSource
from core.anum_parser import parse_anum_file, parse_quaternary_anum


def test_quaternary_rejects_string_tokens():
    parse_quaternary_anum("[01000001]")

    for source in ("window(position)", "a b", "∞ ⟼ ∞"):
        with pytest.raises(ValueError, match="Недопустимый символ"):
            parse_quaternary_anum(source)


def test_string_mode_does_not_parse_as_quaternary():
    source = parse_anum_file("# anum-format: string\nwindow(position)\n")

    assert isinstance(source, AnumSource)
    assert source.format == "string"
    assert source.text == "window(position)"


def test_quaternary_mode_rejects_string_content():
    with pytest.raises(ValueError, match="Недопустимый символ"):
        parse_anum_file("# anum-format: quaternary\nwindow(position)\n")


def test_utf8_payload_example_is_quaternary_not_string():
    form = parse_anum_file(
        "# anum-format: quaternary\n"
        "[01101000][01100101][01101100][01101100][01101111]\n"
    )

    assert isinstance(form, AnumForm)


def test_string_mode_header_is_required_for_named_payloads():
    with pytest.raises(ValueError, match="Недопустимый символ"):
        parse_anum_file("a b")


def test_unknown_anum_format_is_rejected():
    with pytest.raises(ValueError, match="Неизвестный формат"):
        parse_anum_file("# anum-format: yaml\n[]")
