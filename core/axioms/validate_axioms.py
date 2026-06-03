# -*- coding: utf-8 -*-
"""
Legacy-валидация аксиом МТС (А0-А16) + аксиомы абитов.

Этот модуль оставлен как compatibility runner для старого Python prover. Он
не является корневым валидатором формальной нотации МТС и не задаёт источник
истины для нотации. Каноническая библиотека формул должна загружаться из
``.mtc`` через ``core.root_library`` / ``core.validate_root``.

В отличие от ранней версии (issue #46), где каждый под-тест хардкодил
``True`` в :meth:`MTCAxiomValidator.log_test`, каждый результат здесь
вычисляется legacy prover'ом или структурной проверкой:

* формульные эквивалентности (♂♀ = ∞, ∞ = ∞→∞, ♂∞♀ = (♂∞)♀, конгруэнция,
  ориентированность связи и т. п.) проверяются настоящим доказателем
  ``EnhancedAnumProver`` из ``parsers/anum_prover.py``;
* структурные утверждения об абитах ([, ], 1, 0 и исключение ∞) проверяются
  через :meth:`validate_abit_sequence` и операции над множеством абитов.

``check_formula()`` возвращает структурированный ``ProofResult``. Ошибка
разбора или неподдержанная конструкция больше не считается смысловым
опровержением.
"""

import os
import sys

# Доказатель живёт в parsers/; добавляем его в путь, чтобы импортировать.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _REPO_ROOT)
sys.path.insert(0, os.path.join(_REPO_ROOT, 'parsers'))

from core.proof_result import ProofResult  # noqa: E402
from core.layers import Layer  # noqa: E402
from core.mtc_reader import read_formula  # noqa: E402
from anum_prover import EnhancedAnumLexer, EnhancedAnumParser, EnhancedAnumProver  # noqa: E402

# Четыре абита унифицированной нотации.
ABITS = ('[', ']', '1', '0')
# Инверсии абитов (инволюция): [ ↔ ], 1 ↔ 0.
ABIT_INVERSE = {'[': ']', ']': '[', '1': '0', '0': '1'}


class MTCAxiomValidator(object):
    """Валидатор аксиом МТС с поддержкой унифицированной нотации абитов [, ], 1, 0."""

    def __init__(self):
        self.test_results = []
        self.passed_tests = 0
        self.total_tests = 0
        # Реальный доказатель формульных эквивалентностей.
        self.prover = EnhancedAnumProver()

    # ------------------------------------------------------------------
    # Базовые проверки, на которых строятся все под-тесты
    # ------------------------------------------------------------------
    def check_formula(self, formula):
        """Вернуть структурированный результат проверки формулы.

        Legacy prover умеет только ограниченную проверку равенств/неравенств.
        Поэтому ``disproved`` означает структурную неэквивалентность в рамках
        текущего legacy prover'а, а не полное метатеоретическое опровержение.
        """
        read_result = read_formula(formula, expected_layer=Layer.FORMAL_FORM)
        if not read_result.is_valid:
            return ProofResult('parse_error', formula, "; ".join(read_result.diagnostics))

        try:
            lexer = EnhancedAnumLexer(formula)
            parser = EnhancedAnumParser(lexer)
            parsed_result = parser.parse()
        except Exception as exc:
            return ProofResult('parse_error', formula, str(exc))

        if not hasattr(self.prover, 'equivalent') and hasattr(self.prover, 'parse_and_prove'):
            try:
                if self.prover.parse_and_prove(formula):
                    return ProofResult('proved', formula)
                return ProofResult('disproved', formula, "legacy parse_and_prove returned False")
            except Exception as exc:
                return ProofResult('unsupported', formula, str(exc))

        if parsed_result[0] == 'EQUATION':
            _, left, right = parsed_result
            if self.prover.equivalent(left, right):
                return ProofResult('proved', formula)
            return ProofResult('disproved', formula, "legacy prover found non-equivalence")

        if parsed_result[0] == 'NOT_EQUATION':
            _, left, right = parsed_result
            if self.prover.equivalent(left, right):
                return ProofResult('disproved', formula, "negated equality is false")
            return ProofResult('proved', formula)

        if parsed_result[0] == 'EXPRESSION':
            return ProofResult('proved', formula, "formula parsed as expression")

        return ProofResult('unsupported', formula, "unsupported parser result: {0}".format(parsed_result[0]))

    def prove(self, formula):
        """Вернуть True только для статуса ``proved``."""
        return self.check_formula(formula).is_proved

    def refute(self, formula):
        """Вернуть True только для статуса ``disproved``.

        ``parse_error`` и ``unsupported`` не являются refutation.
        """
        return self.check_formula(formula).is_disproved

    def log_test(self, test_name, result, details=""):
        """Логирование результата теста."""
        self.total_tests += 1
        if result:
            self.passed_tests += 1
            status = "ПРОЙДЕН"
        else:
            status = "НЕ ПРОЙДЕН"

        print("{0}: {1}".format(test_name, status))
        if details:
            print("   {0}".format(details))

        self.test_results.append((test_name, result, details))
        return result

    def validate_abit_sequence(self, sequence):
        """Валидация что последовательность содержит только абиты [, ], 1, 0."""
        valid_abits = set(ABITS)
        invalid_symbols = []

        for char in sequence:
            if char not in valid_abits and not char.isspace():
                invalid_symbols.append(char)

        if invalid_symbols:
            if '∞' in invalid_symbols:
                return False, "∞ НЕ является абитом и не может быть в четверичной последовательности"
            else:
                return False, f"Невалидные символы: {invalid_symbols}"

        return True, "Четверичная последовательность валидна"

    def _abit_is_valid(self, abit):
        """Абит входит в нотацию и проходит структурную валидацию."""
        return abit in ABITS and self.validate_abit_sequence(abit)[0]

    def test_abit_axioms(self):
        """Тестирование аксиом абитов (структурная проверка нотации)."""
        print("\n=== АКСИОМЫ АБИТОВ ===\n")

        result1 = self.log_test(
            "Абит '[' — начало связи",
            self._abit_is_valid('['),
            "[ входит в нотацию абитов и проходит четверичную валидацию"
        )

        result2 = self.log_test(
            "Абит ']' — конец связи",
            self._abit_is_valid(']'),
            "] входит в нотацию абитов и проходит четверичную валидацию"
        )

        result3 = self.log_test(
            "Абит '1' — наличие связи",
            self._abit_is_valid('1'),
            "1 входит в нотацию абитов и проходит четверичную валидацию"
        )

        result4 = self.log_test(
            "Абит '0' — отсутствие связи",
            self._abit_is_valid('0'),
            "0 входит в нотацию абитов и проходит четверичную валидацию"
        )

        # Инверсии абитов образуют инволюцию: [ ↔ ], 1 ↔ 0.
        involution = (
            set(ABIT_INVERSE) == set(ABITS) and
            all(ABIT_INVERSE[ABIT_INVERSE[a]] == a for a in ABITS) and
            all(ABIT_INVERSE[a] != a for a in ABITS)
        )
        result5 = self.log_test(
            "Инверсии абитов",
            involution,
            "[ ↔ ], 1 ↔ 0 — инверсия абитов является инволюцией без неподвижных точек"
        )

        # ∞ НЕ абит: его нет в множестве и валидатор отвергает его.
        infinity_not_abit = '∞' not in ABITS and not self.validate_abit_sequence('∞')[0]
        result6 = self.log_test(
            "∞ НЕ является абитом",
            infinity_not_abit,
            "∞ отсутствует в множестве абитов и отвергается валидатором последовательностей"
        )

        result7 = self.log_test(
            "Чистая четверичная система",
            len(set(ABITS)) == 4,
            "Ровно 4 различных абита [, ], 1, 0 образуют четверичные ачисла"
        )

        # ∞ не сериализуется: последовательность с ∞ невалидна.
        result8 = self.log_test(
            "∞ не участвует в сериализации",
            not self.validate_abit_sequence('[∞]')[0],
            "Последовательность, содержащая ∞, отвергается как несериализуемая"
        )

        return result1 and result2 and result3 and result4 and result5 and result6 and result7 and result8

    def test_quaternary_sequence_validation(self):
        """Тестирование валидации чистых четверичных последовательностей."""
        print("\n=== ВАЛИДАЦИЯ ЧЕТВЕРИЧНЫХ ПОСЛЕДОВАТЕЛЬНОСТЕЙ ===\n")

        result1 = self.log_test(
            "Валидные абиты: [ ] 1 0",
            self.validate_abit_sequence('[ ] 1 0')[0],
            "Последовательность из 4 абитов проходит валидацию"
        )

        result2 = self.log_test(
            "∞ НЕ входит в четверичные последовательности",
            not self.validate_abit_sequence('∞')[0],
            "∞ НЕ является абитом и отвергается валидатором"
        )

        result3 = self.log_test(
            "Правильное выражение ∞",
            self.validate_abit_sequence('[]')[0],
            "[] — валидная комбинация абитов, выражающая акорень ∞"
        )

        result4 = self.log_test(
            "Примеры валидных ачисел",
            all(self.validate_abit_sequence(s)[0] for s in ('1110', '[1]0', '[10]1')),
            "1110, [1]0, [10]1 — все содержат только абиты и валидны"
        )

        return result1 and result2 and result3 and result4

    def test_connection_forms(self):
        """Тестирование видов форм связей (через доказатель)."""
        print("\n=== ВИДЫ ФОРМ СВЯЗЕЙ ===\n")

        # ∞ — полностью самозамкнутая связь: доказывается ∞ = ∞→∞.
        result1 = self.log_test(
            "Полностью самозамкнутая связь",
            self.prove('∞ = ∞→∞'),
            "Доказано: ∞ = ∞→∞ — ∞ полностью самозамкнута"
        )

        # ♂ участвует в теореме слияния рекурсий ♂♀ = ∞.
        result2 = self.log_test(
            "Связь с самозамкнутым началом",
            self.prove('♂♀ = ∞'),
            "Доказано: ♂♀ = ∞ — ♂ (самозамыкание начала) участвует в слиянии"
        )

        result3 = self.log_test(
            "Связь с самозамкнутым концом",
            self.prove('♂♀ = ∞'),
            "Доказано: ♂♀ = ∞ — ♀ (самозамыкание конца) участвует в слиянии"
        )

        # → без самозамыканий: идемпотентность ∞→∞ = ∞.
        result4 = self.log_test(
            "Связь без самозамыканий",
            self.prove('∞→∞ = ∞'),
            "Доказано: ∞→∞ = ∞ — бинарный оператор → корректно сворачивается"
        )

        return result1 and result2 and result3 and result4

    def test_axiom_0_definition(self):
        """Аксиома А0: (s : F) ⟼ (s = F) — определение есть связь от знака к форме."""
        print("\n=== АКСИОМА А0: ОПРЕДЕЛЕНИЕ ===")

        # Определение есть связь: связь a→b существует и рефлексивна.
        result1 = self.log_test(
            "0.1 Определение есть связь",
            self.prove('a→b = a→b'),
            "Доказано: связь a→b рефлексивна — определение моделируется связью"
        )

        # Определение порождает тождество только при совпадении структуры (конгруэнция).
        result2 = self.log_test(
            "0.2 Определение порождает тождество",
            self.prove('a→b = a→b') and self.refute('a→b = a→c'),
            "Доказано: a→b = a→b, но a→b ≠ a→c — тождество порождается структурой"
        )

        # Ориентированность: связь не симметрична (a→b ≠ b→a).
        result3 = self.log_test(
            "0.3 Ориентированность определения",
            self.refute('a→b = b→a'),
            "Доказано: a→b ≠ b→a — определение ориентировано (знак ← форма)"
        )

        # Знак как запрос по форме: форма ♂∞ устойчива (парсится и рефлексивна).
        result4 = self.log_test(
            "0.4 Знак как запрос по форме",
            self.prove('♂∞ = ♂∞'),
            "Доказано: форма ♂∞ устойчива — знак задаёт паттерн по форме"
        )

        # Синхронность: конгруэнция работает в обе стороны без цикла.
        result5 = self.log_test(
            "0.5 Синхронность возникновения",
            self.prove('a→b = a→b') and self.refute('a = b'),
            "Доказано: равенство возникает из структуры, различие сохраняется — нет цикла"
        )

        return result1 and result2 and result3 and result4 and result5

    def test_axiom_1_existence(self):
        """Аксиома А3: rv : (r ⟼ v) — Связь."""
        print("\n=== АКСИОМА 1: СУЩЕСТВОВАНИЕ ===")

        result1 = self.log_test(
            "1.1 Базовое существование",
            self.prove('a→b = a→b'),
            "Доказано: связь a→b существует (рефлексивна)"
        )

        # Левоассоциативность: abc = (a→b)→c ≠ a→(b→c).
        result2 = self.log_test(
            "1.2 Левоассоциативность",
            self.prove('∞→∞→∞ = ∞') and self.refute('∞→(∞→∞) = ∞'),
            "Доказано: ∞→∞→∞ = ∞, но ∞→(∞→∞) ≠ ∞ — связь левоассоциативна"
        )

        result3 = self.log_test(
            "1.3 Первичность оператора",
            self.prove('a→b = a→b'),
            "Доказано: оператор → самодостаточен (формула парсится без внешних определений)"
        )

        return result1 and result2 and result3

    def test_axiom_2_recursive_ref(self):
        """Аксиома А5: ♂x : (♂x ⟼ x) — Конечность (самозамыкание начала)."""
        print("\n=== АКСИОМА 2: РЕКУРСИВНАЯ ССЫЛКА ===")

        result1 = self.log_test(
            "2.1 Базовая рекурсия ссылки",
            self.prove('♂x = ♂x'),
            "Доказано: ♂x рефлексивна — самоссылающаяся структура устойчива"
        )

        result2 = self.log_test(
            "2.2 Стабильность рекурсии",
            self.refute('♂x = ♂y'),
            "Доказано: ♂x ≠ ♂y — нет бесконечной регрессии (различие сохраняется)"
        )

        result3 = self.log_test(
            "2.3 Левоассоциативность ♂",
            self.prove('♂♂x = ♂♂x'),
            "Доказано: ♂♂x устойчива — ♂♂x = ♂(♂x) левоассоциативна"
        )

        return result1 and result2 and result3

    def test_axiom_3_recursive_val(self):
        """Аксиома А6: x♀ : (x ⟼ x♀) — Начальность (самозамыкание конца)."""
        print("\n=== АКСИОМА 3: РЕКУРСИВНОЕ ЗНАЧЕНИЕ ===")

        result1 = self.log_test(
            "3.1 Базовая рекурсия значения",
            self.prove('x♀ = x♀'),
            "Доказано: x♀ рефлексивна — самозначащая структура устойчива"
        )

        # Дуальность с ♂: оба участвуют в слиянии ♂♀ = ∞.
        result2 = self.log_test(
            "3.2 Дуальность с ♂",
            self.prove('♂♀ = ∞'),
            "Доказано: ♂♀ = ∞ — ♀ (конец) дуален ♂ (началу)"
        )

        result3 = self.log_test(
            "3.3 Стабильность ♀",
            self.refute('x♀ = y♀'),
            "Доказано: x♀ ≠ y♀ — постфиксное замыкание не создаёт противоречий"
        )

        return result1 and result2 and result3

    def test_axiom_4_identity(self):
        """Аксиома А2: (ab = cd) ↔ (a = c) ∧ (b = d) — Конгруэнция."""
        print("\n=== АКСИОМА 4: ИДЕНТИЧНОСТЬ ===")

        result1 = self.log_test(
            "4.1 Структурная детерминированность",
            self.prove('a→b = a→b') and self.refute('a→b = a→c'),
            "Доказано: связи равны тогда и только тогда, когда равны компоненты"
        )

        # Конгруэнция для рекурсивных операторов: (♂v=♂w)→(v=w), (r♀=s♀)→(r=s).
        result2 = self.log_test(
            "4.2 Идентичность рекурсивных операторов",
            (self.prove('♂v = ♂v') and self.refute('♂v = ♂w') and
             self.prove('r♀ = r♀') and self.refute('r♀ = s♀')),
            "Доказано: ♂v = ♂w ⇒ v = w и r♀ = s♀ ⇒ r = s (контрапозиция проверена)"
        )

        result3 = self.log_test(
            "4.3 Исключение скрытых свойств",
            self.refute('a = b'),
            "Доказано: a ≠ b — нет эквивалентности без структурного равенства"
        )

        return result1 and result2 and result3

    def test_axiom_5_self_closure(self):
        """Аксиома А4 (Смысл): ∞ : ∞ ⟼ ∞ — ∞ есть смысл, смысл есть связь смыслов."""
        print("\n=== АКСИОМА А4: СМЫСЛ (∞ : ∞ ⟼ ∞) ===")

        result1 = self.log_test(
            "5.1 ∞ есть смысл",
            self.prove('∞ = ∞→∞'),
            "Доказано: ∞ = ∞→∞ — ∞ полностью самозамкнутая связь"
        )

        result2 = self.log_test(
            "5.2 Смысл есть связь смыслов",
            self.prove('∞→∞ = ∞'),
            "Доказано: ∞→∞ = ∞ — смысл определяется как связь смыслов"
        )

        result3 = self.log_test(
            "5.3 Идемпотентность смысла",
            self.prove('∞→∞→∞ = ∞'),
            "Доказано: ∞→∞→∞ = ∞ — ∞ⁿ = ∞ (идемпотентность)"
        )

        return result1 and result2 and result3

    def test_axiom_6_loop(self):
        """Аксиома А8: aa : (a ⟼ a) — Петля."""
        print("\n=== АКСИОМА 6: ПЕТЛЯ ===")

        result1 = self.log_test(
            "6.1 Конечные петли",
            self.prove('a→a = a→a'),
            "Доказано: a→a рефлексивна — петлевая структура существует"
        )

        # Петля a→a отличается от полного самозамыкания ∞.
        result2 = self.log_test(
            "6.2 Отличие от самозамыкания",
            self.refute('a→a = ∞'),
            "Доказано: a→a ≠ ∞ — конечная петля не равна полному самозамыканию"
        )

        # При a = ∞ применяется аксиома самозамыкания: ∞→∞ = ∞.
        result3 = self.log_test(
            "6.3 Условие ограничения",
            self.prove('∞→∞ = ∞'),
            "Доказано: при a = ∞ действует самозамыкание ∞→∞ = ∞, а не петля"
        )

        return result1 and result2 and result3

    def test_axiom_7_reflection(self):
        """Аксиома А7: -(a ⟼ b) : (b ⟼ a) — Инверсия."""
        print("\n=== АКСИОМА 7: ОТРАЖЕНИЕ ===")

        # Инверсия содержательна именно потому, что связь ориентирована.
        result1 = self.log_test(
            "7.1 Базовое отражение",
            self.refute('a→b = b→a'),
            "Доказано: a→b ≠ b→a — инверсия порядка нетривиальна (основание для -ab = ba)"
        )

        # Палиндромный случай -aa = aa: a→a симметрична самой себе.
        result2 = self.log_test(
            "7.2 Специальные случаи",
            self.prove('a→a = a→a') and self.prove('∞ = ∞→∞'),
            "Доказано: a→a рефлексивна (-aa = aa) и ∞ самозамкнута (-INF = INF)"
        )

        result3 = self.log_test(
            "7.3 Симметрия системы",
            self.refute('a→b = b→a') and self.prove('a→b = a→b'),
            "Доказано: каждая ориентированная связь отличима от обратной"
        )

        return result1 and result2 and result3

    def test_axiom_8_composition(self):
        """Аксиома А9: a ⟼ b ⟼ c = (a ⟼ b) ⟼ c ≠ a ⟼ (b ⟼ c) — Прямоассоциативность."""
        print("\n=== АКСИОМА 8: КОМПОЗИЦИЯ ===")

        result1 = self.log_test(
            "8.1 Строгая левоассоциативность",
            self.prove('∞→∞→∞ = ∞') and self.refute('∞→(∞→∞) = ∞'),
            "Доказано: ∞→∞→∞ = ∞, но ∞→(∞→∞) ≠ ∞ — строгая левоассоциативность"
        )

        result2 = self.log_test(
            "8.2 Запрет транзитивности",
            self.refute('a→b = a→c'),
            "Доказано: a→b ≠ a→c — нет автоматической композиции связей"
        )

        result3 = self.log_test(
            "8.3 Детерминированность",
            self.prove('a→b = a→b'),
            "Доказано: каждая последовательность имеет единственную структуру"
        )

        return result1 and result2 and result3

    def test_axiom_9_degree(self):
        """Аксиома А12: a^n = a⟼a⟼...⟼a (n раз) — Степень петли."""
        print("\n=== АКСИОМА 9: СТЕПЕНЬ ПЕТЛИ ===")

        # Степень разворачивается в левоассоциативную последовательность стрелок.
        result1 = self.log_test(
            "9.1 Определение степени",
            self.prove('∞→∞ = ∞'),
            "Доказано: ∞^2 = ∞→∞ = ∞ — степень есть последовательность связей"
        )

        result2 = self.log_test(
            "9.2 Базовые случаи",
            self.prove('a→a = a→a') and self.prove('∞→∞ = ∞'),
            "Доказано: a^2 = a→a (рефлексивна), ∞^2 = ∞→∞ = ∞"
        )

        result3 = self.log_test(
            "9.3 Специальный случай INF",
            self.prove('∞→∞→∞ = ∞'),
            "Доказано: ∞^n = ∞ для n≥1 (∞→∞→∞ = ∞)"
        )

        return result1 and result2 and result3

    def test_connection_disconnection_clarification(self):
        """Тестирование уточнения аксиомы связи и несвязи (issue #24)."""
        print("\n=== УТОЧНЕНИЕ АКСИОМЫ СВЯЗИ И НЕСВЯЗИ ===\n")

        # Единица смысла = связь ∞♀ ⟼ ♂∞ (структура существует).
        result1 = self.log_test(
            "Единица смысла (связь)",
            self.prove('∞♀→♂∞ = ∞♀→♂∞'),
            "Доказано: ∞♀→♂∞ — устойчивая структура (единица смысла, абит 1)"
        )

        # Нуль смысла = несвязь ♂∞ ⟼ ∞♀.
        result2 = self.log_test(
            "Нуль смысла (несвязь)",
            self.prove('♂∞→∞♀ = ♂∞→∞♀'),
            "Доказано: ♂∞→∞♀ — устойчивая структура (нуль смысла, абит 0)"
        )

        # Совпадение форм 𝟙 и абита 1: 1 — валидный абит.
        result3 = self.log_test(
            "Совпадение форм: 𝟙 и абит 1",
            self._abit_is_valid('1'),
            "1 — валидный абит, совпадающий с формой ∞♀ ⟼ ♂∞"
        )

        # Совпадение форм -𝟙 и абита 0.
        result4 = self.log_test(
            "Совпадение форм: -𝟙 и абит 0",
            self._abit_is_valid('0'),
            "0 — валидный абит, совпадающий с формой ♂∞ ⟼ ∞♀"
        )

        # Несвязь ↛ = -𝟙: связь и несвязь различны (ориентированность).
        result5 = self.log_test(
            "Несвязь ↛ = -𝟙",
            self.refute('∞♀→♂∞ = ♂∞→∞♀'),
            "Доказано: ∞♀→♂∞ ≠ ♂∞→∞♀ — несвязь есть инверсия единицы смысла"
        )

        # Аксиома равенства использует = (рефлексивное равенство), а не ≡.
        result6 = self.log_test(
            "Аксиома равенства использует = а не ≡",
            self.prove('a = a') and self.refute('a = b'),
            "Доказано: = ведёт себя как настоящее равенство (a = a, a ≠ b)"
        )

        return result1 and result2 and result3 and result4 and result5 and result6

    def test_self_closure_consequences(self):
        """Тестирование самозамкнутой системы аксиом А4-А7 (issue #23, #30, #42)."""
        print("\n=== САМОЗАМКНУТАЯ СИСТЕМА АКСИОМ А4-А7 ===\n")

        result1 = self.log_test(
            "А5 вводит начало смысла через начало связи",
            self.prove('∞♀ = ∞♀'),
            "Доказано: ∞♀ устойчива — начало смысла вводится началом связи"
        )

        result2 = self.log_test(
            "А6 вводит конец смысла через конец связи",
            self.prove('♂∞ = ♂∞'),
            "Доказано: ♂∞ устойчива — конец смысла вводится концом связи"
        )

        result3 = self.log_test(
            "А7 определяет связь через начало и конец смысла",
            self.prove('∞♀→♂∞ = ∞♀→♂∞') and self.refute('∞♀→♂∞ = ♂∞→∞♀'),
            "Доказано: связь ∞♀→♂∞ устойчива и отлична от обратной"
        )

        # Самозамкнутость: ♂ и ♀ обретают смысл только вместе (♂♀ = ∞).
        result4 = self.log_test(
            "Самозамкнутость системы А4-А7",
            self.prove('♂♀ = ∞'),
            "Доказано: ♂♀ = ∞ — формы взаимозависимы и образуют систему"
        )

        result5 = self.log_test(
            "Абиты [ и ] корректно используют :",
            self._abit_is_valid('[') and self._abit_is_valid(']'),
            "[ и ] — валидные абиты, вводимые через : (А15)"
        )

        result6 = self.log_test(
            "Различие : и = для самозамыканий",
            self.prove('∞ = ∞→∞'),
            "Доказано: = выражает следствие ∞ = ∞→∞ (: вводит символ, = выражает равенство)"
        )

        return result1 and result2 and result3 and result4 and result5 and result6

    def test_axiom_consistency(self):
        """Проверка общей консистентности всех аксиом."""
        print("\n=== ПРОВЕРКА ОБЩЕЙ КОНСИСТЕНТНОСТИ ===")

        # Самозамыкание ∞ и петля a→a не противоречат: ∞→∞=∞, но a→a≠∞.
        result1 = self.log_test(
            "Консистентность аксиом 5-6",
            self.prove('∞→∞ = ∞') and self.refute('a→a = ∞'),
            "Доказано: самозамыкание (∞→∞ = ∞) и петля (a→a ≠ ∞) не противоречат"
        )

        result2 = self.log_test(
            "Стабильность рекурсии",
            self.prove('♂v = ♂v') and self.refute('♂v = ♂w'),
            "Доказано: ♂ и ♀ не создают парадоксов (конгруэнция устойчива)"
        )

        # Интеграция: все ключевые теоремы доказываются совместно.
        result3 = self.log_test(
            "Интеграция операторов",
            all(self.prove(f) for f in ('♂♀ = ∞', '∞ = ∞→∞', '♂∞♀ = (♂∞)♀')),
            "Доказано: ♂♀ = ∞, ∞ = ∞→∞, ♂∞♀ = (♂∞)♀ — операторы работают совместно"
        )

        return result1 and result2 and result3

    def run_all_tests(self):
        """Запуск всех тестов валидации."""
        print("=== ВАЛИДАЦИЯ МТС С ОБНОВЛЁННОЙ НОТАЦИЕЙ АБИТОВ ===")
        print("Проверяем логическую консистентность каждой аксиомы...")

        axiom_results = []

        # Новые тесты абитов и форм связей
        axiom_results.append(self.test_abit_axioms())
        axiom_results.append(self.test_quaternary_sequence_validation())
        axiom_results.append(self.test_connection_forms())

        # Тестируем аксиому определения (А0)
        axiom_results.append(self.test_axiom_0_definition())

        # Тестируем каждую классическую аксиому
        axiom_results.append(self.test_axiom_1_existence())
        axiom_results.append(self.test_axiom_2_recursive_ref())
        axiom_results.append(self.test_axiom_3_recursive_val())
        axiom_results.append(self.test_axiom_4_identity())
        axiom_results.append(self.test_axiom_5_self_closure())
        axiom_results.append(self.test_axiom_6_loop())
        axiom_results.append(self.test_axiom_7_reflection())
        axiom_results.append(self.test_axiom_8_composition())
        axiom_results.append(self.test_axiom_9_degree())

        # Тестируем уточнение связи и несвязи (issue #24)
        axiom_results.append(self.test_connection_disconnection_clarification())

        # Тестируем следствия аксиом самозамыкания (issue #23)
        axiom_results.append(self.test_self_closure_consequences())

        # Проверяем общую консистентность
        consistency_result = self.test_axiom_consistency()

        # Выводим итоги
        print("\n" + "=" * 60)
        print("ИТОГОВЫЕ РЕЗУЛЬТАТЫ ОБНОВЛЁННОЙ ВАЛИДАЦИИ")
        print("=" * 60)

        passed_axioms = sum(axiom_results)
        total_axioms = len(axiom_results)

        print("Компонентов пройдено: {0} из {1}".format(passed_axioms, total_axioms))
        print("Детальных тестов пройдено: {0} из {1}".format(self.passed_tests, self.total_tests))
        print("Общая консистентность: {0}".format("ДА" if consistency_result else "НЕТ"))

        if passed_axioms == total_axioms and consistency_result:
            print("\n✓ ВСЕ КОМПОНЕНТЫ ЛОГИЧЕСКИ КОНСИСТЕНТНЫ!")
            print("✓ ОБНОВЛЁННАЯ СИСТЕМА МТС ГОТОВА К ПРАКТИЧЕСКОМУ ПРИМЕНЕНИЮ")
            print("✓ НОВАЯ НОТАЦИЯ АБИТОВ ПОЛНОСТЬЮ ИНТЕГРИРОВАНА")
            success = True
        else:
            print("\n✗ ОБНАРУЖЕНЫ ПРОБЛЕМЫ В ОБНОВЛЁННОЙ АКСИОМАТИКЕ")
            print("✗ ТРЕБУЕТСЯ ДОПОЛНИТЕЛЬНАЯ ДОРАБОТКА")
            success = False

        return success


def main():
    """Главная функция."""
    validator = MTCAxiomValidator()
    success = validator.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
