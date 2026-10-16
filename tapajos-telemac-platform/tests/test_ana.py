import pytest
from scripts.tapajos_data import parse_legacy_xml, ANAClient, select_stations


def test_error_xml_and_month_length():
    with pytest.raises(ValueError, match="Sem dados"):
        parse_legacy_xml("<Data><Error>Sem dados</Error></Data>", "Q")
    d = parse_legacy_xml(
        "<Data><Serie><DataHora>2024-02-01</DataHora><NivelConsistencia>2</NivelConsistencia><Vazao01>10,5</Vazao01><Vazao29>20</Vazao29><Vazao30>999</Vazao30></Serie></Data>",
        "Q",
    )
    assert len(d) == 2
    assert d.value.tolist() == [10.5, 20.0]


def test_auth_required(tmp_path, monkeypatch):
    monkeypatch.delenv("ANA_TOKEN", raising=False)
    c = ANAClient(cache=tmp_path)
    with pytest.raises(RuntimeError, match="ANA_TOKEN"):
        c.inventory()
    c.close()


def test_itaituba_bbox_correction():
    r = [{"Longitude": -55.99, "Latitude": -4.27, "codigoestacao": "example"}]
    assert len(select_stations(r, "itaituba")["features"]) == 1
    assert len(select_stations(r, "medio")["features"]) == 0
