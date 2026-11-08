"""Договор о схеме данных Happy: столбцы, типы, диапазоны, ключи.

Запуск: .venv/bin/python checks_hw2/test_data_contract.py

Договор:
  - Разделитель: пробелы
  - Заголовок: # id mag_r u-g g-r r-i i-z z_spec feat1 feat2 feat3 feat4 feat5
  - Столбцы: 0=id(int), 1=mag_r(float), 2-5=цвета(float), 6=z_spec(float), 7-11=feat(float)
  - id: > 0 (дубликаты возможны — галактика в нескольких каталогах)
  - mag_r: 8..31
  - цвета: -16..17
  - z_spec: 0..5
  - feat: -70..70 (стандартизованные, но C и D имеют сдвиги)
  - Строки: A=74950, B=74900, C=60315, D=74642
"""

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"

EXPECTED_ROWS = {"A": 74950, "B": 74900, "C": 60315, "D": 74642}
EXPECTED_COLS = 12
EXPECTED_HEADER = "# id mag_r u-g g-r r-i i-z z_spec feat1 feat2 feat3 feat4 feat5"


def load_raw(name):
    return np.loadtxt(RAW / f"happy_{name}.txt", comments="#")


def check_header(name):
    path = RAW / f"happy_{name}.txt"
    with open(path, encoding="utf-8") as f:
        header = f.readline().strip()
    assert header == EXPECTED_HEADER, (
        f"{name}: заголовок '{header}' != '{EXPECTED_HEADER}'"
    )


def check_row_count(name):
    data = load_raw(name)
    expected = EXPECTED_ROWS[name]
    assert len(data) == expected, (
        f"{name}: {len(data)} строк, ожидаем {expected}"
    )


def check_col_count(name):
    data = load_raw(name)
    assert data.shape[1] == EXPECTED_COLS, (
        f"{name}: {data.shape[1]} столбцов, ожидаем {EXPECTED_COLS}"
    )


def check_id_positive(name):
    data = load_raw(name)
    assert (data[:, 0] > 0).all(), f"{name}: есть id <= 0"


def check_mag_r_range(name):
    data = load_raw(name)
    assert (data[:, 1] >= 8).all(), f"{name}: есть mag_r < 8"
    assert (data[:, 1] <= 31).all(), f"{name}: есть mag_r > 31"


def check_colors_range(name):
    data = load_raw(name)
    for i, col_name in enumerate(["u-g", "g-r", "r-i", "i-z"], start=2):
        col = data[:, i]
        assert (col >= -16).all(), f"{name}: {col_name} < -16"
        assert (col <= 17).all(), f"{name}: {col_name} > 17"


def check_z_spec_range(name):
    data = load_raw(name)
    zs = data[:, 6]
    assert (zs >= 0).all(), f"{name}: есть z_spec < 0"
    assert (zs <= 5).all(), f"{name}: есть z_spec > 5"


def check_feats_range(name):
    data = load_raw(name)
    for i in range(7, 12):
        col = data[:, i]
        assert (col >= -70).all(), f"{name}: feat{i-6} < -70"
        assert (col <= 70).all(), f"{name}: feat{i-6} > 70"


def check_no_nans(name):
    data = load_raw(name)
    assert not np.isnan(data).any(), f"{name}: есть NaN"


if __name__ == "__main__":
    tests = [
        ("заголовок", check_header),
        ("число строк", check_row_count),
        ("число столбцов", check_col_count),
        ("id > 0", check_id_positive),
        ("mag_r ∈ [8, 31]", check_mag_r_range),
        ("цвета ∈ [-16, 17]", check_colors_range),
        ("z_spec ∈ [0, 5]", check_z_spec_range),
        ("feat ∈ [-70, 70]", check_feats_range),
        ("нет NaN", check_no_nans),
    ]
    passed = 0
    failed = 0
    for label, test_fn in tests:
        try:
            test_fn("A")
            test_fn("B")
            test_fn("C")
            test_fn("D")
            print(f"  PASS: {label}")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL: {label}: {e}")
            failed += 1
        except Exception as e:
            print(f"  ERROR: {label}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)