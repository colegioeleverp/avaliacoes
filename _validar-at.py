#!/usr/bin/env python3
"""Validacao mecanica da AT. Uso: validar_at.py "<pasta do ano>" """
import re, sys, unicodedata
from pathlib import Path

ano = Path(sys.argv[1])
falhas, avisos, info = [], [], []

at = ano / "AT.md"
if not at.exists():
    print(f"FALHA CRITICA: {at} nao existe"); sys.exit(1)
linhas = at.read_text(encoding="utf-8").split("\n")
texto = "\n".join(linhas)

# --- blocos e questoes
blocos = [(i, l[3:].strip()) for i, l in enumerate(linhas) if l.startswith("## ")]
qs = [(i, l) for i, l in enumerate(linhas) if l.startswith("### QUEST")]
info.append(f"blocos: {len(blocos)} -> {', '.join(b for _, b in blocos)}")
info.append(f"questoes: {len(qs)}")

# numeracao continua e com zero a esquerda
nums = []
for i, l in qs:
    m = re.match(r"### QUEST[ÃA]O (\d+)", l)
    if not m: falhas.append(f"L{i+1}: rotulo fora do padrao '### QUESTAO NN': {l!r}"); continue
    if len(m.group(1)) != 2: falhas.append(f"L{i+1}: numero sem dois digitos: {l!r}")
    nums.append(int(m.group(1)))
if nums and nums != list(range(1, len(nums) + 1)):
    falhas.append(f"numeracao nao e continua de 01 a {len(nums)}: {nums}")

# --- alternativas
alts, COMPR = {}, {}
for i, l in enumerate(linhas):
    m = re.match(r"^([a-d])\) ", l)
    if m:
        qidx = max([j for j, _ in qs if j < i], default=None)
        alts.setdefault(qidx, []).append((i, m.group(1), l))
for qidx, itens in alts.items():
    qnum = next((n for (j, _), n in zip(qs, nums) if j == qidx), "?")
    letras = [x[1] for x in itens]
    if letras != ["a", "b", "c", "d"]:
        falhas.append(f"Q{qnum}: alternativas fora do padrao a-b-c-d: {letras}")
    for pos, (i, letra, l) in enumerate(itens):
        tem2 = l.endswith("  ")
        ultima = pos == len(itens) - 1
        if ultima and tem2: falhas.append(f"Q{qnum} alt {letra}: ULTIMA nao pode terminar em 2 espacos")
        if not ultima and not tem2: falhas.append(f"Q{qnum} alt {letra}: FALTAM os 2 espacos finais")
    comprimentos = [len(x[2].rstrip()) - 3 for x in itens]
    if comprimentos and min(comprimentos) >= 25 and max(comprimentos) > 2.0 * min(comprimentos):
        avisos.append(f"Q{qnum}: alternativas em prosa muito desiguais ({min(comprimentos)}-{max(comprimentos)} car.) — pista de forma")
    COMPR[qnum] = {x[1]: len(x[2].rstrip()) - 3 for x in itens}
info.append(f"questoes com 4 alternativas: {sum(1 for v in alts.values() if len(v)==4)}/{len(qs)}")

# --- questoes de interpretacao (tem citacao > antes das alternativas)
interp = 0
for (i, _), n in zip(qs, nums):
    fim = next((j for j, _ in qs if j > i), len(linhas))
    if any(l.startswith("> ") for l in linhas[i:fim]): interp += 1
info.append(f"questoes com suporte citado (interpretacao): {interp}")

# --- proibicoes na folha
for termo in ["Confira você mesmo", "Gabarito", "Resposta correta", "Rubrica"]:
    if termo.lower() in texto.lower(): falhas.append(f"AT.md contem '{termo}' — nao pode na folha do aluno")
if re.search(r"letra \*\*[a-d]\*\*", texto): falhas.append("AT.md parece conter gabarito ('letra **x**')")
if re.search(r"todas as anteriores|nenhuma das anteriores", texto, re.I):
    falhas.append("AT.md contem 'todas/nenhuma das anteriores' — proibido (07 §8.4)")

# --- _ORGANIZACAO
org = ano / "_ORGANIZACAO.md"
if not org.exists(): falhas.append("_ORGANIZACAO.md nao existe")
else:
    o = org.read_text(encoding="utf-8")
    for q in nums:
        if not re.search(rf"\|\s*{q}\s*\|", o) and not re.search(rf"\|\s*0?{q}\s*\|", o):
            avisos.append(f"Q{q:02d} pode nao ter linha na grade do _ORGANIZACAO.md")
    if "11" not in o: avisos.append("_ORGANIZACAO.md nao menciona as 11 checagens")
    # distribuicao da chave de resposta
    chave = re.findall(r"^\|\s*\d+\s*\|\s*\**\s*([a-d])\s*\**\s*\|", o, re.M)
    if chave:
        from collections import Counter
        c = Counter(chave)
        info.append(f"chave: {' · '.join(f'{k} {c[k]}' for k in 'abcd')} (n={len(chave)})")
        maior = max(c.values())
        if maior > 0.45 * len(chave):
            falhas.append(f"chave viciada: letra '{c.most_common(1)[0][0]}' em {maior} de {len(chave)} questoes (>45%)")
        seq, run = 1, 1
        for a, b in zip(chave, chave[1:]):
            run = run + 1 if a == b else 1
            seq = max(seq, run)
        if seq >= 4: avisos.append(f"chave com {seq} respostas iguais seguidas")
        # a alternativa correta e a mais longa?
        mais_longa = 0
        for qn, letra in zip(nums, chave):
            c = COMPR.get(qn)
            if not c or letra not in c: continue
            certa = c[letra]; outras = sorted((v for k, v in c.items() if k != letra), reverse=True)
            if outras and certa > outras[0] * 1.3 and certa - outras[0] >= 12:
                mais_longa += 1
                avisos.append(f"Q{qn:02d}: a alternativa correta ({letra}) e a mais longa por folga ({certa} vs {outras[0]} car.) — pista de forma")
        if mais_longa > 0.25 * len(chave):
            falhas.append(f"pista de forma sistemica: a correta e a mais longa em {mais_longa} de {len(chave)} questoes")
    else:
        avisos.append("nao consegui ler a chave de resposta no _ORGANIZACAO.md")

# --- mapas: sem codigo tecnico no texto corrido
mapas = sorted(ano.glob("_MAPA-*.md"))
info.append(f"mapas: {len(mapas)} -> {', '.join(m.stem.replace('_MAPA-','') for m in mapas)}")
CODIGOS = re.compile(r"\b(N[123]|A[1-6]|OBJ|INT|RC|RES|EXP|ANA|ERR)\b|rubrica", re.I)
for m in mapas:
    for i, l in enumerate(m.read_text(encoding="utf-8").split("\n")):
        if l.startswith("|") or l.startswith("#"): continue
        if CODIGOS.search(l):
            falhas.append(f"{m.name} L{i+1}: codigo tecnico no texto corrido -> {l.strip()[:90]}")

print(f"\n{'='*70}\n  {ano.name}\n{'='*70}")
for x in info:    print(f"  · {x}")
if avisos:
    print(f"\n  AVISOS ({len(avisos)}):")
    for x in avisos: print(f"    ~ {x}")
if falhas:
    print(f"\n  FALHAS ({len(falhas)}):")
    for x in falhas: print(f"    ✗ {x}")
else:
    print("\n  ✓ nenhuma falha mecanica")
