import io
import zipfile
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.api import nestor, cas_parser

client = TestClient(app)


def sample():
    return dict(restart=False, actions=[dict(ActionType='Dump_by_time', TimeStart='2000.01.01-00:00:01', TimeEnd='2000.01.01-00:01:01', FieldDump='100_dump', DumpVolume='12', GrainClass=['0.3', '0.7'])], gaia={'CLASSES TYPE OF SEDIMENT': 'NCO;CO'}, polygons='NAME:100_dump\n0 0\n1 0\n0 1\nEND\n', reference='', restart_file='')


def test_upstream_examples_roundtrip():
    paths = list((nestor.VENDOR / 'examples/nestor').glob('*/_DigActions.dat'))
    if not (nestor.VENDOR / "sources/nestor/readdigactions.f").is_file():
        pytest.skip("Exemplos oficiais exigem o submódulo TELEMAC inicializado")
    assert len(paths) == 4
    for path in paths:
        data = nestor.parse_actions(path.read_text())
        assert nestor.parse_actions(nestor.generate_actions(data)) == data


def test_catalog_matches_upstream():
    response = client.get('/api/nestor/schema')
    assert response.status_code == 200
    catalog = response.json()['gaia']
    assert len(catalog) == 152
    assert catalog['NESTOR']['type'] == 'LOGICAL'
    assert catalog['NESTOR']['default'] == 'NO'


def test_bundle_contains_correct_coupling_and_repeated_classes():
    response = client.post('/api/nestor/bundle', json=sample())
    assert response.status_code == 200
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        text = z.read('nestor_actions.dat').decode()
        assert text.count('GrainClass =') == 2
        assert nestor.parse_actions(text)['actions'][0]['GrainClass'] == ['0.3', '0.7']
        gai = cas_parser.parse(z.read('gaia.cas').decode())
        assert gai['NESTOR'] == 'YES'
        assert cas_parser.scalar(gai['NESTOR ACTION FILE']) in z.namelist()
        assert 'GAIA STEERING FILE' in z.read('coupling_t2d.txt').decode()
        assert 'NESTOR RESTART FILE' not in gai


@pytest.mark.parametrize('update', [
    {'TimeEnd': '2000.01.01-00:00:00'}, {'TimeStart': '2000.02.30-00:00:00'},
    {'GrainClass': ['0.2','0.2']}, {'GrainClass': ['NaN','1']},
    {'DumpRate': '0.1'}, {'DumpVolume': '-1'}, {'DigPlanar': 'TRUE'},
    {'FieldDump': 'missing'}, {'FieldDump': '200_missing'},
    {'DumpPlanar': 'TRUE'}, {'DumpVolume': '1\nENDACTION'},
])
def test_invalid_bundle_rejected(update):
    data = sample()
    data['actions'][0].update(update)
    assert client.post('/api/nestor/bundle', json=data).status_code == 422


def test_class_count_and_auxiliary_dependencies():
    data = sample()
    data['gaia']['CLASSES TYPE OF SEDIMENT'] = 'NCO'
    assert client.post('/api/nestor/bundle', json=data).status_code == 422
    data = sample()
    data['restart'] = True
    assert client.post('/api/nestor/bundle', json=data).status_code == 422
    data['restart_file'] = 'solver restart contents'
    data['actions'][0].update(DumpPlanar='TRUE', ReferenceLevel='SECTIONS')
    assert client.post('/api/nestor/bundle', json=data).status_code == 422
    data['reference'] = '0 0 0 1 0 0 0\n0 1 0 1 1 0 1\nEND\n'
    response = client.post('/api/nestor/bundle', json=data)
    assert response.status_code == 200
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        assert z.read('nestor_reference.dat').decode() == data['reference']
        assert z.read('nestor_restart.dat').decode() == data['restart_file']


@pytest.mark.parametrize('text', ['ACTION\nActionType = Dig_by_time\n', 'RESTART = FALSE\nACTION\nFoo = 1\nENDACTION\nENDFILE', 'RESTART = FALSE\nACTION\nACTION\nENDFILE'])
def test_malformed_import(text):
    assert client.post('/api/nestor/import', files={'file': ('actions.dat', text)}).status_code == 422


def test_packaged_dictionary_matches_checkout(monkeypatch, tmp_path):
    original = nestor.gaia_schema()
    monkeypatch.setattr(nestor, 'VENDOR', tmp_path)
    assert nestor.gaia_schema() == original
