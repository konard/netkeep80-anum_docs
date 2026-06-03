#!/usr/bin/env sh
# Запуск тестов МТС на Linux/macOS — эквивалент tests/test.bat (issue #46, п.6).
#
# test.bat использует команду Windows `py`; в Unix-системах её нет, поэтому
# здесь выбирается доступный интерпретатор (python3 или python).
#
# Скрипт работает из любой директории: тесты запускаются по абсолютному пути
# к каталогу tests/, чтобы поведение совпадало с test.bat.
#
# Использование:
#   sh tests/test.sh            # запустить все тесты
#   ./tests/test.sh             # после chmod +x
set -eu

# Каталог, в котором лежит этот скрипт (каталог tests/).
TESTS_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

# Выбираем доступный интерпретатор Python.
if command -v python3 >/dev/null 2>&1; then
    PY=python3
elif command -v python >/dev/null 2>&1; then
    PY=python
else
    echo "Ошибка: не найден python3 или python в PATH" >&2
    exit 1
fi

# Все аргументы скрипта пробрасываются в pytest (например, -k или имя теста).
exec "$PY" -m pytest "$TESTS_DIR" -v "$@"
