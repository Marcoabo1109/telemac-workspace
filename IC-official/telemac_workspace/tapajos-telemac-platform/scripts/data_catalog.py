"""Validate the Tapajós data catalog and emit a readiness report."""

import argparse
import json
from pathlib import Path

from backend.api import data_catalog


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=data_catalog.CATALOG_PATH)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    catalog = data_catalog.load(args.catalog)
    result = data_catalog.report(catalog)
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text)
    print(text, end="")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
