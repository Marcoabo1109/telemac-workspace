"""Build an explicitly uncalibrated Tapajos scenario from an OSM centreline."""

import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from pyproj import Transformer
from shapely.geometry import LineString, Point, box, mapping
from shapely.ops import transform, substring
from scripts.mesh_generator import generate
from backend.api import slf_io, cli_io, cas_parser, qsl_io

ROOT = Path(__file__).resolve().parents[1]
OSM_URL = "https://api.openstreetmap.org/api/0.6/map?bbox=-55.995,-4.315,-55.955,-4.275"


def prepare(osm_file, out=None):
    out = Path(out or ROOT / "models/tapajos_trecho1")
    out.mkdir(parents=True, exist_ok=True)
    xml = ET.parse(osm_file).getroot()
    nodes = {
        n.get("id"): (float(n.get("lon")), float(n.get("lat")))
        for n in xml.findall("node")
    }
    way = next(w for w in xml.findall("way") if w.get("id") == "26158344")
    tags = {t.get("k"): t.get("v") for t in way.findall("tag")}
    line = LineString([nodes[n.get("ref")] for n in way.findall("nd")])
    clipped = line.intersection(box(-55.995, -4.315, -55.955, -4.275))
    if clipped.geom_type != "LineString":
        raise ValueError("OSM clip changed; review centreline selection")
    forward = Transformer.from_crs(4326, 32721, always_xy=True).transform
    inverse = Transformer.from_crs(32721, 4326, always_xy=True).transform
    axis = transform(forward, clipped)
    # Direction assumed downstream toward north for this local reach.
    if axis.coords[0][1] > axis.coords[-1][1]:
        axis = LineString(list(axis.coords)[::-1])
    length = min(4000.0, axis.length)
    axis = substring(
        axis, (axis.length - length) / 2, (axis.length + length) / 2
    ).simplify(60)
    width = 1200.0  # Assumed, not an OSM bank survey.
    domain = axis.buffer(width / 2, cap_style=2, join_style=2)
    geo = {
        "type": "Feature",
        "properties": {"status": "assumed_width_buffer_of_OSM_axis"},
        "geometry": mapping(transform(inverse, domain)),
    }
    generate(geo, out, 180, 300, 180)
    m = slf_io.read(out / "mesh.slf")
    s = np.array([axis.project(Point(x, y)) for x, y in zip(m.x, m.y)])
    d = np.array([axis.distance(Point(x, y)) for x, y in zip(m.x, m.y)])
    stage = 3.71  # Published September median, gauge zero mapped to model zero by assumption.
    depth = 8.0 - 4.0 * np.minimum(d / (width / 2), 1) ** 2
    m.values[0, 0] = stage - depth + 5e-5 * (axis.length - s)
    m.title = b"TAPAJOS OSM AXIS - ASSUMED BED FLOW DATUM".ljust(72) + b"SERAFIN "
    # SERAFIND prevents metre-scale quantization of large UTM northings.
    m.precision = 8
    m.title = m.title[:72] + b"SERAFIND"
    (out / "mesh.slf").write_bytes(slf_io.write(m))
    rows = cli_io.parse((out / "mesh.cli").read_text())
    upstream, downstream = [], []
    for r in rows:
        n = r[11] - 1
        if s[n] < 1.0:
            upstream.append(n)
        elif s[n] > axis.length - 1.0:
            downstream.append(n)
    if min(len(upstream), len(downstream)) < 3:
        raise ValueError("At least 3 nodes required per open cross-section")
    # Start the contour within a solid bank. TELEMAC FRONT2 independently
    # starts at the southwesternmost point: solver-verified outlet=1, inlet=2.
    labels = [
        "in" if r[11] - 1 in upstream else "out" if r[11] - 1 in downstream else "wall"
        for r in rows
    ]
    first = next(
        i for i, l in enumerate(labels) if l == "in" and labels[i - 1] == "wall"
    )
    start = (first - 1) % len(rows)
    rows = rows[start:] + rows[:start]
    for j, r in enumerate(rows):
        n = r[11] - 1
        r[12] = j + 1
        m.ipobo[n] = j + 1
        if n in upstream:
            r[:3] = [4, 5, 5]
            r[7] = 5
            r[8] = 1.0
        elif n in downstream:
            r[:3] = [5, 4, 4]
            r[7] = 4
    (out / "mesh.slf").write_bytes(slf_io.write(m))
    (out / "mesh.cli").write_text(cli_io.generate(rows))
    params = cas_parser.parse((ROOT / "data/culm/t2d_culm.cas").read_text())
    for k in ["PREVIOUS COMPUTATION FILE", "INITIAL TIME SET TO ZERO"]:
        params.pop(k, None)
    params.update(
        {
            "TITLE": "'TAPAJOS EXPLORATORY ASSUMPTIONS'",
            "GEOMETRY FILE": "'mesh.slf'",
            "BOUNDARY CONDITIONS FILE": "'mesh.cli'",
            "RESULTS FILE": "'r2d_tapajos.slf'",
            "LIQUID BOUNDARIES FILE": "'tapajos.qsl'",
            "COMPUTATION CONTINUED": "NO",
            "TIME STEP": "2",
            "NUMBER OF TIME STEPS": "1800",
            "GRAPHIC PRINTOUT PERIOD": "60",
            "LISTING PRINTOUT PERIOD": "300",
            "INITIAL ELEVATION": str(stage),
            "PRESCRIBED FLOWRATES": "0;6000",
            "PRESCRIBED ELEVATIONS": f"{stage};0",
            "TIDAL FLATS": "NO",
            "NUMBER OF TRACERS": "1",
            "NAMES OF TRACERS": "'PASSIVE TRACER  '",
            "INITIAL VALUES OF TRACERS": "0",
            "PRESCRIBED TRACERS VALUES": "0;1",
            "DIFFUSION OF TRACERS": "YES",
            "COEFFICIENT FOR DIFFUSION OF TRACERS": "5",
            "VARIABLES FOR GRAPHIC PRINTOUTS": "'U,V,S,B,H,T*'",
            "TYPE OF ADVECTION": "1;5;1",
            "SUPG OPTION": "1;0;0",
            "CONTINUITY CORRECTION": "YES",
            "MATRIX-VECTOR PRODUCT": "1",
        }
    )
    (out / "tapajos.cas").write_text(cas_parser.generate(params))
    (out / "tapajos.qsl").write_text(
        qsl_io.generate(
            ["T", "Q(2)", "SL(1)"],
            [[0, 6000, stage], [3600, 6000, stage]],
            ["s", "m3/s", "m"],
        )
    )
    source = {
        "url": OSM_URL,
        "retrieved_on": "2026-09-09",
        "raw_sha256": hashlib.sha256(Path(osm_file).read_bytes()).hexdigest(),
        "way_id": 26158344,
        "version": way.get("version"),
        "timestamp": way.get("timestamp"),
        "tags": tags,
        "attribution": "© OpenStreetMap contributors",
        "license": "ODbL 1.0",
        "license_url": "https://www.openstreetmap.org/copyright",
    }
    gdir = ROOT / "data/tapajos/geometry"
    gdir.mkdir(exist_ok=True)
    (gdir / "osm_tapajos_axis.geojson").write_text(
        json.dumps(
            {"type": "Feature", "properties": source, "geometry": mapping(line)},
            ensure_ascii=False,
            indent=2,
        )
        + "\n"
    )
    assumptions = {
        "status": "exploratory_uncalibrated",
        "collected": {
            "axis": source,
            "stage_statistics": "data/tapajos/stations/itaituba_sgb_monthly_levels.json",
        },
        "assumed": {
            "width_m": width,
            "depth_center_m": 8,
            "depth_bank_m": 4,
            "bed_slope": 5e-5,
            "flow_m3_s": 6000,
            "strickler_m_1_3_s": 30,
            "velocity_diffusivity_m2_s": 2,
            "tracer_diffusivity_m2_s": 5,
            "gauge_to_model_offset_m": 0,
            "initial_velocity_m_s": 0,
            "inlet_normalized_tracer": 1,
            "initial_normalized_tracer": 0,
            "tributaries_wind_rain": "omitted",
            "sediment_reactions_sorption": "omitted",
        },
        "derived": {
            "stage_m": stage,
            "stage_basis": "September climatological median 371 cm / 100; held constant",
            "bed_formula": "stage - (8 - 4*(distance/(width/2))^2) + slope*(L-s)",
            "crs": "EPSG:32721",
            "reach_length_m": axis.length,
            "nodes": len(m.x),
            "triangles": len(m.ikle),
            "liquid_boundary_ids": {"outlet": 1, "inlet": 2},
            "inlet_nodes": [n + 1 for n in upstream],
            "outlet_nodes": [n + 1 for n in downstream],
        },
        "numerics": {
            "dt_s": 2,
            "duration_s": 3600,
            "initialization": "still water at constant elevation; startup transient retained",
        },
        "limitations": [
            "No surveyed bank polygon or bathymetry. Width tags in OSM conflict and were not used as measurements.",
            "No acquired daily flow hydrograph. Flow 6000 m3/s is a scenario assumption.",
            "Gauge zero has not been tied to a geodetic datum.",
            "Normalized conservative tracer is not a measured metal concentration.",
            "One hour demonstrates startup transport; no steady state, convergence or calibration claim.",
        ],
    }
    (out / "assumptions.json").write_text(
        json.dumps(assumptions, ensure_ascii=False, indent=2) + "\n"
    )
    meta = json.loads((out / "mesh.metadata.json").read_text())
    meta.update(
        bathymetry="assumed analytical section; see assumptions.json",
        boundary="inlet flow, outlet stage, wall banks",
        vertical_datum="assumed local gauge zero",
        precision="SERAFIND 64 bit",
    )
    (out / "mesh.metadata.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(json.dumps(assumptions["derived"], indent=2))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("osm_file")
    p.add_argument("--out")
    a = p.parse_args()
    prepare(a.osm_file, a.out)
