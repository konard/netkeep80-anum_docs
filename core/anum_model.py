# -*- coding: utf-8 -*-
"""Minimal models for practical *.anum serialization."""

from dataclasses import dataclass
from enum import Enum


class Abit(Enum):
    """Four base abits of the quaternary anum protocol."""

    OPEN = "["
    CLOSE = "]"
    LINK = "1"
    UNLINK = "0"


@dataclass(frozen=True)
class AnumSource:
    """Raw *.anum source in a declared non-quaternary mode."""

    text: str
    format: str


@dataclass(frozen=True)
class AnumToken:
    """One parsed quaternary abit and its offset in the parsed text."""

    abit: Abit
    offset: int


@dataclass(frozen=True)
class AnumForm:
    """A strict quaternary anum as a sequence of abits."""

    tokens: tuple[AnumToken, ...]
