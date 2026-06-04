# -*- coding: utf-8 -*-
"""Минимальная структурная валидация корневой библиотеки МТС."""

from dataclasses import dataclass
from typing import List

from core.layers import SQUARE_ABIT_SYMBOLS, Layer
from core.root_library import RootLibrary, load_root_library


@dataclass(frozen=True)
class RootValidationResult:
    """Результат проверки корневой библиотеки."""

    status: str
    messages: List[str]
    library: RootLibrary

    @property
    def is_valid(self):
        return self.status == 'valid'


def validate_root_library(path):
    """Проверить, что ``.mtc`` читается как корневая библиотека формул."""

    library = load_root_library(path)
    messages = []

    if not library.formulas:
        messages.append("Корневая библиотека не содержит формул")

    for formula in library.formulas:
        if not formula.read_result.is_valid:
            messages.append(
                "{0}:{1}: {2}".format(
                    formula.source_path,
                    formula.line_no,
                    "; ".join(formula.read_result.diagnostics),
                )
            )

    for symbol, first, second in library.registry.duplicates():
        messages.append(
            "Повторное введение различия {0}: {1}:{2} и {3}:{4}".format(
                symbol,
                first.source_formula.source_path,
                first.source_formula.line_no,
                second.source_formula.source_path,
                second.source_formula.line_no,
            )
        )

    required_symbols = ('∞', '()', '([)', '(])', '(⟼)', '(↛)', '[1]', '[0]', '(=)')
    for symbol in required_symbols:
        if library.registry.lookup(symbol) is None:
            messages.append("Не найдено корневое различие: {0}".format(symbol))

    square_abits = set(library.square_abits())
    expected_abits = set(SQUARE_ABIT_SYMBOLS)
    if square_abits != expected_abits:
        messages.append(
            "Квадратные абиты должны быть {0}, получено {1}".format(
                sorted(expected_abits),
                sorted(square_abits),
            )
        )

    infinity = library.registry.lookup('∞')
    if infinity is not None and infinity.layer == Layer.QUATERNARY_SERIALIZATION:
        messages.append("∞ не должен находиться в слое QUATERNARY_SERIALIZATION")

    return RootValidationResult(
        status='invalid' if messages else 'valid',
        messages=messages,
        library=library,
    )
