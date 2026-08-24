#!/usr/bin/env python3
"""Validação mecânica da AC — a prova discursiva. Uso: _validar-ac.py "<pasta do ano>"

Existe pelo mesmo motivo do `_validar-at.py`: no 4º e no 5º ano a AC é o único
instrumento, e até 24/08/2026 ela fechava sem nenhuma checagem estrutural.

O que ele confere, e onde a regra está:

  volume e pesos      07 §2 (5 × 10,0) · §3.3.1 (EF1: 10 questões, escada própria)
  AC adaptada         08 §4.1 — 5 questões de 2,0, sem a escada
  perfil na folha     08 §4.4 — a folha do aluno NUNCA diz o perfil
  proibições          07 §1 — sem gabarito, sem "Confira você mesmo:"
  dois espaços        07 §6 — nas alternativas, menos a última do bloco
"""
import re, sys
from pathlib import Path

PERFIS = ["TDAH", "TEA", "DISLEX", "DISCALC"]
ESCADA_EF1 = {0.5, 1.0, 1.5, 2.0}
EF1 = ("4º Ano", "5º Ano")

ano = Path(sys.argv[1]) if len(sys.argv) > 1 else None
if not ano or not ano.exists():
    print(__doc__); sys.exit(1)

provas = sorted(ano.glob("AC*.md"))
if not provas:
    print(f"\n  {ano.name}: nenhuma AC nesta pasta — nada a validar\n"); sys.exit(0)

org = (ano / "_ORGANIZACAO.md")
texto_org = org.read_text(encoding="utf-8") if org.exists() else ""
total_falhas = total_avisos = 0
print(f"\n{'=' * 70}\n  {ano.name} · Avaliação de Conteúdo\n{'=' * 70}")
if not org.exists():
    print("  ✗ _ORGANIZACAO.md nao existe — sem ele nao ha gabarito nem matriz")
    total_falhas += 1

for md in provas:
    falhas, avisos, info = [], [], []
    perfil = next((p for p in PERFIS if md.stem.endswith(f"-{p}")), None)
    linhas = md.read_text(encoding="utf-8").split("\n")
    texto = "\n".join(linhas)

    # --- titulo
    if not (linhas and re.match(r"^#\s+.+—\s*.+$", linhas[0])):
        falhas.append("a primeira linha nao e o titulo '# <Disciplina> — <Ano>'")

    # --- questoes, numeracao e pesos
    qs = [(i, l) for i, l in enumerate(linhas) if l.startswith("### QUEST")]
    nums, pesos = [], []
    for i, l in qs:
        m = re.match(r"### QUEST[ÃA]O (\d+)(?:\s*·\s*\(([\d,\.]+)\))?", l)
        if not m:
            falhas.append(f"L{i+1}: rotulo fora do padrao '### QUESTAO NN · (P,P)': {l!r}"); continue
        if len(m.group(1)) != 2:
            falhas.append(f"L{i+1}: numero sem dois digitos: {l!r}")
        nums.append(int(m.group(1)))
        if not m.group(2):
            falhas.append(f"Q{m.group(1)}: sem o peso entre parenteses no rotulo")
        else:
            pesos.append(float(m.group(2).replace(",", ".")))
    if nums and nums != list(range(1, len(nums) + 1)):
        falhas.append(f"numeracao nao e continua de 01 a {len(nums)}: {nums}")

    # --- soma
    soma = sum(pesos)
    if pesos and abs(soma - 10.0) > 0.001:
        falhas.append(f"os pesos somam {soma:.1f}, e a prova vale 10,0")
    info.append(f"{len(qs)} questoes · soma {soma:.1f}")

    # --- volume e escada, por faixa
    if perfil:
        if len(qs) != 5:
            falhas.append(f"versao adaptada com {len(qs)} questoes — o formato do 08 §4.1 tem 5")
        fora = [p for p in pesos if abs(p - 2.0) > 0.001]
        if fora:
            falhas.append(f"versao adaptada com peso diferente de 2,0: {fora} — 08 §4.1 nao usa a escada")
    elif ano.name in EF1:
        if len(qs) != 10:
            falhas.append(f"AC do EF1 com {len(qs)} questoes — 07 §3.3.1 pede 10")
        fora = sorted({p for p in pesos if p not in ESCADA_EF1})
        if fora:
            falhas.append(f"peso fora da escada do EF1 (0,5 · 1,0 · 1,5 · 2,0): {fora}")
        if pesos and abs(pesos[-1] - 2.0) > 0.001:
            avisos.append("a ultima questao nao vale 2,0 — no EF1 ela e a producao final")
        if re.search(r"folha\s+(a|à)\s+parte", texto, re.I):
            falhas.append("a folha manda 'responder em folha a parte' — isso e da diagramacao "
                          "(_ac-para-pdf.py insere sozinho), nao do markdown")
    else:
        if len(qs) != 5:
            avisos.append(f"AC com {len(qs)} questoes — 07 §2 prevê 5 fora do EF1 (confira o briefing da rodada)")

    # --- proibicoes na folha
    for termo in ["Confira você mesmo", "Gabarito", "Resposta correta", "Rubrica"]:
        if termo.lower() in texto.lower():
            falhas.append(f"contem '{termo}' — nao pode na folha do aluno")
    if re.search(r"letra \*\*[a-d]\*\*", texto):
        falhas.append("parece conter gabarito na folha ('letra **x**')")

    # --- o perfil nunca aparece na folha (08 §4.4)
    if perfil:
        for padrao, nome in [(r"\bTEA\b", "TEA"), (r"\bTDAH\b", "TDAH"),
                             (r"dislexi", "dislexia"), (r"discalculi", "discalculia"),
                             (r"neurodivergen", "neurodivergente")]:
            if re.search(padrao, texto, re.I):
                falhas.append(f"a folha nomeia o perfil ('{nome}') — 08 §4.4 proibe: "
                              f"o perfil vive no nome do arquivo, nunca na folha do aluno")
                break

    # --- alternativas: dois espacos, menos a ultima
    alts = {}
    for i, l in enumerate(linhas):
        if re.match(r"^([a-e])\) ", l):
            qidx = max([j for j, _ in qs if j < i], default=None)
            alts.setdefault(qidx, []).append((i, l[0], l))
    for qidx, itens in alts.items():
        qn = next((n for (j, _), n in zip(qs, nums) if j == qidx), "?")
        for pos, (i, letra, l) in enumerate(itens):
            ultima = pos == len(itens) - 1
            if ultima and l.endswith("  "):
                falhas.append(f"Q{qn} alt {letra}: ULTIMA nao pode terminar em 2 espacos")
            if not ultima and not l.endswith("  "):
                falhas.append(f"Q{qn} alt {letra}: FALTAM os 2 espacos finais")
    if alts:
        info.append(f"{len(alts)} questao(oes) com alternativas")

    # --- campo de resposta digitado (07 §6.1: quem cria o espaco e a diagramacao)
    campos = [i + 1 for i, l in enumerate(linhas) if re.fullmatch(r"[\s_\.\-–—]{8,}", l)]
    if campos:
        avisos.append(f"linha(s) so com traco/underscore — parece campo de resposta digitado: L{campos[:5]}")

    # --- a prova aparece no _ORGANIZACAO
    if texto_org:
        disc = md.stem.split("-", 1)[-1]
        if perfil:
            disc = disc[: -(len(perfil) + 1)] if disc.endswith(f"-{perfil}") else disc
        if disc.lower() not in texto_org.lower():
            avisos.append(f"nao achei '{disc}' no _ORGANIZACAO.md — confira se a grade foi escrita")

    marca = "✗" if falhas else ("~" if avisos else "✓")
    print(f"\n  {marca} {md.name}   ({' · '.join(info)})")
    for x in falhas: print(f"      ✗ {x}")
    for x in avisos: print(f"      ~ {x}")
    total_falhas += len(falhas); total_avisos += len(avisos)

print(f"\n  {len(provas)} prova(s) · {total_falhas} falha(s) · {total_avisos} aviso(s)\n")
sys.exit(1 if total_falhas else 0)
