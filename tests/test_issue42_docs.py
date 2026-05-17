# -*- coding: utf-8 -*-
"""Regression checks for the issue #42 MTS foundation rewrite."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_DOCS = [
    ROOT / "docs/theory/Основания МТС.md",
    ROOT / "docs/theory/Новая система аксиом МТС.md",
    ROOT / "docs/specs/Слои нотации МТС.md",
    ROOT / "docs/specs/Шаблонный поиск МТС.md",
    ROOT / "docs/specs/Ачисла и сериализация.md",
]


def read_doc(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_issue42_foundation_documents_exist():
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED_DOCS if not path.exists()]

    assert missing == []


def test_active_theory_uses_template_root_axiom():
    theory = read_doc("docs/theory/Метатеория связей.md")

    assert "∞ : {} = {} ⟼ {}" in theory
    assert "МТС основана на 17 аксиомах" not in theory


def test_readme_marks_issue42_rewrite_as_current_status():
    readme = read_doc("README.md")

    assert "issue #42" in readme
    assert "МТС основана на 17 аксиомах" not in readme
    assert "MTC is based on 17 axioms" not in readme


def test_formal_notation_treats_braces_as_template_search():
    spec = read_doc("docs/specs/Формальная нотация МТС.md")

    assert "{} — шаблонный поиск без фильтра" in spec
    assert "Множества связей" not in spec
