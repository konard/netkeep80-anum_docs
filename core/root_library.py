# -*- coding: utf-8 -*-
"""
Загрузка корневой библиотеки формул МТС из ``.mtc``.

Этот модуль является первым переходным шагом от legacy Python parser/prover к
архитектуре, где формулы МТС первичны, а Python только читает носитель,
сохраняет source locations и строит диагностический реестр различий.
"""

from dataclasses import dataclass
from typing import List

from core.layers import INFINITY_SYMBOL, SQUARE_ABIT_SYMBOLS, Layer
from core.mtc_reader import MTCReadResult, read_formula


@dataclass(frozen=True)
class RootFormula:
    """Одна формула корневой библиотеки с позицией в источнике."""

    text: str
    source_path: str
    line_no: int
    read_result: MTCReadResult


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

    def register(self, entry):
        self._entries[entry.symbol] = entry

    def lookup(self, symbol):
        return self._entries.get(symbol)

    def symbols(self):
        return list(self._entries.keys())

    def entries(self):
        return list(self._entries.values())


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
    if ':' not in text:
        return None

    symbol, introduction = text.split(':', 1)
    symbol = symbol.strip()
    introduction = introduction.strip()
    if not symbol or not introduction:
        return None
    return symbol, introduction


def _infer_definition_layer(symbol, introduction):
    """Диагностически вывести слой из формы введения.

    Это не грамматика МТС и не источник истины: слой выводится из уже
    прочитанной корневой формулы, чтобы ранние проверки могли ловить смешение
    квадратных абитов, смысла связи и конкретной связи.
    """

    if symbol in SQUARE_ABIT_SYMBOLS:
        return Layer.QUATERNARY_SERIALIZATION
    if symbol == INFINITY_SYMBOL:
        return Layer.FORMAL_FORM
    if symbol.startswith('(') and symbol.endswith(')'):
        return Layer.CONNECTION_MEANING
    if symbol.startswith('[') and symbol.endswith(']'):
        return Layer.CONCRETE_CONNECTION
    if symbol.startswith('{') and symbol.endswith('}'):
        return Layer.BUNDLE_FORM
    return Layer.FORMAL_FORM


def _infer_definition_status(symbol, introduction):
    if introduction.startswith('¬'):
        return 'derived'
    if symbol in SQUARE_ABIT_SYMBOLS or symbol == INFINITY_SYMBOL:
        return 'root'
    return 'development'
