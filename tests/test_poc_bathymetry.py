from pathlib import Path
import tempfile
import unittest
import numpy as np
from backend.api.slf_io import read
from poc.bathymetry import BathymetryAnalytic, BathymetryFromFile

GEOMETRY = Path(__file__).resolve().parents[1] / "tapajos-telemac-platform/data/culm/geo_culm.slf"


class TestBottom(unittest.TestCase):
    def test_plane_roundtrip(self):
        mesh = read(GEOMETRY)
        plane = BathymetryAnalytic(lambda x, y: 0.001*x - 0.003*y)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"test.slf"
            plane.write_to_selafin(mesh, path)
            bottom = BathymetryFromFile(path, source_crs="LOCAL", mesh_crs="LOCAL", z_unit="m")
            np.testing.assert_allclose(bottom.evaluate(mesh.x, mesh.y), plane.evaluate(mesh.x, mesh.y), atol=3e-6)
            np.testing.assert_array_equal(mesh.ikle, read(path).ikle)

    def test_crs_mismatch(self):
        with self.assertRaises(ValueError):
            BathymetryFromFile(GEOMETRY, source_crs="EPSG:32630", mesh_crs="LOCAL", z_unit="m")
