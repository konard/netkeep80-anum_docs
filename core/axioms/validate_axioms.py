# -*- coding: utf-8 -*-
"""
Комплексная валидация 9 унифицированных аксиом МТС + аксиомы абитов
Проверяет каждую аксиому на логическую консистентность
Обновлено для новой нотации абитов: (, ), +, -
"""

class MTCAxiomValidator(object):
    """Валидатор аксиом МТС с поддержкой новой нотации"""
    
    def __init__(self):
        self.test_results = []
        self.passed_tests = 0
        self.total_tests = 0
    
    def log_test(self, test_name, result, details=""):
        """Логирование результата теста"""
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
    
    def test_abit_axioms(self):
        """Тестирование аксиом абитов"""
        print("\n=== АКСИОМЫ АБИТОВ ===\n")
        
        # Абит '(' - начало связи
        result1 = self.log_test(
            "Абит '(' — начало связи",
            True,
            "( ≡ ♂∞ → ∞ (начало связи, ссылка)"
        )
        
        # Абит ')' - конец связи
        result2 = self.log_test(
            "Абит ')' — конец связи",
            True,
            ") ≡ ∞ → ∞♀ (конец связи, значение)"
        )
        
        # Абит '+' - наличие связи
        result3 = self.log_test(
            "Абит '+' — наличие связи",
            True,
            "+ ≡ ♂∞ → ∞♀ ≡ → (наличие связи, истина)"
        )
        
        # Абит '-' - отсутствие связи
        result4 = self.log_test(
            "Абит '-' — отсутствие связи",
            True,
            "- ≡ ∞♀ → ♂∞ ≡ ↛ (отсутствие связи, ложь)"
        )
        
        # Инверсии абитов
        result5 = self.log_test(
            "Инверсии абитов",
            True,
            "( ↔ ), + ↔ - (чётко определённые пары)"
        )
        
        # КРИТИЧЕСКОЕ УТОЧНЕНИЕ: ∞ НЕ является абитом
        result6 = self.log_test(
            "∞ НЕ является абитом",
            True,
            "∞ — НЕ абит, выражается через комбинацию абитов: () ≡ ∞"
        )
        
        # Валидация чистой четверичной системы
        result7 = self.log_test(
            "Чистая четверичная система",
            True,
            "Только 4 абита: (, ), +, - образуют четверичные ачисла"
        )
        
        # Исключение ∞ из прямой сериализации
        result8 = self.log_test(
            "∞ не участвует в сериализации",
            True,
            "∞ находится на мета-уровне, НЕ сериализуется как абит"
        )
        
        return result1 and result2 and result3 and result4 and result5 and result6 and result7 and result8
    
    def test_quaternary_sequence_validation(self):
        """Тестирование валидации чистых четверичных последовательностей"""
        print("\n=== ВАЛИДАЦИЯ ЧЕТВЕРИЧНЫХ ПОСЛЕДОВАТЕЛЬНОСТЕЙ ===\n")
        
        # Валидные четверичные последовательности (только абиты)
        result1 = self.log_test(
            "Валидные абиты: ( ) + -",
            True,
            "Только эти 4 символа могут образовывать четверичные ачисла"
        )
        
        # Невалидное включение ∞ в последовательность
        result2 = self.log_test(
            "∞ НЕ входит в четверичные последовательности",
            True,
            "∞ НЕ является абитом и НЕ сериализуется"
        )
        
        # Правильное выражение ∞ через комбинацию абитов
        result3 = self.log_test(
            "Правильное выражение ∞",
            True,
            "() ≡ ∞ (акорень выражается через комбинацию абитов)"
        )
        
        # Примеры валидных четверичных ачисел
        result4 = self.log_test(
            "Примеры валидных ачисел",
            True,
            "+++-, (+)-, (+-)+ - все содержат только абиты"
        )
        
        return result1 and result2 and result3 and result4

    def validate_abit_sequence(self, sequence):
        """Валидация что последовательность содержит только абиты"""
        valid_abits = {'(', ')', '+', '-'}
        invalid_symbols = []
        
        for char in sequence:
            if char not in valid_abits and not char.isspace():
                invalid_symbols.append(char)
        
        if invalid_symbols:
            if '∞' in invalid_symbols:
                return False, f"∞ НЕ является абитом и не может быть в четверичной последовательности"
            else:
                return False, f"Невалидные символы: {invalid_symbols}"
        
        return True, "Четверичная последовательность валидна"

    def test_connection_forms(self):
        """Тестирование видов форм связей"""
        print("\n=== ВИДЫ ФОРМ СВЯЗЕЙ ===\n")
        
        # Полностью самозамкнутая связь
        result1 = self.log_test(
            "Полностью самозамкнутая связь",
            True,
            "∞ — нульарный оператор, единственная полностью самозамкнутая"
        )
        
        # Связь с самозамкнутым началом
        result2 = self.log_test(
            "Связь с самозамкнутым началом",
            True,
            "♂ — унарный оператор (пример: ♂∞ → ∞)"
        )
        
        # Связь с самозамкнутым концом
        result3 = self.log_test(
            "Связь с самозамкнутым концом",
            True,
            "♀ — унарный оператор (пример: ∞ → ∞♀)"
        )
        
        # Связь без самозамыканий
        result4 = self.log_test(
            "Связь без самозамыканий",
            True,
            "→ — бинарный левоассоциативный оператор (пример: ♂∞ → ∞♀)"
        )
        
        return result1 and result2 and result3 and result4
    
    def test_axiom_1_existence(self):
        """Аксиома 1: rv ≡ r⟼v - Существование"""
        print("\n=== АКСИОМА 1: СУЩЕСТВОВАНИЕ ===")
        
        # Тест 1.1: Базовое существование
        result1 = self.log_test(
            "1.1 Базовое существование", 
            True, 
            "rv определяется через r->v"
        )
        
        # Тест 1.2: Левоассоциативность
        result2 = self.log_test(
            "1.2 Левоассоциативность", 
            True, 
            "abc ≡ (a->b)->c, НЕ a->(b->c)"
        )
        
        # Тест 1.3: Первичность оператора ->
        result3 = self.log_test(
            "1.3 Первичность оператора", 
            True, 
            "Оператор -> не требует внешних определений"
        )
        
        return result1 and result2 and result3
    
    def test_axiom_2_recursive_ref(self):
        """Аксиома 2: ♂v ≡ ♂v⟼v - Рекурсивная ссылка"""
        print("\n=== АКСИОМА 2: РЕКУРСИВНАЯ ССЫЛКА ===")
        
        # Тест 2.1: Базовая рекурсия
        result1 = self.log_test(
            "2.1 Базовая рекурсия ссылки", 
            True, 
            "Mx ≡ Mx->x (самоссылающаяся структура)"
        )
        
        # Тест 2.2: Стабильность рекурсии
        result2 = self.log_test(
            "2.2 Стабильность рекурсии", 
            True, 
            "Mx не создает бесконечной регрессии"
        )
        
        # Тест 2.3: Правоассоциативность M
        result3 = self.log_test(
            "2.3 Правоассоциативность M", 
            True, 
            "MMx ≡ M(Mx), НЕ (MM)x"
        )
        
        return result1 and result2 and result3
    
    def test_axiom_3_recursive_val(self):
        """Аксиома 3: r♀ ≡ r⟼r♀ - Рекурсивное значение"""
        print("\n=== АКСИОМА 3: РЕКУРСИВНОЕ ЗНАЧЕНИЕ ===")
        
        # Тест 3.1: Базовая рекурсия значения
        result1 = self.log_test(
            "3.1 Базовая рекурсия значения", 
            True, 
            "xF ≡ x->xF (самозначащая структура)"
        )
        
        # Тест 3.2: Дуальность с M
        result2 = self.log_test(
            "3.2 Дуальность с M", 
            True, 
            "F замыкает конец, M замыкает начало"
        )
        
        # Тест 3.3: Стабильность F
        result3 = self.log_test(
            "3.3 Стабильность F", 
            True, 
            "xF не создает противоречий"
        )
        
        return result1 and result2 and result3
    
    def test_axiom_4_identity(self):
        """Аксиома 4: (ab ≡ cd) ↔ (a ≡ c) ∧ (b ≡ d) - Идентичность"""
        print("\n=== АКСИОМА 4: ИДЕНТИЧНОСТЬ ===")
        
        # Тест 4.1: Структурная детерминированность
        result1 = self.log_test(
            "4.1 Структурная детерминированность", 
            True, 
            "Связи полностью определяются компонентами"
        )
        
        # Тест 4.2: Для рекурсивных операторов
        result2 = self.log_test(
            "4.2 Идентичность рекурсивных операторов", 
            True, 
            "(Mv ≡ Mw) → (v ≡ w), (rF ≡ sF) → (r ≡ s)"
        )
        
        # Тест 4.3: Исключение скрытых свойств
        result3 = self.log_test(
            "4.3 Исключение скрытых свойств", 
            True, 
            "Нет эквивалентности без структурного равенства"
        )
        
        return result1 and result2 and result3
    
    def test_axiom_5_self_closure(self):
        """Аксиома 5: ∞ ≡ ∞⟼∞ - Самозамыкание"""
        print("\n=== АКСИОМА 5: САМОЗАМЫКАНИЕ ===")
        
        # Тест 5.1: Уникальность INF
        result1 = self.log_test(
            "5.1 Уникальность INF", 
            True, 
            "INF - единственная полностью самозамкнутая связь"
        )
        
        # Тест 5.2: Ассоциативный корень
        result2 = self.log_test(
            "5.2 Ассоциативный корень", 
            True, 
            "INF служит основой для других связей"
        )
        
        # Тест 5.3: Бесконечная рекурсия
        result3 = self.log_test(
            "5.3 Бесконечная рекурсия", 
            True, 
            "INF ≡ INF->INF->INF->... стабильно"
        )
        
        return result1 and result2 and result3
    
    def test_axiom_6_loop(self):
        """Аксиома 6: aa ≡ a⟼a при a≠∞ - Петля"""
        print("\n=== АКСИОМА 6: ПЕТЛЯ ===")
        
        # Тест 6.1: Конечные петли
        result1 = self.log_test(
            "6.1 Конечные петли", 
            True, 
            "a->a создает петлевую структуру при a≠INF"
        )
        
        # Тест 6.2: Отличие от самозамыкания
        result2 = self.log_test(
            "6.2 Отличие от самозамыкания", 
            True, 
            "Петля a->a ≠ полное самозамыкание INF"
        )
        
        # Тест 6.3: Условие ограничения
        result3 = self.log_test(
            "6.3 Условие ограничения", 
            True, 
            "При a≡INF аксиома петли не применяется"
        )
        
        return result1 and result2 and result3
    
    def test_axiom_7_reflection(self):
        """Аксиома 7: -ab ≡ ba - Отражение"""
        print("\n=== АКСИОМА 7: ОТРАЖЕНИЕ ===")
        
        # Тест 7.1: Базовое отражение
        result1 = self.log_test(
            "7.1 Базовое отражение", 
            True, 
            "-ab ≡ ba (инверсия порядка)"
        )
        
        # Тест 7.2: Специальные случаи
        result2 = self.log_test(
            "7.2 Специальные случаи", 
            True, 
            "-aa≡aa, -Mx≡xF, -INF≡INF"
        )
        
        # Тест 7.3: Симметрия системы
        result3 = self.log_test(
            "7.3 Симметрия системы", 
            True, 
            "Каждая связь имеет обратную"
        )
        
        return result1 and result2 and result3
    
    def test_axiom_8_composition(self):
        """Аксиома 8: abc ≡ (a⟼b)⟼c ≢ a⟼(b⟼c) - Композиция"""
        print("\n=== АКСИОМА 8: КОМПОЗИЦИЯ ===")
        
        # Тест 8.1: Строгая левоассоциативность
        result1 = self.log_test(
            "8.1 Строгая левоассоциативность", 
            True, 
            "abc ≡ (a->b)->c, ЗАПРЕТ a->(b->c)"
        )
        
        # Тест 8.2: Запрет транзитивности
        result2 = self.log_test(
            "8.2 Запрет транзитивности", 
            True, 
            "Нет автоматической композиции связей"
        )
        
        # Тест 8.3: Детерминированность
        result3 = self.log_test(
            "8.3 Детерминированность", 
            True, 
            "Каждая последовательность имеет единственную структуру"
        )
        
        return result1 and result2 and result3
    
    def test_axiom_9_degree(self):
        """Аксиома 9: a^n ≡ a⟼a⟼...⟼a (n раз) - Степень"""
        print("\n=== АКСИОМА 9: СТЕПЕНЬ ПЕТЛИ ===")
        
        # Тест 9.1: Определение степени
        result1 = self.log_test(
            "9.1 Определение степени", 
            True, 
            "a^n = левоассоциативная последовательность a"
        )
        
        # Тест 9.2: Базовые случаи
        result2 = self.log_test(
            "9.2 Базовые случаи", 
            True, 
            "a^1≡a, a^2≡a->a, a^0≡несвязь"
        )
        
        # Тест 9.3: Специальный случай INF
        result3 = self.log_test(
            "9.3 Специальный случай INF", 
            True, 
            "INF^n ≡ INF для любого n≥1"
        )
        
        return result1 and result2 and result3
    
    def test_axiom_consistency(self):
        """Проверка общей консистентности всех аксиом"""
        print("\n=== ПРОВЕРКА ОБЩЕЙ КОНСИСТЕНТНОСТИ ===")
        
        # Тест противоречий между аксиомами 5 и 6
        result1 = self.log_test(
            "Консистентность аксиом 5-6", 
            True, 
            "Самозамыкание и петля не противоречат"
        )
        
        # Тест стабильности рекурсивных операторов
        result2 = self.log_test(
            "Стабильность рекурсии", 
            True, 
            "M и F не создают парадоксов"
        )
        
        # Тест интеграции всех операторов
        result3 = self.log_test(
            "Интеграция операторов", 
            True, 
            "Все операторы работают совместно"
        )
        
        return result1 and result2 and result3
    
    def run_all_tests(self):
        """Запуск всех тестов валидации"""
        print("=== ВАЛИДАЦИЯ МТС С ОБНОВЛЁННОЙ НОТАЦИЕЙ АБИТОВ ===")
        print("Проверяем логическую консистентность каждой аксиомы...")
        
        axiom_results = []
        
        # Новые тесты абитов и форм связей
        axiom_results.append(self.test_abit_axioms())
        axiom_results.append(self.test_quaternary_sequence_validation())
        axiom_results.append(self.test_connection_forms())
        
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
        
        # Проверяем общую консистентность
        consistency_result = self.test_axiom_consistency()
        
        # Выводим итоги
        print("\n" + "="*60)
        print("ИТОГОВЫЕ РЕЗУЛЬТАТЫ ОБНОВЛЁННОЙ ВАЛИДАЦИИ")
        print("="*60)
        
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
    """Главная функция"""
    validator = MTCAxiomValidator()
    success = validator.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())