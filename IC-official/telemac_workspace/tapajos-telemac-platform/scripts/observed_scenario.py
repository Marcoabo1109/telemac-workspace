"""Prepare an observed-forcing scenario without inventing a vertical datum."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.tapajos_analysis import lag_correlation, permanence


ROOT = Path(__file__).resolve().parents[1]
STATIONS = ROOT / "data" / "tapajos" / "stations" / "processed"
DEFAULT_OUTPUT = ROOT / "data" / "tapajos" / "scenarios" / "observed_2007"
DEFAULT_REPORT = ROOT / "reports" / "hydrology" / "observed_2007"

SOURCES = {
    "q_acara_m3_s": STATIONS
    / "ana_17650002_discharge_consisted_1996-01-01_2011-01-31.csv",
    "h_itaituba_cm": STATIONS
    / "ana_17730000_stage_consisted_1974-01-01_2014-05-31.csv",
    "q_bubure_m3_s": STATIONS
    / "ana_17710000_discharge_consisted_2004-10-21_2025-10-29.csv",
    "h_bubure_cm": STATIONS
    / "ana_17710000_stage_consisted_1995-06-16_2023-12-31.csv",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _load(path: Path, name: str) -> pd.DataFrame:
    data = pd.read_csv(path, parse_dates=["date"])
    required = {"date", "value", "consistency", "unit"}
    if not required.issubset(data.columns):
        raise ValueError(f"{path} is not a canonical daily series")
    if data.date.duplicated().any():
        raise ValueError(f"{path} contains duplicate dates")
    return data.set_index("date")[["value", "consistency"]].rename(
        columns={"value": name, "consistency": f"{name}_consistency"}
    )


def _statistics(values: pd.Series) -> dict:
    return {
        "minimum": float(values.min()),
        "maximum": float(values.max()),
        "mean": float(values.mean()),
        "median": float(values.median()),
        "p05": float(values.quantile(0.05)),
        "p95": float(values.quantile(0.95)),
    }


def _plot_controls(data: pd.DataFrame, report_dir: Path, lag: dict) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    report_dir.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(2, 1, figsize=(12, 7), sharex=True, layout="constrained")
    axes[0].plot(data.index, data.q_acara_m3_s, label="Acará 17650002")
    axes[0].plot(data.index, data.q_bubure_m3_s, label="Buburé 17710000", alpha=0.8)
    axes[0].set_ylabel("Vazão [m³/s]")
    axes[0].legend()
    axes[0].grid(alpha=0.25)
    axes[1].plot(data.index, data.h_itaituba_cm, label="Itaituba 17730000")
    axes[1].plot(data.index, data.h_bubure_cm, label="Buburé 17710000", alpha=0.8)
    axes[1].set(xlabel="Data", ylabel="Cota na régua local [cm]")
    axes[1].legend()
    axes[1].grid(alpha=0.25)
    fig.suptitle("Controles hidrológicos — cenário observado 2007")
    fig.savefig(report_dir / "hydrographs.png", dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), layout="constrained")
    for name, label in [
        ("q_acara_m3_s", "Acará"),
        ("q_bubure_m3_s", "Buburé"),
    ]:
        exceedance, values = permanence(data[name])
        axes[0].plot(exceedance, values, label=label)
    axes[0].set(xlabel="Permanência [%]", ylabel="Vazão [m³/s]")
    axes[0].legend()
    axes[0].grid(alpha=0.25)
    axes[1].plot(
        [item["lag_days"] for item in lag["lags"]],
        [item["correlation"] for item in lag["lags"]],
    )
    axes[1].axvline(lag["best"]["lag_days"], color="tab:red", linestyle="--")
    axes[1].set(
        xlabel="Atraso da cota de Itaituba [dias]",
        ylabel="Correlação vazão–cota",
    )
    axes[1].grid(alpha=0.25)
    fig.suptitle("Curva de permanência e diagnóstico de defasagem")
    fig.savefig(report_dir / "duration_lag.png", dpi=180)
    plt.close(fig)


def prepare(
    start: str = "2007-01-01",
    end: str = "2007-12-31",
    output: Path = DEFAULT_OUTPUT,
    report_dir: Path = DEFAULT_REPORT,
    *,
    make_plots: bool = True,
) -> dict:
    """Build the forcing package; stage remains referenced to the local gauge zero."""
    start_ts, end_ts = pd.Timestamp(start), pd.Timestamp(end)
    if end_ts < start_ts:
        raise ValueError("end must not precede start")
    expected = pd.date_range(start_ts, end_ts, freq="D")
    frames = [_load(path, name) for name, path in SOURCES.items()]
    data = pd.concat(frames, axis=1, sort=False).reindex(expected)
    data.index.name = "date"
    primary = ["q_acara_m3_s", "h_itaituba_cm"]
    if data[primary].isna().any().any():
        missing = data[primary].isna().sum().to_dict()
        raise ValueError(f"primary series are incomplete in selected window: {missing}")
    if not (data[[f"{name}_consistency" for name in primary]] == 2).all().all():
        raise ValueError("primary forcing requires consistency level 2")

    data.insert(0, "time_s", np.arange(len(data), dtype=np.int64) * 86400)
    data["h_itaituba_local_m"] = data.h_itaituba_cm / 100.0
    output.mkdir(parents=True, exist_ok=True)
    daily_path = output / "forcing_daily.csv"
    data.reset_index().to_csv(daily_path, index=False, lineterminator="\n")

    qsl_path = output / "forcing_local_gauge_datum.qsl.template"
    with qsl_path.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write("T Q(2) SL(1)\n")
        stream.write("s m3/s m\n")
        for row in data.itertuples():
            stream.write(
                f"{row.time_s} {row.q_acara_m3_s:.6f} "
                f"{row.h_itaituba_local_m:.6f}\n"
            )

    lag = lag_correlation(data.q_acara_m3_s, data.h_itaituba_cm, max_lag=30)
    if make_plots:
        _plot_controls(data, report_dir, lag)
    summary = {
        "schema_version": 1,
        "scenario": "observed_2007",
        "status": "forcing_prepared_execution_blocked",
        "period": {"start": start, "end": end, "days": len(data)},
        "primary_boundaries": {
            "upstream": "Acará do Tapajós 17650002 discharge",
            "downstream": "Itaituba 17730000 stage",
        },
        "controls": [
            "Buburé 17710000 discharge",
            "Buburé 17710000 stage",
        ],
        "statistics": {
            name: _statistics(data[name])
            for name in [
                "q_acara_m3_s",
                "h_itaituba_cm",
                "q_bubure_m3_s",
                "h_bubure_cm",
            ]
        },
        "lag_diagnostic": lag,
        "execution_ready": False,
        "blocked_by": [
            "Unknown geodetic offset between Itaituba gauge zero and mesh datum",
            "No surveyed bathymetry or verified bank polygon",
            "Propagation and lateral inflows between Acará and Itaituba require calibration",
        ],
        "stage_reference": (
            "The QSL template writes metres above the Itaituba local gauge zero; "
            "it is not a geodetic model elevation and must not be executed as a "
            "calibrated boundary before applying a documented datum offset."
        ),
        "artifacts": {
            "daily_forcing": {
                "path": _display_path(daily_path),
                "sha256": _sha256(daily_path),
            },
            "qsl_template": {
                "path": _display_path(qsl_path),
                "sha256": _sha256(qsl_path),
            },
        },
    }
    summary_path = output / "scenario.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if make_plots:
        report = {
            "scenario": summary["scenario"],
            "period": summary["period"],
            "statistics": summary["statistics"],
            "lag_diagnostic": lag,
            "warning": summary["stage_reference"],
        }
        (report_dir / "control_summary.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", default="2007-01-01")
    parser.add_argument("--end", default="2007-12-31")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    print(
        json.dumps(
            prepare(args.start, args.end, args.output, args.report),
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
