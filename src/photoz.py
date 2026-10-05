"""photo-z методом kNN: обучение на Happy A, предсказания на B и D."""

import csv
import sys
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
RES = ROOT / "results"
RES.mkdir(exist_ok=True)

K = 10
FEATS = slice(7, 12)  # feat1..feat5
ZCOL = 6              # z_spec


def load(name: str) -> np.ndarray:
    """Загрузить файл happy_{name}.txt."""
    return np.loadtxt(RAW / f"happy_{name}.txt", comments="#")


def predict_knn(train: np.ndarray, test: np.ndarray, k: int = K) -> np.ndarray:
    """kNN photo-z: среднее z_spec k ближайших соседей."""
    tree = cKDTree(train[:, FEATS])
    _, nn = tree.query(test[:, FEATS], k=k)
    return train[nn, ZCOL].mean(axis=1)


def metrics(zp: np.ndarray, zs: np.ndarray) -> dict:
    """bias, sigma_nmad, outlier_frac по dz."""
    dz = (zp - zs) / (1 + zs)
    med = np.median(dz)
    return {
        "bias": float(med),
        "sigma_nmad": float(1.4826 * np.median(np.abs(dz - med))),
        "outlier_frac": float(np.mean(np.abs(dz) > 0.15)),
    }


def save_predictions(name: str, data: np.ndarray, z_phot: np.ndarray) -> None:
    """Сохранить id, z_spec, z_phot."""
    path = RES / f"predictions_{name}.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "z_spec", "z_phot"])
        for i in range(len(data)):
            w.writerow([int(data[i, 0]), data[i, ZCOL], z_phot[i]])


def save_metrics(sample: str, n: int, k: int, m: dict) -> None:
    """Добавить строку в metrics.csv."""
    path = RES / "metrics.csv"
    exists = path.exists()
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["sample", "n", "k", "bias", "sigma_nmad", "outlier_frac"])
        if not exists:
            w.writeheader()
        w.writerow({"sample": sample, "n": n, "k": k, **m})


def main():
    print("Загрузка Happy A (обучение)...")
    train = load("A")
    print(f"  {len(train)} галактик")

    for name in ["B", "D"]:
        print(f"\nОбработка {name}...")
        data = load(name)
        print(f"  {len(data)} галактик")

        z_phot = predict_knn(train, data, K)
        save_predictions(name, data, z_phot)

        zs = data[:, ZCOL]
        m = metrics(z_phot, zs)
        save_metrics(name, len(data), K, m)

        print(f"  bias={m['bias']:.6f}, sigma_nmad={m['sigma_nmad']:.6f}, "
              f"outlier_frac={m['outlier_frac']:.6f}")

    print("\nГотово.")


if __name__ == "__main__":
    main()