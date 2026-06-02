# -*- coding: utf-8 -*-
"""Regression checks for the active MTS documentation and root fixture."""

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_DOCS = [
    ROOT / "README.md",
    ROOT / "docs/CONTRIBUTING.md",
    ROOT / "docs/plan.md",
    ROOT / "docs/theory/Основания МТС.md",
    ROOT / "docs/theory/Метатеория связей.md",
    ROOT / "docs/theory/Система аксиом МТС.md",
    ROOT / "docs/theory/Шаблон аксиом МТС.md",
    ROOT / "docs/specs/Слои нотации МТС.md",
    ROOT / "docs/specs/Шаблонный поиск МТС.md",
    ROOT / "docs/specs/Ачисла и сериализация.md",
    ROOT / "docs/specs/Формальная нотация МТС.md",
    ROOT / "docs/specs/Пучковая нотация МТС.md",
    ROOT / "docs/research/Открытые вопросы новой аксиоматики МТС.md",
    ROOT / "tests/mtc_formulas.mtc",
]

THEORY_SURFACE_FILES = {
    "Ключевые идеи МТС.md",
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
    "Пучковая нотация МТС.md",
}

ACTIVE_RESEARCH_FILES = {
    "Открытые вопросы новой аксиоматики МТС.md",
}

ACTIVE_DOCS = [
    "README.md",
    "docs/plan.md",
    "docs/theory/Метатеория связей.md",
    "docs/theory/Основания МТС.md",
    "docs/theory/Система аксиом МТС.md",
    "docs/theory/Шаблон аксиом МТС.md",
    "docs/specs/Ачисла и сериализация.md",
    "docs/specs/Слои нотации МТС.md",
    "docs/specs/Формальная нотация МТС.md",
    "docs/specs/Пучковая нотация МТС.md",
    "docs/specs/Шаблонный поиск МТС.md",
    "docs/research/Открытые вопросы новой аксиоматики МТС.md",
]

RETIREMENT_MARKER_DOCS = [
    *ACTIVE_DOCS,
    "docs/CONTRIBUTING.md",
]

REQUIRED_FORMULAS = [
    "∞ : [] = [] ⟼ []",
    "[] = ∞",
    "∞ = ∞ ⟼ ∞",
    "([]) = []",
    "([][]) = [][]",
    "([] ⟼ []) = [] ⟼ []",
    "[][] : [] ⟼ []",
    "[][] = [] ⟼ []",
    "[][][] : ([][]) ⟼ []",
    "[][][] = ([] ⟼ []) ⟼ []",
    "[][][] = [] ⟼ [] ⟼ []",
    "[]([][]) : [] ⟼ ([][])",
    "[][][] != []([][])",
    "[][][] != [] ⟼ ([] ⟼ [])",
    "♂[] : ♂[] = ♂[] ⟼ []",
    "♂∞ = ♂∞ ⟼ ∞",
    "[]♀ : []♀ = [] ⟼ []♀",
    "∞♀ = ∞ ⟼ ∞♀",
    "{} != []",
    "{[]} != []",
    "{[], []} = {[]}",
    "{[], [][]} = {[][], []}",
    "[]{[], [][]} = {[] ⟼ [], [] ⟼ [][]}",
    "{[], [][]}[] = {[] ⟼ [], [][] ⟼ []}",
    "{[], [][]}{[], [][]} = {[] ⟼ [], [] ⟼ [][], [][] ⟼ [], [][] ⟼ [][]}",
]

FORBIDDEN_ACTIVE_MARKERS = [
    "□",
    "⟦",
    "⟧",
    "{s}",
    "{[}",
    "{]}",
    "{⟼}",
    "∞ : {} = {} ⟼ {}",
    "::=",
    "definition ::=",
    "form ::=",
    "reference ::=",
    "candidate ::=",
    "EBNF",
]

FORBIDDEN_FIXTURE_PREFIXES = (
    "AXIOM ",
    "EXEC ",
    "RULE ",
    "NEGATIVE ",
    "STATUS ",
)

REQUIRED_SYMBOL_ROWS = [
    "`∞`",
    "`[]`",
    "`{}`",
    "`()`",
    "`:`",
    "`=`",
    "`!=`",
    "`⟼`",
    "`♂`",
    "`♀`",
    "`[`",
    "`]`",
    "`1`, `0`",
    "`,`",
]

AXIOM_HEADINGS = [
    "## R1. Акорень через пустую форму одной связи",
    "## R2. Круглая группировка формы",
    "## R3. Последовательность двух форм",
    "## R4. Последовательность трёх форм",
    "## R5. Самозамкнутое начало",
    "## R6. Самозамкнутый конец",
    "## R7. Фигурная пучковая нотация",
    "## R8. Пучковое раскрытие",
]

BUNDLE_FORMULAS = [
    "{} != []",
    "{[]} != []",
    "{[], []} = {[]}",
    "{[], [][]} = {[][], []}",
    "[]{[], [][]} = {[] ⟼ [], [] ⟼ [][]}",
    "{[], [][]}[] = {[] ⟼ [], [][] ⟼ []}",
    "{[], [][]}{[], [][]} = {[] ⟼ [], [] ⟼ [][], [][] ⟼ [], [][] ⟼ [][]}",
]


def read_doc(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def formula_lines() -> list[str]:
    return [
        line.strip()
        for line in read_doc("tests/mtc_formulas.mtc").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def markdown_links(text: str) -> list[str]:
    return re.findall(r"\[[^\]]+\]\(([^)#]+)(?:#[^)]+)?\)", text)


def assert_balanced(line: str, opening: str, closing: str) -> None:
    depth = 0
    for char in line:
        if char == opening:
            depth += 1
        elif char == closing:
            depth -= 1
        assert depth >= 0, line
    assert depth == 0, line


def test_current_foundation_documents_exist():
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED_DOCS if not path.exists()]

    assert missing == []


def test_documentation_surface_is_small_and_explicit():
    assert {path.name for path in (ROOT / "docs/theory").glob("*.md")} == THEORY_SURFACE_FILES
    assert {path.name for path in (ROOT / "docs/specs").glob("*.md")} == ACTIVE_SPEC_FILES
    assert {path.name for path in (ROOT / "docs/research").glob("*.md")} == ACTIVE_RESEARCH_FILES


def test_mtc_formula_fixture_uses_root_bracket_system():
    lines = formula_lines()

    assert lines == REQUIRED_FORMULAS

    for line in lines:
        assert not line.startswith(FORBIDDEN_FIXTURE_PREFIXES), line
        assert_balanced(line, "{", "}")
        assert_balanced(line, "(", ")")
        assert_balanced(line, "[", "]")
        assert "!" not in line.replace("!=", ""), line


def test_mtc_formula_fixture_rejects_retired_external_mechanisms():
    fixture = read_doc("tests/mtc_formulas.mtc")

    for marker in FORBIDDEN_ACTIVE_MARKERS:
        assert marker not in fixture, marker


def test_active_docs_reject_retired_external_mechanisms():
    for relative_path in RETIREMENT_MARKER_DOCS:
        text = read_doc(relative_path)
        markers = [marker for marker in FORBIDDEN_ACTIVE_MARKERS if marker in text]

        assert markers == [], relative_path


def test_readme_is_current_entrypoint():
    readme = read_doc("README.md")

    for required in [
        "Что сейчас является МТС",
        "Формальная нотация МТС — система смысловых различий",
        "Первичные скобочные нотации",
        "Где система аксиом",
        "Где тест формул",
        "tests/mtc_formulas.mtc",
        "Корневая система формул является корневой библиотекой апрувера",
    ]:
        assert required in readme


def test_readme_links_point_to_existing_local_files():
    readme = read_doc("README.md")

    for target in markdown_links(readme):
        if target.startswith(("http://", "https://")):
            continue
        path = ROOT / target.replace("%20", " ")
        assert path.exists(), target


def test_formal_notation_spec_defines_new_root_frame():
    spec = read_doc("docs/specs/Формальная нотация МТС.md")

    for required in [
        "формальная нотация МТС = система смысловых различий",
        "строковое ачисло",
        "последовательность различий",
        "интерпретация формулы",
        "скобки = границы контейнера",
        "контейнер = область чтения данной нотации",
        ": не является процедурным присваиванием",
        "корневая библиотека апрувера",
    ]:
        assert required in spec

    for row in REQUIRED_SYMBOL_ROWS:
        assert row in spec, row


def test_axiom_template_requires_formula_based_axioms():
    template = read_doc("docs/theory/Шаблон аксиом МТС.md")

    for required in [
        "Статус: актуальное, нормативное.",
        "каждая аксиома имеет формулу формальной нотации МТС",
        "Если смысл не выражен формулой",
        "Система формул аксиом решается одновременно",
        "Корневая система формул является корневой библиотекой апрувера",
        "tests/mtc_formulas.mtc",
    ]:
        assert required in template


def test_axiom_system_matches_root_fixture():
    system = read_doc("docs/theory/Система аксиом МТС.md")

    for heading in AXIOM_HEADINGS:
        assert heading in system, heading

    for formula in REQUIRED_FORMULAS:
        assert formula in system, formula

    assert "Система аксиом как корневая библиотека апрувера" in system


def test_bundle_notation_spec_keeps_bundle_rules_without_deletion_root():
    spec = read_doc("docs/specs/Пучковая нотация МТС.md")

    for required in [
        "пучковая нотация",
        "пучок / асеть связей",
        "пучок не тождественен элементу",
        "порядок элементов не важен",
        "повтор элемента не создаёт новый элемент пучка",
        "операционное удаление не входит в корневое ядро",
    ]:
        assert required in spec

    for formula in BUNDLE_FORMULAS:
        assert formula in spec, formula

    for marker in ["delete", "-/>", "OP(", "NF("]:
        assert marker not in spec, marker


def test_open_questions_hold_deferred_topics():
    questions = read_doc("docs/research/Открытые вопросы новой аксиоматики МТС.md")

    for required in [
        "повторные пустые формы внутри шаблона",
        "позиции в последовательности",
        "пустое `()`",
        "переменные как производный механизм",
        "подстановку через неразличимость",
        "смысл отдельных границ `[` и `]`",
        "операционное удаление в пучковой нотации",
        "будущий апрувер должен решать систему формул одновременно",
    ]:
        assert required in questions


def test_active_docs_do_not_reference_archives_or_legacy_fixtures():
    for relative_path in ACTIVE_DOCS:
        text = read_doc(relative_path)

        assert "archive/" not in text, relative_path
        assert "tests/issue42_mtc_formulas.mtc" not in text, relative_path
        assert "tests/legacy_mtc_formulas.mtc" not in text, relative_path
