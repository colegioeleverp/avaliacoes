#!/usr/bin/env python3
"""Valida a reescrita v2 dos mapas. Uso: _validar-mapas.py "<pasta do ano>" [...]"""
import re, sys, unicodedata
from pathlib import Path

APRENDER = "**O aluno precisa aprender:**"
AVALIAR  = "**A avaliação vai verificar se ele:**"
IGNORAR  = ("como ler este mapa", "cobertura", "o que este mapa mostra")
CODIGOS  = re.compile(r"\b(N[123]|A[1-6]|OBJ|INT|RC|RES|EXP|ANA|ERR)\b|rubrica|matriz de especifica", re.I)

def validar(md: Path):
    linhas = md.read_text(encoding="utf-8").split("\n")
    falhas, secoes = [], []
    atual = None
    for i, l in enumerate(linhas):
        if l.startswith("## "):
            if atual: secoes.append(atual)
            atual = {"titulo": l[3:].strip(), "linha": i + 1, "corpo": []}
        elif atual is not None:
            atual["corpo"].append((i + 1, l))
    if atual: secoes.append(atual)

    if "**Por quê.**" in "\n".join(linhas):
        falhas.append("bloco 'Por quê' ainda presente")

    com_tabela = 0
    for s in secoes:
        t = s["titulo"].lower()
        if any(t.startswith(x) for x in IGNORAR): continue
        corpo = "\n".join(l for _, l in s["corpo"])
        if "Reconhecer" not in corpo: continue          # secao sem tabela de niveis
        com_tabela += 1
        if APRENDER not in corpo: falhas.append(f"L{s['linha']} «{s['titulo'][:44]}»: falta '{APRENDER}'")
        if AVALIAR  not in corpo: falhas.append(f"L{s['linha']} «{s['titulo'][:44]}»: falta '{AVALIAR}'")
        if APRENDER in corpo and AVALIAR in corpo and corpo.index(APRENDER) > corpo.index(AVALIAR):
            falhas.append(f"L{s['linha']} «{s['titulo'][:44]}»: as duas linhas estao invertidas")
        if re.search(r"[·(]\s*\d+\s+aulas", s["titulo"]):
            falhas.append(f"L{s['linha']} «{s['titulo'][:44]}»: carga horaria no titulo")

    # codigo tecnico no texto corrido
    for i, l in enumerate(linhas):
        if l.startswith("|") or l.startswith("#") or not l.strip(): continue
        if CODIGOS.search(l):
            falhas.append(f"L{i+1}: codigo tecnico -> {l.strip()[:80]}")

    # a tabela de niveis nao pode ter perdido colunas
    for i, l in enumerate(linhas):
        if "Reconhecer" in l and l.startswith("|"):
            n = len([c for c in l.strip().strip("|").split("|")])
            if n < 6: falhas.append(f"L{i+1}: tabela de niveis com {n} colunas (esperado 6)")
    return com_tabela, falhas

EQUIV = {
 "Operações": {"Operações"},
 "Matemática Financeira": {"Matemática Financeira"},
 "Geometria e Física": {"Geometria e Física", "Geometria", "Física"},
 "Estudos Sociais": {"Estudos Sociais", "História", "Geografia", "Filosofia", "Sociologia"},
}

def cobertura(pasta: Path):
    """Todo bloco da prova tem mapa? Foi assim que o de Quimica da 1a serie escapou."""
    at = pasta / "AT.md"
    if not at.exists(): return []
    blocos = [l[3:].strip() for l in at.read_text(encoding="utf-8").split("\n") if l.startswith("## ")]
    mapas = {m.stem.replace("_MAPA-", "") for m in pasta.glob("_MAPA-*.md")}
    return [f"bloco «{b}» da prova nao tem mapa" for b in blocos if not (EQUIV.get(b, {b}) & mapas)]

def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)

def cobertura_ac(pasta: Path):
    """Toda AC tem mapa? (no EF1 a AC e o unico instrumento, e nao ha AT.md)"""
    mapas = {nfc(m.stem.replace("_MAPA-", "")) for m in pasta.glob("_MAPA-*.md")}
    return [f"AC de «{d}» nao tem mapa" for d in
            (nfc(a.stem.replace("AC-", "")) for a in pasta.glob("AC-*.md")) if d not in mapas]

total_sec = total_falhas = 0
for ano in sys.argv[1:]:
    p = Path(ano)
    print(f"\n{'='*66}\n  {p.name}\n{'='*66}")
    for x in cobertura(p) + cobertura_ac(p):
        print(f"  ✗ {x}"); total_falhas += 1
    for md in sorted(p.glob("_MAPA-*.md")):
        n, f = validar(md)
        total_sec += n; total_falhas += len(f)
        marca = "✓" if not f else "✗"
        print(f"  {marca} {md.stem.replace('_MAPA-',''):<28} {n} capítulos")
        for x in f: print(f"      ✗ {x}")
print(f"\n{total_sec} capítulos verificados · {total_falhas} falhas")
