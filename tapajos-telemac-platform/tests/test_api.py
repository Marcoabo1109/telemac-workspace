from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_example_and_exports():
    e = client.get("/api/example")
    assert e.status_code == 200
    e = e.json()
    assert len(e["mesh"]["x"]) == 1130
    assert client.post("/api/cas/export", json=e["params"]).status_code == 200
    assert client.post("/api/qsl/export", json=e["qsl"]).status_code == 200
    assert client.post("/api/cli/export", json=e["cli"]).status_code == 200
    assert client.post("/api/cas/export", json={"TIME STEP": -1}).status_code == 422


def test_binary_import_edit():
    b = client.get("/api/example/geo_culm.slf").content
    r = client.post(
        "/api/mesh/export",
        files={"file": ("mesh.slf", b)},
        data={"edits": '{"0":42.5}'},
    )
    assert r.status_code == 200
    r = client.post("/api/mesh/import", files={"file": ("mesh.slf", r.content)})
    assert r.status_code == 200
    assert r.json()["values"][0][0] == 42.5
