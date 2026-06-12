# -*- coding: utf-8 -*-
"""CLI for practical *.anum parser, projection and symbolic realization."""

import argparse
from pathlib import Path

from core.anum_memory import AnumMemory, Link, SymbolicAnum
from core.anum_model import AnumForm, AnumSource
from core.anum_parser import normalize_anum_form, parse_anum_file
from core.anum_projector import project_two_abit_form


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Инструменты для практической нотации *.anum"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    parse_parser = subparsers.add_parser("parse", help="Разобрать файл *.anum")
    parse_parser.add_argument("file", help="Путь к файлу *.anum")

    project_parser = subparsers.add_parser(
        "project",
        help="Показать проекцию двухабитных квадратных форм",
    )
    project_parser.add_argument("file", help="Путь к файлу *.anum")

    normalize_parser = subparsers.add_parser(
        "normalize",
        help="Удалить пробелы и комментарии из quaternary *.anum",
    )
    normalize_parser.add_argument("file", help="Путь к файлу *.anum")

    realize_parser = subparsers.add_parser(
        "realize",
        help="Материализовать строковую символическую связь",
    )
    realize_parser.add_argument("file", help="Путь к файлу *.anum")

    args = parser.parse_args(argv)

    try:
        if args.command == "parse":
            _command_parse(args.file)
        elif args.command == "project":
            _command_project(args.file)
        elif args.command == "normalize":
            _command_normalize(args.file)
        elif args.command == "realize":
            _command_realize(args.file)
        else:
            parser.error(f"Неизвестная команда: {args.command}")
    except (TypeError, ValueError) as exc:
        parser.exit(1, f"{exc}\n")

    return 0


def _read_source(path: str) -> AnumForm | AnumSource:
    text = Path(path).read_text(encoding="utf-8")
    return parse_anum_file(text)


def _command_parse(path: str) -> None:
    source = _read_source(path)
    if isinstance(source, AnumForm):
        _print_form(source)
        return

    print("format: string")
    print("text:")
    print(source.text)


def _command_project(path: str) -> None:
    source = _read_source(path)
    if not isinstance(source, AnumForm):
        raise ValueError("project поддерживает только quaternary *.anum")
    if len(source.tokens) % 2 != 0:
        raise ValueError("project ожидает чётное число квадратных абитов")

    for index in range(0, len(source.tokens), 2):
        left = source.tokens[index].abit
        right = source.tokens[index + 1].abit
        projection = project_two_abit_form(left, right)

        print(f"input: {projection.source}")
        print(f"projection: {projection.arrow_form}")
        print(f"protocol_value: {projection.protocol_value}")
        print(f"meaning: {projection.meaning}")
        if index + 2 < len(source.tokens):
            print()


def _command_normalize(path: str) -> None:
    source = _read_source(path)
    if not isinstance(source, AnumForm):
        raise ValueError("normalize поддерживает только quaternary *.anum")

    print(normalize_anum_form(source))


def _command_realize(path: str) -> None:
    source = _read_source(path)
    if not isinstance(source, AnumSource) or source.format != "string":
        raise ValueError(
            "realize в прототипе поддерживает только string *.anum вида: a b"
        )

    anum = _parse_symbolic_link(source.text)
    memory = AnumMemory()
    realized = memory.realize(anum)

    if isinstance(realized, Link):
        print(f"realized: {realized.left} ⟼ {realized.right}")
        return

    print(f"realized: {realized!r}")


def _print_form(form: AnumForm) -> None:
    print("format: quaternary")
    print("tokens:")
    for index, token in enumerate(form.tokens):
        print(f"  {index}: {token.abit.value}")


def _parse_symbolic_link(text: str) -> SymbolicAnum:
    parts = text.split()
    if len(parts) != 2:
        raise ValueError(
            "string *.anum для realize должен содержать ровно два имени"
        )
    return SymbolicAnum(parts[0], parts[1])


if __name__ == "__main__":
    raise SystemExit(main())
