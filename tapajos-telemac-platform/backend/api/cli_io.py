import math

PRESETS = {"parede": [2, 2, 2], "entrada": [4, 5, 5], "saida": [5, 4, 4]}


def parse(text):
    rows = []
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith(("#", "/")):
            continue
        row = [float(v) for v in line.split()]
        if len(row) != 13 or not all(math.isfinite(v) for v in row):
            raise ValueError("CLI deve conter 13 campos finitos por nó")
        for i in (0, 1, 2, 7, 11, 12):
            if row[i] != int(row[i]):
                raise ValueError("Código e índice devem ser inteiros")
            row[i] = int(row[i])
        if row[11] < 1 or row[12] < 1:
            raise ValueError("Índices de fronteira começam em 1")
        rows.append(row)
    if not rows:
        raise ValueError("CLI vazio")
    if len({r[11] for r in rows}) != len(rows):
        raise ValueError("Nó de fronteira duplicado")
    return rows


def generate(rows):
    text = "\n".join(" ".join(str(v) for v in r) for r in rows) + "\n"
    parse(text)
    return text
