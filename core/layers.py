# -*- coding: utf-8 -*-
"""Явные слои чтения формальной нотации МТС."""

import enum


class Layer(enum.Enum):
    """Слой, в котором читается строковая запись."""

    STRING_ANUM = "string_anum"
    FORMAL_FORM = "formal_form"
    SINGLE_CONNECTION_FORM = "single_connection_form"
    CONCRETE_CONNECTION = "concrete_connection"
    CONNECTION_MEANING = "connection_meaning"
    BUNDLE_FORM = "bundle_form"
    ASET = "aset"
    QUATERNARY_SERIALIZATION = "quaternary_serialization"


SQUARE_ABIT_SYMBOLS = ('([)', '(])', '[1]', '[0]')
INFINITY_SYMBOL = '∞'
