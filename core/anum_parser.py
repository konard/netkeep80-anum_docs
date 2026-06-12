# -*- coding: utf-8 -*-
"""Parser for practical *.anum files.

This parser is intentionally separate from ``core.mtc_reader`` and from the
UTF-8 payload codec in ``converters.anum_to_text``. The strict quaternary mode
does not apply ordinary bracket-balance rules: ``][``, ``[[`` and ``]]`` are
valid two-abit forms.
"""

from core.anum_model import Abit, AnumForm, AnumSource, AnumToken


ANUM_FORMAT_HEADER = "# anum-format:"
FORMAT_QUATERNARY = "quaternary"
FORMAT_STRING = "string"
SUPPORTED_FORMATS = (FORMAT_QUATERNARY, FORMAT_STRING)

_ABIT_BY_SYMBOL = {abit.value: abit for abit in Abit}


def parse_quaternary_anum(text: str) -> AnumForm:
    """Parse strict quaternary anum text into abits.

    Significant symbols are only ``[``, ``]``, ``1`` and ``0``. Whitespace is
    ignored. ``#`` starts a comment that runs to the end of the line.
    """

    tokens = []
    in_comment = False

    for offset, char in enumerate(text):
        if in_comment:
            if char in "\r\n":
                in_comment = False
            continue

        if char == "#":
            in_comment = True
            continue

        if char.isspace():
            continue

        abit = _ABIT_BY_SYMBOL.get(char)
        if abit is not None:
            tokens.append(AnumToken(abit=abit, offset=offset))
            continue

        raise ValueError(
            'Недопустимый символ в quaternary anum в позиции '
            f'{offset}: "{char}"'
        )

    return AnumForm(tokens=tuple(tokens))


def parse_anum_file(text: str) -> AnumForm | AnumSource:
    """Parse a complete *.anum file.

    Without an explicit header the file is parsed as strict quaternary.
    ``# anum-format: string`` keeps the payload as a string source and never
    feeds it into the quaternary parser.
    """

    format_name, body = _split_format_header(text)

    if format_name == FORMAT_QUATERNARY:
        return parse_quaternary_anum(body)
    if format_name == FORMAT_STRING:
        return AnumSource(text=body.strip(), format=FORMAT_STRING)

    raise ValueError(f'Неизвестный формат anum: "{format_name}"')


def normalize_quaternary_anum(text: str) -> str:
    """Return quaternary text without whitespace and comments."""

    form = parse_quaternary_anum(text)
    return normalize_anum_form(form)


def normalize_anum_form(form: AnumForm) -> str:
    """Return the compact textual representation of a parsed quaternary form."""

    return "".join(token.abit.value for token in form.tokens)


def _split_format_header(text: str) -> tuple[str, str]:
    """Return declared format and body after an optional leading header."""

    offset = 0
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        next_offset = offset + len(line)

        if not stripped:
            offset = next_offset
            continue

        if stripped.startswith("#"):
            if stripped.startswith(ANUM_FORMAT_HEADER):
                format_name = stripped[len(ANUM_FORMAT_HEADER):].strip()
                return format_name, text[next_offset:]
            offset = next_offset
            continue

        break

    return FORMAT_QUATERNARY, text
