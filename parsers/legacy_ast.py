# -*- coding: utf-8 -*-
"""
Legacy runtime AST для старых parser/prover.

Этот модуль является временным compatibility-layer. Он содержит Python-
представления, которые ранее дублировались между ``anum_prover.py`` и
``mtc_formula_prover.py``. Модуль не является ядром МТС, формальной
спецификацией нотации или источником новых правил.

Канонический источник правил формальной нотации МТС — корневая библиотека
``.mtc``-формул, читаемая через ``core.root_library``. Новые правила нотации
должны попадать в ``.mtc``-формулы, а не в этот legacy AST.

Состав:
- :class:`AnumToken`            — токен лексического анализатора;
- :class:`AnumExpression`       — базовый класс всех выражений;
- :class:`Symbol`               — именованный символ (переменная);
- :class:`Connection`           — связь (reference → value);
- :class:`AbitStart`/:class:`AbitEnd`/:class:`AbitConnect`/:class:`AbitDisconnect`
                                — абиты структуры;
- :class:`AssociativeRoot`      — акорень ∞;
- :class:`ConnectionForm`       — форма связи (♂, ♀, →, отрицание);
- :class:`ComplexClosure`       — сложное замыкание вида ♂∞♀;
- :class:`NegationExpression`   — отрицание выражения (например, -♂x);
- :class:`PowerLoopExpression`  — степень петли (например, a^2).

Модуль не содержит лексеров/парсеров/доказателей — только переносимые
структуры данных, нужные для совместимости старых реализаций.
"""


class AnumToken(object):
    """Токен лексического анализатора МТС."""

    def __init__(self, type_, value, position=0):
        self.type = type_
        self.value = value
        self.position = position

    def __repr__(self):
        return "Token({0}, '{1}')".format(self.type, self.value)


class AnumExpression(object):
    """Базовый класс всех выражений МТС."""

    def __repr__(self):
        return self.__str__()


class Symbol(AnumExpression):
    """Именованный символ (переменная) выражения."""

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return isinstance(other, Symbol) and self.name == other.name

    def __hash__(self):
        return hash(('Symbol', self.name))


class Connection(AnumExpression):
    """Связь между ссылкой (reference) и значением (value): (reference→value)."""

    def __init__(self, reference, value):
        self.reference = reference
        self.value = value

    def __str__(self):
        return "({0}→{1})".format(self.reference, self.value)

    def __eq__(self, other):
        return (isinstance(other, Connection) and
                self.reference == other.reference and
                self.value == other.value)

    def __hash__(self):
        return hash(('Connection', self.reference, self.value))


class AbitStart(AnumExpression):
    """Абит начала структуры: ( ."""

    def __str__(self):
        return "("

    def __eq__(self, other):
        return isinstance(other, AbitStart)

    def __hash__(self):
        return hash(('AbitStart',))


class AbitEnd(AnumExpression):
    """Абит конца структуры: ) ."""

    def __str__(self):
        return ")"

    def __eq__(self, other):
        return isinstance(other, AbitEnd)

    def __hash__(self):
        return hash(('AbitEnd',))


class AbitConnect(AnumExpression):
    """Абит связи: + ."""

    def __str__(self):
        return "+"

    def __eq__(self, other):
        return isinstance(other, AbitConnect)

    def __hash__(self):
        return hash(('AbitConnect',))


class AbitDisconnect(AnumExpression):
    """Абит несвязи: - ."""

    def __str__(self):
        return "-"

    def __eq__(self, other):
        return isinstance(other, AbitDisconnect)

    def __hash__(self):
        return hash(('AbitDisconnect',))


class AssociativeRoot(AnumExpression):
    """Акорень ∞."""

    def __str__(self):
        return "∞"

    def __eq__(self, other):
        return isinstance(other, AssociativeRoot)

    def __hash__(self):
        return hash(('AssociativeRoot',))

    @staticmethod
    def from_abit_combination():
        return AssociativeRoot()


class ConnectionForm(AnumExpression):
    """Форма связи: ♂ (REF), ♀ (VAL), → (ARROW) или отрицание (NEGATION).

    Ветка ``NEGATION`` используется только в ``mtc_formula_prover.py``;
    для остальных доказателей она инертна и не влияет на поведение.
    """

    def __init__(self, form_type):
        self.form_type = form_type

    def __str__(self):
        if self.form_type == 'REF':
            return "♂"
        elif self.form_type == 'VAL':
            return "♀"
        elif self.form_type == 'ARROW':
            return "→"
        elif self.form_type == 'NEGATION':
            return "-"
        return "unknown_form"

    def __eq__(self, other):
        return isinstance(other, ConnectionForm) and self.form_type == other.form_type

    def __hash__(self):
        return hash(('ConnectionForm', self.form_type))


class ComplexClosure(AnumExpression):
    """Сложное замыкание вида ♂∞♀."""

    def __init__(self, parts):
        self.parts = parts

    def __str__(self):
        return ''.join(str(part) for part in self.parts)

    def __eq__(self, other):
        return isinstance(other, ComplexClosure) and self.parts == other.parts

    def __hash__(self):
        return hash(('ComplexClosure', tuple(self.parts)))


class NegationExpression(AnumExpression):
    """Отрицание выражения, например -♂x."""

    def __init__(self, expression):
        self.expression = expression

    def __str__(self):
        return "-{0}".format(self.expression)

    def __eq__(self, other):
        return isinstance(other, NegationExpression) and self.expression == other.expression

    def __hash__(self):
        return hash(('NegationExpression', self.expression))


class PowerLoopExpression(AnumExpression):
    """Степень петли, например a^2."""

    def __init__(self, base, exponent):
        self.base = base
        self.exponent = exponent

    def __str__(self):
        return "{0}^{1}".format(self.base, self.exponent)

    def __eq__(self, other):
        return (isinstance(other, PowerLoopExpression) and
                self.base == other.base and
                self.exponent == other.exponent)

    def __hash__(self):
        return hash(('PowerLoopExpression', self.base, self.exponent))
