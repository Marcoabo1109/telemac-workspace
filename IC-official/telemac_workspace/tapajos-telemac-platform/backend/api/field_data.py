"""Quality checks for observed daily hydrological series used in Phase 3."""

from __future__ import annotations

import csv
from collections import Counter
from datetime import date, timedelta
import math
from pathlib import Path


REQUIRED_COLUMNS = {"date", "value", "consistency", "unit"}


def analyse_daily_csv(path: Path, expected_unit: str | None = None) -> dict:
    """Validate a canonical daily series and report coverage without filling gaps."""
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        missing_columns = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing_columns:
            raise ValueError(
                "missing columns: " + ", ".join(sorted(missing_columns))
            )
        rows = list(reader)
    if not rows:
        raise ValueError("daily series is empty")

    observations: list[tuple[date, float, str, str]] = []
    for line, row in enumerate(rows, start=2):
        try:
            stamp = date.fromisoformat(row["date"])
            value = float(row["value"])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"invalid date/value at CSV line {line}") from exc
        if not math.isfinite(value):
            raise ValueError(f"non-finite value at CSV line {line}")
        consistency = str(row["consistency"]).strip()
        unit = str(row["unit"]).strip()
        if not consistency or not unit:
            raise ValueError(f"missing consistency/unit at CSV line {line}")
        if expected_unit and unit != expected_unit:
            raise ValueError(f"unexpected unit {unit!r}; expected {expected_unit!r}")
        observations.append((stamp, value, consistency, unit))

    dates = [row[0] for row in observations]
    if dates != sorted(dates):
        raise ValueError("daily series must be sorted by date")
    if len(dates) != len(set(dates)):
        raise ValueError("daily series contains duplicate dates")
    units = sorted({row[3] for row in observations})
    if len(units) != 1:
        raise ValueError("daily series contains mixed units")

    gaps = []
    for previous, current in zip(dates, dates[1:]):
        missing = (current - previous).days - 1
        if missing > 0:
            gaps.append(
                {
                    "start": (previous + timedelta(days=1)).isoformat(),
                    "end": (current - timedelta(days=1)).isoformat(),
                    "days": missing,
                }
            )
    expected_days = (dates[-1] - dates[0]).days + 1
    missing_days = expected_days - len(dates)
    values = [row[1] for row in observations]
    consistency = Counter(row[2] for row in observations)
    return {
        "records": len(observations),
        "start": dates[0].isoformat(),
        "end": dates[-1].isoformat(),
        "expected_days": expected_days,
        "missing_days": missing_days,
        "completeness_percent": round(100 * len(dates) / expected_days, 2),
        "gap_count": len(gaps),
        "maximum_gap_days": max((gap["days"] for gap in gaps), default=0),
        "gaps": gaps,
        "unit": units[0],
        "minimum": min(values),
        "maximum": max(values),
        "consistency_counts": dict(sorted(consistency.items())),
    }


def phase3_report(catalog: dict, root: Path) -> dict:
    """Summarize acquired observed series and remaining Phase 3 requirements."""
    series = []
    missing = []
    for dataset in catalog.get("datasets", []):
        if dataset.get("fitness") != "required":
            continue
        if dataset.get("status") == "missing":
            missing.append(
                {
                    "id": dataset.get("id"),
                    "title": dataset.get("title"),
                    "category": dataset.get("category"),
                }
            )
            continue
        if dataset.get("category") not in {"flow", "stage"}:
            continue
        path = root / dataset["local_path"]
        expected_unit = dataset.get("variables", [{}])[0].get("unit")
        series.append(
            {
                "id": dataset["id"],
                "title": dataset["title"],
                "category": dataset["category"],
                "station": dataset.get("station"),
                "quality": analyse_daily_csv(path, expected_unit),
                "vertical_datum": dataset.get("spatial_reference", {}).get(
                    "vertical_datum"
                ),
                "limitations": dataset.get("limitations", []),
            }
        )
    return {"phase": 3, "observed_series": series, "missing_requirements": missing}
