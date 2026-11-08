"""Свойства kNN photo-z: 7 содержательных проверок корректности расчёта.

Запуск: .venv/bin/python checks_hw2/test_photoz_properties.py
        или: .venv/bin/python -m pytest checks_hw2/test_photoz_properties.py -v

Свойства:
  1. Предсказания — выпуклая комбинация z_spec (в диапазоне обучающей)
  2. Согласованность с независимым kNN (дерево scipy)
  3. z_spec в диапазоне [0, 5]
  4. Предсказание = среднее, а не медиана
  5. Порядок строк и id совпадают с raw-файлом
  6. Количество строк совпадает
  7. Правильные столбцы feat1..feat5 (slice 7:12)
"""

import csv
import sys
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
RES = ROOT / "results"
K = 10
FEATS = slice(7, 12)
ZCOL = 6


def load(name):
    return np.loadtxt(RAW / f"happy_{name}.txt", comments="#")


def predict_knn(train, test, k=K):
    tree = cKDTree(train[:, FEATS])
    _, nn = tree.query(test[:, FEATS], k=k)
    return train[nn, ZCOL].mean(axis=1)


def load_predictions(name):
    path = RES / f"predictions_{name}.csv"
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    ids = np.array([int(r["id"]) for r in rows])
    zs = np.array([float(r["z_spec"]) for r in rows])
    zp = np.array([float(r["z_phot"]) for r in rows])
    return ids, zs, zp


# ============================================================
# СВОЙСТВО 1: Предсказания — в диапазоне обучающей выборки
# Среднее k соседей всегда ∈ [min(z_spec_train), max(z_spec_train)]
# ============================================================
def test_predictions_in_range():
    """z_phot ∈ [min(z_spec_train), max(z_spec_train)] для всех галактик."""
    train = load("A")
    z_min, z_max = train[:, ZCOL].min(), train[:, ZCOL].max()
    for name in ["B", "C", "D"]:
        _, _, zp = load_predictions(name)
        assert zp.min() >= z_min - 1e-10, (
            f"{name}: z_phot.min()={zp.min():.6f} < z_spec.min()={z_min:.6f}"
        )
        assert zp.max() <= z_max + 1e-10, (
            f"{name}: z_phot.max()={zp.max():.6f} > z_spec.max()={z_max:.6f}"
        )


# ============================================================
# СВОЙСТВО 2: Согласованность с независимым kNN
# Пересчёт деревом scipy даёт те же значения (до 1e-4)
# ============================================================
def test_predictions_match_independent_knn():
    """z_phot из файла совпадает с независимым kNN до 1e-4."""
    train = load("A")
    for name in ["B", "C", "D"]:
        data = load(name)
        _, _, zp = load_predictions(name)
        ref = predict_knn(train, data, K)
        diff = np.abs(ref - zp)
        assert diff.max() < 1e-4, (
            f"{name}: max|z_phot − kNN| = {diff.max():.2e}"
        )


# ============================================================
# СВОЙСТВО 3: z_spec в проверочных выборках — в диапазоне [0, 5]
# ============================================================
def test_z_spec_range():
    """z_spec ∈ [0, 5] для всех галактик в проверочных выборках."""
    for name in ["B", "C", "D"]:
        data = load(name)
        zs = data[:, ZCOL]
        assert (zs >= 0).all(), f"{name}: есть z_spec < 0"
        assert (zs <= 5).all(), f"{name}: есть z_spec > 5"


# ============================================================
# СВОЙСТВО 4: Предсказание = среднее, а не медиана
# Замена среднего на медиану даёт отличия
# ============================================================
def test_knn_is_mean_not_median():
    """Предсказание = среднее z_spec соседей, а не медиана."""
    train = load("A")
    data = load("B")
    tree = cKDTree(train[:, FEATS])
    _, nn = tree.query(data[:, FEATS], k=K)

    z_mean = train[nn, ZCOL].mean(axis=1)
    z_median = np.median(train[nn, ZCOL], axis=1)

    _, _, zp = load_predictions("B")
    diff_mean = np.abs(z_mean - zp)
    diff_median = np.abs(z_median - zp)

    assert diff_mean.max() < 1e-4, "Среднее не совпадает с z_phot"
    assert (diff_median > 1e-6).any(), (
        "Медиана совпадает со средним — возможно, z_phot считается как медиана"
    )


# ============================================================
# СВОЙСТВО 5: Порядок строк и id совпадают с raw-файлом
# ============================================================
def test_row_order_preserved():
    """id и z_spec в predictions.csv совпадают с raw-файлом по порядку."""
    for name in ["B", "C", "D"]:
        data = load(name)
        ids, zs, _ = load_predictions(name)
        assert np.array_equal(ids, data[:, 0].astype(int)), (
            f"{name}: id не совпадает с raw"
        )
        assert np.allclose(zs, data[:, ZCOL]), (
            f"{name}: z_spec не совпадает с raw"
        )


# ============================================================
# СВОЙСТВО 6: Количество строк совпадает
# ============================================================
def test_row_count_matches():
    """Число строк predictions.csv = число строк в raw-файле."""
    for name in ["B", "C", "D"]:
        data = load(name)
        _, _, zp = load_predictions(name)
        assert len(zp) == len(data), (
            f"{name}: {len(zp)} строк в predictions, {len(data)} в raw"
        )


# ============================================================
# СВОЙСТВО 7: Правильные столбцы feat1..feat5 (slice 7:12)
# Сдвиг на один столбец (slice 6:11) даёт другой результат
# ============================================================
def test_features_columns():
    """kNN использует столбцы 7..11 (feat1..feat5), а не 6..10."""
    train = load("A")
    data = load("B")

    correct_feats = train[:, FEATS]
    _, correct_nn = cKDTree(correct_feats).query(data[:, FEATS], k=K)
    correct_zp = train[correct_nn, ZCOL].mean(axis=1)

    wrong_feats = train[:, slice(6, 11)]
    _, wrong_nn = cKDTree(wrong_feats).query(data[:, slice(6, 11)], k=K)
    wrong_zp = train[wrong_nn, ZCOL].mean(axis=1)

    _, _, zp = load_predictions("B")

    assert np.abs(correct_zp - zp).max() < 1e-4, (
        "Правильные столбцы не совпадают с z_phot"
    )
    assert np.abs(wrong_zp - zp).max() > 1e-3, (
        "Сдвинутые столбцы совпали с z_phot — ошибка не обнаружена"
    )


if __name__ == "__main__":
    tests = [
        test_predictions_in_range,
        test_predictions_match_independent_knn,
        test_z_spec_range,
        test_knn_is_mean_not_median,
        test_row_order_preserved,
        test_row_count_matches,
        test_features_columns,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS: {t.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL: {t.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"  ERROR: {t.__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)