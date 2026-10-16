"""Package the synthetic examples and their evidence without temporary builds."""
import argparse
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from scripts.sediment_benchmarks import ROOT


def package(target):
    folders = sorted((ROOT/'models').glob('synthetic*'))+[ROOT/'reports/synthetic_transport']
    files = {p for folder in folders for p in folder.rglob('*') if p.is_file()
             and not any('.cas_' in part or part=='__pycache__' for part in p.relative_to(ROOT).parts)}
    for rel in ['docs/SYNTHETIC_SEDIMENT_LAB.md', 'backend/__init__.py', 'backend/api/__init__.py',
                'backend/api/synthetic_sediment.py', 'backend/api/cas_parser.py', 'backend/api/slf_io.py',
                'scripts/__init__.py', 'scripts/sediment_benchmarks.py', 'scripts/audit_synthetic_benchmarks.py',
                'scripts/synthetic_transport_study.py', 'scripts/prepare_sand_diagnostic.py',
                'scripts/plot_synthetic_transport.py', 'scripts/summarize_synthetic_lab.py',
                'scripts/package_synthetic_lab.py', 'tests/test_synthetic_sediment.py', 'LICENSE', 'requirements.txt',
                'docker/run-telemac']:
        files.add(ROOT/rel)
    target = Path(target); target.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(target, 'w', ZIP_DEFLATED) as z:
        for p in sorted(files):
            if p.name == '.DS_Store' or p.suffix == '.pyc': continue
            z.write(p, p.relative_to(ROOT))
        z.writestr('LEIA-ME.txt', '''Laboratório sintético de sedimentos, micropoluentes e dragagem.
Repositório: https://github.com/Marcoabo1109/IC
Comece por docs/SYNTHETIC_SEDIMENT_LAB.md e reports/synthetic_transport/README.md.
O pacote reúne entradas, fontes, referências oficiais, resultados próprios e tentativas reprovadas identificadas.
Use o ambiente e as dependências do repositório completo para reprodução; o binário TELEMAC não está incluído.
A fonte upstream deve corresponder ao commit d1bff193746fd76425d7715a6e4d20d42eb8877e (v8p5r0).
GAIA/Nestor, WAQTEL e tanque com espécie X são componentes de teste distintos; não representam um modelo integrado calibrado do rio.
Nenhum dado de campo, custo observado ou limiar ambiental foi utilizado nos exemplos novos.
''')
    with ZipFile(target) as z:
        if z.testzip() is not None: raise ValueError('Archive integrity failure')
        print(f'{target}: {len(z.namelist())} arquivos, {target.stat().st_size/1e6:.1f} MB; integridade conferida')


if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--out', type=Path, required=True);a=p.parse_args();package(a.out)
