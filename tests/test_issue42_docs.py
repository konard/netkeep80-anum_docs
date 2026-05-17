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
    ROOT / "docs/research/Открытые вопросы новой аксиоматики МТС.md",
]

ACTIVE_FOUNDATION_DOCS = [
    "docs/theory/Метатеория связей.md",
    "docs/theory/Основания МТС.md",
    "docs/specs/Формальная нотация МТС.md",
    "docs/specs/Шаблонный поиск МТС.md",
]

BRACE_NEGATIONS = [
    "{} ≠ пустое множество",
    "{} ≠ пустой результат поиска",
    "{} ≠ несвязь",
    "{} ≠ 0",
]

REPEATED_BRACE_RULE = (
    "Внутри одного исполнения шаблона все одинаковые вхождения `{}` "
    "относятся к одной и той же связи-кандидату."
)

STALE_ACTIVE_THEORY_MARKERS = [
    "Сводная таблица аксиом А0-А16",
    "Аксиома единицы смысла: 1 : [⟼]",
    "Начало связи: [⟼]♀",
    "Конец связи: ♂[⟼]",
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


def test_historical_bracket_analysis_is_not_active_theory():
    active_path = ROOT / "docs/theory/Анализ природы скобок в МТС.md"
    archive_path = ROOT / "archive/Анализ природы скобок в МТС.md"

    assert not active_path.exists()
    assert archive_path.exists()
    assert "Статус: исторический" in archive_path.read_text(encoding="utf-8")


def test_active_foundation_docs_keep_brace_search_boundaries():
    for relative_path in ACTIVE_FOUNDATION_DOCS:
        text = read_doc(relative_path)
        missing = [line for line in BRACE_NEGATIONS if line not in text]

        assert missing == [], relative_path


def test_active_foundation_docs_bind_repeated_empty_braces():
    for relative_path in ACTIVE_FOUNDATION_DOCS:
        assert REPEATED_BRACE_RULE in read_doc(relative_path), relative_path


def test_formal_notation_separates_candidate_and_reference():
    spec = read_doc("docs/specs/Формальная нотация МТС.md")

    assert "{} не является частным случаем `{s}`" in spec
    assert "{s} не является поиском без фильтра" in spec


def test_active_theory_has_no_stale_core_markers():
    theory_paths = (ROOT / "docs/theory").glob("*.md")

    for path in theory_paths:
        text = path.read_text(encoding="utf-8")
        stale_markers = [marker for marker in STALE_ACTIVE_THEORY_MARKERS if marker in text]

        assert stale_markers == [], str(path.relative_to(ROOT))


def test_active_specs_do_not_promote_bracketed_arrow_as_core():
    active_docs = ACTIVE_FOUNDATION_DOCS + [
        "docs/theory/Новая система аксиом МТС.md",
        "docs/specs/Ачисла и сериализация.md",
    ]

    for relative_path in active_docs:
        text = read_doc(relative_path)

        assert "Запись `[⟼]` может" not in text, relative_path
        assert "[⟼]` как базов" not in text, relative_path
