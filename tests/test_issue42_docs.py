# -*- coding: utf-8 -*-
"""Regression checks for the current MTS documentation and formula fixture."""

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
    ROOT / "tests/mtc_formulas.mtc",
]

REMOVED_ACTIVE_FILES = [
    ROOT / "docs/theory/Анализ природы скобок в МТС.md",
    ROOT / "docs/theory/Анализ формулы связи ♂∞♀.md",
    ROOT / "docs/theory/Ответ на вопрос о связи и ролях в МТС.md",
    ROOT / "docs/theory/Переосмысление операторов начала и конца связи.md",
    ROOT / "docs/research/Вопросы и ответы.md",
    ROOT / "docs/research/Отличия между знаками равенства.md",
    ROOT / "docs/research/Проработка аксиом самозамыканий начала и конца.md",
]

REMOVED_TEST_FIXTURES = [
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
    "docs/plan.md",
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

REQUIRED_FORMULAS = [
    "∞ : {} = {} ⟼ {}",
    "∞ = ∞ ⟼ ∞",
    "({}) = {}",
    "{}{} : ({}) ⟼ {}",
    "{}({}) : {} ⟼ ({})",
    "{}{} : {} ⟼ {}",
    "{}{} = {} ⟼ {}",
    "{}{}{} : ({}{}) ⟼ {}",
    "{}{}{} = (({}) ⟼ {}) ⟼ {}",
    "{}{}{} = {} ⟼ {} ⟼ {}",
    "{}({}{}) : {} ⟼ ({}{})",
    "{}{}{} != {}({}{})",
    "{}{}{} != {} ⟼ ({} ⟼ {})",
    "♂{} : ♂{} = ♂{} ⟼ {}",
    "♂∞ = ♂∞ ⟼ ∞",
    "{}♀ : {}♀ = {} ⟼ {}♀",
    "∞♀ = ∞ ⟼ ∞♀",
    "∞♀ : [⟼]♀",
    "♂∞ : ♂[⟼]",
    "(⟼) : [] ⟼ []",
    "[⟼] : ∞♀ ⟼ ♂∞",
    "¬[] : ♂[] ⟼ []♀",
    "¬[⟼] : ♂[⟼] ⟼ [⟼]♀",
    "¬[⟼] : ♂∞ ⟼ ∞♀",
    "(=) : {[]♀ = []♀, ♂[] = ♂[]}",
    "(!=) : ¬(=)",
    "[] != [] : ¬([] = [])",
    "↛ : ¬[⟼]",
    "[ : ∞♀",
    "] : ♂∞",
    "1 : [⟼]",
    "0 : [↛]",
]

FORBIDDEN_FIXTURE_PREFIXES = (
    "AXIOM ",
    "EXEC ",
    "RULE ",
    "NEGATIVE ",
    "STATUS ",
)

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

POSITIONAL_SEQUENCE_RULE = (
    "В последовательностной записи `{}{}...` каждое вхождение `{}` "
    "задаёт отдельную позицию кандидата."
)

GROUPING_RULE = (
    "Круглые скобки не меняют смысл формы, но выделяют форму как целый операнд."
)

GROUPING_BOUNDARY_RULE = (
    "Круглые скобки фиксируют границу уже собранной формы"
)

FORMAL_SEQUENCE_DISTINCTION = "{}{}{} != {}({}{})"

NEW_ROOT_LAYER_FORMULAS = [
    "∞♀ : [⟼]♀",
    "♂∞ : ♂[⟼]",
    "(⟼) : [] ⟼ []",
    "[⟼] : ∞♀ ⟼ ♂∞",
    "¬[] : ♂[] ⟼ []♀",
    "¬[⟼] : ♂[⟼] ⟼ [⟼]♀",
    "¬[⟼] : ♂∞ ⟼ ∞♀",
    "(=) : {[]♀ = []♀, ♂[] = ♂[]}",
    "(!=) : ¬(=)",
    "[] != [] : ¬([] = [])",
    "↛ : ¬[⟼]",
    "[ : ∞♀",
    "] : ♂∞",
    "1 : [⟼]",
    "0 : [↛]",
]

NEW_ROOT_LAYER_TERMS = [
    "смысл связи",
    "конкретная связь",
    "инверсия формы связи",
    "смысл равенства",
    "смысл неравенства",
    "абиты квадратной нотации",
    "∞ не является абитом",
    "¬[=] не означает !=",
]

SEQUENCE_DOCS = [
    "docs/specs/Шаблонный поиск МТС.md",
    "docs/specs/Формальная нотация МТС.md",
    "docs/theory/Система аксиом МТС.md",
    "docs/theory/Шаблон аксиом МТС.md",
]

GROUPING_DOCS = [
    "docs/specs/Формальная нотация МТС.md",
    "docs/theory/Система аксиом МТС.md",
]

REQUIRED_SYMBOLS = [
    "∞",
    "{}",
    "{",
    "}",
    ":",
    "=",
    "!=",
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
    "[]",
    "[⟼]",
    "[↛]",
    "(⟼)",
    "(=)",
    "(!=)",
    "¬[]",
    "¬[⟼]",
]

SYSTEM_STATUS_ROWS = [
    "`∞`",
    "`{}`",
    "`{`",
    "`}`",
    "`:`",
    "`=`",
    "`!=`",
    "`⟼`",
    "`♂`",
    "`♀`",
    "`[`",
    "`]`",
    "`1`, `0`",
    "`¬`",
    "`↛`",
    "`[]`",
    "`∞♀`",
    "`♂∞`",
    "`(⟼)`",
    "`[⟼]`",
    "`¬[]`",
    "`¬[⟼]`",
    "`(=)`",
    "`(!=)`",
    "`[↛]`",
]

STALE_ACTIVE_MARKERS = [
    "Сводная таблица аксиом А0-А16",
    "МТС основана на 17 аксиомах",
    "MTC is based on 17 axioms",
    "Аксиома единицы смысла: 1 : [⟼]",
    "Начало связи: [⟼]♀",
    "Конец связи: ♂[⟼]",
    "tests/issue42_mtc_formulas.mtc",
    "tests/legacy_mtc_formulas.mtc",
    "legacy parser does not execute this fixture",
    "legacy-прувер",
    "AXIOM root:",
    "EXEC root:",
    "RULE repeated-empty-braces:",
    "NEGATIVE empty-braces:",
    "STATUS parser:",
    "{s}",
    "{[}",
    "{]}",
    "{⟼}",
    "::=",
    "definition ::=",
    "definition  ::=",
    "form ::=",
    "form        ::=",
    "reference ::=",
    "reference   ::=",
    "candidate ::=",
    "candidate   ::=",
]

PROCESS_ACTIVE_MARKERS = [
    "issue #42",
    "issue 42",
    "issue42",
    "legacy",
    "старая система",
    "старые",
    "историческ",
    "архив",
    "прежн",
    "временный",
    "временные",
    "временная",
    "устар",
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
    left, separator, _right = line.partition(":")
    return bool(separator) and left.strip() in {"[", "]"}


def registered_notation_characters() -> set[str]:
    spec = read_doc("docs/specs/Формальная нотация МТС.md")
    registry_entries: list[str] = []

    for line in spec.splitlines():
        if line.startswith("| `"):
            registry_entries.extend(re.findall(r"`([^`]+)`", line.split("|", 2)[1]))

    characters: set[str] = {" "}
    for entry in registry_entries:
        characters.update(char for char in entry if char != "s")

    return characters


def test_current_foundation_documents_exist():
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED_DOCS if not path.exists()]

    assert missing == []


def test_active_document_surface_is_small_and_explicit():
    assert {path.name for path in (ROOT / "docs/theory").glob("*.md")} == ACTIVE_THEORY_FILES
    assert {path.name for path in (ROOT / "docs/specs").glob("*.md")} == ACTIVE_SPEC_FILES
    assert {path.name for path in (ROOT / "docs/research").glob("*.md")} == ACTIVE_RESEARCH_FILES


def test_removed_historical_files_are_not_active_or_rearchived():
    missing_from_active = [path for path in REMOVED_ACTIVE_FILES if path.exists()]
    assert missing_from_active == []

    rearchived = [ROOT / "archive" / path.name for path in REMOVED_ACTIVE_FILES]
    assert [path for path in rearchived if path.exists()] == []


def test_only_current_formula_fixture_is_present():
    assert (ROOT / "tests/mtc_formulas.mtc").exists()
    assert [path for path in REMOVED_TEST_FIXTURES if path.exists()] == []


def test_mtc_formula_fixture_uses_pure_formulas():
    lines = formula_lines()

    assert lines == REQUIRED_FORMULAS

    for line in lines:
        assert not line.startswith(FORBIDDEN_FIXTURE_PREFIXES), line
        assert_balanced(line, "{", "}")
        assert_balanced(line, "(", ")")
        if not is_single_abit_definition(line):
            assert_balanced(line, "[", "]")


def test_mtc_formula_fixture_uses_only_registered_notation_symbols():
    allowed = registered_notation_characters()
    unknown = {
        char
        for line in formula_lines()
        for char in line
        if char not in allowed
    }

    assert unknown == set()


def test_bang_is_used_only_as_not_equal_token():
    for line in formula_lines():
        assert "!" not in line.replace("!=", ""), line


def test_active_theory_uses_template_root_axiom():
    theory = read_doc("docs/theory/Метатеория связей.md")

    assert "∞ : {} = {} ⟼ {}" in theory
    assert "∞ = ∞ ⟼ ∞" in read_doc("tests/mtc_formulas.mtc")


def test_readme_is_current_entrypoint():
    readme = read_doc("README.md")

    for required in [
        "Что сейчас является МТС",
        "Где система аксиом",
        "Где формальная нотация",
        "Где тест формул",
        "Как проверить согласованность",
        "tests/mtc_formulas.mtc",
    ]:
        assert required in readme


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


def test_new_root_layer_formulas_are_documented():
    for relative_path in [
        "docs/specs/Формальная нотация МТС.md",
        "docs/theory/Система аксиом МТС.md",
        "docs/specs/Ачисла и сериализация.md",
    ]:
        text = read_doc(relative_path)
        missing = [formula for formula in NEW_ROOT_LAYER_FORMULAS if formula not in text]

        assert missing == [], relative_path


def test_new_root_layer_terms_are_documented():
    for relative_path in [
        "docs/specs/Формальная нотация МТС.md",
        "docs/theory/Система аксиом МТС.md",
        "docs/specs/Ачисла и сериализация.md",
        "docs/research/Открытые вопросы новой аксиоматики МТС.md",
    ]:
        text = read_doc(relative_path)
        missing = [term for term in NEW_ROOT_LAYER_TERMS if term not in text]

        assert missing == [], relative_path


def test_axiom_template_is_normative():
    template = read_doc("docs/theory/Шаблон аксиом МТС.md")

    assert "Статус: актуальное, нормативное." in template
    assert "Каждая аксиома вводит ровно один смысловой механизм." in template
    assert "Арность / валентность" in template
    assert "Критерий готовности аксиомы" in template
    assert "tests/mtc_formulas.mtc" in template


def test_axiom_system_has_symbol_statuses_and_core_cards():
    system = read_doc("docs/theory/Система аксиом МТС.md")

    assert "символ → слой → аксиома → зависит от → следствия → тесты" in system
    for row_marker in SYSTEM_STATUS_ROWS:
        assert row_marker in system, row_marker

    for heading in [
        "## А1. Акорень",
        "## А2. Группировка формы",
        "## А3. Последовательность двух форм",
        "## А4. Прямоассоциативность последовательности",
        "## А5. Самозамкнутое начало",
        "## А6. Самозамкнутый конец",
        "## А7. Начало и конец акорня",
        "## А8. Смысл связи и конкретная связь",
        "## А9. Инверсия формы связи",
        "## А10. Смысл равенства",
        "## А11. Неравенство как инверсия смысла равенства",
        "## А12. Несвязь",
        "## А13. Абиты квадратной нотации",
    ]:
        assert heading in system

    for formula in [
        "({}) = {}",
        "{}{} : ({}) ⟼ {}",
        "{}({}) : {} ⟼ ({})",
        "{}{} : {} ⟼ {}",
        "{}{}{} : ({}{}) ⟼ {}",
        "{}{}{} = (({}) ⟼ {}) ⟼ {}",
        "{}{}{} = {} ⟼ {} ⟼ {}",
        "{}({}{}) : {} ⟼ ({}{})",
        "{}{}{} != {}({}{})",
        "{}{}{} != {} ⟼ ({} ⟼ {})",
        *NEW_ROOT_LAYER_FORMULAS,
    ]:
        assert formula in system

    assert "Что не входит в рабочее ядро" in system
    assert "tests/mtc_formulas.mtc" in system


def test_active_foundation_docs_keep_brace_search_boundaries():
    for relative_path in ACTIVE_FOUNDATION_DOCS:
        text = read_doc(relative_path)
        missing = [line for line in BRACE_NEGATIONS if line not in text]

        assert missing == [], relative_path


def test_active_foundation_docs_bind_repeated_empty_braces():
    for relative_path in ACTIVE_FOUNDATION_DOCS:
        assert REPEATED_BRACE_RULE in read_doc(relative_path), relative_path


def test_sequence_docs_describe_positional_candidates():
    for relative_path in SEQUENCE_DOCS:
        assert POSITIONAL_SEQUENCE_RULE in read_doc(relative_path), relative_path


def test_grouping_docs_define_parentheses():
    for relative_path in GROUPING_DOCS:
        text = read_doc(relative_path)

        assert GROUPING_RULE in text, relative_path
        assert GROUPING_BOUNDARY_RULE in text, relative_path
        assert FORMAL_SEQUENCE_DISTINCTION in text, relative_path


def test_formal_notation_separates_candidate_and_reference():
    spec = read_doc("docs/specs/Формальная нотация МТС.md")

    assert "{} не является смысловой ссылкой на знак" in spec
    assert "смысловые ссылки через фигурные скобки больше не используются" in spec


def test_formal_notation_supports_sequence_and_grouping_forms():
    spec = read_doc("docs/specs/Формальная нотация МТС.md")

    for required in [
        "{}{} : ({}) ⟼ {}",
        "{}({}) : {} ⟼ ({})",
        "{}{} : {} ⟼ {}",
        "{}{}{} : ({}{}) ⟼ {}",
        "{}({}{}) : {} ⟼ ({}{})",
        "{}{}{} != {}({}{})",
        "{}{}{} != {} ⟼ ({} ⟼ {})",
        "(⟼) : [] ⟼ []",
        "[⟼] : ∞♀ ⟼ ♂∞",
        "¬[] : ♂[] ⟼ []♀",
        "(=) : {[]♀ = []♀, ♂[] = ♂[]}",
        "(!=) : ¬(=)",
    ]:
        assert required in spec


def test_active_docs_do_not_promote_old_or_temporary_surfaces():
    for relative_path in ACTIVE_DOCS:
        text = read_doc(relative_path)
        markers = [marker for marker in STALE_ACTIVE_MARKERS if marker in text]
        process_markers = [
            marker
            for marker in PROCESS_ACTIVE_MARKERS
            if marker.casefold() in text.casefold()
        ]

        assert markers == [], relative_path
        assert process_markers == [], relative_path
        assert "archive/" not in text, relative_path
