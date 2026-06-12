# -*- coding: utf-8 -*-
"""Minimal symbolic memory model for anum deserialization tests."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Link:
    """A materialized symbolic link."""

    left: str
    right: str


@dataclass(frozen=True)
class SymbolicAnum:
    """A symbolic anum whose denotation is ``left ⟼ right``."""

    left: str
    right: str


@dataclass(frozen=True)
class Quote:
    """A non-materializing quote wrapper."""

    value: Any


def deserialize(anum: Any) -> Any:
    """Return the denotation of one symbolic deserialization step.

    ``SymbolicAnum("a", "b")`` denotes ``Link("a", "b")``. A quote raises the
    description level, so ``Quote(A)`` denotes ``A`` instead of ``den(A)``.
    """

    if isinstance(anum, Quote):
        return anum.value
    if isinstance(anum, SymbolicAnum):
        return Link(anum.left, anum.right)
    if isinstance(anum, Link):
        return anum
    raise TypeError(f"Неподдерживаемое symbolic anum значение: {anum!r}")


class AnumMemory:
    """Small test double for separating load/find/realize semantics."""

    def __init__(self):
        self.raw_forms = set()
        self.links = set()

    def load(self, anum: Any) -> Any:
        """Store raw description without creating its denotation."""

        self.raw_forms.add(anum)
        return anum

    def decode(self, anum: Any) -> Any:
        """Decode a loaded form without materializing its denotation."""

        return anum

    def project_K(self, anum: Any) -> Any:
        """Project a symbolic form in the current test context."""

        return deserialize(anum)

    def find(self, anum: Any) -> bool:
        """Check whether the projected denotation already exists."""

        projected = self.project_K(anum)
        if isinstance(projected, Link):
            return projected in self.links
        return projected in self.raw_forms

    def realize(self, anum: Any) -> Any:
        """Materialize the projected denotation when it is a link."""

        projected = self.project_K(anum)
        if isinstance(projected, Link):
            self.links.add(projected)
        else:
            self.raw_forms.add(projected)
        return projected
