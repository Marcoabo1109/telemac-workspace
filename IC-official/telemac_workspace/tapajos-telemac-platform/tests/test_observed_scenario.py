from scripts.observed_scenario import prepare


def test_observed_scenario_prepares_complete_2007_window(tmp_path):
    result = prepare(
        output=tmp_path / "scenario",
        report_dir=tmp_path / "report",
        make_plots=False,
    )
    assert result["period"] == {
        "start": "2007-01-01",
        "end": "2007-12-31",
        "days": 365,
    }
    assert result["execution_ready"] is False
    assert result["statistics"]["q_acara_m3_s"]["minimum"] > 0
    qsl = (tmp_path / "scenario" / "forcing_local_gauge_datum.qsl.template")
    lines = qsl.read_text().splitlines()
    assert lines[:2] == ["T Q(2) SL(1)", "s m3/s m"]
    assert len(lines) == 367
