"""GMSH polygonal mesher; explicit WGS84 input and projected metre coordinates."""

import argparse
import json
from pathlib import Path
import numpy as np
from shapely.geometry import shape, LineString
from shapely.ops import transform
from pyproj import Transformer
from backend.api.slf_io import Serafin, write


def project(geojson):
    g = geojson.get("geometry", geojson)
    if geojson.get("type") == "FeatureCollection":
        if len(geojson["features"]) != 1:
            raise ValueError("Forneça exatamente um domínio Polygon")
        g = geojson["features"][0]["geometry"]
    poly = shape(g)
    if poly.geom_type != "Polygon" or not poly.is_valid or poly.area <= 0:
        raise ValueError("Domínio deve ser Polygon válido, não linha central")
    lon, lat = poly.centroid.coords[0]
    if not (
        -180 <= poly.bounds[0] <= poly.bounds[2] <= 180
        and -80 < poly.bounds[1] <= poly.bounds[3] < 84
    ):
        raise ValueError("GeoJSON deve estar em WGS84 lon/lat")
    epsg = (32700 if lat < 0 else 32600) + int((lon + 180) // 6) + 1
    tr = Transformer.from_crs(4326, epsg, always_xy=True)
    return transform(tr.transform, poly), epsg


def boundary_order(triangles):
    edges = {}
    for t in triangles:
        for a, b in zip(t, np.roll(t, -1)):
            key = tuple(sorted((int(a), int(b))))
            edges[key] = edges.get(key, 0) + 1
    adj = {}
    for (a, b), n in edges.items():
        if n == 1:
            adj.setdefault(a, []).append(b)
            adj.setdefault(b, []).append(a)
    if any(len(v) != 2 for v in adj.values()):
        raise ValueError("Fronteira não manifold")
    order = []
    remaining = set(adj)
    while remaining:
        start = min(remaining)
        prev = None
        cur = start
        while cur in remaining:
            order.append(cur)
            remaining.remove(cur)
            nxt = next(x for x in adj[cur] if x != prev)
            prev, cur = cur, nxt
        if cur != start:
            raise ValueError("Contorno aberto")
    return order


def generate(
    geometry,
    out,
    lc_canal=200,
    lc_planicie=800,
    lc_fronteira=200,
    backend="gmsh",
    bottom=None,
):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    if not all(
        np.isfinite(v) and v >= 1 for v in (lc_canal, lc_planicie, lc_fronteira)
    ):
        raise ValueError("Tamanhos devem ser finitos e >= 1 m")
    if lc_canal > lc_planicie:
        raise ValueError("lc_canal deve ser <= lc_planicie")
    poly, epsg = project(geometry)
    if poly.area / lc_canal**2 > 300000:
        raise ValueError("Domínio muito grande para o mesher interativo")
    # Medial axis proxy along the long side; replace with measured channel centreline for studies.
    rect = poly.minimum_rotated_rectangle
    corners = np.array(rect.exterior.coords)[:4]
    lengths = np.linalg.norm(np.roll(corners, -1, axis=0) - corners, axis=1)
    i = int(np.argmin(lengths))
    a = (corners[i] + corners[(i + 1) % 4]) / 2
    b = (corners[(i + 2) % 4] + corners[(i + 3) % 4]) / 2
    axis = LineString([a, b]).intersection(poly)
    rings = [list(poly.exterior.coords)[:-1]] + [
        list(r.coords)[:-1] for r in poly.interiors
    ]
    if backend == "gmsh":
        import gmsh

        if getattr(gmsh, "isInitialized", lambda: False)():
            raise ValueError("GMSH ocupado")
        gmsh.initialize()
        gmsh.option.setNumber("General.Terminal", 0)
        try:
            gmsh.model.add("tapajos")
            loops = []
            lines = []
            for coords in rings:
                points = [
                    gmsh.model.geo.addPoint(x, y, 0, lc_fronteira) for x, y in coords
                ]
                ls = [
                    gmsh.model.geo.addLine(p, points[(j + 1) % len(points)])
                    for j, p in enumerate(points)
                ]
                lines += ls
                loops.append(gmsh.model.geo.addCurveLoop(ls))
            surface = gmsh.model.geo.addPlaneSurface(loops)
            axispoints = []
            for f in np.linspace(0, 1, 30):
                p = axis.interpolate(float(f), normalized=True)
                axispoints.append(gmsh.model.geo.addPoint(p.x, p.y, 0, lc_canal))
            gmsh.model.geo.synchronize()
            gmsh.model.addPhysicalGroup(2, [surface], 1)
            dist = gmsh.model.mesh.field.add("Distance")
            gmsh.model.mesh.field.setNumbers(dist, "PointsList", axispoints)
            threshold = gmsh.model.mesh.field.add("Threshold")
            for k, v in {
                "InField": dist,
                "SizeMin": lc_canal,
                "SizeMax": lc_planicie,
                "DistMin": lc_canal * 2,
                "DistMax": lc_planicie * 4,
            }.items():
                gmsh.model.mesh.field.setNumber(threshold, k, v)
            gmsh.model.mesh.field.setAsBackgroundMesh(threshold)
            gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
            gmsh.model.mesh.generate(2)
            gmsh.write(str(out / "mesh.msh"))
            gmsh.write(str(out / "mesh.geo_unrolled"))
            (out / "mesh.geo").write_text((out / "mesh.geo_unrolled").read_text())
            tags, xyz, _ = gmsh.model.mesh.getNodes()
            coords = np.array(xyz).reshape(-1, 3)
            _, nodes = gmsh.model.mesh.getElementsByType(2)
            lookup = {int(tag): i for i, tag in enumerate(tags)}
            tri = np.array([lookup[int(n)] for n in nodes]).reshape(-1, 3)
            used = np.unique(tri)
            remap = {int(v): i for i, v in enumerate(used)}
            xy = coords[used, :2]
            tri = np.array([[remap[int(v)] for v in t] for t in tri])
        finally:
            gmsh.finalize()
    elif backend == "delaunay":
        from scipy.spatial import Delaunay

        # Exact polygon coverage is mandatory; reject rather than silently bridge concave banks.
        from shapely.geometry import Point, Polygon

        points = []
        for ring in rings:
            for a, b in zip(ring, ring[1:] + ring[:1]):
                for t in np.linspace(
                    0,
                    1,
                    max(2, int(np.linalg.norm(np.array(a) - b) / lc_fronteira) + 1),
                    endpoint=False,
                ):
                    points.append(np.array(a) * (1 - t) + np.array(b) * t)
        minx, miny, maxx, maxy = poly.bounds
        for x in np.arange(minx, maxx, lc_canal):
            for y in np.arange(miny, maxy, lc_canal):
                if poly.contains(Point(x, y)):
                    points.append((x, y))
        xy = np.unique(np.round(points, 8), axis=0)
        tri = Delaunay(xy).simplices
        tri = np.array([t for t in tri if poly.buffer(1e-6).covers(Polygon(xy[t]))])
        area = sum(Polygon(xy[t]).area for t in tri)
        if abs(area - poly.area) > poly.area * 1e-6:
            raise ValueError("Delaunay não preservou o domínio; utilize GMSH")
    else:
        raise ValueError("Backend desconhecido")
    for t in tri:
        v = xy[t]
        cross = (v[1, 0] - v[0, 0]) * (v[2, 1] - v[0, 1]) - (v[1, 1] - v[0, 1]) * (
            v[2, 0] - v[0, 0]
        )
        if cross < 0:
            t[1], t[2] = t[2], t[1]
    order = boundary_order(tri)
    ipobo = np.zeros(len(xy), dtype=int)
    ipobo[order] = np.arange(1, len(order) + 1)
    z = np.full(len(xy), 0.0 if bottom is None else float(bottom))
    mesh = Serafin(
        b"TAPAJOS APPROXIMATE - UNCALIBRATED".ljust(72) + b"SERAFIN ",
        [("BOTTOM", "M")],
        np.zeros(10, dtype=int),
        None,
        tri,
        ipobo,
        xy[:, 0],
        xy[:, 1],
        np.array([0.0]),
        z[None, None, :],
    )
    (out / "mesh.slf").write_bytes(write(mesh))
    (out / "mesh.cli").write_text(
        "\n".join(
            f"2 2 2 0. 0. 0. 0. 2 0. 0. 0. {n + 1} {j + 1}" for j, n in enumerate(order)
        )
        + "\n"
    )
    meta = {
        "crs": f"EPSG:{epsg}",
        "horizontal_unit": "m",
        "vertical_datum": None,
        "bathymetry": "placeholder_zero" if bottom is None else "constant_synthetic",
        "boundary": "all walls; classify liquid boundaries before simulation",
        "refinement": "approximate medial axis, not surveyed thalweg",
        "nodes": len(xy),
        "triangles": len(tri),
        "calibrated": False,
    }
    (out / "mesh.metadata.json").write_text(json.dumps(meta, indent=2))
    (out / "domain.geojson").write_text(json.dumps(geometry))
    return meta


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("geojson")
    p.add_argument("--out", default="data/tapajos/meshes")
    p.add_argument("--lc-canal", type=float, default=200)
    p.add_argument("--lc-planicie", type=float, default=800)
    p.add_argument("--lc-fronteira", type=float, default=200)
    p.add_argument("--backend", choices=["gmsh", "delaunay"], default="gmsh")
    a = p.parse_args()
    print(
        generate(
            json.loads(Path(a.geojson).read_text()),
            a.out,
            a.lc_canal,
            a.lc_planicie,
            a.lc_fronteira,
            a.backend,
        )
    )
