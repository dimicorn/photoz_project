"""Проверка результата: .venv/bin/python checks/check.py. Код 0 — принято, 1 — нет.

Проверка не доверяет агенту: метрики пересчитываются по файлам предсказаний,
а photo-z каждой галактики пересчитывается независимо: деревом scipy
(cKDTree) для всех строк и прямым перебором на numpy для 200 случайных.
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
FEATS = slice(7, 12)          # feat1..feat5 в файлах Happy
ZCOL = 6                      # z_spec
errors = []


def load(name):
    return np.loadtxt(RAW / f"happy_{name}.txt", comments="#")


def metrics(zp, zs):
    dz = (zp - zs) / (1 + zs)
    med = np.median(dz)
    return {"bias": med,
            "sigma_nmad": 1.4826 * np.median(np.abs(dz - med)),
            "outlier_frac": np.mean(np.abs(dz) > 0.15)}


train = load("A")
tree = cKDTree(train[:, FEATS])
rng = np.random.default_rng(2026)
reported = {}
if (RES / "metrics.csv").is_file():
    reported = {r["sample"]: r for r in csv.DictReader(open(RES / "metrics.csv", encoding="utf-8"))}
else:
    errors.append("нет файла results/metrics.csv")

for name in ["B", "D"]:
    path = RES / f"predictions_{name}.csv"
    if not path.is_file():
        errors.append(f"нет файла results/predictions_{name}.csv")
        continue
    data = load(name)
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    if not rows or not {"id", "z_spec", "z_phot"} <= set(rows[0]):
        errors.append(f"{path.name}: нужны столбцы id, z_spec, z_phot")
        continue
    if len(rows) != len(data):
        errors.append(f"{path.name}: строк {len(rows)}, в данных {len(data)}")
        continue
    zs = np.array([float(r["z_spec"]) for r in rows])
    zp = np.array([float(r["z_phot"]) for r in rows])
    if np.max(np.abs(zs - data[:, ZCOL])) > 1e-5:
        errors.append(f"{path.name}: z_spec не совпадает с data/raw (порядок строк?)")
    # независимый пересчёт kNN: все строки — дерево scipy, 200 строк — перебор numpy
    _, nn = tree.query(data[:, FEATS], k=K)
    ref = train[nn, ZCOL].mean(axis=1)
    bad = np.abs(ref - zp) > 1e-4
    if bad.any():
        errors.append(f"{path.name}: photo-z расходится с независимым kNN в {bad.sum()} строках")
    for i in rng.choice(len(data), 200, replace=False):
        d2 = np.sum((train[:, FEATS] - data[i, FEATS]) ** 2, axis=1)
        if abs(train[np.argpartition(d2, K)[:K], ZCOL].mean() - ref[i]) > 1e-6:
            errors.append("перебор numpy и дерево scipy расходятся: проверка неисправна")
            break
    # метрики из файла метрик против пересчёта
    m = metrics(zp, zs)
    if name not in reported:
        errors.append(f"metrics.csv: нет строки для выборки {name}")
        continue
    r = reported[name]
    if int(float(r.get("n", -1))) != len(data) or int(float(r.get("k", -1))) != K:
        errors.append(f"metrics.csv, {name}: n или k не совпадают ({r.get('n')}, {r.get('k')})")
    for key, val in m.items():
        try:
            if abs(float(r[key]) - val) > 1e-4:
                errors.append(f"metrics.csv, {name}: {key}={r[key]}, пересчёт {val:.5f}")
        except (KeyError, ValueError):
            errors.append(f"metrics.csv, {name}: нет числа {key}")
    if name == "B" and not 0.01 < m["sigma_nmad"] < 0.08:
        errors.append(f"σ_NMAD на B = {m['sigma_nmad']:.4f} вне 0,01–0,08: проверьте признаки и k")

print("\n".join(errors) if errors else "принято")
sys.exit(1 if errors else 0)
