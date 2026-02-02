# -*- coding: utf-8 -*-
"""
MTC Notation System - Система разграничения и обработки нотаций МТС

Реализует три типа нотаций:
1. Четверичные ачисла (Quaternary Anums) - только (, ), +, -
2. Строковые ачисла (String Anums) - текст с ссылками на абиты {+}, {-}, etc.
3. Формулы МТС (MTC Formulas) - математические выражения с операторами

Использование:
py core/notation_system.py
"""

import re
import enum
from typing import Union, List, Tuple, Optional
from dataclasses import dataclass

class NotationType(enum.Enum):
    """Типы нотаций МТС"""
    QUATERNARY = "quaternary"     # Четверичные ачисла: ()+- только
    STRING = "string"             # Строковые ачисла: текст с {абит} ссылками
    FORMULA = "formula"           # Формулы МТС: выражения с операторами

@dataclass
class ParsedExpression:
    """Результат парсинга выражения"""
    content: str
    notation_type: NotationType
    abit_references: List[str]
    confidence: float = 1.0

@dataclass
class ValidationResult:
    """Результат валидации"""
    is_valid: bool
    message: str
    suggestions: Optional[List[str]] = None

class NotationDetector:
    """Детектор типов нотаций МТС"""
    
    # Индикаторы формул МТС
    FORMULA_OPERATORS = ['==', '≡', '≢', '!=', '→', '↛', '->', '!=']
    FORMULA_SYMBOLS = ['♂', '♀', '∞']
    
    # Четверичные абиты
    QUATERNARY_ABITS = set('()+- ')
    
    # Паттерн для ссылок на абиты в строках (исправлен)
    ABIT_REFERENCE_PATTERN = r'\{([+\-()∞])\}'
    
    @classmethod
    def detect_notation_type(cls, input_text: str) -> NotationType:
        """
        Автоматическое определение типа нотации
        
        Args:
            input_text: Входной текст для анализа
            
        Returns:
            NotationType: Определенный тип нотации
        """
        if not input_text or not input_text.strip():
            return NotationType.QUATERNARY
        
        text = input_text.strip()
        
        # Проверка на четверичное ачисло (только абиты)
        if cls._is_pure_quaternary(text):
            return NotationType.QUATERNARY
        
        # Проверка на формулу МТС (содержит операторы или символы формул)
        if cls._is_mtc_formula(text):
            return NotationType.FORMULA
        
        # По умолчанию - строковое ачисло
        return NotationType.STRING
    
    @classmethod
    def _is_pure_quaternary(cls, text: str) -> bool:
        """Проверка на чистое четверичное ачисло"""
        return all(char in cls.QUATERNARY_ABITS for char in text)
    
    @classmethod
    def _is_mtc_formula(cls, text: str) -> bool:
        """Проверка на формулу МТС"""
        # Проверяем наличие операторов формул
        for operator in cls.FORMULA_OPERATORS:
            if operator in text:
                return True
        
        # Проверяем наличие символов формул
        for symbol in cls.FORMULA_SYMBOLS:
            if symbol in text:
                return True
        
        return False
    
    @classmethod
    def extract_abit_references(cls, text: str) -> List[str]:
        """Извлечение ссылок на абиты из текста"""
        return re.findall(cls.ABIT_REFERENCE_PATTERN, text)
    
    @classmethod
    def get_confidence(cls, text: str, detected_type: NotationType) -> float:
        """Получение уровня уверенности в определении типа"""
        if detected_type == NotationType.QUATERNARY:
            if cls._is_pure_quaternary(text):
                return 1.0
            else:
                return 0.0
        
        elif detected_type == NotationType.FORMULA:
            operator_count = sum(1 for op in cls.FORMULA_OPERATORS if op in text)
            symbol_count = sum(1 for sym in cls.FORMULA_SYMBOLS if sym in text)
            
            if operator_count > 0 and symbol_count > 0:
                return 1.0
            elif operator_count > 0 or symbol_count > 0:
                return 0.8
            else:
                return 0.3
        
        else:  # STRING
            abit_refs = cls.extract_abit_references(text)
            if abit_refs:
                return 0.9
            else:
                return 0.7

class AbitReferenceResolver:
    """Резолвер ссылок на абиты"""
    
    # Карта ссылок на абиты - ИСПРАВЛЕНО согласно документации
    ABIT_MAP = {
        '+': '+',        # абит связи (истина)
        '-': '-',        # абит несвязи (ложь) 
        '(': '(',        # абит начала связи
        ')': ')',        # абит конца связи
        '∞': '()',       # ассоциативный корень выражается как () - КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ
    }
    
    @classmethod
    def resolve_abit_reference(cls, abit_ref: str) -> str:
        """
        Разрешение ссылки на абит
        
        Args:
            abit_ref: Ссылка на абит (например, '+', '-', '∞')
            
        Returns:
            str: Разрешенное значение абита
        """
        return cls.ABIT_MAP.get(abit_ref, '')
    
    @classmethod
    def resolve_all_references(cls, text: str) -> str:
        """
        Разрешение всех ссылок на абиты в тексте
        
        Args:
            text: Текст со ссылками на абиты {+}, {-}, etc.
            
        Returns:
            str: Текст с разрешенными ссылками
        """
        def replace_reference(match):
            abit_ref = match.group(1)
            return cls.resolve_abit_reference(abit_ref)
        
        pattern = r'\{([+\-()∞])\}'
        return re.sub(pattern, replace_reference, text)

class NotationConverter:
    """Конвертер между типами нотаций"""
    
    def __init__(self):
        self.abit_resolver = AbitReferenceResolver()
    
    def string_to_quaternary(self, string_anum: str) -> str:
        """
        Конвертация строкового ачисла в четверичное
        
        Args:
            string_anum: Строковое ачисло с возможными ссылками на абиты
            
        Returns:
            str: Четверичное представление
        """
        result = []
        i = 0
        
        while i < len(string_anum):
            if string_anum[i:i+1] == '{':
                # Найти закрывающую скобку
                end = string_anum.find('}', i)
                if end != -1:
                    abit_ref = string_anum[i+1:end]
                    resolved = self.abit_resolver.resolve_abit_reference(abit_ref)
                    result.append(resolved)
                    i = end + 1
                else:
                    # Обработать как обычный символ
                    result.append(self._char_to_quaternary(string_anum[i]))
                    i += 1
            else:
                # Обычный символ - конвертировать в четверичное
                result.append(self._char_to_quaternary(string_anum[i]))
                i += 1
        
        return ''.join(result)
    
    def _char_to_quaternary(self, char: str) -> str:
        """Конвертация символа в четверичное представление"""
        if char in '()+- ':
            return char  # Уже четверичный символ
        
        # UTF-8 -> binary -> quaternary mapping
        try:
            utf8_bytes = char.encode('utf-8')
            quaternary = ''
            for byte in utf8_bytes:
                binary = format(byte, '08b')
                for bit in binary:
                    quaternary += '+' if bit == '1' else '-'
            return f'({quaternary})'  # Группировка в скобки для разделения
        except Exception:
            return ''  # Неконвертируемый символ
    
    def quaternary_to_string(self, quaternary: str) -> str:
        """
        Конвертация четверичного ачисла в строковое представление
        
        Args:
            quaternary: Четверичное ачисло
            
        Returns:
            str: Строковое представление
        """
        # Для простоты - возвращаем как есть с объяснением
        return f'quaternary:{quaternary}'
    
    def formula_to_string(self, formula: str) -> str:
        """Конвертация формулы в строковое представление"""
        return f'formula:{formula}'

class NotationValidator:
    """Валидатор нотаций МТС"""
    
    @classmethod
    def validate_quaternary(cls, text: str) -> ValidationResult:
        """Валидация четверичного ачисла"""
        if not text:
            return ValidationResult(True, "Пустое четверичное ачисло валидно")
        
        invalid_chars = [c for c in text if c not in '()+- ']
        
        if invalid_chars:
            return ValidationResult(
                False, 
                f"Недопустимые символы в четверичном ачисле: {set(invalid_chars)}",
                ["Используйте только символы: (, ), +, -, пробел"]
            )
        
        return ValidationResult(True, "Валидное четверичное ачисло")
    
    @classmethod
    def validate_string_anum(cls, text: str) -> ValidationResult:
        """Валидация строкового ачисла"""
        # Проверка корректности ссылок на абиты
        abit_refs = NotationDetector.extract_abit_references(text)
        
        valid_refs = set(AbitReferenceResolver.ABIT_MAP.keys())
        invalid_refs = [ref for ref in abit_refs if ref not in valid_refs]
        
        if invalid_refs:
            return ValidationResult(
                False,
                f"Недопустимые ссылки на абиты: {set(invalid_refs)}",
                [f"Доступные ссылки: {list(valid_refs)}"]
            )
        
        return ValidationResult(True, "Валидное строковое ачисло")
    
    @classmethod  
    def validate_formula(cls, text: str) -> ValidationResult:
        """Валидация формулы МТС"""
        # Базовая проверка на наличие операторов
        has_operators = any(op in text for op in NotationDetector.FORMULA_OPERATORS)
        has_symbols = any(sym in text for sym in NotationDetector.FORMULA_SYMBOLS)
        
        if not (has_operators or has_symbols):
            return ValidationResult(
                False,
                "Формула МТС должна содержать операторы или символы",
                ["Используйте операторы: ==, ≡, ≢, →", "Или символы: ♂, ♀, ∞"]
            )
        
        return ValidationResult(True, "Валидная формула МТС")

class MTC_NotationAPI:
    """Унифицированный API для работы с нотациями МТС"""
    
    def __init__(self):
        self.detector = NotationDetector()
        self.converter = NotationConverter()
        self.validator = NotationValidator()
    
    def parse(self, input_data: str, notation_type: Optional[NotationType] = None) -> ParsedExpression:
        """
        Парсинг с автоопределением или явным указанием типа
        
        Args:
            input_data: Входные данные
            notation_type: Явно указанный тип нотации (опционально)
            
        Returns:
            ParsedExpression: Результат парсинга
        """
        if notation_type is None:
            notation_type = self.detector.detect_notation_type(input_data)
        
        confidence = self.detector.get_confidence(input_data, notation_type)
        abit_references = self.detector.extract_abit_references(input_data)
        
        return ParsedExpression(
            content=input_data,
            notation_type=notation_type,
            abit_references=abit_references,
            confidence=confidence
        )
    
    def convert(self, source: str, from_type: NotationType, to_type: NotationType) -> str:
        """
        Конвертация между типами нотаций
        
        Args:
            source: Исходный текст
            from_type: Исходный тип нотации
            to_type: Целевой тип нотации
            
        Returns:
            str: Конвертированный текст
        """
        if from_type == to_type:
            return source
        
        if from_type == NotationType.STRING and to_type == NotationType.QUATERNARY:
            return self.converter.string_to_quaternary(source)
        elif from_type == NotationType.QUATERNARY and to_type == NotationType.STRING:
            return self.converter.quaternary_to_string(source)
        elif from_type == NotationType.FORMULA and to_type == NotationType.STRING:
            return self.converter.formula_to_string(source)
        else:
            return f"Конвертация {from_type} -> {to_type} не реализована"
    
    def validate(self, input_data: str, expected_type: NotationType) -> ValidationResult:
        """
        Валидация соответствия ожидаемому типу
        
        Args:
            input_data: Входные данные
            expected_type: Ожидаемый тип нотации
            
        Returns:
            ValidationResult: Результат валидации
        """
        if expected_type == NotationType.QUATERNARY:
            return self.validator.validate_quaternary(input_data)
        elif expected_type == NotationType.STRING:
            return self.validator.validate_string_anum(input_data)
        elif expected_type == NotationType.FORMULA:
            return self.validator.validate_formula(input_data)
        else:
            return ValidationResult(False, f"Неизвестный тип нотации: {expected_type}")
    
    def analyze(self, input_data: str) -> dict:
        """
        Полный анализ входных данных
        
        Args:
            input_data: Входные данные
            
        Returns:
            dict: Детальный анализ
        """
        parsed = self.parse(input_data)
        validation = self.validate(input_data, parsed.notation_type)
        
        return {
            'input': input_data,
            'detected_type': parsed.notation_type.value,
            'confidence': parsed.confidence,
            'abit_references': parsed.abit_references,
            'is_valid': validation.is_valid,
            'validation_message': validation.message,
            'suggestions': validation.suggestions or []
        }

def demonstrate_notation_system():
    """Демонстрация работы системы нотаций"""
    api = MTC_NotationAPI()
    
    test_cases = [
        # Четверичные ачисла
        "++--",
        "(())",
        "+-+()",
        
        # Строковые ачисла  
        '"hello{+}world"',
        '"начало{(}данные{)}конец"',
        '"test{∞}infinity"',
        
        # Формулы МТС
        "+ == +",
        "♂♀ ≡ ∞", 
        "() == ∞",
        "♂∞♀ == (♂∞)♀",
        
        # Неоднозначные случаи
        "abc",
        "++abc--",
        "test = test"
    ]
    
    print("=== ДЕМОНСТРАЦИЯ СИСТЕМЫ НОТАЦИЙ МТС ===\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Тест {i}: {test_case}")
        analysis = api.analyze(test_case)
        
        print(f"  Тип: {analysis['detected_type']}")
        print(f"  Уверенность: {analysis['confidence']:.1f}")
        print(f"  Валидность: {'✅' if analysis['is_valid'] else '❌'}")
        
        if analysis['abit_references']:
            print(f"  Ссылки на абиты: {analysis['abit_references']}")
        
        if not analysis['is_valid']:
            print(f"  Проблема: {analysis['validation_message']}")
        
        # Пример конвертации для строковых ачисел
        if analysis['detected_type'] == 'string':
            converted = api.convert(test_case, NotationType.STRING, NotationType.QUATERNARY)
            print(f"  Четверичное представление: {converted}")
        
        print()

if __name__ == "__main__":
    demonstrate_notation_system()