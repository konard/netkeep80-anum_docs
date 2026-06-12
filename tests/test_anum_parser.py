# -*- coding: utf-8 -*-
"""Tests for strict *.anum quaternary parsing."""

import pytest

from core.anum_model import Abit, AnumForm
from core.anum_parser import parse_anum_file, parse_quaternary_anum


def token_values(form: AnumForm) -> list[str]:
    return [token.abit.value for token in form.tokens]


@pytest.mark.parametrize("source", ["[]", "][", "[[", "]]", "[01000001]"])
def test_quaternary_parser_accepts_all_abit_forms(source):
    form = parse_quaternary_anum(source)

    assert token_values(form) == list(source)


def test_quaternary_parser_ignores_whitespace_and_comments():
    form = parse_quaternary_anum("  [ 0 1 ]  # byte shell\n][")

    assert token_values(form) == ["[", "0", "1", "]", "]", "["]
    assert [token.offset for token in form.tokens] == [2, 4, 6, 8, 24, 25]


@pytest.mark.parametrize("source", ["a", "b", "∞", "♂", "♀", "⟼", '"'])
def test_quaternary_parser_rejects_non_quaternary_characters(source):
    with pytest.raises(ValueError, match="Недопустимый символ"):
        parse_quaternary_anum(source)


def test_quaternary_parser_does_not_use_bracket_balance():
    assert token_values(parse_quaternary_anum("][")) == ["]", "["]


def test_anum_file_defaults_to_quaternary_mode_without_header():
    source = parse_anum_file("[01000001]")

    assert isinstance(source, AnumForm)
    assert token_values(source) == list("[01000001]")
    assert source.tokens[0].abit is Abit.OPEN


def test_anum_file_parses_explicit_quaternary_header():
    source = parse_anum_file("# anum-format: quaternary\n[]")

    assert isinstance(source, AnumForm)
    assert token_values(source) == ["[", "]"]
