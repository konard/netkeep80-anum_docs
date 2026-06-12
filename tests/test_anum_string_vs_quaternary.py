# -*- coding: utf-8 -*-
"""Tests that string and strict quaternary *.anum modes stay separate."""

import pytest

from core.anum_model import AnumSource
from core.anum_parser import parse_anum_file, parse_quaternary_anum


def test_strict_quaternary_accepts_only_quaternary_payload():
    parse_quaternary_anum("[01000001]")

    with pytest.raises(ValueError, match="Недопустимый символ"):
        parse_quaternary_anum("window(position)")


def test_explicit_string_mode_keeps_text_payload_as_string_source():
    source = parse_anum_file("# anum-format: string\nwindow(position)")

    assert source == AnumSource(text="window(position)", format="string")


def test_explicit_quaternary_mode_rejects_string_payload():
    with pytest.raises(ValueError, match="Недопустимый символ"):
        parse_anum_file("# anum-format: quaternary\nwindow(position)")


def test_string_mode_header_is_required_for_named_payloads():
    with pytest.raises(ValueError, match="Недопустимый символ"):
        parse_anum_file("a b")


def test_unknown_anum_format_is_rejected():
    with pytest.raises(ValueError, match="Неизвестный формат"):
        parse_anum_file("# anum-format: yaml\n[]")
