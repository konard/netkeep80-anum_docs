# -*- coding: utf-8 -*-
"""Tests for the practical *.anum core: parsing, projection and memory."""

import pytest

from core.anum_memory import AnumMemory, Link, Quote, SymbolicAnum, deserialize
from core.anum_model import Abit, AnumForm, AnumSource
from core.anum_parser import parse_anum_file, parse_quaternary_anum
from core.anum_projector import project_two_abit_form


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


def test_symbolic_deserialize_and_quote_levels():
    form = SymbolicAnum("a", "b")

    assert deserialize(form) == Link("a", "b")
    assert deserialize(Quote(form)) == form
    assert deserialize(Quote(Quote(form))) == Quote(form)


def test_load_and_find_do_not_materialize_denoted_link():
    memory = AnumMemory()
    form = SymbolicAnum("a", "b")
    link = Link("a", "b")

    memory.load(form)
    assert link not in memory.links

    assert memory.find(form) is False
    assert link not in memory.links

    memory.realize(form)
    assert link in memory.links
    assert memory.find(form) is True


def test_realizing_quote_does_not_materialize_inner_denotation():
    memory = AnumMemory()
    form = SymbolicAnum("a", "b")

    realized = memory.realize(Quote(form))

    assert realized == form
    assert Link("a", "b") not in memory.links
    assert form in memory.raw_forms
