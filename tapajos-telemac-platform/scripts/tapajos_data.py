"""ANA HidroWebService client. Token stays in environment; offline XML supported."""

import argparse
import calendar
from datetime import date, timedelta
import hashlib
import json
import os
from pathlib import Path
import re
import time
import xml.etree.ElementTree as ET
import httpx
import pandas as pd

BASE = "https://www.ana.gov.br/hidrowebservice"
REACHES = {
    "alto": (-58.5, -13.0, -55.5, -9.0),
    "medio": (-57.5, -9.0, -55.0, -5.5),
    "baixo": (-55.5, -5.5, -54.5, -2.4),
}
# The provided middle bbox excludes Itaituba (~4.3 S). Offer an explicitly separate search window.
REACHES["itaituba"] = (-56.5, -4.8, -55.5, -3.8)


class ANAClient:
    def __init__(
        self,
        token=None,
        cache="data/tapajos/stations/cache",
        min_interval=2.0,
        transport=None,
    ):
        self.token = token or os.getenv("ANA_TOKEN")
        self.cache = Path(cache)
        self.cache.mkdir(parents=True, exist_ok=True)
        self.schema = None
        self.interval = max(1.0, min_interval)
        self.last = 0.0
        self.client = httpx.Client(timeout=45, transport=transport)

    def close(self):
        self.client.close()

    def get(self, route, params):
        if not self.token:
            raise RuntimeError(
                "ANA_TOKEN ausente. Solicite acesso ao HidroWebService; consulte docs/SCIENCE.md."
            )
        if not re.fullmatch(r"/EstacoesTelemetricas/[A-Za-z0-9]+/v1", route):
            raise ValueError("Rota ANA inválida")
        key = hashlib.sha256(
            json.dumps([route, params], sort_keys=True).encode()
        ).hexdigest()
        path = self.cache / (key + ".json")
        if path.exists():
            return json.loads(path.read_text())
        for attempt in range(4):
            time.sleep(max(0, self.interval - (time.monotonic() - self.last)))
            r = self.client.get(
                BASE + route,
                params=params,
                headers={
                    "accept": "application/json",
                    "Authorization": self.token
                    if self.token.startswith("Bearer ")
                    else "Bearer " + self.token,
                },
            )
            self.last = time.monotonic()
            if r.status_code in (401, 403):
                raise RuntimeError(
                    "Token ANA inválido/expirado ou acesso não autorizado; atualize ANA_TOKEN"
                )
            if r.status_code == 429 or r.status_code >= 500:
                wait = r.headers.get("Retry-After", "")
                if wait.isdigit() and int(wait) > 60:
                    raise RuntimeError(
                        "ANA solicitou espera maior que 60 s; retome posteriormente"
                    )
                time.sleep(int(wait) if wait.isdigit() else 2 ** (attempt + 1))
                continue
            r.raise_for_status()
            data = r.json()
            if str(data.get("code", 200)) != "200" or data.get(
                "status", "OK"
            ).upper() not in ("OK", "SUCESSO", "SUCCESS"):
                raise ValueError("ANA: " + str(data.get("message", "resposta de erro")))
            if not isinstance(data.get("items"), list):
                raise ValueError("Resposta ANA sem items; schema requer revisão")
            path.write_text(json.dumps(data, ensure_ascii=False))
            return data
        raise RuntimeError("ANA indisponível após tentativas limitadas")

    def inventory(self, **filters):
        return self.get("/EstacoesTelemetricas/HidroInventarioEstacoes/v1", filters)[
            "items"
        ]

    def history_params(self, route, station, start, end):
        # Resolve names from current official OpenAPI; never send guessed parameter labels.
        if self.schema is None:
            local = os.getenv("ANA_OPENAPI_FILE")
            if local:
                self.schema = json.loads(Path(local).read_text())
            else:
                r = self.client.get(BASE + "/api-docs/swagger-config")
                r.raise_for_status()
                config = r.json()
                url = config.get("url") or config["urls"][0]["url"]
                from urllib.parse import urljoin, urlparse

                url = urljoin(BASE + "/", url)
                if urlparse(url).hostname != "www.ana.gov.br":
                    raise ValueError("Schema fora do domínio ANA")
                r = self.client.get(url)
                r.raise_for_status()
                self.schema = r.json()
        operation = self.schema.get("paths", {}).get(route, {}).get("get")
        if not operation:
            raise ValueError("Rota histórica ausente do schema atual")
        params = {}
        found = set()
        import unicodedata

        for p in operation.get("parameters", []):
            if "$ref" in p:
                target = self.schema
                for part in p["$ref"].removeprefix("#/").split("/"):
                    target = target[part]
                p = target
            if p.get("in") != "query":
                continue
            name = p["name"]
            n = normal(
                unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
            )
            if "codigo" in n and "estacao" in n:
                params[name] = station
                found.add("station")
            elif "data" in n and ("inicial" in n or "inicio" in n):
                params[name] = start.isoformat()
                found.add("start")
            elif "data" in n and ("final" in n or "fim" in n):
                params[name] = end.isoformat()
                found.add("end")
            elif p.get("required"):
                default = p.get("schema", {}).get("default")
                if default is None:
                    raise ValueError("Parâmetro obrigatório requer revisão: " + name)
                params[name] = default
        if found != {"station", "start", "end"}:
            raise ValueError(
                "Schema de período não reconhecido; adaptar cliente conforme Swagger"
            )
        return params

    def history(self, station, start, end, kind="Q"):
        if kind not in ("Q", "H"):
            raise ValueError("kind Q ou H")
        route = (
            "/EstacoesTelemetricas/"
            + ("HidroSerieVazao" if kind == "Q" else "HidroSerieCotas")
            + "/v1"
        )
        current = start
        items = []
        while current <= end:
            stop = min(end, current + timedelta(days=365))
            data = self.get(route, self.history_params(route, station, current, stop))
            items += data["items"]
            current = stop + timedelta(days=1)
        return items


def normal(key):
    return re.sub("[^a-z0-9]", "", key.lower())


def monthly_records(records, kind):
    """Parse monthly daily columns; fail on unknown schema instead of inventing data."""
    rows = []
    prefix = "vazao" if kind == "Q" else "cota"
    for record in records:
        record = {normal(k): v for k, v in record.items()}
        stamp = record.get("datahoramedicao", record.get("data"))
        if not stamp:
            continue
        dt = pd.to_datetime(stamp, dayfirst=False)
        consistency = int(
            record.get("nivelconsistencia", record.get("consistencia", 0)) or 0
        )
        daily = False
        for day in range(1, calendar.monthrange(dt.year, dt.month)[1] + 1):
            value = record.get(f"{prefix}{day:02d}")
            if value in (None, ""):
                continue
            daily = True
            try:
                value = float(str(value).replace(",", "."))
            except ValueError:
                continue
            if pd.notna(value):
                rows.append(
                    (date(dt.year, dt.month, day).isoformat(), value, consistency)
                )
        if not daily and prefix in record and record[prefix] not in (None, ""):
            rows.append(
                (
                    dt.date().isoformat(),
                    float(str(record[prefix]).replace(",", ".")),
                    consistency,
                )
            )
    if not rows:
        raise ValueError(
            "Sem medições reconhecidas; verifique resposta bruta e schema antes de converter"
        )
    df = pd.DataFrame(rows, columns=["date", "value", "consistency"])
    df = df.sort_values(["date", "consistency"]).drop_duplicates("date", keep="last")
    # Keep stage in original cm; datum conversion only at TELEMAC boundary stage.
    df["unit"] = "m3/s" if kind == "Q" else "cm"
    return df.reset_index(drop=True)


def parse_legacy_xml(text, kind):
    root = ET.fromstring(text)
    errors = [
        e.text
        for e in root.iter()
        if e.tag.split("}")[-1].lower() == "error" and e.text
    ]
    if errors:
        raise ValueError("ANA: " + "; ".join(errors))
    records = []
    for e in root.iter():
        record = {c.tag.split("}")[-1]: c.text for c in e if len(c) == 0}
        if "DataHora" in record or "Data" in record:
            if "DataHora" in record:
                record["Data"] = record.pop("DataHora")
            records.append(record)
    return monthly_records(records, kind)


def select_stations(records, reach):
    west, south, east, north = REACHES[reach]
    features = []
    for r in records:
        try:
            x = float(r["Longitude"])
            y = float(r["Latitude"])
        except (KeyError, TypeError, ValueError):
            continue
        if west <= x <= east and south <= y <= north:
            features.append(
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [x, y]},
                    "properties": r,
                }
            )
    return {"type": "FeatureCollection", "features": features}


def overpass(reach, out):
    w, s, e, n = REACHES[reach]
    query = f'[out:json][timeout:25];way["waterway"="river"]({s},{w},{n},{e});out geom;'
    with httpx.Client(timeout=40) as c:
        r = c.post("https://overpass-api.de/api/interpreter", data={"data": query})
        r.raise_for_status()
        data = r.json()
    features = [
        {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": [[p["lon"], p["lat"]] for p in el["geometry"]],
            },
            "properties": {"osm_id": el["id"], **el.get("tags", {})},
        }
        for el in data.get("elements", [])
        if len(el.get("geometry", [])) >= 2
    ]
    result = {
        "type": "FeatureCollection",
        "features": features,
        "attribution": "© OpenStreetMap contributors, ODbL; river centreline is not bank polygon",
    }
    Path(out).write_text(json.dumps(result, ensure_ascii=False))
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--reach", choices=REACHES, default="itaituba")
    p.add_argument("--inventory-json", help="Inventário previamente baixado da ANA")
    p.add_argument("--xml")
    p.add_argument("--kind", choices=["Q", "H"], default="Q")
    p.add_argument("--out", default="data/tapajos/stations")
    p.add_argument("--station")
    p.add_argument(
        "--start",
        default=(pd.Timestamp.today() - pd.DateOffset(years=10)).date().isoformat(),
    )
    p.add_argument("--end", default=date.today().isoformat())
    p.add_argument("--overpass", action="store_true")
    p.add_argument("--query-params", help="JSON de filtros conforme Swagger atual")
    a = p.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    if a.xml:
        parse_legacy_xml(Path(a.xml).read_text(), a.kind).to_csv(
            out / "offline_series.csv", index=False
        )
    elif a.overpass:
        overpass(a.reach, out / "river_centerlines.geojson")
    else:
        client = ANAClient()
        try:
            if a.inventory_json:
                records = json.loads(Path(a.inventory_json).read_text())
                records = (
                    records.get("items", []) if isinstance(records, dict) else records
                )
            else:
                if not a.query_params:
                    raise ValueError(
                        "Forneça --query-params com filtros do Swagger ou --inventory-json; evita consulta sem filtro"
                    )
                records = client.inventory(**json.loads(a.query_params))
            selected = select_stations(records, a.reach)
            (out / "tapajos_stations.geojson").write_text(
                json.dumps(selected, ensure_ascii=False, indent=2)
            )
            codes = (
                [a.station]
                if a.station
                else [
                    str(f["properties"]["codigoestacao"]) for f in selected["features"]
                ]
            )
            for code in codes:
                for kind in ("Q", "H"):
                    raw = client.history(
                        code,
                        date.fromisoformat(a.start),
                        date.fromisoformat(a.end),
                        kind,
                    )
                    (out / f"raw_{kind}_{code}.json").write_text(
                        json.dumps(raw, ensure_ascii=False)
                    )
                    df = monthly_records(raw, kind)
                    df = df[(df.date >= a.start) & (df.date <= a.end)]
                    df.to_csv(out / f"tapajos_{kind}_{code}.csv", index=False)
        finally:
            client.close()
