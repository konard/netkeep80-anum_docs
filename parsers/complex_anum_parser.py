# -*- coding: utf-8 -*-
"""
Complex Anum Parser for MTC - парсер сложных ачисел для МТС

Обрабатывает сложные выражения типа window(position)(x)(10)(int)
с правильным разделением между абитами и обычными символами/числами
"""

import re
from extended_anum_parser import (
    AbitNotation, UTF8ByteProcessor, 
    ExtendedAnumToken, ExtendedAnumLexer
)

class ComplexAnumExpression:
    """Базовый класс для сложных выражений ачисел"""
    pass

class StringAnum(ComplexAnumExpression):
    """Строковое ачисло (последовательность символов -> ачисло)"""
    
    def __init__(self, text, anum_sequence):
        self.text = text                    # оригинальная строка
        self.anum_sequence = anum_sequence  # последовательность абитов
    
    def __str__(self):
        return f'StringAnum("{self.text}" -> {self.anum_sequence})'

class NumberAnum(ComplexAnumExpression):
    """Числовое ачисло (число как есть, без преобразования в абиты)"""
    
    def __init__(self, number):
        self.number = number
    
    def __str__(self):
        return f'NumberAnum({self.number})'

class ContextGroup(ComplexAnumExpression):
    """Контекстная группа (expr1)(expr2)..."""
    
    def __init__(self, expressions):
        self.expressions = expressions
    
    def __str__(self):
        expr_strs = [str(expr) for expr in self.expressions]
        return f'ContextGroup([{", ".join(expr_strs)}])'

class ComplexAnumStructure(ComplexAnumExpression):
    """Сложная структура типа window(position)(x)(10)(int)"""
    
    def __init__(self, base_anum, context_groups):
        self.base_anum = base_anum          # базовое ачисло (например, "window")
        self.context_groups = context_groups # список контекстных групп
    
    def __str__(self):
        groups_str = "".join([str(group) for group in self.context_groups])
        return f'ComplexStructure({self.base_anum}{groups_str})'

class ComplexAnumLexer(ExtendedAnumLexer):
    """Расширенный лексер для сложных ачисел"""
    
    def __init__(self, text, abit_notation=None):
        super().__init__(text, abit_notation)
        self.in_parentheses = False  # флаг для отслеживания контекста в скобках
    
    def read_number(self):
        """Чтение многозначного числа"""
        result = ''
        while self.current_char and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return result
    
    def read_identifier(self):
        """Чтение идентификатора (слова)"""
        result = ''
        while (self.current_char and 
               (self.current_char.isalnum() or self.current_char == '_')):
            result += self.current_char
            self.advance()
        return result
    
    def get_next_token(self):
        """Получение следующего токена с учетом контекста"""
        
        while self.current_char:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            # Обычные скобки (НЕ абиты) - контекстные группы
            if self.current_char == '(':
                self.in_parentheses = True
                self.advance()
                return ExtendedAnumToken('LPAREN', '(', self.position)
            
            if self.current_char == ')':
                self.in_parentheses = False  
                self.advance()
                return ExtendedAnumToken('RPAREN', ')', self.position)
            
            # В скобках числа остаются числами (НЕ абиты!)
            if self.current_char.isdigit():
                number = self.read_number()
                return ExtendedAnumToken('NUMBER', number, self.position)
            
            # В скобках слова остаются идентификаторами
            if self.current_char.isalpha() or self.current_char == '_':
                word = self.read_identifier()
                
                # Специальные ключевые слова
                if word == 'INF':
                    return ExtendedAnumToken('INFINITY', 'INF', self.position)
                
                # Проверка на word-based абиты (только вне скобок)
                if not self.in_parentheses and self.abit_notation.is_abit_symbol(word):
                    abit_type = self.abit_notation.get_abit_type(word)
                    return ExtendedAnumToken('ABIT', word, self.position, abit_type)
                
                # Обычный идентификатор
                return ExtendedAnumToken('IDENTIFIER', word, self.position)
            
            # Абиты (символьные) - только вне скобок для + и ~
            if (not self.in_parentheses and 
                self.current_char in '+~' and 
                self.abit_notation.is_abit_symbol(self.current_char)):
                abit_type = self.abit_notation.get_abit_type(self.current_char)
                symbol = self.current_char
                self.advance()
                return ExtendedAnumToken('ABIT', symbol, self.position, abit_type)
            
            # Остальные символы - используем родительский метод
            # Но игнорируем проверку на абиты в скобках
            return super().get_next_token()
        
        return ExtendedAnumToken('EOF', None, self.position)

class ComplexAnumParser:
    """Парсер для сложных выражений ачисел"""
    
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
        self.utf8_processor = UTF8ByteProcessor()
    
    def eat(self, token_type):
        """Потребление токена указанного типа"""
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            raise ValueError(f"Ожидался {token_type}, получен {self.current_token.type}")
    
    def parse_parentheses_group(self):
        """Парсинг группы в скобках (expr)"""
        self.eat('LPAREN')
        
        expressions = []
        
        # Парсим содержимое скобок
        while self.current_token.type != 'RPAREN' and self.current_token.type != 'EOF':
            
            if self.current_token.type == 'IDENTIFIER':
                # Строка -> строковое ачисло
                text = self.current_token.value
                anum_seq = self.utf8_processor.string_to_anum(text, self.lexer.abit_notation)
                anum_str = ''.join(anum_seq)
                expressions.append(StringAnum(text, anum_str))
                self.eat('IDENTIFIER')
            
            elif self.current_token.type == 'NUMBER':
                # Число остается числом
                number = int(self.current_token.value)
                expressions.append(NumberAnum(number))
                self.eat('NUMBER')
            
            elif self.current_token.type == 'SYMBOL':
                # Одиночный символ -> строковое ачисло
                char = self.current_token.value
                anum_seq = self.utf8_processor.char_to_anum(char, self.lexer.abit_notation)
                expressions.append(StringAnum(char, anum_seq))
                self.eat('SYMBOL')
            
            else:
                raise ValueError(f"Неожиданный токен в скобках: {self.current_token.type}")
        
        self.eat('RPAREN')
        return ContextGroup(expressions)
    
    def parse_base_expression(self):
        """Парсинг базового выражения"""
        
        if self.current_token.type == 'IDENTIFIER':
            # Строка -> строковое ачисло  
            text = self.current_token.value
            anum_seq = self.utf8_processor.string_to_anum(text, self.lexer.abit_notation)
            anum_str = ''.join(anum_seq)
            self.eat('IDENTIFIER')
            return StringAnum(text, anum_str)
        
        elif self.current_token.type == 'SYMBOL':
            # Одиночный символ -> строковое ачисло
            char = self.current_token.value
            anum_seq = self.utf8_processor.char_to_anum(char, self.lexer.abit_notation)
            self.eat('SYMBOL')
            return StringAnum(char, anum_seq)
        
        elif self.current_token.type == 'NUMBER':
            # Число (вне скобок) -> числовое ачисло
            number = int(self.current_token.value)
            self.eat('NUMBER')
            return NumberAnum(number)
        
        else:
            raise ValueError(f"Неожиданный токен: {self.current_token.type}")
    
    def parse_complex_structure(self):
        """Парсинг сложной структуры"""
        
        # Парсим базовое выражение
        base = self.parse_base_expression()
        
        # Парсим последующие контекстные группы
        context_groups = []
        
        while self.current_token.type == 'LPAREN':
            group = self.parse_parentheses_group()
            context_groups.append(group)
        
        if context_groups:
            return ComplexAnumStructure(base, context_groups)
        else:
            return base
    
    def parse(self):
        """Основная функция парсинга"""
        result = self.parse_complex_structure()
        
        if self.current_token.type != 'EOF':
            raise ValueError("Неожиданные символы в конце выражения")
        
        return result

def test_complex_parsing():
    """Тестирование парсинга сложных выражений"""
    
    print("=== Тестирование парсинга сложных ачисел ===\n")
    
    abit_notation = AbitNotation('compact')
    
    test_cases = [
        "window",
        "window(position)",
        "window(position)(x)",
        "window(position)(x)(10)",
        "window(position)(x)(10)(int)",
        "int(10)",
        "boolean(true)",
        "x",
        "42"
    ]
    
    for expression in test_cases:
        print(f"Выражение: {expression}")
        
        try:
            lexer = ComplexAnumLexer(expression, abit_notation)
            parser = ComplexAnumParser(lexer)
            result = parser.parse()
            
            print(f"Результат: {result}")
            
            # Дополнительная информация для сложных структур
            if isinstance(result, ComplexAnumStructure):
                print(f"  Базовое ачисло: {result.base_anum}")
                for i, group in enumerate(result.context_groups):
                    print(f"  Группа {i+1}: {group}")
            
        except Exception as e:
            print(f"Ошибка: {e}")
        
        print()

def demonstrate_abit_conflict_resolution():
    """Демонстрация решения конфликта абитов"""
    
    print("=== Демонстрация решения конфликта нотации абитов ===\n")
    
    # Проблематичное выражение с конфликтом
    problematic = "10"  # Это должно быть число десять, НЕ два абита
    
    print(f"Выражение: '{problematic}'")
    print("Проблема: Если использовать 1 и 0 как абиты, то это стало бы 'связь + несвязь'")
    print("Решение: Используем + и ~ для абитов, а 1 и 0 остаются цифрами\n")
    
    abit_notation = AbitNotation('compact')
    lexer = ComplexAnumLexer(problematic, abit_notation)
    parser = ComplexAnumParser(lexer)
    result = parser.parse()
    
    print(f"Результат парсинга: {result}")
    print(f"Тип: {type(result).__name__}")
    
    if isinstance(result, NumberAnum):
        print(f"Число: {result.number}")
    
    print("\n" + "="*50)
    
    # Пример с настоящими абитами
    abit_example = "++~+"
    print(f"\nАбиты: '{abit_example}'")
    print("Это последовательность: связь + связь + несвязь + связь")
    
    lexer = ComplexAnumLexer(abit_example, abit_notation)
    
    tokens = []
    while True:
        token = lexer.get_next_token()
        tokens.append(token)
        if token.type == 'EOF':
            break
    
    print("Токены:")
    for token in tokens[:-1]:  # исключаем EOF
        if token.abit_type:
            print(f"  {token.value} -> {token.abit_type}")

if __name__ == "__main__":
    test_complex_parsing()
    demonstrate_abit_conflict_resolution()