"""SERAFIN/SERAFIND triangular 2-D, big/little endian, Fortran records."""

from dataclasses import dataclass
import io
import struct
import numpy as np


@dataclass
class Serafin:
    title: bytes
    variables: list
    iparam: np.ndarray
    date: object
    ikle: np.ndarray
    ipobo: np.ndarray
    x: np.ndarray
    y: np.ndarray
    times: np.ndarray
    values: np.ndarray
    endian: str = ">"
    precision: int = 4

    def field(self, name, frame=0):
        names = [n.strip().upper() for n, u in self.variables]
        return self.values[frame, names.index(name.upper())]

    def summary(self, frame=0):
        frame = max(0, min(frame, len(self.times) - 1))
        return dict(
            title=self.title[:72].decode("latin1").strip(),
            variables=[{"name": n, "unit": u} for n, u in self.variables],
            x=self.x.tolist(),
            y=self.y.tolist(),
            triangles=self.ikle.tolist(),
            ipobo=self.ipobo.tolist(),
            times=self.times.tolist(),
            values=self.values[frame].tolist() if len(self.times) else [],
            frame=frame,
        )


def read(data):
    if hasattr(data, "read"):
        data = data.read()
    elif not isinstance(data, bytes):
        data = open(data, "rb").read()
    if len(data) < 4:
        raise ValueError("SERAFIN truncado")
    endian = ">" if struct.unpack(">i", data[:4])[0] == 80 else "<"
    stream = io.BytesIO(data)

    def rec(optional=False):
        b = stream.read(4)
        if not b and optional:
            return None
        if len(b) != 4:
            raise ValueError("Marcador truncado")
        n = struct.unpack(endian + "i", b)[0]
        if n < 0 or n > len(data) - stream.tell() - 4:
            raise ValueError("Comprimento de registro inválido")
        b = stream.read(n)
        tail = stream.read(4)
        if len(tail) != 4 or struct.unpack(endian + "i", tail)[0] != n:
            raise ValueError("Marcadores Fortran inconsistentes")
        return b

    def ints(b):
        return np.frombuffer(b, dtype=endian + "i4").astype(np.int32)

    title = rec()
    if len(title) != 80:
        raise ValueError("Título SERAFIN inválido")
    nv = ints(rec())
    if len(nv) != 2 or min(nv) < 0:
        raise ValueError("Variáveis inválidas")
    variables = []
    for _ in range(int(sum(nv))):
        v = rec()
        if len(v) != 32:
            raise ValueError("Nome/unidade inválido")
        variables.append(
            (v[:16].decode("latin1").strip(), v[16:].decode("latin1").strip())
        )
    iparam = ints(rec())
    if len(iparam) != 10 or iparam[6] not in (0, 1):
        raise ValueError("Somente SERAFIN 2D é suportado")
    date = ints(rec()) if iparam[9] == 1 else None
    dims = ints(rec())
    if len(dims) != 4:
        raise ValueError("Dimensões inválidas")
    ne, npoin, ndp, _ = dims
    if ne <= 0 or npoin <= 0 or ndp != 3:
        raise ValueError("Malha deve conter triângulos 2D")
    ikle = ints(rec()).reshape(ne, ndp) - 1
    ipobo = ints(rec())
    if len(ipobo) != npoin or ikle.min() < 0 or ikle.max() >= npoin:
        raise ValueError("Conectividade inválida")
    xb = rec()
    precision = len(xb) // int(npoin)
    if precision not in (4, 8) or len(xb) != npoin * precision:
        raise ValueError("Precisão inválida")

    def floats(b, n):
        if len(b) != n * precision:
            raise ValueError("Campo truncado")
        a = np.frombuffer(b, dtype=endian + f"f{precision}").astype(float)
        if not np.isfinite(a).all():
            raise ValueError("Campo contém NaN/Inf")
        return a

    x = floats(xb, npoin)
    y = floats(rec(), npoin)
    times = []
    values = []
    while True:
        b = rec(True)
        if b is None:
            break
        times.append(floats(b, 1)[0])
        values.append([floats(rec(), npoin) for _ in variables])
    return Serafin(
        title,
        variables,
        iparam,
        date,
        ikle,
        ipobo,
        x,
        y,
        np.array(times),
        np.array(values).reshape(len(times), len(variables), npoin),
        endian,
        precision,
    )


def write(mesh):
    out = io.BytesIO()
    e = mesh.endian

    def rec(b):
        out.write(struct.pack(e + "i", len(b)) + b + struct.pack(e + "i", len(b)))

    def ints(a):
        return np.asarray(a, dtype=e + "i4").tobytes()

    def floats(a):
        a = np.asarray(a, dtype=e + f"f{mesh.precision}")
        if not np.isfinite(a).all():
            raise ValueError("Valeur non finie")
        return a.tobytes()

    rec(mesh.title.ljust(80, b" ")[:80])
    rec(ints([len(mesh.variables), 0]))
    for n, u in mesh.variables:
        rec(n.encode("latin1").ljust(16)[:16] + u.encode("latin1").ljust(16)[:16])
    rec(ints(mesh.iparam))
    if mesh.iparam[9] == 1:
        rec(ints(mesh.date))
    rec(ints([len(mesh.ikle), len(mesh.x), 3, 1]))
    rec(ints(mesh.ikle + 1))
    rec(ints(mesh.ipobo))
    rec(floats(mesh.x))
    rec(floats(mesh.y))
    for t, fields in zip(mesh.times, mesh.values, strict=True):
        rec(floats([t]))
        for f in fields:
            rec(floats(f))
    blob = out.getvalue()
    read(blob)  # structural validation before export
    return blob
