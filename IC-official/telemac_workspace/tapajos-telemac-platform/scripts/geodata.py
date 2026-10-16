"""Explicit HydroSHEDS file download, GeoJSON clipping and DEM window extraction."""

from pathlib import Path
from urllib.parse import urlparse
import hashlib
import json
import httpx
from shapely.geometry import shape, mapping, box


def download_hydrosheds(url, out):
    host = urlparse(url).hostname or ""
    if not (host == "hydrosheds.org" or host.endswith(".hydrosheds.org")):
        raise ValueError("Informe URL HTTPS oficial do HydroSHEDS")
    if not url.startswith("https://"):
        raise ValueError("HTTPS obrigatório")
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with httpx.stream("GET", url, timeout=60, follow_redirects=True) as r:
        r.raise_for_status()
        with out.open("wb") as f:
            for b in r.iter_bytes():
                f.write(b)
    meta = {
        "source": url,
        "sha256": hashlib.sha256(out.read_bytes()).hexdigest(),
        "license": "Consultar licença HydroSHEDS específica do produto; download não implica redistribuição",
    }
    out.with_suffix(out.suffix + ".json").write_text(json.dumps(meta, indent=2))
    return meta


def clip_geojson(source, out, bbox):
    data = json.loads(Path(source).read_text())
    domain = box(*bbox)
    features = []
    for f in data["features"]:
        g = shape(f["geometry"]).intersection(domain)
        if not g.is_empty:
            features.append({**f, "geometry": mapping(g)})
    Path(out).write_text(
        json.dumps({"type": "FeatureCollection", "features": features})
    )
    return len(features)


def crop_dem(source, out, bounds, bounds_crs="EPSG:4326"):
    import rasterio
    from rasterio.warp import transform_bounds
    from rasterio.windows import from_bounds

    with rasterio.open(source) as src:
        if not src.crs:
            raise ValueError("DEM sem CRS")
        b = transform_bounds(bounds_crs, src.crs, *bounds)
        w = from_bounds(*b, transform=src.transform).round_offsets().round_lengths()
        data = src.read(window=w)
        profile = src.profile.copy()
        profile.update(
            driver="GTiff",
            height=data.shape[1],
            width=data.shape[2],
            transform=src.window_transform(w),
        )
        if data.size == 0:
            raise ValueError("Recorte fora do raster")
        with rasterio.open(out, "w", **profile) as dst:
            dst.write(data)
    Path(str(out) + ".json").write_text(
        json.dumps(
            {
                "source": str(source),
                "purpose": "topografia; não batimetria submersa",
                "datum_vertical": "verificar na fonte",
            },
            indent=2,
        )
    )
