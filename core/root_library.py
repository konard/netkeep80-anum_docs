# -*- coding: utf-8 -*-
"""
Загрузка корневой библиотеки формул МТС из ``.mtc``.

Этот модуль удерживает архитектуру, где формулы МТС первичны, а Python только
читает носитель, сохраняет source locations и строит диагностический реестр
различий.
"""

import enum
from dataclasses import dataclass
from typing import List

from core.layers import INFINITY_SYMBOL, SQUARE_ABIT_SYMBOLS, Layer
from core.mtc_reader import MTCReadResult, find_top_level_operators, read_formula


class FormulaKind(enum.Enum):
    """Минимальная классификация корневой формулы по top-level операторам."""

    DEFINITION = "definition"
    EQUATION = "equation"
    NON_EQUATION = "non_equation"
    EXPRESSION = "expression"


ROOT_SYMBOL_LAYERS = {
    '∞': Layer.FORMAL_FORM,
    '[]': Layer.SINGLE_CONNECTION_FORM,
    '[][]': Layer.FORMAL_FORM,
    '[][][]': Layer.FORMAL_FORM,
    '(⟼)': Layer.CONNECTION_MEANING,
    '[⟼]': Layer.CONCRETE_CONNECTION,
    '(=)': Layer.FORMAL_FORM,
    '(!=)': Layer.FORMAL_FORM,
    '↛': Layer.FORMAL_FORM,
    '[': Layer.QUATERNARY_SERIALIZATION,
    ']': Layer.QUATERNARY_SERIALIZATION,
    '1': Layer.QUATERNARY_SERIALIZATION,
    '0': Layer.QUATERNARY_SERIALIZATION,
}


@dataclass(frozen=True)
class RootFormula:
    """Одна формула корневой библиотеки с позицией в источнике."""

    text: str
    source_path: str
    line_no: int
    read_result: MTCReadResult
    kind: FormulaKind


@dataclass(frozen=True)
class DifferenceEntry:
    """Различие, введённое формулой вида ``A : F``."""

    symbol: str
    introduction: str
    layer: Layer
    status: str
    source_formula: RootFormula


class DifferenceRegistry(object):
    """Реестр различий, построенный из формул корневой библиотеки."""

    def __init__(self):
        self._entries = {}
        self._duplicates = []

    def register(self, entry):
        existing = self._entries.get(entry.symbol)
        if existing is not None:
            self._duplicates.append((entry.symbol, existing, entry))
            return
        self._entries[entry.symbol] = entry

    def lookup(self, symbol):
        return self._entries.get(symbol)

    def symbols(self):
        return list(self._entries.keys())

    def entries(self):
        return list(self._entries.values())

    def duplicates(self):
        return list(self._duplicates)


@dataclass(frozen=True)
class RootLibrary:
    """Загруженная корневая библиотека формул."""

    formulas: List[RootFormula]
    registry: DifferenceRegistry

    def texts(self):
        return [formula.text for formula in self.formulas]

    def square_abits(self):
        """Вернуть квадратные абиты, которые реально введены в .mtc."""

        return [
            symbol for symbol in SQUARE_ABIT_SYMBOLS
            if self.registry.lookup(symbol) is not None
        ]


def load_root_library(path):
    """Загрузить ``.mtc``-файл как одновременно решаемую библиотеку формул."""

    formulas = []
    with open(path, 'r', encoding='utf-8') as source:
        for line_no, raw_line in enumerate(source, 1):
            stripped = raw_line.strip()
            if not stripped or stripped.startswith('#'):
                continue

            read_result = read_formula(
                stripped,
                expected_layer=Layer.FORMAL_FORM,
                source_path=path,
                line_no=line_no,
            )
            formulas.append(
                RootFormula(
                    text=stripped,
                    source_path=path,
                    line_no=line_no,
                    read_result=read_result,
                    kind=classify_formula_kind(stripped),
                )
            )

    registry = build_difference_registry(formulas)
    return RootLibrary(formulas=formulas, registry=registry)


def build_difference_registry(formulas):
    """Построить реестр различий из формул ``A : F``."""

    registry = DifferenceRegistry()
    for formula in formulas:
        definition = _extract_definition(formula.text)
        if definition is None:
            continue

        symbol, introduction = definition
        registry.register(
            DifferenceEntry(
                symbol=symbol,
                introduction=introduction,
                layer=_infer_definition_layer(symbol, introduction),
                status=_infer_definition_status(symbol, introduction),
                source_formula=formula,
            )
        )

    return registry


def _extract_definition(text):
    positions = find_top_level_operators(text, ':')
    if len(positions) != 1:
        return None

    pos = positions[0]
    symbol = text[:pos].strip()
    introduction = text[pos + 1:].strip()
    if not symbol or not introduction:
        return None
    return symbol, introduction


def classify_formula_kind(text):
    """Классифицировать формулу без введения внешней grammar."""

    if len(find_top_level_operators(text, ':')) == 1:
        return FormulaKind.DEFINITION
    if find_top_level_operators(text, '!='):
        return FormulaKind.NON_EQUATION
    if find_top_level_operators(text, '='):
        return FormulaKind.EQUATION
    return FormulaKind.EXPRESSION


def _infer_definition_layer(symbol, introduction):
    """Диагностически вывести слой по явной таблице корневых различий.

    Таблица фиксирует текущий fixture ``tests/mtc_formulas.mtc``. Неизвестные
    различия временно читаются как формальные формы в статусе development,
    пока слой не стабилизирован отдельной корневой формулой.
    """

    return ROOT_SYMBOL_LAYERS.get(symbol, Layer.FORMAL_FORM)


def _infer_definition_status(symbol, introduction):
    if introduction.startswith('¬'):
        return 'derived'
    if symbol in SQUARE_ABIT_SYMBOLS or symbol == INFINITY_SYMBOL:
        return 'root'
    return 'development'
