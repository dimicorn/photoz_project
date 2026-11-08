"""Согласованность метрик: пересчёт из predictions → metrics.csv.

Запуск: .venv/bin/python checks_hw2/test_metrics_consistency.py

Проверяет:
  1. Метрики в metrics.csv совпадают с пересчётом из predictions
  2. sigma_nmad в диапазоне [0.01, 0.15] для всех выборок
  3. bias близок к нулю (|bias| < 0.1) для репрезентативных выборок
  4. outlier_frac = доля |dz| > 0.15
  5. n и k в metrics.csv совпадают с данными
"""

import csv
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
RES = ROOT / "results"
K = 10


def load(name):
    return np.loadtxt(RAW / f"happy_{name}.txt", comments="#")


def load_predictions(name):
    path = RES / f"predictions_{name}.csv"
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    zs = np.array([float(r["z_spec"]) for r in rows])
    zp = np.array([float(r["z_phot"]) for r in rows])
    return zs, zp


def load_metrics():
    path = RES / "metrics.csv"
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    return {r["sample"]: r for r in rows}


def compute_metrics(zp, zs):
    dz = (zp - zs) / (1 + zs)
    med = np.median(dz)
    return {
        "bias": float(med),
        "sigma_nmad": float(1.4826 * np.median(np.abs(dz - med))),
        "outlier_frac": float(np.mean(np.abs(dz) > 0.15)),
    }


# ============================================================
# ТЕСТ 1: Метрики совпадают с пересчётом из predictions
# ============================================================
def test_metrics_match_predictions():
    """Метрики в metrics.csv = пересчёт из predictions_B/C/D.csv."""
    reported = load_metrics()
    for name in ["B", "C", "D"]:
        zs, zp = load_predictions(name)
        m = compute_metrics(zp, zs)
        r = reported[name]
        for key in ["bias", "sigma_nmad", "outlier_frac"]:
            diff = abs(float(r[key]) - m[key])
            assert diff < 1e-4, (
                f"{name}: {key} = {r[key]}, пересчёт = {m[key]:.6f}, разность = {diff:.2e}"
            )


# ============================================================
# ТЕСТ 2: sigma_nmad в разумном диапазоне
# ============================================================
def test_sigma_nmad_range():
    """sigma_nmad ∈ [0.01, 0.15] для всех выборок."""
    reported = load_metrics()
    for name in ["B", "C", "D"]:
        s = float(reported[name]["sigma_nmad"])
        assert 0.01 <= s <= 0.15, (
            f"{name}: sigma_nmad = {s:.4f} вне [0.01, 0.15]"
        )


# ============================================================
# ТЕСТ 3: bias близок к нулю для репрезентативных выборок
# ============================================================
def test_bias_reasonable():
    """|bias| < 0.1 для всех выборок."""
    reported = load_metrics()
    for name in ["B", "C", "D"]:
        b = float(reported[name]["bias"])
        assert abs(b) < 0.1, (
            f"{name}: bias = {b:.6f}, модуль > 0.1"
        )


# ============================================================
# ТЕСТ 4: outlier_frac = доля |dz| > 0.15
# ============================================================
def test_outlier_frac_consistent():
    """outlier_frac = доля галактик с |dz| > 0.15."""
    reported = load_metrics()
    for name in ["B", "C", "D"]:
        zs, zp = load_predictions(name)
        dz = np.abs((zp - zs) / (1 + zs))
        expected_frac = float(np.mean(dz > 0.15))
        reported_frac = float(reported[name]["outlier_frac"])
        assert abs(expected_frac - reported_frac) < 1e-4, (
            f"{name}: outlier_frac = {reported_frac:.6f}, пересчёт = {expected_frac:.6f}"
        )


# ============================================================
# ТЕСТ 5: n и k в metrics.csv совпадают с данными
# ============================================================
def test_n_and_k():
    """n = число строк в raw, k = 10."""
    reported = load_metrics()
    for name in ["B", "C", "D"]:
        data = load(name)
        r = reported[name]
        assert int(float(r["n"])) == len(data), (
            f"{name}: n = {r['n']}, строк = {len(data)}"
        )
        assert int(float(r["k"])) == K, (
            f"{name}: k = {r['k']}, ожидаем {K}"
        )


# ============================================================
# ТЕСТ 6: Гипотеза: σ_NMAD растёт B < C < D
# ============================================================
def test_sigma_nmad_monotonic():
    """sigma_nmad(B) < sigma_nmad(C) < sigma_nmad(D)."""
    reported = load_metrics()
    s_b = float(reported["B"]["sigma_nmad"])
    s_c = float(reported["C"]["sigma_nmad"])
    s_d = float(reported["D"]["sigma_nmad"])
    assert s_b < s_c, f"B={s_b:.4f} >= C={s_c:.4f}"
    assert s_c < s_d, f"C={s_c:.4f} >= D={s_d:.4f}"


if __name__ == "__main__":
    tests = [
        ("метрики совпадают с predictions", test_metrics_match_predictions),
        ("sigma_nmad в диапазоне", test_sigma_nmad_range),
        ("bias в разумных пределах", test_bias_reasonable),
        ("outlier_frac согласован", test_outlier_frac_consistent),
        ("n и k совпадают", test_n_and_k),
        ("σ_NMAD растёт B < C < D", test_sigma_nmad_monotonic),
    ]
    passed = 0
    failed = 0
    for label, test_fn in tests:
        try:
            test_fn()
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