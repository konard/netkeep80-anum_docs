# -*- coding: utf-8 -*-
"""CLI smoke tests for converters.anum_cli."""

import subprocess
import sys


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "converters.anum_cli", *args],
        check=True,
        capture_output=True,
        text=True,
    )


def test_cli_parse_outputs_quaternary_tokens(tmp_path):
    anum_file = tmp_path / "sample.anum"
    anum_file.write_text("# anum-format: quaternary\n[]\n", encoding="utf-8")

    result = run_cli("parse", str(anum_file))

    assert "format: quaternary" in result.stdout
    assert "0: [" in result.stdout
    assert "1: ]" in result.stdout


def test_cli_project_outputs_two_abit_projection(tmp_path):
    anum_file = tmp_path / "forms.anum"
    anum_file.write_text("# anum-format: quaternary\n[]\n][\n", encoding="utf-8")

    result = run_cli("project", str(anum_file))

    assert "input: []" in result.stdout
    assert "protocol_value: 0" in result.stdout
    assert "input: ][" in result.stdout
    assert "protocol_value: 1" in result.stdout


def test_cli_normalize_removes_comments_and_whitespace(tmp_path):
    anum_file = tmp_path / "spaced.anum"
    anum_file.write_text("# anum-format: quaternary\n[ 0 1 ] # comment\n", encoding="utf-8")

    result = run_cli("normalize", str(anum_file))

    assert result.stdout.strip() == "[01]"


def test_cli_realize_string_symbolic_link(tmp_path):
    anum_file = tmp_path / "link.anum"
    anum_file.write_text("# anum-format: string\na b\n", encoding="utf-8")

    result = run_cli("realize", str(anum_file))

    assert "realized: a ⟼ b" in result.stdout
