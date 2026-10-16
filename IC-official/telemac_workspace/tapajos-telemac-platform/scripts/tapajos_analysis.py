"""Daily station comparison; positive lag means downstream station is delayed."""

import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd


def lag_correlation(upstream, downstream, max_lag=30, min_pairs=20):
    a = upstream.copy()
    b = downstream.copy()
    if not isinstance(a.index, pd.DatetimeIndex) or not isinstance(
        b.index, pd.DatetimeIndex
    ):
        raise ValueError("Índice temporal obrigatório")
    if a.index.has_duplicates or b.index.has_duplicates:
        raise ValueError("Datas duplicadas")
    a = a.sort_index().resample("D").mean()
    b = b.sort_index().resample("D").mean()
    candidates = []
    for lag in range(-max_lag, max_lag + 1):
        shifted = b.copy()
        shifted.index -= pd.Timedelta(days=lag)
        paired = pd.concat(
            [a.rename("a"), shifted.rename("b")], axis=1, sort=True
        ).dropna()
        if len(paired) < min_pairs or paired.a.std() == 0 or paired.b.std() == 0:
            continue
        candidates.append(
            {
                "lag_days": lag,
                "correlation": float(paired.a.corr(paired.b)),
                "pairs": len(paired),
            }
        )
    if not candidates:
        raise ValueError("Sobreposição insuficiente ou série constante")
    # Pairwise Pearson avoids bias from zero filling gaps and differing overlap lengths.
    return {
        "best": max(candidates, key=lambda v: v["correlation"]),
        "lags": candidates,
        "interpretation": "lag > 0: jusante atrasada; associação não prova tempo de viagem; avaliar tendência/sazonalidade",
    }


def permanence(values):
    q = np.sort(np.asarray(values, dtype=float)[np.isfinite(values)])[::-1]
    if len(q) == 0:
        raise ValueError("Série sem dados")
    return np.arange(1, len(q) + 1) / (len(q) + 1) * 100, q


def report(up_csv, down_csv, out):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)

    def load(p):
        d = pd.read_csv(p)
        return pd.Series(
            d.value.to_numpy(float), index=pd.to_datetime(d.date, utc=True)
        )

    a, b = load(up_csv), load(down_csv)
    result = lag_correlation(a, b)
    fig, ax = plt.subplots(1, 2, figsize=(10, 4), layout="constrained")
    for series, label in [(a, "Montante"), (b, "Jusante")]:
        x, y = permanence(series.values)
        ax[0].plot(x, y, label=label)
    ax[0].set(xlabel="Permanência [%]", ylabel="Vazão [m³/s]")
    ax[0].legend()
    ax[0].grid(alpha=0.2)
    ax[1].plot(
        [v["lag_days"] for v in result["lags"]],
        [v["correlation"] for v in result["lags"]],
    )
    ax[1].set(xlabel="Atraso de jusante [dias]", ylabel="Correlação de Pearson")
    ax[1].grid(alpha=0.2)
    fig.savefig(out / "analysis.png", dpi=160)
    plt.close(fig)
    (out / "analysis.json").write_text(json.dumps(result, indent=2))
    best = result["best"]
    (out / "report.html").write_text(
        f'<!doctype html><meta charset="utf-8"><title>Análise hidrológica</title><h1>Comparação de séries de vazão</h1><p>Lag: {best["lag_days"]} dias; r = {best["correlation"]:.4f}; pares = {best["pairs"]}.</p><p>{result["interpretation"]}</p><img src="analysis.png" width="1000">'
    )
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("upstream")
    p.add_argument("downstream")
    p.add_argument("--out", default="reports/hydrology")
    a = p.parse_args()
    print(report(a.upstream, a.downstream, a.out)["best"])
