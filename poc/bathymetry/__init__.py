"""Cotas em metros, positivas para cima, no referencial horizontal da malha."""
from abc import ABC, abstractmethod
from dataclasses import replace
from pathlib import Path

import numpy as np
from pyproj import CRS
from scipy.interpolate import LinearNDInterpolator, NearestNDInterpolator

from backend.api import slf_io


class Bathymetry(ABC):
    @abstractmethod
    def evaluate(self, x, y):
        """Retorna cotas nos pares de coordenadas indicados."""

    def write_to_selafin(self, mesh, path):
        z = np.broadcast_to(self.evaluate(mesh.x + mesh.iparam[2], mesh.y + mesh.iparam[3]), mesh.x.shape)
        if not np.isfinite(z).all():
            raise ValueError("Malha fora da cobertura ou cota inválida")
        variables = list(mesh.variables)
        values = mesh.values.copy()
        names = [name.upper() for name, unit in variables]
        if "BOTTOM" in names:
            index = names.index("BOTTOM")
            values[:, index] = z
            variables[index] = ("BOTTOM", "M")
        else:
            variables.append(("BOTTOM", "M"))
            values = np.concatenate([values, np.broadcast_to(z, (len(mesh.times), 1, z.size))], axis=1)
        if not len(mesh.times):
            raise ValueError("A geometria deve ter ao menos um registro")
        Path(path).write_bytes(slf_io.write(replace(mesh, variables=variables, values=values)))


class BathymetryAnalytic(Bathymetry):
    def __init__(self, function):
        self.function = function

    def evaluate(self, x, y):
        x, y = np.broadcast_arrays(x, y)
        return np.broadcast_to(self.function(x, y), x.shape)


def trapezoidal(x, y):
    return -3 + 0.5 * np.maximum(abs(y) - 8, 0)


def pool_riffle(x, y):
    return trapezoidal(x, y - 10*np.sin(x/80)) + 0.6*np.cos(x/40)


def step(x, y):
    return np.where(x < 50, -2., -3.)


def sill(x, y):
    return -3 + np.exp(-((x-50)/5)**2)


class BathymetryFromFile(Bathymetry):
    def __init__(self, path, *, source_crs, mesh_crs, z_unit, method="linear"):
        path = Path(path)
        if z_unit != "m" or not source_crs or not mesh_crs:
            raise ValueError("Declare CRS e cotas em metros")
        def crs(value):
            if value == "LOCAL":
                return value
            result = CRS.from_user_input(value)
            if not result.is_projected or result.axis_info[0].unit_conversion_factor != 1:
                raise ValueError("Use um CRS projetado em metros")
            return result
        if crs(source_crs) != crs(mesh_crs):
            raise ValueError("Reprojete os dados para o CRS da malha")
        if path.suffix.lower() in {".slf", ".geo"}:
            mesh = slf_io.read(path)
            unit = dict(mesh.variables).get("BOTTOM", "").upper()
            if unit not in {"", "M"}:
                raise ValueError("Unidade de BOTTOM incompatível")
            x, y, z = mesh.x + mesh.iparam[2], mesh.y + mesh.iparam[3], mesh.field("BOTTOM")
        elif path.suffix.lower() in {".tif", ".tiff"}:
            import rasterio
            with rasterio.open(path) as raster:
                if not raster.crs or crs(raster.crs) != crs(mesh_crs):
                    raise ValueError("CRS do raster incompatível")
                grid = raster.read(1, masked=True)
                row, col = np.where(~np.ma.getmaskarray(grid))
                x, y = raster.xy(row, col)
                z = grid.data[row, col]
        elif path.suffix.lower() == ".csv":
            data = np.genfromtxt(path, delimiter=",", names=True)
            x, y, z = (data[key] for key in ("x","y","z"))
        elif path.suffix.lower() == ".xyz":
            x, y, z = np.loadtxt(path, unpack=True)
        else:
            raise ValueError("Formato de batimetria desconhecido")
        interpolator = {"linear": LinearNDInterpolator, "nearest": NearestNDInterpolator}[method]
        if not np.isfinite(np.column_stack((x,y,z))).all():
            raise ValueError("Amostra inválida")
        self.interpolate = interpolator(np.column_stack((x,y)), z)

    def evaluate(self, x, y):
        return self.interpolate(x, y)
