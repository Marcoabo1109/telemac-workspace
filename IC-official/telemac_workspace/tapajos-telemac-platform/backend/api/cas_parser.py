"""TELEMAC steering syntax. Preserve unknown keywords; validate editable subset."""

import math
import re

DEFAULTS = {
    "LAW OF BOTTOM FRICTION": 3,
    "FRICTION COEFFICIENT": 30.0,
    "VELOCITY DIFFUSIVITY": 2.0,
    "TURBULENCE MODEL": 1,
    "TIME STEP": 2.0,
    "NUMBER OF TIME STEPS": 27000,
    "SOLVER ACCURACY": 1e-4,
    "SOLVER": 1,
    "IMPLICITATION FOR DEPTH": 1.0,
    "IMPLICITATION FOR VELOCITY": 1.0,
}
CHOICES = {
    "LAW OF BOTTOM FRICTION": {
        0: "Nenhum",
        1: "Haaland",
        2: "Chézy",
        3: "Strickler",
        4: "Manning",
        5: "Nikuradse",
        7: "Colebrook",
    },
    "TURBULENCE MODEL": {
        1: "Viscosidade constante",
        2: "Elder",
        3: "k-epsilon",
        4: "Smagorinsky",
        5: "Comprimento de mistura",
        6: "Spalart–Allmaras",
    },
    "SOLVER": {
        1: "Gradiente conjugado",
        2: "Resíduo conjugado",
        3: "Gradiente conjugado normal",
        4: "Erro mínimo",
        6: "CGSTAB",
        7: "GMRES",
        8: "Direto",
    },
}


def parse(text):
    lines = []
    for line in text.splitlines():
        # A slash outside a quoted string begins a TELEMAC comment.
        quote = None
        out = ""
        i = 0
        while i < len(line):
            c = line[i]
            if c in "'\"":
                if quote == c and i + 1 < len(line) and line[i + 1] == c:
                    out += c + c
                    i += 2
                    continue
                quote = None if quote == c else (c if quote is None else quote)
            if c == "/" and quote is None:
                break
            out += c
            i += 1
        lines.append(out)
    clean = "\n".join(lines)
    # Mask quoted content so ':' or '=' inside TITLE never become assignments.
    masked = list(clean)
    quote = None
    i = 0
    while i < len(clean):
        c = clean[i]
        if quote:
            masked[i] = " "
            if c == quote:
                if i + 1 < len(clean) and clean[i + 1] == quote:
                    masked[i + 1] = " "
                    i += 1
                else:
                    quote = None
        elif c in "'\"":
            quote = c
            masked[i] = " "
        i += 1
    if quote:
        raise ValueError("Chaîne non terminée / aspas não fechadas")
    matches = list(re.finditer(r"([A-Za-z][A-Za-z0-9 ()_\-]*)\s*[:=]", "".join(masked)))
    result = {}
    for i, m in enumerate(matches):
        k = " ".join(m.group(1).upper().split())
        raw = (
            clean[
                m.end() : matches[i + 1].start() if i + 1 < len(matches) else len(clean)
            ]
            .strip()
            .rstrip(";")
            .strip()
        )
        if not raw:
            raise ValueError(f"Sem valor: {k}")
        result[k] = raw
    if not result:
        raise ValueError("Nenhuma palavra-chave encontrada")
    return result


def scalar(value):
    return str(value).strip().strip("'\"")


def validate(params):
    for k in DEFAULTS:
        if k not in params:
            continue
        try:
            v = float(scalar(params[k]).replace("D", "E").replace("d", "e"))
        except ValueError:
            raise ValueError(f"{k}: número esperado")
        if not math.isfinite(v):
            raise ValueError(f"{k}: valor não finito")
        if k in CHOICES and v not in CHOICES[k]:
            raise ValueError(f"{k}: opção inválida")
        if k in ("TIME STEP", "SOLVER ACCURACY") and v <= 0:
            raise ValueError(f"{k} deve ser positivo")
        if k == "NUMBER OF TIME STEPS" and (v < 1 or v != int(v)):
            raise ValueError("Número de passos deve ser inteiro positivo")
        if k.startswith("IMPLICITATION") and not 0 <= v <= 1:
            raise ValueError(f"{k} fora de [0,1]")
        if k == "VELOCITY DIFFUSIVITY" and v < 0:
            raise ValueError("Difusividade negativa")
    law = int(float(scalar(params.get("LAW OF BOTTOM FRICTION", 3))))
    if law != 0 and float(scalar(params.get("FRICTION COEFFICIENT", 30))) <= 0:
        raise ValueError("Coeficiente de atrito deve ser positivo")
    # No invented universal calibration bounds: physical plausibility is site dependent.
    return params


def generate(params):
    validate(params)
    lines = []
    for k, v in params.items():
        if not re.fullmatch(r"[A-Z][A-Z0-9 ()_\-]*", k):
            raise ValueError("Palavra-chave inválida")
        if "\n" in str(v) or "\r" in str(v):
            raise ValueError("Valor deve ocupar uma linha")
        lines.append(f"{k} = {v}")
    text = "\n".join(lines) + "\n"
    if set(parse(text)) != set(params):
        raise ValueError("Sintaxe ambígua; use aspas em valores textuais")
    return text
