# -*- coding: utf-8 -*-
"""
Extended Anum Parser for MTC with UTF-8 byte processing
Расширенный парсер ачисел для МТС с обработкой байтов UTF-8

Решает проблему конфликта нотации абитов в строковых ачислах:
- Использует специальные обозначения для абитов чтобы не конфликтовать с обычными цифрами
- Поддерживает обработку UTF-8 байтов
- Обрабатывает сложные ачисла типа window(position)(x)(10)(int)
"""

import re
import sys
import os

class AbitNotation:
    """Специальные обозначения для абитов в строковых ачислах

    КРИТИЧНОЕ ПОНИМАНИЕ:
    - Только 4 символа являются абитами: [, ], 1, 0
    - ∞ (ассоциативный корень) НЕ является абитом!
    - ∞ может быть выражен через комбинацию абитов: [] = ∞
    - ∞ находится на мета-теоретическом уровне
    """
    
    # Варианты обозначений для абитов связь/несвязь
    VARIANTS = {
        'symbols': {
            'connection': '⊤',      # ⊤ (истина, наличие связи)
            'no_connection': '⊥',   # ⊥ (ложь, отсутствие связи)
            'open_context': '[',    # [ (открытие контекста)
            'close_context': ']'    # ] (закрытие контекста)
        },
        'words': {
            'connection': 'true',
            'no_connection': 'false',
            'open_context': 'open',
            'close_context': 'close'
        },
        'compact': {
            'connection': '1',      # 1 (единица смысла)
            'no_connection': '0',   # 0 (нуль смысла)
            'open_context': '[',    # [ (начало смысла)
            'close_context': ']'    # ] (конец смысла)
        },
        'brackets': {
            'connection': '[1]',    # [1] (в квадратных скобках)
            'no_connection': '[0]', # [0] (в квадратных скобках)
            'open_context': '[',    # [ (квадратные скобки)
            'close_context': ']'    # ] (квадратные скобки)
        },
        'new_abit_notation': {
            'connection': '1',      # 1 (абит единицы смысла)
            'no_connection': '0',   # 0 (абит нуля смысла)
            'open_context': '[',    # [ (абит начала смысла)
            'close_context': ']'    # ] (абит конца смысла)
        }
    }
    
    def __init__(self, variant='new_abit_notation'):
        """Инициализация с выбранным вариантом нотации"""
        if variant not in self.VARIANTS:
            raise ValueError(f"Неизвестный вариант нотации: {variant}")
        self.current = self.VARIANTS[variant]
        self.variant_name = variant
    
    def get_abit_symbol(self, abit_type):
        """Получение символа для типа абита"""
        return self.current.get(abit_type, '?')
    
    def is_abit_symbol(self, symbol):
        """Проверка является ли символ абитом"""
        return symbol in self.current.values()
    
    def get_abit_type(self, symbol):
        """Получение типа абита по символу"""
        for abit_type, abit_symbol in self.current.items():
            if abit_symbol == symbol:
                return abit_type
        return None
    
    def validate_quaternary_sequence(self, sequence):
        """Валидация что последовательность содержит только абиты (НЕ ∞!)"""
        invalid_chars = []
        
        for char in sequence:
            if char.isspace():
                continue  # Пропускаем пробелы
            
            if char == '∞':
                invalid_chars.append(f"'{char}' (∞ НЕ является абитом!)")
            elif not self.is_abit_symbol(char):
                invalid_chars.append(f"'{char}' (не является абитом)")
        
        if invalid_chars:
            return False, f"Невалидные символы в четверичной последовательности: {', '.join(invalid_chars)}"
        
        return True, "Четверичная последовательность валидна"
    
    def get_infinity_representation(self):
        """Получение правильного представления ∞ через комбинацию абитов"""
        open_abit = self.get_abit_symbol('open_context')
        close_abit = self.get_abit_symbol('close_context')
        return f"{open_abit}{close_abit}"  # () = ∞

class UTF8ByteProcessor:
    """Обработчик UTF-8 байтов для чистой четверичной системы ачисел

    КРИТИЧНО: Использует только 4 абита: [, ], 1, 0
    ∞ НЕ сериализуется как абит, он находится на мета-уровне
    """
    
    @staticmethod
    def char_to_utf8_bytes(char):
        """Преобразование символа в байты UTF-8"""
        return char.encode('utf-8')
    
    @staticmethod
    def utf8_bytes_to_binary(utf8_bytes):
        """Преобразование UTF-8 байтов в двоичную строку"""
        binary_parts = []
        for byte in utf8_bytes:
            binary_parts.append(format(byte, '08b'))
        return ''.join(binary_parts)
    
    @staticmethod
    def binary_to_anum_sequence(binary_string, abit_notation):
        """Преобразование двоичной строки в чистую четверичную последовательность абитов"""
        connection_sym = abit_notation.get_abit_symbol('connection')
        no_connection_sym = abit_notation.get_abit_symbol('no_connection')
        
        # Критическая проверка: это должны быть абиты, НЕ ∞!
        if connection_sym == '∞' or no_connection_sym == '∞':
            raise ValueError("∞ НЕ является абитом и не может быть в четверичной последовательности!")
        
        anum_sequence = []
        for bit in binary_string:
            if bit == '1':
                anum_sequence.append(connection_sym)
            elif bit == '0':
                anum_sequence.append(no_connection_sym)
            else:
                raise ValueError(f"Неожиданный символ в двоичной строке: {bit}")
        
        return ''.join(anum_sequence)
    
    @classmethod
    def char_to_anum(cls, char, abit_notation):
        """Полное преобразование символа в ачисло"""
        utf8_bytes = cls.char_to_utf8_bytes(char)
        binary_string = cls.utf8_bytes_to_binary(utf8_bytes)
        anum_sequence = cls.binary_to_anum_sequence(binary_string, abit_notation)
        return anum_sequence
    
    @classmethod
    def string_to_anum(cls, text, abit_notation):
        """Преобразование строки в чистую четверичную последовательность ачисел"""
        anum_parts = []
        for char in text:
            char_anum = cls.char_to_anum(char, abit_notation)
            # Валидация что результат содержит только абиты
            is_valid, error_msg = abit_notation.validate_quaternary_sequence(char_anum)
            if not is_valid:
                raise ValueError(f"Невалидная четверичная последовательность для '{char}': {error_msg}")
            anum_parts.append(char_anum)
        return anum_parts
    
    @staticmethod 
    def validate_pure_quaternary_output(anum_sequence):
        """Валидация что выходная последовательность содержит только абиты"""
        valid_abits = {'1', '0', '[', ']'}
        for char in anum_sequence:
            if char not in valid_abits and not char.isspace():
                if char == '∞':
                    raise ValueError("КРИТИЧНО: ∞ НЕ является абитом и не может быть в четверичной последовательности!")
                else:
                    raise ValueError(f"Невалидный символ '{char}' в четверичной последовательности")
        return True

class ExtendedAnumToken:
    """Расширенный токен для обработки абитов и UTF-8"""
    
    def __init__(self, type_, value, position=0, abit_type=None):
        self.type = type_          # 'SYMBOL', 'ABIT', 'OPERATOR', 'PAREN', 'UTF8_CHAR', 'EOF'
        self.value = value         # actual value
        self.position = position
        self.abit_type = abit_type # тип абита если токен является абитом
    
    def __repr__(self):
        if self.abit_type:
            return f"Token({self.type}, '{self.value}', abit={self.abit_type})"
        return f"Token({self.type}, '{self.value}')"

class ExtendedAnumLexer:
    """Расширенный лексический анализатор для ачисел с поддержкой UTF-8 и специальных абитов"""
    
    def __init__(self, text, abit_notation=None):
        self.text = text
        self.position = 0
        self.current_char = self.text[0] if text else None
        self.abit_notation = abit_notation or AbitNotation('compact')
    
    def advance(self):
        """Переход к следующему символу"""
        self.position += 1
        if self.position >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.position]
    
    def peek(self, offset=1):
        """Просмотр символа на offset позиций вперед"""
        peek_pos = self.position + offset
        if peek_pos >= len(self.text):
            return None
        return self.text[peek_pos]
    
    def skip_whitespace(self):
        """Пропуск пробельных символов"""
        while self.current_char and self.current_char.isspace():
            self.advance()
    
    def read_word(self):
        """Чтение слова (для word-based абитов)"""
        result = ''
        
        while (self.current_char and 
               (self.current_char.isalpha() or self.current_char == '_')):
            result += self.current_char
            self.advance()
        
        return result
    
    def read_bracketed_abit(self):
        """Чтение абита в квадратных скобках [1] или [0]"""
        if self.current_char != '[':
            return None
        
        self.advance()  # skip '['
        
        if self.current_char in '01':
            digit = self.current_char
            self.advance()
            
            if self.current_char == ']':
                self.advance()  # skip ']'
                return f'[{digit}]'
        
        # Если не получилось прочитать правильный формат, откатываемся
        self.position -= 1
        self.current_char = self.text[self.position] if self.position < len(self.text) else None
        return None
    
    def get_next_token(self):
        """Получение следующего токена"""
        while self.current_char:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            # Проверка на абиты в квадратных скобках (для variant 'brackets')
            if self.current_char == '[' and self.abit_notation.variant_name == 'brackets':
                bracketed = self.read_bracketed_abit()
                if bracketed:
                    abit_type = self.abit_notation.get_abit_type(bracketed)
                    return ExtendedAnumToken('ABIT', bracketed, self.position, abit_type)

            # Проверка на простые символы абитов (single character)
            if self.abit_notation.is_abit_symbol(self.current_char):
                abit_type = self.abit_notation.get_abit_type(self.current_char)
                symbol = self.current_char
                self.advance()
                return ExtendedAnumToken('ABIT', symbol, self.position, abit_type)
            
            # Проверка на word-based абиты
            if self.current_char.isalpha():
                word = self.read_word()
                if self.abit_notation.is_abit_symbol(word):
                    abit_type = self.abit_notation.get_abit_type(word)
                    return ExtendedAnumToken('ABIT', word, self.position, abit_type)
                # Обычные символы и ключевые слова
                elif word == 'INF':
                    return ExtendedAnumToken('INFINITY', 'INF', self.position)
                else:
                    return ExtendedAnumToken('SYMBOL', word, self.position)
            
            # Операторы
            if self.current_char == '=':
                self.advance()
                return ExtendedAnumToken('EQUALS', '=', self.position)
            
            # Обработка минуса: стрелка '->' или простой минус
            # Примечание: '-' больше не является абитом (абит нуля теперь '0')
            if self.current_char == '-':
                next_char = self.peek()
                if next_char == '>':
                    # Это стрелка
                    self.advance()
                    self.advance()
                    return ExtendedAnumToken('ARROW', '->', self.position)
                else:
                    self.advance()
                    return ExtendedAnumToken('MINUS', '-', self.position)
            
            # Специальные операторы
            if self.current_char == 'M':
                self.advance()
                return ExtendedAnumToken('RECURSIVE_REF', 'M', self.position)
            
            if self.current_char == 'F':
                self.advance()
                return ExtendedAnumToken('RECURSIVE_VAL', 'F', self.position)
            
            # Круглые скобки — используются для приоритета, НЕ абиты
            if self.current_char == '(':
                self.advance()
                return ExtendedAnumToken('LPAREN', '(', self.position)

            if self.current_char == ')':
                self.advance()
                return ExtendedAnumToken('RPAREN', ')', self.position)
            
            # Цифры (не абиты!)
            if self.current_char.isdigit():
                digit = self.current_char
                self.advance()
                return ExtendedAnumToken('DIGIT', digit, self.position)
            
            # UTF-8 символы (не ASCII)
            if ord(self.current_char) > 127:
                utf8_char = self.current_char
                self.advance()
                return ExtendedAnumToken('UTF8_CHAR', utf8_char, self.position)
            
            # Другие символы
            if self.current_char == '_':
                self.advance()
                return ExtendedAnumToken('SYMBOL', '_', self.position)
            
            # Неизвестный символ
            raise ValueError(f"Неизвестный символ: '{self.current_char}' в позиции {self.position}")
        
        return ExtendedAnumToken('EOF', None, self.position)

def test_abit_notations():
    """Тестирование различных вариантов нотации абитов"""
    
    test_expressions = [
        "INF 1 0 [ 1 ]",      # new_abit_notation
        "INF true false open true close",  # words notation
        "INF ⊤ ⊥ [ ⊤ ]",       # symbols notation
        "INF [1] [0] [ [1] ]", # brackets notation
        "INF 1 0 [ 1 ]"       # compact notation
    ]
    
    variants = ['new_abit_notation', 'words', 'symbols', 'brackets', 'compact']
    
    for i, variant in enumerate(variants):
        print(f"\n=== Тестирование нотации '{variant}' ===")
        abit_notation = AbitNotation(variant)
        
        print("Символы абитов:")
        for abit_type, symbol in abit_notation.current.items():
            print(f"  {abit_type}: '{symbol}'")
        
        expression = test_expressions[i]
        print(f"\nТестовое выражение: {expression}")
        
        try:
            lexer = ExtendedAnumLexer(expression, abit_notation)
            tokens = []
            
            while True:
                token = lexer.get_next_token()
                tokens.append(token)
                if token.type == 'EOF':
                    break
            
            print("Токены:")
            for token in tokens[:-1]:  # исключаем EOF
                print(f"  {token}")
                
        except Exception as e:
            print(f"Ошибка: {e}")

def test_utf8_processing():
    """Тестирование обработки UTF-8"""
    
    print("\n=== Тестирование обработки UTF-8 ===")
    
    abit_notation = AbitNotation('compact')
    processor = UTF8ByteProcessor()
    
    test_chars = ['w', 'и', '🌟', '中']
    
    for char in test_chars:
        print(f"\nСимвол: '{char}'")
        
        # UTF-8 байты
        utf8_bytes = processor.char_to_utf8_bytes(char)
        print(f"UTF-8 байты: {[hex(b) for b in utf8_bytes]}")
        
        # Двоичное представление
        binary = processor.utf8_bytes_to_binary(utf8_bytes)
        print(f"Двоичное: {binary}")
        
        # Ачисло
        anum = processor.char_to_anum(char, abit_notation)
        print(f"Ачисло: {anum}")

def test_complex_string_processing():
    """Тестирование обработки сложных строк"""
    
    print("\n=== Тестирование сложных строк ===")
    
    abit_notation = AbitNotation('compact')
    processor = UTF8ByteProcessor()
    
    test_string = "window"
    print(f"Строка: '{test_string}'")
    
    anum_parts = processor.string_to_anum(test_string, abit_notation)
    
    print("Разложение по символам:")
    for i, char in enumerate(test_string):
        print(f"  '{char}' -> {anum_parts[i]}")
    
    # Полная последовательность
    full_anum = ''.join(anum_parts)
    print(f"\nПолное ачисло: {full_anum}")

if __name__ == "__main__":
    print("Extended Anum Parser for MTC - Тестирование")
    
    test_abit_notations()
    test_utf8_processing()
    test_complex_string_processing()