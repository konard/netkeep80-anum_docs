# -*- coding: utf-8 -*-
"""Regression checks for issue #57: current MTS core only."""

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_DOCS = [
    ROOT / "README.md",
    ROOT / "docs/CONTRIBUTING.md",
    ROOT / "docs/theory/Основания МТС.md",
    ROOT / "docs/theory/Метатеория связей.md",
    ROOT / "docs/theory/Система аксиом МТС.md",
    ROOT / "docs/theory/Шаблон аксиом МТС.md",
    ROOT / "docs/specs/Ачисла и сериализация.md",
    ROOT / "docs/specs/Протокол абитов ачисел.md",
    ROOT / "docs/specs/Пучковая нотация МТС.md",
    ROOT / "docs/specs/Семантика вхождений МТС.md",
    ROOT / "docs/specs/Слои нотации МТС.md",
    ROOT / "docs/specs/Формальная нотация МТС.md",
    ROOT / "docs/specs/Шаблонный поиск МТС.md",
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
    "Протокол абитов ачисел.md",
    "Пучковая нотация МТС.md",
    "Семантика вхождений МТС.md",
    "Слои нотации МТС.md",
    "Формальная нотация МТС.md",
    "Шаблонный поиск МТС.md",
}

# ``archive`` and ``docs/research`` are intentionally not forbidden on current
# main: archival material has returned, and ``docs/research`` contains the
# protected read-only source notes guarded by CI.
# ``pics`` is also intentionally NOT forbidden: the owner asked to keep the
# illustrations (issue #57 review: "картинки удалять не надо было").
FORBIDDEN_DIRECTORIES = [
    "archive2",
    "faq",
    "history",
    "legacy",
    "old",
    "pdf",
    "drafts",
    "docs/history",
    "docs/legacy",
]

# Illustrations must remain available in the repository.
REQUIRED_DIRECTORIES = [
    "pics",
]

ACTIVE_DOCS = [
    "README.md",
    "docs/CONTRIBUTING.md",
    "docs/theory/Метатеория связей.md",
    "docs/theory/Основания МТС.md",
    "docs/theory/Система аксиом МТС.md",
    "docs/theory/Шаблон аксиом МТС.md",
    "docs/specs/Ачисла и сериализация.md",
    "docs/specs/Протокол абитов ачисел.md",
    "docs/specs/Пучковая нотация МТС.md",
    "docs/specs/Семантика вхождений МТС.md",
    "docs/specs/Слои нотации МТС.md",
    "docs/specs/Формальная нотация МТС.md",
    "docs/specs/Шаблонный поиск МТС.md",
]

# Core dictionary of the current root: every entry must stay in the fixture.
REQUIRED_ROOT_FORMULAS = [
    "∞ : [] = [] ⟼ []",
    "[] = ∞",
    "∞ = ∞ ⟼ ∞",
    "() : ♀() ⟼ ()♂",
    "([) : (♀∞)",
    "(]) : (∞♂)",
    "(⟼) : (♀∞ ⟼ ∞♂)",
    "(↛) : (∞♂ ⟼ ♀∞)",
    "[1] : (⟼)",
    "[0] : (↛)",
    # Start/end of the link form in the current orientation (♀F — start, F♂ — end).
    "♀[] : ♀[] = ♀[] ⟼ []",
    "[]♂ : []♂ = [] ⟼ []♂",
    # Equality as a match of self-closure forms, plus its negation.
    "(=) : {♀[] = ♀[], []♂ = []♂}",
    "(!=) : ¬(=)",
]

# Minimal sequence layer that must remain available in the root fixture.
REQUIRED_SEQUENCE_FORMULAS = [
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
]

# Minimal bundle layer and the distinctness of the empty bundle from the link form.
REQUIRED_BUNDLE_FORMULAS = [
    "{} != []",
    "{[]} != []",
    "{[], []} = {[]}",
    "{[], [][]} = {[][], []}",
    "[]{} = {}",
    "{}[] = {}",
    "[]{[], [][]} = {[] ⟼ [], [] ⟼ [][]}",
    "{[], [][]}[] = {[] ⟼ [], [][] ⟼ []}",
    "{[], [][]}{[], [][]} = {[] ⟼ [], [] ⟼ [][], [][] ⟼ [], [][] ⟼ [][]}",
]

# The retired equality polarity. It is assembled from fragments on purpose: the
# pre-merge guard `rg "\(=\) : \{\[\]♀ = \[\]♀, ♂\[\] = ♂\[\]\}"` must report no
# matches, so the forbidden literal must never appear contiguously in the source,
# yet the test below still has to detect it if it ever returns to the fixture.
_RETIRED_EQUALITY = "(=) : {" + "[]♀ = []♀, ♂[] = ♂[]}"

# The retired equality polarity and the contradictory empty-form inequality must
# never come back to the active root surface.
FORBIDDEN_ROOT_FORMULAS = [
    _RETIRED_EQUALITY,
    "[] != [] : ¬([] = [])",
]

# The old start/end orientation must not appear as a literal in the fixture.
FORBIDDEN_FIXTURE_SUBSTRINGS = [
    "[]♀",
    "♂[]",
]

FORBIDDEN_ACTIVE_MARKERS = [
    "\u25a1",
    "\u27e6",
    "\u27e7",
    "{" + "s}",
    "{[}",
    "{]}",
    "{⟼}",
    "∞ : {} = {} ⟼ {}",
    "::" + "=",
    "definition ::" + "=",
    "form ::" + "=",
    "reference ::" + "=",
    "candidate ::" + "=",
    "EB" + "NF",
    "8 как активный " + "абит",
    "6 как активный " + "абит",
    "9 как активный " + "абит",
    "старое 8 " + "= 0",
    "0 = " + "отсутствие связи",
    "0 — " + "отсутствие связи",
    "0 — " + "пустота",
    "несвязь существует " + "в натуре",
    "несвязь существует как " + "отдельная сущность",
    "архив " + "старых",
]

FORBIDDEN_FIXTURE_LINES = {
    "[ : ∞♀",
    "] : ♂∞",
    "1 : [⟼]",
    "0 : [↛]",
    "(⟼) : [] ⟼ []",
    "[⟼] : ∞♀ ⟼ ♂∞",
    "↛ : ¬[⟼]",
}

REQUIRED_OCCURRENCE_ROLES = [
    "container-boundary",
    "literal-abit",
    "one-link-form",
    "abit-form",
    "bundle-form",
    "formal-form",
    "empty-formal-form",
    "grouped-form",
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


def has_literal_square_abit_round_form(line: str) -> bool:
    return line.startswith("([) : ") or line.startswith("(]) : ")


def test_current_foundation_documents_exist():
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED_DOCS if not path.exists()]

    assert missing == []


def test_documentation_surface_is_current_and_explicit():
    assert {path.name for path in (ROOT / "docs/theory").glob("*.md")} == THEORY_SURFACE_FILES
    assert {path.name for path in (ROOT / "docs/specs").glob("*.md")} == ACTIVE_SPEC_FILES
    assert not (ROOT / "docs/plan.md").exists()


def test_legacy_directories_are_removed():
    existing = [relative_path for relative_path in FORBIDDEN_DIRECTORIES if (ROOT / relative_path).exists()]

    assert existing == []


def test_illustrations_are_preserved():
    # The owner explicitly asked to keep the illustrations of issue #57.
    for relative_path in REQUIRED_DIRECTORIES:
        directory = ROOT / relative_path
        assert directory.is_dir(), relative_path
        assert any(directory.iterdir()), relative_path


def test_mtc_formula_fixture_uses_current_root_dictionary():
    lines = formula_lines()
    line_set = set(lines)

    for required in (
        REQUIRED_ROOT_FORMULAS + REQUIRED_SEQUENCE_FORMULAS + REQUIRED_BUNDLE_FORMULAS
    ):
        assert required in line_set, required

    assert line_set.isdisjoint(FORBIDDEN_ROOT_FORMULAS)
    assert line_set.isdisjoint(FORBIDDEN_FIXTURE_LINES)

    fixture_text = read_doc("tests/mtc_formulas.mtc")
    for forbidden in FORBIDDEN_FIXTURE_SUBSTRINGS:
        assert forbidden not in fixture_text, forbidden

    for line in lines:
        assert_balanced(line, "{", "}")
        assert_balanced(line, "(", ")")
        if not has_literal_square_abit_round_form(line):
            assert_balanced(line, "[", "]")


def test_active_docs_reject_retired_external_mechanisms():
    for relative_path in ACTIVE_DOCS:
        text = read_doc(relative_path)
        markers = [marker for marker in FORBIDDEN_ACTIVE_MARKERS if marker in text]

        assert markers == [], relative_path


def test_readme_is_current_entrypoint():
    readme = read_doc("README.md")

    for required in [
        "Что сейчас является МТС",
        "Онтологическое ядро",
        "Базовый словарь акорня",
        "Скобочные нотации",
        "Корневой fixture",
        "Спецификации",
        "Команды проверки",
        "tests/mtc_formulas.mtc",
        "core/mtc_reader.py",
        "core/root_library.py",
    ]:
        assert required in readme


def test_readme_links_point_to_existing_local_files():
    readme = read_doc("README.md")

    for target in markdown_links(readme):
        if target.startswith(("http://", "https://")):
            continue
        path = ROOT / target.replace("%20", " ")
        assert path.exists(), target


def test_ontology_core_is_normative_across_docs():
    combined = "\n".join(read_doc(relative_path) for relative_path in ACTIVE_DOCS)

    for required in [
        "связь — единственная форма существования",
        "существовать — значит быть связью",
        "смысл не существует отдельно от связи",
        "связь и есть смысл в своей различённой форме",
        "несвязь не существует в натуре",
        "смысл несвязи выражается связью",
        "0 — абит связи, несущей смысл несвязи",
        "↛ — смысл несвязи",
        "акорень несёт смысл смысла",
    ]:
        assert required in combined


def test_bracket_notations_are_distinguished():
    combined = "\n".join(read_doc(relative_path) for relative_path in ACTIVE_DOCS)

    for required in [
        "(...) — круглая формальная нотация",
        "[...] — квадратная ачисловая нотация",
        "{...} — пучковая нотация",
        "[] — минимальная завершённая форма одной связи",
        "() — минимальная формальная форма смысла",
        "{} — пустой пучок связей",
    ]:
        assert required in combined


def test_formal_notation_spec_defines_current_root_frame():
    spec = read_doc("docs/specs/Формальная нотация МТС.md")

    for required in [
        "## Связь и смысл",
        "## Натуральная связь и смысловая роль",
        "## Базовый словарь акорня",
        "## Пустая круглая форма смысла",
        "## Квадратная абитовая нотация",
        "## Разные скобочные нотации",
        "## Семантика вхождений",
        "∞ : [] = [] ⟼ []",
        "() : ♀() ⟼ ()♂",
        "([) : (♀∞)",
        "(]) : (∞♂)",
        "(⟼) : (♀∞ ⟼ ∞♂)",
        "(↛) : (∞♂ ⟼ ♀∞)",
        "[1] : (⟼)",
        "[0] : (↛)",
    ]:
        assert required in spec


def test_occurrence_semantics_document_defines_roles():
    spec = read_doc("docs/specs/Семантика вхождений МТС.md")

    for role in REQUIRED_OCCURRENCE_ROLES:
        assert role in spec

    for required in [
        "видимый знак не равен вхождению знака",
        "([) как незакрытый квадратный контейнер",
        "(]) как лишнюю закрывающую квадратную скобку",
        "() : ♀() ⟼ ()♂",
        "Reader должен различать",
    ]:
        assert required in spec


def test_anum_serialization_defines_current_square_abits():
    spec = read_doc("docs/specs/Ачисла и сериализация.md")

    for required in [
        "[ и ] — квадратные абиты полюсов формы",
        "[1] — квадратная форма абита связи",
        "[0] — квадратная форма абита несвязи",
        "0 не означает отсутствие связи в натуре",
        "0 означает абит связи, несущей смысл несвязи",
        "ачисло — последовательность абитов, интерпретируемая в ассоциативном контексте",
        "() — минимальная формальная форма смысла",
    ]:
        assert required in spec


def test_nonconnection_and_inversion_are_not_mixed():
    combined = "\n".join(read_doc(relative_path) for relative_path in ACTIVE_DOCS)

    for required in [
        "инверсия связи меняет направление натуральной связи",
        "инверсия смысла меняет смысл на обратный",
        "обратное направление связи не является отсутствием связи",
        "абит 0 не является отсутствием связи в натуре",
    ]:
        assert required in combined


def test_equality_is_read_as_form_self_closure_match():
    combined = "\n".join(read_doc(relative_path) for relative_path in ACTIVE_DOCS)

    for required in [
        "равенство фиксирует совпадение форм связей",
        "равенство не является простой идентичностью определения",
        "формы связей являются видами самозамыканий",
        "рекурсивная процедура сравнения различает формы рекурсий",
        "равенство не требует бесконечного раскрытия рекурсивных связей",
        "(=) : {♀[] = ♀[], []♂ = []♂}",
        "(!=) : ¬(=)",
    ]:
        assert required in combined

    for forbidden in [
        "равенство является простой идентичностью определения",
        "равенство — это текстовое совпадение определений",
        "равенство требует полного раскрытия связи",
        _RETIRED_EQUALITY,
    ]:
        assert forbidden not in combined


def test_empty_forms_are_documented_as_distinct():
    combined = "\n".join(read_doc(relative_path) for relative_path in ACTIVE_DOCS)

    for required in [
        "[] != ()",
        "() != {}",
        "{} != []",
    ]:
        assert required in combined, required


def test_fixture_records_nonconnection_assertions():
    lines = set(formula_lines())

    for required in [
        "{} != []",
        "{[]} != []",
        "[][][] != []([][])",
        "[][][] != [] ⟼ ([] ⟼ [])",
    ]:
        assert required in lines, required


def test_current_start_end_polarity_is_documented():
    combined = "\n".join(read_doc(relative_path) for relative_path in ACTIVE_DOCS)

    for required in [
        "♀[] : ♀[] = ♀[] ⟼ []",
        "[]♂ : []♂ = [] ⟼ []♂",
    ]:
        assert required in combined, required
