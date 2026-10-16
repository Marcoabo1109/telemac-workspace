"""Nestor editor, grounded in the vendored TELEMAC v8p5r0 Fortran readers."""
from datetime import datetime
from pathlib import Path
import io
import json
import math
import re
import zipfile
from . import cas_parser

SOURCE = 'https://gitlab.pam-retd.fr/otm/telemac-mascaret'
COMMIT = 'd1bff193746fd76425d7715a6e4d20d42eb8877e'
VENDOR = Path(__file__).resolve().parents[2] / 'vendor/telemac'
REFERENCES = ['NO', 'GRID', 'SECTIONS', 'WATERLVL1', 'WATERLVL2', 'WATERLVL3']
COMMON = ['TimeStart', 'TimeEnd']
FIELDS = {
    'Dig_by_time': COMMON + ['FieldDig', 'DigVolume', 'FieldDump', 'DumpRate', 'DumpPlanar', 'ReferenceLevel'],
    'Dump_by_time': COMMON + ['FieldDump', 'DumpVolume', 'DumpPlanar', 'ReferenceLevel', 'GrainClass'],
    'Dig_by_criterion': COMMON + ['TimeRepeat', 'FieldDig', 'ReferenceLevel', 'DigRate', 'DigDepth', 'CritDepth', 'MinVolume', 'MinVolumeRadius', 'FieldDump', 'DumpRate', 'DumpPlanar'],
    'Save_water_level': ['TimeStart', 'ReferenceLevel'],
    'Backfill_to_level': COMMON + ['FieldDump', 'ReferenceLevel', 'CritDepth', 'GrainClass'],
}
REQUIRED = {
    'Dig_by_time': COMMON + ['FieldDig', 'DigVolume'],
    'Dump_by_time': COMMON + ['FieldDump', 'DumpVolume', 'GrainClass'],
    'Dig_by_criterion': COMMON + ['TimeRepeat', 'FieldDig', 'ReferenceLevel', 'DigRate', 'DigDepth', 'CritDepth', 'MinVolume', 'MinVolumeRadius'],
    'Save_water_level': ['TimeStart', 'ReferenceLevel'],
    'Backfill_to_level': COMMON + ['FieldDump', 'ReferenceLevel', 'CritDepth', 'GrainClass'],
}
LABELS = {
    'TimeStart': 'Início · aaaa.mm.dd-hh:mm:ss', 'TimeEnd': 'Fim · aaaa.mm.dd-hh:mm:ss',
    'TimeRepeat': 'Intervalo de verificação · s', 'FieldDig': 'Área de dragagem · ID de 3 dígitos',
    'FieldDump': 'Área de despejo · opcional na dragagem', 'DigVolume': 'Volume dragado · m³',
    'DumpVolume': 'Volume despejado · m³', 'DigRate': 'Taxa de dragagem · m/s',
    'DumpRate': 'Taxa de despejo · m/s', 'DigDepth': 'Profundidade de dragagem · m',
    'CritDepth': 'Profundidade crítica · m', 'MinVolume': 'Volume mínimo · m³',
    'MinVolumeRadius': 'Raio do volume mínimo · m', 'DumpPlanar': 'Despejo planar',
    'ReferenceLevel': 'Superfície de referência', 'GrainClass': 'Frações por classe GAIA · separadas por ; · soma = 1',
}
NUMERIC = {'TimeRepeat', 'DigVolume', 'DumpVolume', 'DigRate', 'DumpRate', 'DigDepth', 'CritDepth', 'MinVolume', 'MinVolumeRadius'}


def gaia_schema():
    """Read keyword types/defaults/help from the actual upstream dictionary."""
    dictionary = VENDOR / 'sources/gaia/gaia.dico'
    if not dictionary.is_file():
        snapshot = Path(__file__).resolve().parents[1] / 'data/gaia_v8p5r0.json'
        return json.loads(snapshot.read_text())['keywords']
    result = {}
    for block in re.split(r'(?m)^NOM\s*=', (VENDOR / 'sources/gaia/gaia.dico').read_text())[1:]:
        name = re.search(r"(?m)^NOM1\s*=\s*'([^']+)'", block)
        if not name:
            continue
        def value(key):
            m = re.search(rf'(?m)^{key}\s*=\s*(.*)', block)
            return m[1].strip() if m else ''
        help_match = re.search(r"AIDE1\s*=\s*'([\s\S]*?)'\s*(?:/|$)", block)
        result[name[1]] = {'type': value('TYPE'), 'default': value('DEFAUT1'), 'help': help_match[1] if help_match else ''}
    return result


def parse_actions(text):
    actions, current, restart, ended = [], None, None, False
    allowed = set().union(*FIELDS.values()) | {'ActionType', 'DigPlanar'}
    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.split('/', 1)[0].strip()
        if not line:
            continue
        if ended:
            raise ValueError('Conteúdo após ENDFILE')
        if line == 'ACTION':
            if current is not None:
                raise ValueError('ACTION sem ENDACTION')
            current = {}
        elif line == 'ENDACTION':
            if current is None:
                raise ValueError('ENDACTION sem ACTION')
            actions.append(current)
            current = None
        elif line == 'ENDFILE':
            if current is not None:
                raise ValueError('Falta ENDACTION')
            ended = True
        elif '=' in line:
            key, value = (s.strip() for s in line.split('=', 1))
            if key == 'RESTART' and current is None:
                if restart is not None or value.upper() not in ('TRUE', 'FALSE', '.TRUE.', '.FALSE.'):
                    raise ValueError('RESTART inválido ou repetido')
                restart = value.upper().strip('.') == 'TRUE'
            elif current is not None and key in allowed and value:
                if key == 'GrainClass':
                    current.setdefault(key, []).append(value)
                elif key in current:
                    raise ValueError(f'Campo repetido: {key}')
                else:
                    current[key] = value
            else:
                raise ValueError(f'Linha {number}: campo desconhecido ou fora de ACTION: {key}')
        else:
            raise ValueError(f'Linha {number}: sintaxe inválida')
    if not ended or restart is None or not actions:
        raise ValueError('Esperados RESTART, ACTION/ENDACTION e ENDFILE')
    return {'restart': restart, 'actions': actions}


def number(value):
    try:
        n = float(str(value).replace('D', 'E').replace('d', 'e'))
    except (ValueError, TypeError):
        raise ValueError(f'Número inválido: {value}')
    if not math.isfinite(n):
        raise ValueError('Número não finito')
    return n


def validate_actions(data, class_count=None):
    if not isinstance(data, dict):
        raise ValueError('Configuração deve ser um objeto')
    if not isinstance(data.get('restart'), bool) or not isinstance(data.get('actions'), list) or not data['actions']:
        raise ValueError('Informe RESTART e pelo menos uma ação')
    for i, action in enumerate(data['actions'], 1):
        if not isinstance(action, dict):
            raise ValueError(f'Ação {i}: esperado objeto de parâmetros')
        kind = action.get('ActionType')
        if kind not in FIELDS:
            raise ValueError(f'Ação {i}: tipo incompatível com GAIA: {kind}')
        for key in REQUIRED[kind]:
            if key not in action or action[key] == '' or action[key] == []:
                raise ValueError(f'Ação {i}: falta {key}')
        for key, value in action.items():
            if key not in FIELDS[kind] + ['ActionType', 'DigPlanar']:
                raise ValueError(f'Ação {i}: {key} não se aplica a {kind}')
            if key == 'GrainClass':
                if not isinstance(value, list):
                    raise ValueError('GrainClass deve ser uma lista')
                fractions = [number(v) for v in value]
                if any(v < 0 or v > 1 for v in fractions) or abs(sum(fractions) - 1) > 1e-10:
                    raise ValueError('GrainClass: frações entre 0 e 1 com soma igual a 1')
                if class_count is not None and len(fractions) != class_count:
                    raise ValueError('GrainClass: quantidade diferente das classes GAIA')
                continue
            if any(c in str(value) for c in '\n\r/='):
                raise ValueError(f'{key}: valor deve ocupar uma linha sem delimitadores')
            if key in NUMERIC:
                n = number(value)
                if key not in ('DigDepth', 'CritDepth') and n < 0:
                    raise ValueError(f'{key}: deve ser não negativo')
            if key in ('FieldDig', 'FieldDump') and not re.fullmatch(r'\d{3}\S{0,29}', str(value)):
                raise ValueError(f'{key}: use 3 dígitos iniciais, sem espaços, até 32 caracteres')
            if key in ('DigPlanar', 'DumpPlanar') and str(value).upper().strip('.') not in ('TRUE', 'FALSE'):
                raise ValueError(f'{key}: esperado TRUE ou FALSE')
            if key == 'DigPlanar' and str(value).upper().strip('.') != 'FALSE':
                raise ValueError('DigPlanar=TRUE não é suportado pelo TELEMAC v8p5r0')
            if key == 'ReferenceLevel' and value not in REFERENCES:
                raise ValueError('ReferenceLevel inválido')
        try:
            start = datetime.strptime(action['TimeStart'], '%Y.%m.%d-%H:%M:%S')
            if kind != 'Save_water_level' and datetime.strptime(action['TimeEnd'], '%Y.%m.%d-%H:%M:%S') <= start:
                raise ValueError('Fim deve ser posterior ao início')
        except ValueError as exc:
            raise ValueError(f'Ação {i}: datas inválidas ({exc})')
        if str(action.get('DumpPlanar', '')).upper().strip('.') == 'TRUE' and 'ReferenceLevel' not in action:
            raise ValueError('DumpPlanar exige ReferenceLevel')
        if kind == 'Dig_by_criterion' and 'FieldDump' in action and 'DumpRate' not in action:
            raise ValueError('Dragagem por critério com despejo exige DumpRate')
        if kind == 'Save_water_level' and action['ReferenceLevel'] not in REFERENCES[3:]:
            raise ValueError('Save_water_level exige WATERLVL1, WATERLVL2 ou WATERLVL3')
    return data


def generate_actions(data, class_count=None):
    validate_actions(data, class_count)
    lines = ['RESTART = ' + ('TRUE' if data['restart'] else 'FALSE')]
    for action in data['actions']:
        lines += ['ACTION', '  ActionType = ' + action['ActionType']]
        # The Fortran reader needs ActionType and TimeStart before TimeEnd.
        for key in dict.fromkeys(FIELDS[action['ActionType']] + ['DigPlanar']):
            if key in action:
                for value in action[key] if key == 'GrainClass' else [action[key]]:
                    lines.append(f'  {key} = {value}')
        lines.append('ENDACTION')
    return '\n'.join(lines + ['ENDFILE', ''])


def polygons(text):
    result, current = [], None
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith(('#', '/', 'INSEL', 'DAMM')):
            continue
        if line.startswith('END'):
            break
        if line.startswith('NAME:'):
            name = line[5:].strip()
            if not re.fullmatch(r'\d{3}\S{0,29}', name):
                raise ValueError('Polígono: nome deve iniciar com 3 dígitos e ter até 32 caracteres')
            current = {'name': name, 'points': []}
            result.append(current)
        elif current is not None:
            values = line.split()
            if len(values) != 2:
                raise ValueError('Polígono: esperadas duas coordenadas X Y')
            current['points'].append([number(v) for v in values])
        else:
            raise ValueError('Polígono sem NAME:')
    if not result:
        raise ValueError('Informe pelo menos um polígono')
    for p in result:
        if len(set(map(tuple, p['points']))) < 3:
            raise ValueError(f"Polígono {p['name']}: mínimo de 3 vértices distintos")
    return result


def bundle(data):
    validate_actions(data)
    if not isinstance(data.get('gaia'), dict):
        raise ValueError('Informe os parâmetros GAIA')
    for key in ('polygons', 'reference', 'restart_file'):
        if not isinstance(data.get(key, ''), str):
            raise ValueError(f'{key}: esperado texto')
    gaia = dict(data['gaia'])
    types = cas_parser.scalar(gaia.get('CLASSES TYPE OF SEDIMENT', '')).split(';')
    if not types or any(t.strip().strip("'\"") not in ('CO', 'NCO') for t in types):
        raise ValueError('Configure CLASSES TYPE OF SEDIMENT: CO ou NCO, separados por ;')
    actions = generate_actions(data, len(types))
    poly = polygons(data.get('polygons', ''))
    ids = {p['name'][:3] for p in poly}
    for a in data['actions']:
        for key in ('FieldDig', 'FieldDump'):
            if key in a and a[key][:3] not in ids:
                raise ValueError(f"{key}: polígono não encontrado: {a[key]}")
    files = {'nestor_actions.dat': actions, 'nestor_polygons.dat': data['polygons']}
    gaia.update({'NESTOR': 'YES', 'NESTOR ACTION FILE': "'nestor_actions.dat'", 'NESTOR POLYGON FILE': "'nestor_polygons.dat'"})
    needs_reference = any(a.get('ReferenceLevel') in ('GRID', 'SECTIONS') for a in data['actions'])
    if needs_reference and not data.get('reference', '').strip():
        raise ValueError('GRID/SECTIONS exige arquivo de superfície de referência')
    for key, field, filename, needed in (
        ('NESTOR SURFACE REFERENCE FILE', 'reference', 'nestor_reference.dat', needs_reference),
        ('NESTOR RESTART FILE', 'restart_file', 'nestor_restart.dat', data['restart']),
    ):
        gaia.pop(key, None)
        if needed:
            if not data.get(field, '').strip():
                raise ValueError(f'Arquivo obrigatório: {key}')
            files[filename] = data[field]
            gaia[key] = f"'{filename}'"
    files['gaia.cas'] = cas_parser.generate(gaia)
    files['coupling_t2d.txt'] = "COUPLING WITH = 'GAIA'\nGAIA STEERING FILE = 'gaia.cas'\n"
    files['LEIA-ME.txt'] = (
        'Configuração GAIA/Nestor — TELEMAC v8p5r0\n'
        f'Fonte: {SOURCE}/-/tree/{COMMIT}\n'
        'Acrescente coupling_t2d.txt ao CAS hidrodinâmico; não o use como caso completo.\n'
        'Inclua geometria, fronteiras sedimentológicas e demais entradas referenciadas no GAIA.\n'
        'Datas das ações devem coincidir com ORIGINAL DATE OF TIME / ORIGINAL HOUR OF TIME do caso.\n'
        'Coordenadas e superfícies devem usar o CRS e datum da malha.\n'
        'Referência/restart são preservados como texto, sem validação integral do formato.\n'
        'O editor não valida estabilidade, calibração ou execução do solver.\n'
        'O executor web atual não executa acoplamento GAIA; execute o caso completo pelo CLI TELEMAC.\n'
    )
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, content in files.items():
            z.writestr(name, content)
    return stream.getvalue()
