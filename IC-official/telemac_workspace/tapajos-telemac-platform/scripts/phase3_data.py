"""Ingest and audit observed field data for Phase 3 without filling gaps."""

from __future__ import annotations

import argparse
from datetime import date
import hashlib
import json
from pathlib import Path
import shutil

from backend.api.field_data import analyse_daily_csv
from scripts.tapajos_data import parse_legacy_xml


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def ingest_ana_xml(
    source: Path,
    output: Path,
    *,
    kind: str,
    station: str,
    source_url: str,
    retrieved_on: str,
) -> dict:
    """Preserve an ANA XML response and create a canonical audited CSV."""
    if kind not in {"H", "Q"}:
        raise ValueError("kind must be H (stage) or Q (discharge)")
    observations = parse_legacy_xml(source.read_text(encoding="utf-8-sig"), kind)
    variable = "stage" if kind == "H" else "discharge"
    start, end = observations.date.min(), observations.date.max()
    stem = f"ana_{station}_{variable}_consisted_{start}_{end}"
    raw_dir = output / "raw"
    processed_dir = output / "processed"
    manifest_dir = output / "manifests"
    for directory in (raw_dir, processed_dir, manifest_dir):
        directory.mkdir(parents=True, exist_ok=True)
    raw_path = raw_dir / f"{stem}.xml"
    csv_path = processed_dir / f"{stem}.csv"
    manifest_path = manifest_dir / f"{stem}.json"
    if source.resolve() != raw_path.resolve():
        shutil.copyfile(source, raw_path)
    observations.to_csv(csv_path, index=False, lineterminator="\n")
    quality = analyse_daily_csv(csv_path, "cm" if kind == "H" else "m3/s")
    manifest = {
        "schema_version": 1,
        "dataset": f"ANA station {station} {variable}",
        "source": {
            "institution": "Agência Nacional de Águas e Saneamento Básico (ANA)",
            "url": source_url,
            "retrieved_on": retrieved_on,
            "service": "HidroSerieHistorica (legacy read-only service)",
        },
        "transformation": {
            "parser": "scripts.tapajos_data.parse_legacy_xml",
            "gap_policy": "No interpolation; absent dates remain absent",
            "duplicate_policy": "Highest consistency record retained per date",
        },
        "artifacts": {
            "raw": {"path": str(raw_path), "sha256": digest(raw_path)},
            "canonical": {"path": str(csv_path), "sha256": digest(csv_path)},
        },
        "quality": quality,
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return {**manifest, "manifest_path": str(manifest_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--xml", type=Path, required=True)
    parser.add_argument("--kind", choices=["H", "Q"], required=True)
    parser.add_argument("--station", required=True)
    parser.add_argument("--out", type=Path, default=Path("data/tapajos/stations"))
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--retrieved-on", default=date.today().isoformat())
    args = parser.parse_args()
    result = ingest_ana_xml(
        args.xml,
        args.out,
        kind=args.kind,
        station=args.station,
        source_url=args.source_url,
        retrieved_on=args.retrieved_on,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
