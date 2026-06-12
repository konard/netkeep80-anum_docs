# -*- coding: utf-8 -*-
"""Protocol projection for two-abit square forms."""

from dataclasses import dataclass

from core.anum_model import Abit


ALPHA = "α"
BETA = "β"


@dataclass(frozen=True)
class TwoAbitProjection:
    """Projection of a two-abit square form into the issue #61 protocol."""

    source: str
    left: Abit
    right: Abit
    arrow_form: str
    protocol_value: str | None
    meaning: str


_PROJECTIONS = {
    (Abit.OPEN, Abit.OPEN): (
        f"{ALPHA} ⟼ {ALPHA}",
        None,
        "open-open boundary form",
    ),
    (Abit.OPEN, Abit.CLOSE): (
        f"{ALPHA} ⟼ {BETA}",
        "0",
        "container / unlink / non-materializing description",
    ),
    (Abit.CLOSE, Abit.OPEN): (
        f"{BETA} ⟼ {ALPHA}",
        "1",
        "bridge / link / materializing transition",
    ),
    (Abit.CLOSE, Abit.CLOSE): (
        f"{BETA} ⟼ {BETA}",
        None,
        "close-close boundary form",
    ),
}


def project_two_abit_form(left: Abit, right: Abit) -> TwoAbitProjection:
    """Project one of ``[[``, ``[]``, ``][`` or ``]]``."""

    projection = _PROJECTIONS.get((left, right))
    if projection is None:
        raise ValueError(
            "Проекция определена только для двух квадратных абитов: "
            f'{left.value}{right.value}'
        )

    arrow_form, protocol_value, meaning = projection
    return TwoAbitProjection(
        source=left.value + right.value,
        left=left,
        right=right,
        arrow_form=arrow_form,
        protocol_value=protocol_value,
        meaning=meaning,
    )
