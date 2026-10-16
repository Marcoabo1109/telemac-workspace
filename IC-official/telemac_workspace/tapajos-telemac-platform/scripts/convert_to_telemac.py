"""Canonical CSV: date,value. ANA stage requires explicit unit + gauge datum."""

import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from backend.api.qsl_io import generate


def series_to_qsl(
    csv, kind="Q", boundary=1, unit="m3/s", datum_offset=None, max_gap_hours=24
):
    df = pd.read_csv(csv, sep=None, engine="python")
    if not {"date", "value"} <= set(df):
        raise ValueError("CSV deve ter colunas date,value")
    dates = pd.to_datetime(df.date, utc=True)
    values = pd.to_numeric(df.value, errors="raise").to_numpy(float)
    if (
        dates.isna().any()
        or dates.duplicated().any()
        or not dates.is_monotonic_increasing
    ):
        raise ValueError("Datas inválidas/duplicadas/não crescentes")
    if kind == "SL":
        if datum_offset is None:
            raise ValueError("Cota de régua precisa de datum_offset explícito [m]")
        if unit not in ("cm", "m"):
            raise ValueError("Unidade de cota deve ser cm ou m")
        values = values * (0.01 if unit == "cm" else 1) + datum_offset
    elif kind != "Q" or unit != "m3/s":
        raise ValueError("Vazão deve estar em m3/s")
    t = (dates - dates.iloc[0]).dt.total_seconds().to_numpy()
    from backend.api.qsl_io import validate

    cols = ["T", f"{kind}({boundary})"]
    rows = np.column_stack([t, values])
    validate(cols, rows, max_gap=max_gap_hours * 3600)
    return generate(cols, rows)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("csv")
    p.add_argument("--out", default="boundaries.qsl")
    p.add_argument("--kind", choices=["Q", "SL"], default="Q")
    p.add_argument("--boundary", type=int, default=1)
    p.add_argument("--unit", default="m3/s")
    p.add_argument("--datum-offset", type=float)
    p.add_argument("--max-gap-hours", type=float, default=24)
    a = p.parse_args()
    Path(a.out).write_text(
        series_to_qsl(
            a.csv, a.kind, a.boundary, a.unit, a.datum_offset, a.max_gap_hours
        )
    )
