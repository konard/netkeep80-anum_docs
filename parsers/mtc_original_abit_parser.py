# -*- coding: utf-8 -*-
"""
MTC Original Abit Parser - парсер с оригинальной нотацией абитов МТС

Использует оригинальные абиты из МТС:
♂ - абит ссылки/начальности (постфиксный оператор)
♀ - абит значения/конечности (префиксный оператор)
→ - связь (♀∞ → ∞♂)
, - несвязь (∞♂ → ♀∞)

Решение проблемы контекста: используем специальные разделители для группировки
"""

import re
import sys
import os

class MTCAbitNotation:
    """Оригинальная нотация абитов МТС"""
    
    ABITS = {
        'reference_start': '♂',    # абит ссылки/начальности (постфикс)
        'value_end': '♀',          # абит значения/конечности (префикс)
        'connection': '→',         # связь (♀∞ → ∞♂)
        'no_connection': ',',      # несвязь (∞♂ → ♀∞)
        'infinity': '∞'            # ассоциативный корень
    }
    
    # Контекстные разделители для решения проблемы с запятыми
    CONTEXT_SEPARATORS = {
        'group_start': '⟨',        # начало группы (вместо обычных скобок)
        'group_end': '⟩',          # конец группы
        'sequence_sep': '·',       # разделитель последовательности (точка по середине)
        'list_sep': ';',           # разделитель списка (вместо запятой в контексте)
        'escape_start': '⦃',       # экранирование начало
        'escape_end': '⦄'          # экранирование конец
    }
    
    def __init__(self):
        self.current = self.ABITS.copy()
        self.separators = self.CONTEXT_SEPARATORS.copy()
    
    def is_abit(self, symbol):
        """Проверка является ли символ абитом"""
        return symbol in self.current.values()
    
    def is_context_separator(self, symbol):
        """Проверка является ли символ контекстным разделителем"""
        return symbol in self.separators.values()
    
    def get_abit_type(self, symbol):
        """Получение типа абита по символу"""
        for abit_type, abit_symbol in self.current.items():
            if abit_symbol == symbol:
                return abit_type
        return None
    
    def get_separator_type(self, symbol):
        """Получение типа разделителя по символу"""
        for sep_type, sep_symbol in self.separators.items():
            if sep_symbol == symbol:
                return sep_type
        return None

class ContextualCommaResolver:
    """Решатель проблемы контекстной запятой"""
    
    def __init__(self, abit_notation):
        self.abit_notation = abit_notation
    
    def resolve_comma_context(self, text):
        """Разрешение контекста запятых в тексте"""
        
        # Стратегия 1: Экранирование абитов-запятых
        # ⦃,⦄ - абит несвязи
        # ,   - обычная запятая (разделитель)
        
        result = []
        i = 0
        
        while i < len(text):
            char = text[i]
            
            # Проверяем экранированные абиты
            if char == '⦃':
                # Ищем закрывающую скобку
                end_pos = text.find('⦄', i + 1)
                if end_pos != -1:
                    escaped_content = text[i+1:end_pos]
                    if escaped_content == ',':
                        # Это абит несвязи
                        result.append(('ABIT', ',', 'no_connection'))
                        i = end_pos + 1
                        continue
                    else:
                        # Обычный экранированный текст
                        result.append(('ESCAPED', escaped_content))
                        i = end_pos + 1
                        continue
            
            # Проверяем на абиты
            elif self.abit_notation.is_abit(char):
                if char == ',':
                    # Контекстная проверка: если запятая между абитами - это абит
                    # Если запятая между словами - это разделитель
                    is_abit_comma = self._is_abit_comma_context(text, i)
                    if is_abit_comma:
                        abit_type = self.abit_notation.get_abit_type(char)
                        result.append(('ABIT', char, abit_type))
                    else:
                        result.append(('SEPARATOR', char, 'list_separator'))
                else:
                    abit_type = self.abit_notation.get_abit_type(char)
                    result.append(('ABIT', char, abit_type))
                i += 1
            
            # Проверяем контекстные разделители
            elif self.abit_notation.is_context_separator(char):
                sep_type = self.abit_notation.get_separator_type(char)
                result.append(('CONTEXT_SEP', char, sep_type))
                i += 1
            
            # Обычные символы
            else:
                result.append(('CHAR', char))
                i += 1
        
        return result
    
    def _is_abit_comma_context(self, text, comma_pos):
        """Определение является ли запятая абитом по контексту"""
        
        # Правило: если рядом с запятой есть другие абиты - скорее всего это абит
        # Если рядом обычные символы/слова - скорее всего разделитель
        
        # Ищем ближайшие не-пробельные символы до и после запятой
        before_abit = self._find_nearest_non_space_before(text, comma_pos)
        after_abit = self._find_nearest_non_space_after(text, comma_pos)
        
        # Если с обеих сторон абиты - это абит
        if (before_abit and after_abit and 
            self.abit_notation.is_abit(before_abit) and
            self.abit_notation.is_abit(after_abit) and
            before_abit != ',' and after_abit != ','):
            return True
        
        # Если хотя бы с одной стороны абит и не находимся в группе ⟨⟩ - вероятно абит
        if (before_abit and self.abit_notation.is_abit(before_abit) and before_abit != ',') or \
           (after_abit and self.abit_notation.is_abit(after_abit) and after_abit != ','):
            # Проверяем, не находимся ли мы внутри группы
            if not self._is_inside_group(text, comma_pos):
                return True
        
        # В остальных случаях - разделитель
        return False
    
    def _find_nearest_non_space_before(self, text, pos):
        """Поиск ближайшего не-пробельного символа перед позицией"""
        i = pos - 1
        while i >= 0 and text[i].isspace():
            i -= 1
        return text[i] if i >= 0 else None
    
    def _find_nearest_non_space_after(self, text, pos):
        """Поиск ближайшего не-пробельного символа после позиции"""
        i = pos + 1
        while i < len(text) and text[i].isspace():
            i += 1
        return text[i] if i < len(text) else None
    
    def _is_inside_group(self, text, pos):
        """Проверка находится ли позиция внутри группы ⟨⟩"""
        group_start_count = 0
        for i in range(pos):
            if text[i] == '⟨':
                group_start_count += 1
            elif text[i] == '⟩':
                group_start_count -= 1
        return group_start_count > 0

class MTCOriginalToken:
    """Токен для оригинальной нотации МТС"""
    
    def __init__(self, type_, value, position=0, abit_type=None, sep_type=None):
        self.type = type_          # 'ABIT', 'CONTEXT_SEP', 'SYMBOL', 'NUMBER', etc.
        self.value = value         # actual value
        self.position = position
        self.abit_type = abit_type # тип абита если применимо
        self.sep_type = sep_type   # тип разделителя если применимо
    
    def __repr__(self):
        extras = []
        if self.abit_type:
            extras.append(f"abit={self.abit_type}")
        if self.sep_type:
            extras.append(f"sep={self.sep_type}")
        
        extra_str = f", {', '.join(extras)}" if extras else ""
        return f"Token({self.type}, '{self.value}'{extra_str})"

class MTCOriginalLexer:
    """Лексер для оригинальной нотации МТС"""
    
    def __init__(self, text):
        self.text = text
        self.position = 0
        self.current_char = self.text[0] if text else None
        self.abit_notation = MTCAbitNotation()
        self.comma_resolver = ContextualCommaResolver(self.abit_notation)
        
        # Предварительная обработка текста для разрешения контекста запятых
        self.resolved_tokens = self.comma_resolver.resolve_comma_context(text)
        self.token_index = 0
    
    def get_next_token(self):
        """Получение следующего токена из предварительно обработанного списка"""
        
        while self.token_index < len(self.resolved_tokens):
            token_data = self.resolved_tokens[self.token_index]
            self.token_index += 1
            
            token_type = token_data[0]
            token_value = token_data[1]
            
            if token_type == 'ABIT':
                abit_type = token_data[2]
                return MTCOriginalToken('ABIT', token_value, self.token_index, abit_type=abit_type)
            
            elif token_type == 'CONTEXT_SEP':
                sep_type = token_data[2] 
                return MTCOriginalToken('CONTEXT_SEP', token_value, self.token_index, sep_type=sep_type)
            
            elif token_type == 'SEPARATOR':
                sep_type = token_data[2]
                return MTCOriginalToken('SEPARATOR', token_value, self.token_index, sep_type=sep_type)
            
            elif token_type == 'ESCAPED':
                return MTCOriginalToken('ESCAPED', token_value, self.token_index)
            
            elif token_type == 'CHAR':
                char = token_value
                
                if char.isspace():
                    continue  # пропускаем пробелы
                
                elif char.isdigit():
                    # Собираем многозначное число
                    number = self._collect_number()
                    return MTCOriginalToken('NUMBER', number, self.token_index)
                
                elif char.isalpha() or char == '_':
                    # Собираем идентификатор
                    identifier = self._collect_identifier()
                    
                    # Проверяем специальные ключевые слова
                    if identifier == 'INF':
                        return MTCOriginalToken('INFINITY', identifier, self.token_index)
                    else:
                        return MTCOriginalToken('SYMBOL', identifier, self.token_index)
                
                elif char == '(':
                    return MTCOriginalToken('LPAREN', char, self.token_index)
                
                elif char == ')':
                    return MTCOriginalToken('RPAREN', char, self.token_index)
                
                elif char == '=':
                    return MTCOriginalToken('EQUALS', char, self.token_index)
                
                else:
                    return MTCOriginalToken('UNKNOWN', char, self.token_index)
        
        return MTCOriginalToken('EOF', None, self.token_index)
    
    def _collect_number(self):
        """Сбор многозначного числа"""
        number = ''
        
        # Откатываемся на один токен чтобы захватить текущую цифру
        current_pos = self.token_index - 1
        
        while (current_pos < len(self.resolved_tokens) and 
               self.resolved_tokens[current_pos][0] == 'CHAR' and
               self.resolved_tokens[current_pos][1].isdigit()):
            number += self.resolved_tokens[current_pos][1]
            current_pos += 1
        
        # Обновляем позицию
        self.token_index = current_pos
        
        return number
    
    def _collect_identifier(self):
        """Сбор идентификатора"""
        identifier = ''
        
        # Откатываемся на один токен чтобы захватить текущий символ
        current_pos = self.token_index - 1
        
        while (current_pos < len(self.resolved_tokens) and 
               self.resolved_tokens[current_pos][0] == 'CHAR' and
               (self.resolved_tokens[current_pos][1].isalnum() or 
                self.resolved_tokens[current_pos][1] == '_')):
            identifier += self.resolved_tokens[current_pos][1]
            current_pos += 1
        
        # Обновляем позицию
        self.token_index = current_pos
        
        return identifier

def test_original_mtc_notation():
    """Тестирование оригинальной нотации МТС"""
    
    print("="*60)
    print("ТЕСТИРОВАНИЕ: Оригинальная нотация абитов МТС")
    print("="*60)
    
    notation = MTCAbitNotation()
    
    print("\n📋 АБИТЫ МТС:")
    for abit_type, symbol in notation.current.items():
        print(f"  {abit_type}: '{symbol}'")
    
    print("\n📋 КОНТЕКСТНЫЕ РАЗДЕЛИТЕЛИ:")
    for sep_type, symbol in notation.separators.items():
        print(f"  {sep_type}: '{symbol}'")
    
    print("\n🧪 ТЕСТОВЫЕ ВЫРАЖЕНИЯ:")
    
    test_cases = [
        # Простые абиты
        "♂→♀",                              # простая последовательность абитов
        "♂→,→♀",                           # с запятой как абитом несвязи
        
        # Контекст с запятыми  
        "window⟨position, x, 10⟩",          # запятые как разделители в группе
        "♂→⦃,⦄→♀",                         # экранированная запятая как абит
        "array⟨length; 100; string⟩",       # альтернативный разделитель
        
        # Сложные случаи
        "♂window→⦃,⦄→position♀",           # смешанный контекст
        "data⟨♂→♀; ⦃,⦄; →⟩",               # абиты в группе
        
        # Практические примеры
        "function⟨main; void⟩",
        "variable⟨name; string⟩"
    ]
    
    for expr in test_cases:
        print(f"\n🔍 Выражение: {expr}")
        
        try:
            lexer = MTCOriginalLexer(expr)
            tokens = []
            
            while True:
                token = lexer.get_next_token()
                tokens.append(token)
                if token.type == 'EOF':
                    break
            
            print("   Токены:")
            for token in tokens[:-1]:  # исключаем EOF
                print(f"     {token}")
                
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")

def test_comma_context_resolution():
    """Тестирование разрешения контекста запятых"""
    
    print("\n" + "="*60)
    print("ТЕСТИРОВАНИЕ: Разрешение контекста запятых")
    print("="*60)
    
    notation = MTCAbitNotation()
    resolver = ContextualCommaResolver(notation)
    
    test_cases = [
        ("♂,♀", "Запятая между абитами - это абит"),
        ("a, b", "Запятая между словами - разделитель"),
        ("♂→,→♀", "Запятая в последовательности абитов - абит"),
        ("list⟨a, b, c⟩", "Запятые в группе - разделители"),
        ("⦃,⦄", "Экранированная запятая - абит"),
        ("♂ , ♀", "Запятая с пробелами между абитами - абит"),
        ("word1, word2", "Запятая между словами - разделитель")
    ]
    
    for expr, description in test_cases:
        print(f"\n🔍 '{expr}' - {description}")
        
        resolved = resolver.resolve_comma_context(expr)
        
        print("   Разрешение:")
        for item in resolved:
            if len(item) >= 3:
                print(f"     {item[0]}: '{item[1]}' ({item[2]})")
            else:
                print(f"     {item[0]}: '{item[1]}'")

def demonstrate_practical_usage():
    """Демонстрация практического использования"""
    
    print("\n" + "="*60)
    print("ДЕМОНСТРАЦИЯ: Практическое применение")
    print("="*60)
    
    print("\n🎯 РЕШЕНИЕ ПРОБЛЕМЫ КОНТЕКСТА:")
    print("1. ⦃,⦄ - экранирование для абитов несвязи")
    print("2. ⟨⟩ - группировка вместо () для избежания конфликтов")
    print("3. ; - альтернативный разделитель вместо запятой")
    print("4. Контекстный анализ для автоматического различения")
    
    print("\n🛠️ ПРИМЕРЫ ПРИМЕНЕНИЯ:")
    
    examples = [
        ("Абиты МТС", "♂→♀", "Простая связь"),
        ("Несвязь", "♂→⦃,⦄→♀", "Связь через несвязь"),
        ("Функция", "function⟨main; void⟩", "Группировка параметров"),
        ("Массив", "array⟨data; 100; int⟩", "Структура данных"),
        ("Смешанный", "♂window→⦃,⦄→position♀", "Абиты + контекст")
    ]
    
    for category, expression, description in examples:
        print(f"\n📋 {category}:")
        print(f"   Выражение: {expression}")
        print(f"   Описание: {description}")

if __name__ == "__main__":
    test_original_mtc_notation()
    test_comma_context_resolution()
    demonstrate_practical_usage()