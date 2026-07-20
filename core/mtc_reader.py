# -*- coding: utf-8 -*-
"""
Технический reader формальной нотации МТС.

Reader фиксирует строковый носитель, границы контейнеров и source span. Он
намеренно не задаёт источник смысла нотации: смысл должен приходить из
корневой библиотеки ``.mtc``-формул.
"""

from dataclasses import dataclass
from typing import List, Optional

from core.layers import Layer


_OPEN_TO_CLOSE = {
    '(': ')',
    '[': ']',
    '{': '}',
}

_CLOSE_TO_OPEN = {close: open_ for open_, close in _OPEN_TO_CLOSE.items()}

_CONTAINER_KIND = {
    '(': 'round',
    '[': 'square',
    '{': 'curly',
}


@dataclass
class ContainerSpan:
    """Границы контейнера в исходной строке."""

    kind: str
    open_symbol: str
    close_symbol: str
    start: int
    end: Optional[int] = None


@dataclass
class ReadToken:
    """Минимальная единица строкового носителя."""

    value: str
    start: int
    end: int


@dataclass
class MTCReadResult:
    """Результат чтения формулы без назначения внешней грамматики."""

    text: str
    status: str
    layer: Optional[Layer]
    containers: List[ContainerSpan]
    tokens: List[ReadToken]
    diagnostics: List[str]
    source_path: Optional[str] = None
    line_no: Optional[int] = None

    @property
    def is_valid(self):
        return self.status == 'valid'


def read_formula(text, expected_layer=None, source_path=None, line_no=None):
    """Прочитать строковую формулу как носитель различий и контейнеров."""

    diagnostics = []
    top_level_colons = find_top_level_operators(text, ':')
    if len(top_level_colons) > 1:
        diagnostics.append(
            "Оператор введения различия ':' должен быть единственным на верхнем уровне"
        )

    containers = []
    stack = []
    tokens = []
    token_start = None
    token_chars = []
    literal_lhs_span = _literal_definition_lhs_span(text)

    def flush_token(pos):
        if token_chars:
            tokens.append(ReadToken(''.join(token_chars), token_start, pos))
            token_chars[:] = []

    for pos, char in enumerate(text):
        if char.isspace():
            flush_token(pos)
            token_start = None
            continue

        if _is_literal_square_abit_in_round_form(text, pos, stack):
            if token_start is None:
                token_start = pos
            token_chars.append(char)
            continue

        if char in _OPEN_TO_CLOSE and not _in_span(pos, literal_lhs_span):
            flush_token(pos)
            token_start = None
            span = ContainerSpan(
                kind=_CONTAINER_KIND[char],
                open_symbol=char,
                close_symbol=_OPEN_TO_CLOSE[char],
                start=pos,
            )
            containers.append(span)
            stack.append((char, span))
            tokens.append(ReadToken(char, pos, pos + 1))
            continue

        if char in _CLOSE_TO_OPEN and not _in_span(pos, literal_lhs_span):
            flush_token(pos)
            token_start = None
            expected_open = _CLOSE_TO_OPEN[char]
            if not stack:
                diagnostics.append("Лишнее закрытие контейнера {0} в позиции {1}".format(char, pos))
            else:
                open_char, span = stack.pop()
                if open_char != expected_open:
                    diagnostics.append(
                        "Неверное закрытие контейнера {0} в позиции {1}; ожидалось {2}".format(
                            char,
                            pos,
                            _OPEN_TO_CLOSE[open_char],
                        )
                    )
                else:
                    span.end = pos + 1
            tokens.append(ReadToken(char, pos, pos + 1))
            continue

        if token_start is None:
            token_start = pos
        token_chars.append(char)

    flush_token(len(text))

    for open_char, span in stack:
        diagnostics.append(
            "Незакрытый контейнер {0} в позиции {1}".format(open_char, span.start)
        )

    layer = expected_layer
    if layer is None:
        diagnostics.append("Слой чтения не указан; результат является диагностическим guess, не спецификацией")
        status = 'ambiguous'
    elif diagnostics:
        status = 'invalid'
    else:
        status = 'valid'

    return MTCReadResult(
        text=text,
        status=status,
        layer=layer,
        containers=containers,
        tokens=tokens,
        diagnostics=diagnostics,
        source_path=source_path,
        line_no=line_no,
    )


def find_top_level_operators(text, operator):
    """Найти все позиции оператора вне ``()``, ``[]`` и ``{}``.

    Это технический scanner строкового носителя, а не грамматика МТС. Он нужен
    для ранней классификации формул и корректного чтения ``A : F`` без split по
    двоеточию внутри контейнеров.
    """

    if not operator:
        raise ValueError("operator must not be empty")

    positions = []
    stack = []
    literal_lhs_span = _literal_definition_lhs_span(text) if operator == ':' else None
    pos = 0

    while pos < len(text):
        if text.startswith(operator, pos) and not stack:
            positions.append(pos)
            pos += len(operator)
            continue

        char = text[pos]
        if _is_literal_square_abit_in_round_form(text, pos, stack):
            pos += 1
            continue

        if char in _OPEN_TO_CLOSE and not _in_span(pos, literal_lhs_span):
            stack.append(char)
        elif char in _CLOSE_TO_OPEN and not _in_span(pos, literal_lhs_span):
            expected_open = _CLOSE_TO_OPEN[char]
            if stack and stack[-1] == expected_open:
                stack.pop()

        pos += 1

    return positions


def _literal_definition_lhs_span(text):
    """Вернуть span одиночного bracket-символа перед ``:``.

    Формулы ``[ : ...`` и ``] : ...`` вводят сами bracket-различия; в этой
    позиции bracket не является границей контейнера.
    """

    start = len(text) - len(text.lstrip())
    if start >= len(text) or text[start] not in ('[', ']'):
        return None

    pos = start + 1
    while pos < len(text) and text[pos].isspace():
        pos += 1

    if pos >= len(text) or text[pos] != ':':
        return None

    return start, start + 1


def _is_literal_square_abit_in_round_form(text, pos, stack):
    """Проверить ``([)`` и ``(])`` как круглые формы с буквальным абитом."""

    if text[pos] not in ('[', ']'):
        return False
    if not stack or _stack_open_symbol(stack[-1]) != '(':
        return False
    if pos == 0 or text[pos - 1] != '(':
        return False
    return pos + 1 < len(text) and text[pos + 1] == ')'


def _stack_open_symbol(item):
    if isinstance(item, tuple):
        return item[0]
    return item


def _in_span(pos, span):
    return span is not None and span[0] <= pos < span[1]
