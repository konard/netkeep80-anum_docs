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
    ROOT / "docs/research/Ключевые идеи МТС.md",
    ROOT / "docs/research/Открытые вопросы новой аксиоматики МТС.md",
    ROOT / "tests/mtc_formulas.mtc",
]

THEORY_SURFACE_FILES = {
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
    "Ключевые идеи МТС.md",
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
    "∞♀ : [⟼]♀",
    "♂∞ : ♂[⟼]",
    "(⟼) : [] ⟼ []",
    "[⟼] : ∞♀ ⟼ ♂∞",
    "¬[] : ♂[] ⟼ []♀",
    "¬[⟼] : ♂[⟼] ⟼ [⟼]♀",
    "¬[⟼] = ♂∞ ⟼ ∞♀",
    "(=) : {[]♀ = []♀, ♂[] = ♂[]}",
    "(!=) : ¬(=)",
    "[] != [] : ¬([] = [])",
    "↛ : ¬[⟼]",
    "[ : ∞♀",
    "] : ♂∞",
    "1 : [⟼]",
    "0 : [↛]",
    "{} != []",
    "{[]} != []",
    "{[], []} = {[]}",
    "{[], [][]} = {[][], []}",
    "[]{[], [][]} = {[] ⟼ [], [] ⟼ [][]}",
    "{[], [][]}[] = {[] ⟼ [], [][] ⟼ []}",
    "{[], [][]}{[], [][]} = {[] ⟼ [], [] ⟼ [][], [][] ⟼ [], [][] ⟼ [][]}",
    "[]{} = {}",
    "{}[] = {}",
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
    "`(⟼)`",
    "`[⟼]`",
    "`¬`",
    "`↛`",
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
    "## R9. Начало и конец акорня",
    "## R10. Смысл связи и конкретная связь",
    "## R11. Инверсия формы связи",
    "## R12. Смысл равенства",
    "## R13. Неравенство как инверсия смысла равенства",
    "## R14. Несвязь",
    "## R15. Абиты квадратной нотации",
]

BUNDLE_FORMULAS = [
    "{} != []",
    "{[]} != []",
    "{[], []} = {[]}",
    "{[], [][]} = {[][], []}",
    "[]{[], [][]} = {[] ⟼ [], [] ⟼ [][]}",
    "{[], [][]}[] = {[] ⟼ [], [][] ⟼ []}",
    "{[], [][]}{[], [][]} = {[] ⟼ [], [] ⟼ [][], [][] ⟼ [], [][] ⟼ [][]}",
    "[]{} = {}",
    "{}[] = {}",
]

AXIOM_CARD_DOCS = [
    "docs/theory/Система аксиом МТС.md",
    "docs/theory/Шаблон аксиом МТС.md",
]

AXIOM_CARD_POSITIVE_SECTIONS = [
    "Формула:",
    "Вводимые различия:",
    "Чтение:",
    "Слои различения:",
    "Связанные формулы:",
    "Слой развития:",
]

RETIRED_CARD_SECTIONS = [
    "Что запрещает",
    "**Какие различия вводит**",
    "**Как читается**",
    "**Что запрещает**",
    "**Следствия**",
    "**Открытые вопросы**",
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


def is_single_abit_definition(line: str) -> bool:
    return line.startswith("[ : ") or line.startswith("] : ")


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
        if not is_single_abit_definition(line):
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


def test_readme_softens_unresolved_formula_layer():
    readme = read_doc("README.md")

    for required in [
        "Практически стабильно:",
        "Рабочий слой текущего fixture:",
        "`(=)`, `(!=)`, `¬[]`, `¬[⟼]`, `↛` и `0`",
        "продолжают развиваться в слое развития",
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
        ": вводит различие через формулу",
        "корневая библиотека апрувера",
        "## Связь и смысл связи",
        "## Инверсия",
        "## Равенство и результат сравнения",
        "## Неравенство как инверсия смысла равенства",
        "## Абиты квадратной нотации",
        "(⟼) : [] ⟼ []",
        "[⟼] : ∞♀ ⟼ ♂∞",
        "(!=) : ¬(=)",
        "¬[=] — инверсия конкретной связи знака равенства",
        "(!=) — смысл неравенства",
        "Абитами являются `[`, `]`, `1`, `0`",
    ]:
        assert required in spec

    for row in REQUIRED_SYMBOL_ROWS:
        assert row in spec, row


def test_axiom_template_requires_formula_based_axioms():
    template = read_doc("docs/theory/Шаблон аксиом МТС.md")

    for required in [
        "Статус: актуальное, нормативное.",
        "каждая аксиома имеет формулу формальной нотации МТС",
        "Смысл входит в корневую библиотеку как аксиома через свою формулу",
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


def test_axiom_cards_use_positive_template():
    for relative_path in AXIOM_CARD_DOCS:
        text = read_doc(relative_path)

        for section in AXIOM_CARD_POSITIVE_SECTIONS:
            assert section in text, (relative_path, section)

        for retired in RETIRED_CARD_SECTIONS:
            assert retired not in text, (relative_path, retired)


def test_bundle_notation_spec_keeps_bundle_rules_without_deletion_root():
    spec = read_doc("docs/specs/Пучковая нотация МТС.md")

    for required in [
        "пучковая нотация",
        "пучок / асеть связей",
        "пучок и его элемент принадлежат разным слоям различения",
        "порядок элементов не важен",
        "пучок удерживает каждую форму один раз",
        "## Пустое пучковое раскрытие",
        "[]{} = {}",
        "{}[] = {}",
        "пустой исходящий / входящий пучок в описательном смысле",
        "Операционное изменение асети ведётся в слое развития",
    ]:
        assert required in spec

    for formula in BUNDLE_FORMULAS:
        assert formula in spec, formula

    for marker in ["delete", "-/>", "OP(", "NF("]:
        assert marker not in spec, marker


def test_anum_serialization_defines_square_abits():
    spec = read_doc("docs/specs/Ачисла и сериализация.md")

    for required in [
        "абиты квадратной нотации",
        "[ и ] являются абитами",
        "[] является минимальной ачисловой записью акорня",
        "∞ — знак полного самозамыкания",
        "1 вводится как абит конкретной связи",
        "0 вводится как абит несвязи",
        "[ : ∞♀",
        "] : ♂∞",
        "1 : [⟼]",
        "0 : [↛]",
    ]:
        assert required in spec


def test_template_search_distinguishes_repetition_positions_and_comparison():
    spec = read_doc("docs/specs/Шаблонный поиск МТС.md")

    for required in [
        "внутри формулы после `:` повторные `[]` могут читаться как один образец",
        "в последовательности `[][]` эти же `[]` читаются как позиции",
        "в формулах равенства повторные `[]` могут читаться как позиционные сравниваемые формы",
    ]:
        assert required in spec


def test_open_questions_hold_deferred_topics():
    questions = read_doc("docs/research/Открытые вопросы новой аксиоматики МТС.md")

    for required in [
        "полную формализацию позиционного чтения повторных `[]`",
        "полную модель результата сравнения",
        "тип результата `[] = []`",
        "строгую семантику `↛`",
        "связь `0` с сериализацией отсутствия",
        "пустое `()`",
        "будущую теорию переменных и подстановки",
        "операционное удаление в пучковой нотации",
        "Операционное чтение `[]{}` и `{}[]`",
        "будущий апрувер должен решать систему формул одновременно",
    ]:
        assert required in questions


def test_active_docs_do_not_reference_archives_or_legacy_fixtures():
    for relative_path in ACTIVE_DOCS:
        text = read_doc(relative_path)

        assert "archive/" not in text, relative_path
        assert "tests/issue42_mtc_formulas.mtc" not in text, relative_path
        assert "tests/legacy_mtc_formulas.mtc" not in text, relative_path
