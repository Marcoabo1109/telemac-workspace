"""Depth-averaged diagnostics; friction formula limited to Strickler/Manning."""

import argparse
import json
from pathlib import Path
import numpy as np
from backend.api.slf_io import read


def metrics(mesh, law=3, coefficient=30.0, rho=1000.0, dry=1e-3):
    if coefficient <= 0 or law not in (3, 4):
        raise ValueError("Use coeficiente positivo Strickler (3) ou Manning (4)")
    names = [n.strip().upper() for n, u in mesh.variables]

    def field(aliases):
        ix = next((names.index(n) for n in aliases if n in names), None)
        if ix is None:
            raise ValueError("Campo ausente: " + str(aliases))
        return mesh.values[:, ix, :]

    h = field(["WATER DEPTH", "HAUTEUR D'EAU"])
    u = field(["VELOCITY U", "VITESSE U"])
    v = field(["VELOCITY V", "VITESSE V"])
    wet = h > dry
    speed = np.hypot(u, v)
    froude = np.zeros_like(h)
    tau = np.zeros_like(h)
    np.divide(speed, np.sqrt(9.81 * np.maximum(h, 0)), out=froude, where=wet)
    n = 1 / coefficient if law == 3 else coefficient
    np.divide(
        rho * 9.81 * n * n * speed**2, np.cbrt(np.maximum(h, 0)), out=tau, where=wet
    )
    return dict(speed=speed, froude=froude, bed_shear_pa=tau, wet=wet)


def export_vtk(mesh, out, frame=0):
    out = Path(out)
    with out.open("w") as f:
        f.write(
            "# vtk DataFile Version 3.0\nTELEMAC results\nASCII\nDATASET UNSTRUCTURED_GRID\n"
        )
        f.write(f"POINTS {len(mesh.x)} float\n")
        for x, y in zip(mesh.x, mesh.y):
            f.write(f"{x} {y} 0\n")
        f.write(f"CELLS {len(mesh.ikle)} {4 * len(mesh.ikle)}\n")
        for t in mesh.ikle:
            f.write("3 " + " ".join(map(str, t)) + "\n")
        f.write(f"CELL_TYPES {len(mesh.ikle)}\n" + "5\n" * len(mesh.ikle))
        f.write(f"POINT_DATA {len(mesh.x)}\n")
        for (n, u), vals in zip(mesh.variables, mesh.values[frame]):
            name = "".join(c if c.isalnum() else "_" for c in n)
            f.write(f"SCALARS {name} float 1\nLOOKUP_TABLE default\n")
            for v in vals:
                f.write(f"{v}\n")


def animate(mesh, path, variable="WATER DEPTH"):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation

    names = [n.strip().upper() for n, u in mesh.variables]
    data = mesh.values[:, names.index(variable), :]
    fig, ax = plt.subplots(figsize=(9, 5), layout="constrained")
    artist = ax.tripcolor(
        mesh.x,
        mesh.y,
        mesh.ikle,
        data[0],
        shading="gouraud",
        vmin=data.min(),
        vmax=data.max(),
    )
    ax.set_aspect("equal")
    fig.colorbar(artist, ax=ax, label=mesh.variables[names.index(variable)][1])
    ax.set(xlabel="x [m]", ylabel="y [m]")

    def update(i):
        artist.set_array(data[i])
        ax.set_title(f"{variable} • t={mesh.times[i]:g} s")
        return [artist]

    ani = FuncAnimation(fig, update, frames=len(data))
    ani.save(
        str(path), writer="pillow" if str(path).endswith(".gif") else "ffmpeg", fps=5
    )
    plt.close(fig)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("slf")
    p.add_argument("--out", default="reports/scenario")
    p.add_argument("--law", type=int, default=3)
    p.add_argument("--coefficient", type=float, default=30)
    p.add_argument("--animate", choices=["gif", "mp4"])
    a = p.parse_args()
    m = read(a.slf)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    d = metrics(m, a.law, a.coefficient)
    np.savez_compressed(out / "fields.npz", **d)
    (out / "metrics.json").write_text(
        json.dumps({k: float(v.max()) for k, v in d.items() if k != "wet"}, indent=2)
    )
    export_vtk(m, out / "results.vtk", -1)
    if a.animate:
        animate(m, out / f"depth.{a.animate}")
