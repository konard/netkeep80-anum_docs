# -*- coding: utf-8 -*-
"""Regression checks for issue #61: abits as arrow forms."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_SPEC = ROOT / "docs/specs/Протокол абитов ачисел.md"
ANUM_SPEC = ROOT / "docs/specs/Ачисла и сериализация.md"
ROOT_FIXTURE = ROOT / "tests/mtc_formulas.mtc"


def read_doc(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_issue61_protocol_spec_exists_and_records_arrow_hypothesis():
    assert PROTOCOL_SPEC.exists()

    spec = read_doc(PROTOCOL_SPEC)
    for required in [
        "абиты нельзя мыслить как символы строки",
        "минимальные стрелочные формы вокруг акорня",
        "α := ∞♀",
        "β := ♂∞",
        "[ := α",
        "] := β",
        "0 := [] := α ⟼ β",
        "1 := ][ := β ⟼ α",
        "[[ := α ⟼ α",
        "[] := α ⟼ β",
        "][ := β ⟼ α",
        "]] := β ⟼ β",
        "project_protocol([]) = 0",
        "project_protocol(][) = 1",
    ]:
        assert required in spec, required


def test_issue61_protocol_does_not_reject_two_abit_forms_as_invalid_strings():
    spec = read_doc(PROTOCOL_SPEC)

    for required in [
        "Все четыре двухабитные формы существуют",
        "`][` не является ошибкой ведущей закрывающей скобки",
        "`[[` и `]]` не являются ошибками",
        "`[]` и `][` читаются не как строки, а как связи",
    ]:
        assert required in spec, required


def test_issue61_protocol_separates_load_decode_project_realize_and_find():
    spec = read_doc(PROTOCOL_SPEC)

    for required in [
        "load(A)",
        "decode(A)",
        "project_K(A)",
        "realize(A)",
        "find(A)",
        "raw(∞ab) = ((∞ ⟼ a) ⟼ b)",
        "den(∞ab) = a ⟼ b",
        "raw(∞ab) не содержит a ⟼ b",
        "load(∞ab) не создаёт a ⟼ b",
        "realize(∞ab) создаёт или получает a ⟼ b",
        "find(∞ab) проверяет наличие a ⟼ b, но не создаёт её",
        "D([∞ab]) = ∞ab",
        "D([[∞ab]]) = [∞ab]",
    ]:
        assert required in spec, required


def test_issue61_is_linked_from_anum_serialization_without_replacing_root_fixture():
    anum_spec = read_doc(ANUM_SPEC)
    root_fixture = read_doc(ROOT_FIXTURE)

    assert "Протокол абитов ачисел" in anum_spec
    assert "Протокол абитов ачисел.md" in anum_spec

    for forbidden in [
        "[ : ∞♀",
        "] : ♂∞",
        "0 : ∞♀ ⟼ ♂∞",
        "1 : ♂∞ ⟼ ∞♀",
    ]:
        assert forbidden not in root_fixture, forbidden
