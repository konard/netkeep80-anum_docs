# -*- coding: utf-8 -*-
"""Tests for the minimal non-materializing anum memory model."""

from core.anum_memory import AnumMemory, Link, Quote, SymbolicAnum, deserialize


def test_symbolic_deserialize_and_quote_levels():
    form = SymbolicAnum("a", "b")

    assert deserialize(form) == Link("a", "b")
    assert deserialize(Quote(form)) == form
    assert deserialize(Quote(Quote(form))) == Quote(form)


def test_load_and_find_do_not_materialize_denoted_link():
    memory = AnumMemory()
    form = SymbolicAnum("a", "b")
    link = Link("a", "b")

    memory.load(form)
    assert link not in memory.links

    assert memory.find(form) is False
    assert link not in memory.links

    memory.realize(form)
    assert link in memory.links
    assert memory.find(form) is True


def test_realizing_quote_does_not_materialize_inner_denotation():
    memory = AnumMemory()
    form = SymbolicAnum("a", "b")

    realized = memory.realize(Quote(form))

    assert realized == form
    assert Link("a", "b") not in memory.links
    assert form in memory.raw_forms
