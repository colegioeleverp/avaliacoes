#!/usr/bin/env python3
"""Move os PDFs dos mapas das pastas de ano para uma pasta por disciplina.

Os .md continuam nas pastas de ano — sao a fonte, e e la que a coordenacao
cruza caderno e prova. So o PDF, que e o que vai para o professor, se
reorganiza por disciplina.
"""
import shutil, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
DESTINO = RAIZ / "MAPAS"
ANOS = ["4º Ano", "5º Ano", "6º Ano", "7º Ano", "8º Ano", "9º Ano", "1ª Série", "2ª Série", "3ª Série"]
# nomes antigos, caso sobre algum arquivo de rodadas anteriores
# nomes antigos, caso sobre arquivo de rodada anterior
ALIAS = {"Matemática 1": "Operações", "Matemática 3": "Matemática Financeira",
         "Matemática 2 e Física": "Geometria e Física"}

movidos, faltando = [], []
for ano in ANOS:
    pasta = RAIZ / ano
    for md in sorted(pasta.glob("_MAPA-*.md")):
        pdf = md.with_suffix(".pdf")
        disc = md.stem.replace("_MAPA-", "")
        if not pdf.exists():
            faltando.append(f"{ano} / {disc}"); continue
        alvo_dir = DESTINO / ALIAS.get(disc, disc)
        alvo_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(pdf), str(alvo_dir / f"{ano}.pdf"))
        movidos.append((ALIAS.get(disc, disc), ano))

print(f"{len(movidos)} PDFs organizados em {DESTINO.name}/\n")
for d in sorted({d for d, _ in movidos}):
    anos = [a for x, a in movidos if x == d]
    anos.sort(key=lambda a: ANOS.index(a))
    print(f"  {d:<24} {len(anos)}  ·  {' · '.join(anos)}")
if faltando:
    print(f"\n  ⚠ sem PDF gerado ({len(faltando)}): " + " · ".join(faltando))
