import re
import numpy as np


def parse(text):
    lines = [
        x.strip()
        for x in text.splitlines()
        if x.strip() and not x.lstrip().startswith(("#", "/"))
    ]
    if len(lines) < 4:
        raise ValueError("Cabeçalho, unidades e ao menos dois registros esperados")
    columns = lines[0].split()
    units = lines[1].split()
    rows = [[float(v.replace("D", "E")) for v in line.split()] for line in lines[2:]]
    validate(columns, rows)
    if len(units) != len(columns):
        raise ValueError("Número de unidades incorreto")
    return dict(columns=columns, units=units, rows=rows)


def validate(columns, rows, min_dt=0, max_gap=None):
    if (
        not columns
        or columns[0] != "T"
        or len(columns) < 2
        or len(set(columns)) != len(columns)
    ):
        raise ValueError("Colunas: T Q(n) SL(n), sem duplicatas")
    if any(not re.fullmatch(r"(Q|SL|U|V|TR)\([1-9][0-9]*\)", c) for c in columns[1:]):
        raise ValueError("Fronteira líquida inválida")
    a = np.asarray(rows, dtype=float)
    if (
        a.ndim != 2
        or a.shape[1] != len(columns)
        or len(a) < 2
        or not np.isfinite(a).all()
    ):
        raise ValueError("Série incompleta ou não finita")
    dt = np.diff(a[:, 0])
    if a[0, 0] < 0 or np.any(dt <= min_dt):
        raise ValueError("Tempos devem ser crescentes e respeitar dt mínimo")
    if max_gap is not None and np.any(dt > max_gap):
        raise ValueError("Lacuna temporal excede limite")
    return a


def generate(columns, rows, units=None):
    a = validate(columns, rows)
    units = units or ["s"] + [
        "m3/s" if c.startswith("Q(") else "m" for c in columns[1:]
    ]
    if len(units) != len(columns):
        raise ValueError("Unidades inconsistentes")
    return (
        " ".join(columns)
        + "\n"
        + " ".join(units)
        + "\n"
        + "\n".join(" ".join(f"{v:.17g}" for v in row) for row in a)
        + "\n"
    )
