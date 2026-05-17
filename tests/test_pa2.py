#!/usr/bin/env python3
"""PA2 tester for sat_solver.py."""

from __future__ import annotations

import argparse
import ast
import importlib.util
import sys
from pathlib import Path


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location('submission_sat_solver', path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'Could not load module from {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fixture_paths(root: Path) -> list[Path]:
    return sorted((root / 'tests' / 'fixtures').glob('*.txt'))


def split_fixture(text: str) -> tuple[str, str]:
    marker = '=== EXPECTED ==='
    if marker not in text:
        raise ValueError('Fixture missing === EXPECTED ===')
    left, right = text.split(marker, 1)
    input_text = left.replace('=== INPUT ===', '').strip()
    expected_text = right.strip()
    return input_text, expected_text


def parse_input(text: str):
    clauses = ast.literal_eval(text)
    return clauses, {}


def expected_is_sat(text: str) -> bool:
    expected = text.strip().lower()
    if expected not in {'satisfiable: true', 'satisfiable: false'}:
        raise ValueError('Expected section must be `satisfiable: true|false`')
    return expected.endswith('true')


def run_case(module, fixture_path: Path) -> tuple[bool, str, object]:
    input_text, expected_text = split_fixture(fixture_path.read_text(encoding='utf-8'))
    clauses, assignment = parse_input(input_text)
    want_sat = expected_is_sat(expected_text)

    result = module.sat_solve(clauses, dict(assignment))
    got_sat = result is not None
    if got_sat != want_sat:
        return False, f'expected satisfiable={want_sat}, got satisfiable={got_sat}', result

    return True, 'PASS', result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--solution',
        default='sat_solver.py',
        help='Path to solution file relative to PA2 root',
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    fixtures = fixture_paths(root)
    total = len(fixtures)
    solution_path = (root / args.solution).resolve()
    if not solution_path.exists():
        print(f'TOTAL: 0/{total}')
        print(f'  - Solution file not found: {solution_path}')
        sys.exit(1)

    try:
        module = load_module(solution_path)
    except Exception as exc:
        print(f'TOTAL: 0/{total}')
        print(f'  - Could not import solution: {exc}')
        sys.exit(1)

    earned = 0
    issues = []
    for i, fixture_path in enumerate(fixtures, start=1):
        label = fixture_path.stem.replace('case_', '')
        ok, msg, result = run_case(module, fixture_path)
        if ok:
            earned += 1
            print(f'FIXTURE_{i} ({label}): 1/1 [PASS]')
        else:
            print(f'FIXTURE_{i} ({label}): 0/1 [FAIL]')
            issues.append(f'{label}: {msg}')
        print(f'  RESULT: {result!r}')

    for issue in issues:
        print(f'  - {issue}')
    print(f'TOTAL: {earned}/{total}')

    if earned < total:
        sys.exit(1)


if __name__ == '__main__':
    main()
