# -*- coding: utf-8 -*-
"""Структурированный результат legacy-доказателя."""

from dataclasses import dataclass


PROOF_STATUSES = ('proved', 'disproved', 'unknown', 'parse_error', 'unsupported')


@dataclass(frozen=True)
class ProofResult:
    """Результат проверки одной формулы legacy prover'ом."""

    status: str
    formula: str
    reason: str = None

    @property
    def is_proved(self):
        return self.status == 'proved'

    @property
    def is_disproved(self):
        return self.status == 'disproved'
