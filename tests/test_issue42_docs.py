# -*- coding: utf-8 -*-
"""Regression checks for the issue #42 MTS foundation rewrite."""

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_DOCS = [
    ROOT / "docs/theory/Основания МТС.md",
    ROOT / "docs/theory/Метатеория связей.md",
    ROOT / "docs/theory/Система аксиом МТС.md",
    ROOT / "docs/theory/Шаблон аксиом МТС.md",
    ROOT / "docs/specs/Слои нотации МТС.md",
    ROOT / "docs/specs/Шаблонный поиск МТС.md",
    ROOT / "docs/specs/Ачисла и сериализация.md",
    ROOT / "docs/specs/Формальная нотация МТС.md",
    ROOT / "docs/research/Открытые вопросы новой аксиоматики МТС.md",
    ROOT / "tests/issue42_mtc_formulas.mtc",
    ROOT / "tests/legacy_mtc_formulas.mtc",
]

ACTIVE_THEORY_FILES = {
    "Метатеория связей.md",
    "Основания МТС.md",
    "Система аксиом МТС.md",
    "Шаблон аксиом МТС.md",
}

ACTIVE_SPEC_FILES = {
    "Ачисла и сериализация.md",
    "Слои нотации МТС.md",
    "Формальная нотация МТС.md",
    "Шаблонный поиск МТС.md",
}

ACTIVE_RESEARCH_FILES = {
    "Открытые вопросы новой аксиоматики МТС.md",
}

ACTIVE_FOUNDATION_DOCS = [
    "docs/theory/Метатеория связей.md",
    "docs/theory/Основания МТС.md",
    "docs/specs/Формальная нотация МТС.md",
    "docs/specs/Шаблонный поиск МТС.md",
]

ACTIVE_DOCS = [
    "README.md",
    "docs/theory/Метатеория связей.md",
    "docs/theory/Основания МТС.md",
    "docs/theory/Система аксиом МТС.md",
    "docs/theory/Шаблон аксиом МТС.md",
    "docs/specs/Ачисла и сериализация.md",
    "docs/specs/Слои нотации МТС.md",
    "docs/specs/Формальная нотация МТС.md",
    "docs/specs/Шаблонный поиск МТС.md",
    "docs/research/Открытые вопросы новой аксиоматики МТС.md",
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

REQUIRED_SYMBOLS = [
    "∞",
    "{}",
    "{s}",
    "{",
    "}",
    ":",
    "=",
    "⟼",
    "♂",
    "♀",
    "¬",
    "↛",
    "[",
    "]",
    "1",
    "0",
    "(",
    ")",
    ",",
]

ISSUE42_FIXTURE_LINES = {
    "AXIOM root: ∞ : {} = {} ⟼ {}",
    "EXEC root: ∞ : ∞ ⟼ ∞",
    "AXIOM self-start: ♂{} : ♂{} = ♂{} ⟼ {}",
    "EXEC self-start: ♂X : ♂X ⟼ X",
    "AXIOM self-end: {}♀ : {}♀ = {} ⟼ {}♀",
    "EXEC self-end: X♀ : X ⟼ X♀",
    "AXIOM abit-start: {[} : ∞♀",
    "AXIOM abit-end: {]} : ♂∞",
    "AXIOM arrow-meaning: {⟼} : {[} ⟼ {]}",
    "RULE repeated-empty-braces: one-candidate-per-template-execution",
    "RULE template-execution: candidate -> form-constraint -> found-meaning -> introduced-sign",
    "RULE candidate-reference-distinction: {} is not {s}",
    "NEGATIVE empty-braces: {} не пустое множество",
    "NEGATIVE empty-braces: {} не пустой результат поиска",
    "NEGATIVE empty-braces: {} не несвязь",
    "NEGATIVE empty-braces: {} не 0",
    "NEGATIVE brackets: [] не формульная группировка",
    "NEGATIVE brackets: старая скобочная запись связи не базовое ядро",
    "STATUS parser: parsers/mtc_formula_prover.py is legacy and does not execute this fixture",
}


def read_doc(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def markdown_links(text: str) -> list[str]:
    return re.findall(r"\[[^\]]+\]\(([^)#]+)(?:#[^)]+)?\)", text)


def test_issue42_foundation_documents_exist():
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED_DOCS if not path.exists()]

    assert missing == []


def test_active_document_surface_is_small_and_explicit():
    assert {path.name for path in (ROOT / "docs/theory").glob("*.md")} == ACTIVE_THEORY_FILES
    assert {path.name for path in (ROOT / "docs/specs").glob("*.md")} == ACTIVE_SPEC_FILES
    assert {path.name for path in (ROOT / "docs/research").glob("*.md")} == ACTIVE_RESEARCH_FILES


def test_issue42_renamed_old_formula_fixture_to_legacy():
    assert not (ROOT / "tests/mtc_formulas.mtc").exists()
    assert (ROOT / "tests/legacy_mtc_formulas.mtc").exists()

    legacy = read_doc("tests/legacy_mtc_formulas.mtc")
    assert "a^20 == aaaaaaaaaaaaaaaaaaaa" in legacy


def test_issue42_formula_fixture_matches_new_working_core():
    lines = {
        line.strip()
        for line in read_doc("tests/issue42_mtc_formulas.mtc").splitlines()
        if line.strip() and not line.startswith("#")
    }

    missing = sorted(ISSUE42_FIXTURE_LINES - lines)
    assert missing == []


def test_active_theory_uses_template_root_axiom():
    theory = read_doc("docs/theory/Метатеория связей.md")

    assert "∞ : {} = {} ⟼ {}" in theory
    assert "МТС основана на 17 аксиомах" not in theory


def test_readme_marks_issue42_rewrite_as_current_status():
    readme = read_doc("README.md")

    assert "issue #42" in readme
    assert "tests/issue42_mtc_formulas.mtc" in readme
    assert "tests/legacy_mtc_formulas.mtc" in readme
    assert "МТС основана на 17 аксиомах" not in readme
    assert "MTC is based on 17 axioms" not in readme


def test_readme_links_point_to_existing_local_files():
    readme = read_doc("README.md")

    for target in markdown_links(readme):
        if target.startswith(("http://", "https://")):
            continue
        path = ROOT / target.replace("%20", " ")
        assert path.exists(), target


def test_formal_notation_treats_braces_as_template_search():
    spec = read_doc("docs/specs/Формальная нотация МТС.md")

    assert "{} — шаблонный поиск без фильтра" in spec
    assert "Множества связей" not in spec


def test_formal_notation_has_complete_symbol_registry():
    spec = read_doc("docs/specs/Формальная нотация МТС.md")

    for symbol in REQUIRED_SYMBOLS:
        assert f"| `{symbol}` |" in spec, symbol

    assert "Нужна ли аксиома" in spec
    assert "служебная запись" in spec
    assert "открыт вопрос" in spec


def test_axiom_template_is_normative():
    template = read_doc("docs/theory/Шаблон аксиом МТС.md")

    assert "Статус: актуальное, нормативное." in template
    assert "Каждая аксиома вводит ровно один смысловой механизм." in template
    assert "Арность / валентность" in template
    assert "Критерий готовности аксиомы" in template
    assert "tests/issue42_mtc_formulas.mtc" in template


def test_axiom_system_has_dependency_table_and_all_core_cards():
    system = read_doc("docs/theory/Система аксиом МТС.md")

    assert "символ → слой → аксиома → зависит от → следствия → тесты" in system
    for heading in [
        "## А1. Акорень",
        "## А2. Самозамкнутое начало",
        "## А3. Самозамкнутый конец",
        "## А4. Смысл абита начала",
        "## А5. Смысл абита конца",
        "## А6. Смысл конструктора связи",
    ]:
        assert heading in system

    assert "Что не входит в рабочее ядро" in system
    assert "tests/issue42_mtc_formulas.mtc" in system


def test_historical_bracket_analysis_is_not_active_theory():
    active_path = ROOT / "docs/theory/Анализ природы скобок в МТС.md"
    archive_path = ROOT / "archive/Анализ природы скобок в МТС.md"

    assert not active_path.exists()
    assert archive_path.exists()
    assert "Статус: исторический" in archive_path.read_text(encoding="utf-8")


def test_legacy_notes_are_not_active_theory_or_research():
    moved_files = [
        "Анализ формулы связи ♂∞♀.md",
        "Переосмысление операторов начала и конца связи.md",
        "Ответ на вопрос о связи и ролях в МТС.md",
        "Вопросы и ответы.md",
        "Отличия между знаками равенства.md",
        "Проработка аксиом самозамыканий начала и конца.md",
    ]

    for name in moved_files:
        assert not (ROOT / "docs/theory" / name).exists()
        assert not (ROOT / "docs/research" / name).exists()
        archived = ROOT / "archive" / name
        assert archived.exists()
        assert "Статус: исторический" in archived.read_text(encoding="utf-8")


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


def test_active_docs_do_not_promote_old_bracketed_arrow_core():
    for relative_path in ACTIVE_DOCS:
        text = read_doc(relative_path)
        assert "[⟼]" not in text, relative_path


def test_active_theory_has_no_stale_core_markers():
    for path in (ROOT / "docs/theory").glob("*.md"):
        text = path.read_text(encoding="utf-8")
        stale_markers = [marker for marker in STALE_ACTIVE_THEORY_MARKERS if marker in text]

        assert stale_markers == [], str(path.relative_to(ROOT))
