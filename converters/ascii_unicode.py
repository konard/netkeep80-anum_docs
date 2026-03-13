# -*- coding: utf-8 -*-
"""
Конвертер ASCII ↔ Unicode нотаций МТС.

Таблица соответствия нотаций (anum_docs ↔ aprover):

  anum_docs (Unicode)  |  aprover (ASCII)  |  Описание
  ─────────────────────┼───────────────────┼──────────────────────
  ⟼                    |  ->               |  Конструктор связи
  ¬⟼                   |  !->              |  Отрицание стрелки
  ¬                    |  !                |  Инверсия
  ♂                    |  M                |  Начальность (самозамыкание начала, постфиксный)
  ♀                    |  F                |  Конечность (самозамыкание конца, префиксный)
  ∞                    |  INF              |  Акорень
  =                    |  =                |  Тождественность
  ≠                    |  !=               |  Отрицание тождества
  :                    |  :                |  Оператор определения
  [                    |  [                |  Абит начала смысла
  ]                    |  ]                |  Абит конца смысла
  1                    |  1                |  Абит единицы смысла
  0                    |  0                |  Абит нуля смысла

Примечание: Символы абитов в anum_docs и aprover теперь унифицированы.

Использование:
  python3 converters/ascii_unicode.py --to-ascii "♀∞♂ = (♀∞)♂"
  python3 converters/ascii_unicode.py --to-unicode "F INF M = (F INF) M"
"""

import sys
import re
import argparse


# Таблица соответствия: anum_docs (Unicode) → aprover (ASCII)
# Порядок важен: длинные токены проверяются первыми
_UNICODE_TO_ASCII = [
    ('¬⟼', '!->'),
    ('⟼', '->'),
    ('≠', '!='),
    ('¬', '!'),
    ('♂', 'M'),
    ('♀', 'F'),
    ('∞', 'INF'),
]

# Обратная таблица: aprover (ASCII) → anum_docs (Unicode)
# Порядок важен: длинные токены проверяются первыми
_ASCII_TO_UNICODE = [
    ('!->', '¬⟼'),
    ('->', '⟼'),
    ('!=', '≠'),
    ('!', '¬'),
    ('INF', '∞'),
    ('M', '♂'),
    ('F', '♀'),
]

# Абиты: anum_docs и aprover теперь используют одинаковые символы
# Конвертация — тождественная (для обратной совместимости)
_ABIT_TO_APROVER = [
    ('[', '['),
    (']', ']'),
    ('1', '1'),
    ('0', '0'),
]

# Абиты: aprover → anum_docs (тождественная конвертация)
_APROVER_TO_ABIT = [
    ('[', '['),
    (']', ']'),
    ('1', '1'),
    ('0', '0'),
]


def _replace_tokens(text: str, table: list) -> str:
    """Последовательная замена токенов по таблице соответствия.

    Длинные токены в таблице должны идти перед короткими,
    чтобы избежать частичных замен.
    """
    result = text
    for src, dst in table:
        result = result.replace(src, dst)
    return result


def _is_alnum(c: str) -> bool:
    """Проверка, является ли символ буквой или цифрой."""
    return c.isalnum() and c not in '♂♀∞⟼¬≠'


def _tokenize_unicode(formula: str) -> list:
    """Разбиение Unicode-формулы на токены для замены.

    Находит Unicode-символы МТС и разделяет их от окружающего текста.
    Возвращает список пар (текст, is_mtc_symbol).
    """
    # Сортируем по длине убывающей для жадного сопоставления
    patterns = sorted([src for src, _ in _UNICODE_TO_ASCII], key=len, reverse=True)
    tokens = []
    i = 0
    while i < len(formula):
        matched = False
        for pat in patterns:
            if formula[i:i+len(pat)] == pat:
                tokens.append((pat, True))
                i += len(pat)
                matched = True
                break
        if not matched:
            tokens.append((formula[i], False))
            i += 1
    return tokens


def unicode_to_ascii(formula: str) -> str:
    """Конвертация формулы из Unicode (anum_docs) в ASCII (aprover).

    Вставляет пробелы между соседними алфавитно-цифровыми токенами,
    чтобы M, F, INF не сливались друг с другом.

    Args:
        formula: Формула в Unicode нотации (♂, ♀, →, ∞).

    Returns:
        Формула в ASCII нотации (M, F, ->, INF).
    """
    table = dict(_UNICODE_TO_ASCII)
    tokens = _tokenize_unicode(formula)

    parts = []
    for text, is_mtc in tokens:
        replacement = table[text] if is_mtc else text
        # Вставляем пробел между двумя алфавитно-цифровыми частями
        if parts and parts[-1] and replacement:
            last_char = parts[-1][-1]
            first_char = replacement[0]
            if _is_alnum(last_char) and _is_alnum(first_char):
                parts.append(' ')
        parts.append(replacement)

    return ''.join(parts)


def ascii_to_unicode(formula: str) -> str:
    """Конвертация формулы из ASCII (aprover) в Unicode (anum_docs).

    Args:
        formula: Формула в ASCII нотации (M, F, ->, INF).

    Returns:
        Формула в Unicode нотации (♂, ♀, →, ∞).
    """
    return _replace_tokens(formula, _ASCII_TO_UNICODE)


def abits_to_aprover(anum: str) -> str:
    """Конвертация абитовой нотации anum_docs → aprover.

    После унификации символов абитов конвертация является тождественной.

    Args:
        anum: Абитовая запись: [, ], 1, 0

    Returns:
        Абитовая запись: [, ], 1, 0
    """
    return _replace_tokens(anum, _ABIT_TO_APROVER)


def aprover_to_abits(aprover_anum: str) -> str:
    """Конвертация абитовой нотации aprover → anum_docs.

    После унификации символов абитов конвертация является тождественной.

    Args:
        aprover_anum: Абитовая запись: [, ], 1, 0

    Returns:
        Абитовая запись: [, ], 1, 0
    """
    return _replace_tokens(aprover_anum, _APROVER_TO_ABIT)


def main():
    parser = argparse.ArgumentParser(
        description='Конвертер ASCII ↔ Unicode нотаций МТС'
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--to-ascii', type=str, default=None,
        help='Конвертировать формулу из Unicode в ASCII'
    )
    group.add_argument(
        '--to-unicode', type=str, default=None,
        help='Конвертировать формулу из ASCII в Unicode'
    )
    group.add_argument(
        '--to-aprover', type=str, default=None,
        help='Конвертировать абиты anum_docs → aprover (тождественная операция после унификации)'
    )
    group.add_argument(
        '--to-anum', type=str, default=None,
        help='Конвертировать абиты aprover → anum_docs (тождественная операция после унификации)'
    )

    args = parser.parse_args()

    if args.to_ascii is not None:
        print(unicode_to_ascii(args.to_ascii))
    elif args.to_unicode is not None:
        print(ascii_to_unicode(args.to_unicode))
    elif args.to_aprover is not None:
        print(abits_to_aprover(args.to_aprover))
    elif args.to_anum is not None:
        print(aprover_to_abits(args.to_anum))


if __name__ == '__main__':
    main()
