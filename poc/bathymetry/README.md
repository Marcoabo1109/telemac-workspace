# Batimetria

Da raiz, defina PYTHONPATH=.:tapajos-telemac-platform. CSV requer cabeçalho x,y,z. XYZ contém três colunas numéricas sem cabeçalho. Cotas são positivas para cima. Declare metros e o mesmo datum vertical. LOCAL exige confirmação de que as duas fontes compartilham a mesma origem e eixos métricos. O exemplo Culm não informa EPSG. O modo linear retorna NaN fora do fecho convexo; a escrita rejeita nós descobertos. Nearest extrapola. Raster usa centros dos pixels válidos e triangulação, podendo preencher lacunas internas.

```python
from backend.api.slf_io import read
from poc.bathymetry import BathymetryAnalytic, BathymetryFromFile, pool_riffle
mesh = read("tapajos-telemac-platform/data/culm/geo_culm.slf")
BathymetryAnalytic(pool_riffle).write_to_selafin(mesh, "analytic.slf")
survey = BathymetryFromFile("pontos.csv", source_crs="EPSG:31981",
                            mesh_crs="EPSG:31981", z_unit="m", method="nearest")
```

As funções trapezoidal, pool_riffle, step e sill usam coordenadas locais em metros. Uma máscara f(x,y,z) descreveria materiais por camada e exigiria estratigrafia GAIA separada. BOTTOM é uma única superfície comum a T2D e GAIA. Ao modificar o fundo, prepare condições iniciais compatíveis.
