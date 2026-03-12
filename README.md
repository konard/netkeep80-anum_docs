# Метатеория связей (МТС) — Документация и инструменты

## Описание

**Метатеория связей (МТС)** — это формальная система, в которой всё есть связь. Система является онтологически замкнутой: не существует внешних сущностей, которые не могут быть выражены через связи. МТС устраняет традиционный дуализм между «объектами» и «отношениями», сводя их к единой категории — направленным связям.

Данный репозиторий содержит документацию, инструменты и реализацию протокола **ачисел** (ассоциативных чисел) на основе МТС.

## Основные концепции

### Два домена МТС

| Домен | Уровень | Символы | Назначение |
|-------|---------|---------|------------|
| **Формы связей** | Теоретический | `⟼`, `∞`, `♂`, `♀`, `¬` | Аксиомы, теоремы, формальные конструкции |
| **Сериализация** | Практический | `[`, `]`, `1`, `0` | Представление данных в виде последовательностей |

### Абиты

**Абиты** (ассоциативные биты) — четыре базовые связи вокруг акорня `∞`, формирующие четверичную систему сериализации:

| Абит | Форма | Описание |
|------|-------|----------|
| `[` | `♂∞` | Начало смысла — самозамкнутое начало акорня |
| `]` | `∞♀` | Конец смысла — самозамкнутый конец акорня |
| `1` | `♂∞ ⟼ ∞♀` | Единица смысла — связь от начала к концу |
| `0` | `∞♀ ⟼ ♂∞` | Нуль смысла — инверсия единицы |

> **Важно:** `∞` (акорень) **не является абитом**. Это мета-конструкт, выражаемый через комбинацию абитов: `[] ≡ ∞`.

### Ачисла

**Ачисло** (ассоциативное число) — конечная последовательность абитов, являющаяся уникальным идентификатором связи. Используется для кодирования данных, сериализации структур МТС и преобразования UTF-8 текста в связи.

### Система аксиом

МТС основана на 12 аксиомах (А0–А11):

| Аксиома | Формула | Описание |
|---------|---------|----------|
| А0. Определение | `(s : F) ⟼ (s = F)` | Знак как запрос по форме |
| А1. Тождественность | `x = x` | Структурная неразличимость |
| А2. Конгруэнция | `{(a = c), (b = d)} ⟼ ((a⟼b) = (c⟼d))` | Структурная прозрачность |
| А3. Связь | `rv : r ⟼ v` | Базовый конструктор |
| А4. Смысл | `∞ : ∞ ⟼ ∞` | ∞ есть смысл, смысл есть связь смыслов |
| А5. Самозамыкание начала | `♂v : ♂v ⟼ v` | Начало замкнуто на связь |
| А6. Самозамыкание конца | `r♀ : r ⟼ r♀` | Конец замкнут на связь |
| А7. Инверсия | `¬(a ⟼ b) = b ⟼ a` | Обращение направления |
| А8. Единица смысла | `1 : ♂∞ ⟼ ∞♀` | Направленная связь |
| А9. Нуль смысла | `0 : ¬1` | Инверсия единицы |
| А10. Абиты | `[ : ♂∞`, `] : ∞♀`, `1 : 1`, `0 : 0` | Четверичная система |
| А11. Левоассоциативность | `abc = (a ⟼ b) ⟼ c` | Порядок группировки |

Подробное описание аксиом и теорем: [`docs/theory/Метатеория связей.md`](docs/theory/Метатеория%20связей.md)

## Структура репозитория

```
anum_docs/
├── README.md                     # Описание проекта (этот файл)
├── LICENSE                       # Лицензия (Unlicense)
├── .gitignore
│
├── core/                         # Ядро системы
│   ├── axioms/                   # Валидация аксиом МТС
│   │   └── validate_axioms.py
│   └── notation_system.py        # Система нотации абитов
│
├── parsers/                      # Парсеры ачисел и формул МТС
│   ├── anum_prover.py            # Основной движок доказательств
│   ├── mtc_formula_prover.py     # Движок доказательств формул МТС
│   ├── complex_anum_parser.py    # Парсер сложных ачисел
│   ├── extended_anum_parser.py   # Расширенный парсер
│   └── mtc_original_abit_parser.py
│
├── converters/                   # Конвертеры между форматами нотаций
│   ├── text_to_anum.py           # UTF-8 текст → четверичное ачисло
│   ├── anum_to_text.py           # Четверичное ачисло → UTF-8 текст
│   └── ascii_unicode.py          # ASCII ↔ Unicode нотации
│
├── tests/                        # Тесты
│   ├── test_converters.py        # Тесты конвертеров
│   └── mtc_formulas.mtc          # Тестовые формулы МТС
│
├── docs/                         # Документация
│   ├── theory/                   # Теория МТС
│   │   └── Метатеория связей.md  # Чистовик теории (А0–А11)
│   ├── specs/                    # Спецификации
│   ├── research/                 # Исследования
│   ├── CONTRIBUTING.md           # Руководство по вкладу
│   ├── BEST-PRACTICES.md         # Лучшие практики
│   └── CI-CD-BEST-PRACTICES.md   # Практики CI/CD
│
├── faq/                          # Часто задаваемые вопросы
├── pics/                         # Изображения
├── pdf/                          # PDF-документы
└── archive/                      # Архив старых файлов
```

## Быстрый старт

### Требования

- Python 3.11+

### Запуск тестов

```bash
# Тесты конвертеров
python3 -m pytest tests/test_converters.py -v

# Запуск движка формул МТС
python3 parsers/mtc_formula_prover.py tests/mtc_formulas.mtc
```

### Конвертация текста

```bash
# UTF-8 текст → ачисло
python3 converters/text_to_anum.py

# Ачисло → UTF-8 текст
python3 converters/anum_to_text.py

# ASCII ↔ Unicode нотация
python3 converters/ascii_unicode.py
```

## Три нотации МТС

| Нотация | Расширение | Описание |
|---------|------------|----------|
| **Формальная** | `.mtl` | Язык запросов по форме связей (основной язык теории) |
| **Строковая** | `.astr` | UTF-8 представление как левоассоциативная цепочка |
| **Четверичная** | `.anum` | Алфавит из 4 абитов: `[`, `]`, `1`, `0` |

### Соответствие нотаций anum_docs и aprover

| anum_docs | aprover | Описание |
|-----------|---------|----------|
| `⟼` | `->` | Конструктор связи |
| `¬⟼` | `!->` | Отрицание стрелки |
| `¬` | `!` | Инверсия |
| `[` | `[` | Абит начала смысла |
| `]` | `]` | Абит конца смысла |
| `1` | `1` | Абит единицы смысла |
| `0` | `0` | Абит нуля смысла |

> **Примечание:** Символы абитов в anum_docs и aprover теперь унифицированы.

Подробнее: [netkeep80/aprover](https://github.com/netkeep80/aprover)

## Документация

- **Теория МТС** — [`docs/theory/Метатеория связей.md`](docs/theory/Метатеория%20связей.md)
- **Формальная нотация** — [`docs/specs/Формальная нотация МТС.md`](docs/specs/Формальная%20нотация%20МТС.md)
- **FAQ** — [`faq/`](faq/)
- **Руководство по вкладу** — [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md)

## CI/CD

Проект использует GitHub Actions для непрерывной интеграции:

- **Lint** — проверка кода с помощью [Ruff](https://github.com/astral-sh/ruff)
- **Tests** — запуск тестов конвертеров через pytest
- **Structure** — проверка чистоты корневой директории и наличия обязательных каталогов
- **Docs** — проверка размера файлов документации

## Лицензия

Проект распространяется под лицензией [Unlicense](LICENSE) (общественное достояние).

---

# Metatheory of Links (MTC) — Documentation and Tools

## Description

**Metatheory of Links (MTC)** is a formal system where everything is a link. The system is ontologically closed: there are no external entities that cannot be expressed through links. MTC eliminates the traditional dualism between "objects" and "relations" by reducing them to a single category — directed links.

This repository contains documentation, tools, and the implementation of the **anumber** (associative number) protocol based on MTC.

## Core Concepts

### Two Domains of MTC

| Domain | Level | Symbols | Purpose |
|--------|-------|---------|---------|
| **Link forms** | Theoretical | `⟼`, `∞`, `♂`, `♀`, `¬` | Axioms, theorems, formal constructions |
| **Serialization** | Practical | `[`, `]`, `1`, `0` | Data representation as sequences |

### Abits

**Abits** (associative bits) are four basic links around the aroot `∞`, forming a quaternary serialization system:

| Abit | Form | Description |
|------|------|-------------|
| `[` | `♂∞` | Start of meaning — self-closed start of aroot |
| `]` | `∞♀` | End of meaning — self-closed end of aroot |
| `1` | `♂∞ ⟼ ∞♀` | Unit of meaning — link from start to end |
| `0` | `∞♀ ⟼ ♂∞` | Zero of meaning — inversion of unit |

> **Important:** `∞` (aroot) **is not an abit**. It is a meta-theoretical construct expressed through a combination of abits: `[] ≡ ∞`.

### Anumbers

An **anumber** (associative number) is a finite sequence of abits serving as a unique link identifier. It is used for data encoding, MTC structure serialization, and UTF-8 text-to-link conversion.

### Axiom System

MTC is based on 12 axioms (A0–A11):

| Axiom | Formula | Description |
|-------|---------|-------------|
| A0. Definition | `(s : F) ⟼ (s = F)` | Sign as a form query |
| A1. Identity | `x = x` | Structural indistinguishability |
| A2. Congruence | `{(a = c), (b = d)} ⟼ ((a⟼b) = (c⟼d))` | Structural transparency |
| A3. Link | `rv : r ⟼ v` | Basic constructor |
| A4. Meaning | `∞ : ∞ ⟼ ∞` | ∞ is meaning, meaning is a link of meanings |
| A5. Start self-closure | `♂v : ♂v ⟼ v` | Start closed on link |
| A6. End self-closure | `r♀ : r ⟼ r♀` | End closed on link |
| A7. Inversion | `¬(a ⟼ b) = b ⟼ a` | Direction reversal |
| A8. Unit of meaning | `1 : ♂∞ ⟼ ∞♀` | Directed link |
| A9. Zero of meaning | `0 : ¬1` | Inversion of unit |
| A10. Abits | `[ : ♂∞`, `] : ∞♀`, `1 : 1`, `0 : 0` | Quaternary system |
| A11. Left-associativity | `abc = (a ⟼ b) ⟼ c` | Grouping order |

Full axiom descriptions and theorems: [`docs/theory/Метатеория связей.md`](docs/theory/Метатеория%20связей.md)

## Repository Structure

```
anum_docs/
├── README.md                     # Project description (this file)
├── LICENSE                       # License (Unlicense)
├── .gitignore
│
├── core/                         # Core system
│   ├── axioms/                   # MTC axiom validation
│   │   └── validate_axioms.py
│   └── notation_system.py        # Abit notation system
│
├── parsers/                      # Anumber and MTC formula parsers
│   ├── anum_prover.py            # Main proof engine
│   ├── mtc_formula_prover.py     # MTC formula proof engine
│   ├── complex_anum_parser.py    # Complex anumber parser
│   ├── extended_anum_parser.py   # Extended parser
│   └── mtc_original_abit_parser.py
│
├── converters/                   # Notation format converters
│   ├── text_to_anum.py           # UTF-8 text → quaternary anumber
│   ├── anum_to_text.py           # Quaternary anumber → UTF-8 text
│   └── ascii_unicode.py          # ASCII ↔ Unicode notation
│
├── tests/                        # Tests
│   ├── test_converters.py        # Converter tests
│   └── mtc_formulas.mtc          # MTC test formulas
│
├── docs/                         # Documentation
│   ├── theory/                   # MTC theory
│   │   └── Метатеория связей.md  # Final theory document (A0–A11)
│   ├── specs/                    # Specifications
│   ├── research/                 # Research
│   ├── CONTRIBUTING.md           # Contributing guide
│   ├── BEST-PRACTICES.md         # Best practices
│   └── CI-CD-BEST-PRACTICES.md   # CI/CD practices
│
├── faq/                          # Frequently asked questions
├── pics/                         # Images
├── pdf/                          # PDF documents
└── archive/                      # Archived files
```

## Quick Start

### Requirements

- Python 3.11+

### Running Tests

```bash
# Converter tests
python3 -m pytest tests/test_converters.py -v

# Run MTC formula engine
python3 parsers/mtc_formula_prover.py tests/mtc_formulas.mtc
```

### Text Conversion

```bash
# UTF-8 text → anumber
python3 converters/text_to_anum.py

# Anumber → UTF-8 text
python3 converters/anum_to_text.py

# ASCII ↔ Unicode notation
python3 converters/ascii_unicode.py
```

## Three MTC Notations

| Notation | Extension | Description |
|----------|-----------|-------------|
| **Formal** | `.mtl` | Link form query language (main theory language) |
| **String** | `.astr` | UTF-8 representation as left-associative chain |
| **Quaternary** | `.anum` | Alphabet of 4 abits: `[`, `]`, `1`, `0` |

### Notation Correspondence: anum_docs vs aprover

| anum_docs | aprover | Description |
|-----------|---------|-------------|
| `⟼` | `->` | Link constructor |
| `¬⟼` | `!->` | Arrow negation |
| `¬` | `!` | Inversion |
| `[` | `[` | Start-of-meaning abit |
| `]` | `]` | End-of-meaning abit |
| `1` | `1` | Unit-of-meaning abit |
| `0` | `0` | Zero-of-meaning abit |

> **Note:** Abit symbols in anum_docs and aprover are now unified.

More details: [netkeep80/aprover](https://github.com/netkeep80/aprover)

## Documentation

- **MTC Theory** — [`docs/theory/Метатеория связей.md`](docs/theory/Метатеория%20связей.md)
- **Formal Notation** — [`docs/specs/Формальная нотация МТС.md`](docs/specs/Формальная%20нотация%20МТС.md)
- **FAQ** — [`faq/`](faq/)
- **Contributing Guide** — [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md)

## CI/CD

The project uses GitHub Actions for continuous integration:

- **Lint** — code checking with [Ruff](https://github.com/astral-sh/ruff)
- **Tests** — running converter tests via pytest
- **Structure** — checking root directory cleanliness and required directories
- **Docs** — checking documentation file sizes

## License

The project is released under the [Unlicense](LICENSE) (public domain).
