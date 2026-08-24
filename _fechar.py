#!/usr/bin/env python3
"""O portão: decide se uma prova pode ser impressa, e registra quem decidiu.

Uso:  python3 AVALIACAO/_fechar.py "6º Ano"
      python3 AVALIACAO/_fechar.py --todos
      python3 AVALIACAO/_fechar.py "4º Ano" --publicar        (copia para o Drive)
      python3 AVALIACAO/_fechar.py --todos --bimestre 3 --bloco 2

Roda os dois validadores, confere o que eles não conferem (gabarito escrito,
PDF mais novo que a folha, versões adaptadas coerentes com a base) e grava um
`_FECHAMENTO.md` na pasta do ano, com data e responsável.

Enquanto houver falha, --publicar não copia nada. É essa a trava que substitui
a revisão manual: prova com falha não chega ao Drive de impressão.
"""
import re, shutil, subprocess, sys, unicodedata
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _ambiente as amb

RAIZ = amb.RAIZ_AVALIACAO
ANOS = ["4º Ano", "5º Ano", "6º Ano", "7º Ano", "8º Ano", "9º Ano",
        "1ª Série", "2ª Série", "3ª Série"]
PERFIS = ["TDAH", "TEA", "DISLEX", "DISCALC"]
# nome interno -> nome que a escola imprime
DISCIPLINA_ESCOLA = {"Matemática EF1": "Matemática", "Matemática 1": "Operações",
                     "Matemática 2 e Física": "Geometria e Física",
                     "Matemática 3": "Matemática Financeira"}


def rotulo_ano(ano: str) -> str:
    """'4º Ano' -> '4ANO' · '1ª Série' -> '1SERIE'"""
    n = re.match(r"(\d+)", ano).group(1)
    return f"{n}SERIE" if "érie" in ano or "erie" in ano else f"{n}ANO"


def nome_impressao(ano: str, arquivo: Path, bimestre: int) -> str:
    """O nome com que a escola imprime: 4ANO_3bimestre_AC1_Matemática_TEA.pdf"""
    base = arquivo.stem                       # AC1-Matemática EF1-TEA  |  AT-TEA  |  AT
    perfil = next((p for p in PERFIS if base.endswith(f"-{p}")), None)
    if perfil:
        base = base[: -(len(perfil) + 1)]
    partes = base.split("-", 1)
    instrumento = partes[0]                   # AT · AC · AC1 · AC2
    disciplina = partes[1] if len(partes) > 1 else None
    if disciplina:
        disciplina = DISCIPLINA_ESCOLA.get(disciplina, disciplina)
    pedacos = [rotulo_ano(ano), f"{bimestre}bimestre", instrumento]
    if disciplina:
        pedacos.append(disciplina)
    if perfil:
        pedacos.append(perfil)
    return "_".join(pedacos) + ".pdf"


def roda(script: str, *args) -> tuple[str, int]:
    r = subprocess.run([sys.executable, str(RAIZ / script), *args],
                       capture_output=True, text=True)
    saida = r.stdout + r.stderr
    n = 0
    m = re.search(r"FALHAS \((\d+)\)", saida)
    if m:
        n = int(m.group(1))
    m = re.search(r"·\s*(\d+) falhas", saida)
    if m:
        n += int(m.group(1))
    m = re.search(r"·\s*(\d+) falha\(s\)", saida)
    if m:
        n += int(m.group(1))
    if "FALHA CRITICA" in saida:
        n += 1
    return saida, n


def questoes(md: Path) -> list[str]:
    return re.findall(r"^###\s+QUEST[ÃA]O\s+(\d+)", md.read_text(encoding="utf-8"), re.M)


def blocos(md: Path) -> list[str]:
    """Os blocos de disciplina — só as seções que de fato têm questão dentro.

    A versão adaptada pode trazer seção a mais que a regular não tem (a
    `## Tabela de apoio` da DISCALC é o caso previsto em `08` §2.1). Seção
    sem questão não é bloco de disciplina e não entra na comparação.
    """
    texto = md.read_text(encoding="utf-8")
    secoes = re.split(r"^##\s+(.+)$", texto, flags=re.M)[1:]
    return [titulo.strip() for titulo, corpo in zip(secoes[::2], secoes[1::2])
            if re.search(r"^###\s+QUEST", corpo, re.M)]


def fechar_ano(ano: str, bimestre: int, bloco: int, publicar: bool):
    pasta = RAIZ / ano
    falhas, avisos, notas = [], [], []
    if not pasta.exists():
        return [f"a pasta {ano} não existe"], [], [], [], []

    provas = sorted([p for p in pasta.glob("*.md")
                     if not p.name.startswith("_")
                     and not any(p.stem.endswith(f"-{x}") for x in PERFIS)])
    adaptadas = sorted([p for p in pasta.glob("*.md")
                        if any(p.stem.endswith(f"-{x}") for x in PERFIS)])
    if not provas:
        return [f"{ano}: nenhuma prova encontrada"], [], [], [], []

    # 1. validadores
    if (pasta / "AT.md").exists():
        saida, n = roda("_validar-at.py", str(pasta))
        notas.append(("validador da AT", saida))
        if n:
            falhas.append(f"o validador da AT acusou {n} falha(s) — veja o relatório abaixo")
    if list(pasta.glob("AC*.md")):
        saida, n = roda("_validar-ac.py", str(pasta))
        notas.append(("validador da AC", saida))
        if n:
            falhas.append(f"o validador da AC acusou {n} falha(s) — veja o relatório abaixo")
    if list(pasta.glob("_MAPA-*.md")):
        saida, n = roda("_validar-mapas.py", str(pasta))
        notas.append(("validador dos mapas", saida))
        if n:
            falhas.append(f"o validador dos mapas acusou {n} falha(s)")
    else:
        falhas.append("nenhum _MAPA-<Disciplina>.md nesta pasta — o professor fica sem a visão da prova")

    # 2. gabarito escrito
    org = pasta / "_ORGANIZACAO.md"
    if not org.exists():
        falhas.append("_ORGANIZACAO.md não existe — sem ele não há gabarito nem matriz")
    else:
        o = org.read_text(encoding="utf-8")
        for prova in provas:
            if prova.name == "AT.md":
                continue
            disc = prova.stem.split("-", 1)[-1]
            if disc.lower() not in o.lower():
                avisos.append(f"{prova.name}: não achei menção a '{disc}' no _ORGANIZACAO.md — confira se a grade dessa prova foi escrita")

    # 3. cada folha tem PDF, e o PDF é mais novo que ela
    for md in provas + adaptadas:
        pdf = md.with_suffix(".pdf")
        if not pdf.exists():
            falhas.append(f"{md.name}: sem PDF gerado")
        elif pdf.stat().st_mtime < md.stat().st_mtime:
            falhas.append(f"{md.name}: o PDF é mais antigo que a folha — regere antes de publicar")

    # 4. versões adaptadas coerentes com a base (08 §3.1.1)
    for base in provas:
        irmas = [p for p in adaptadas if p.stem.startswith(base.stem + "-")]
        faltando = [p for p in PERFIS if not (pasta / f"{base.stem}-{p}.md").exists()]
        if not irmas:
            avisos.append(f"{base.name}: nenhuma versão adaptada — confirme se este ano tem aluno de algum perfil")
        elif faltando:
            avisos.append(f"{base.name}: sem as versões {' · '.join(faltando)}")
        if base.name == "AT.md" and irmas:
            qb, bb = questoes(base), blocos(base)
            for irma in irmas:
                if questoes(irma) != qb:
                    falhas.append(f"{irma.name}: número ou numeração de questões diferente da AT regular "
                                  f"({len(questoes(irma))} vs {len(qb)}) — a adaptada tem de ser comparável")
                if blocos(irma) != bb:
                    falhas.append(f"{irma.name}: os blocos de disciplina não batem com a AT regular")

    # 5. nomes de impressão
    nomes = [(md.with_suffix(".pdf"), nome_impressao(ano, md, bimestre))
             for md in provas + adaptadas if md.with_suffix(".pdf").exists()]

    # 6. publicação
    publicados = []
    if publicar and not falhas:
        destino = amb.drive() / f"{bimestre}º Bimestre - Bloco {bloco}" / ano
        destino.mkdir(parents=True, exist_ok=True)
        for pdf, nome in nomes:
            shutil.copy2(pdf, destino / nome)
            publicados.append(destino / nome)
        # os mapas do professor vão para outra árvore, por disciplina
        mapas_drive = amb.drive() / "MAPAS AVALIAÇÕES"
        for mapa in sorted((RAIZ / "MAPAS").glob(f"*/{ano}.pdf")):
            alvo = mapas_drive / mapa.parent.name
            alvo.mkdir(parents=True, exist_ok=True)
            shutil.copy2(mapa, alvo / mapa.name)
            publicados.append(alvo / mapa.name)
    elif publicar and falhas:
        avisos.append("publicação bloqueada: resolva as falhas acima e rode de novo")

    return falhas, avisos, nomes, publicados, notas


def relatorio(ano, falhas, avisos, nomes, publicados, bimestre, bloco, notas=()):
    agora = datetime.now().strftime("%d/%m/%Y às %H:%M")
    linhas = [f"# Fechamento — {ano}", "",
              f"> Gerado por `_fechar.py` em {agora}, por **{amb.quem()}**.",
              f"> {bimestre}º Bimestre · Bloco {bloco} · impressão como `{bimestre}bimestre`.",
              "> Este arquivo é gerado por script. Não edite à mão — rode o script de novo.", ""]
    if falhas:
        linhas += [f"## ❌ Não pode ser impressa — {len(falhas)} falha(s)", ""]
        linhas += [f"{i}. {f}" for i, f in enumerate(falhas, 1)]
    else:
        linhas += ["## ✅ Pronta para impressão", "",
                   "Os dois validadores passaram, o gabarito está escrito, cada folha tem PDF "
                   "atualizado e as versões adaptadas batem com a regular."]
    linhas.append("")
    if avisos:
        linhas += [f"## Avisos — {len(avisos)}", "",
                   "Não impedem a impressão, mas alguém precisa ter olhado.", ""]
        linhas += [f"- {a}" for a in avisos] + [""]
    if nomes:
        linhas += ["## Nomes de impressão", "", "| Arquivo | Nome no Drive |", "|---|---|"]
        linhas += [f"| `{p.name}` | `{n}` |" for p, n in nomes] + [""]
    if publicados:
        linhas += [f"## Publicado no Drive — {len(publicados)} arquivo(s)", "",
                   f"Destino: `{publicados[0].parent}`", ""]
    if falhas and notas:
        linhas += ["## O que os validadores disseram", ""]
        for titulo, saida in notas:
            linhas += [f"### {titulo}", "", "```", saida.strip(), "```", ""]
    return "\n".join(linhas) + "\n"


if __name__ == "__main__":
    args = sys.argv[1:]
    bimestre = int(args[args.index("--bimestre") + 1]) if "--bimestre" in args else 3
    bloco = int(args[args.index("--bloco") + 1]) if "--bloco" in args else 1
    publicar = "--publicar" in args
    if publicar and "--bloco" not in args:
        print("\n  ✗ --publicar exige --bloco <N>: sem ele a prova iria para a pasta do Bloco 1\n"
              "    no Drive, seja qual for o bloco de verdade.\n", file=sys.stderr)
        sys.exit(2)
    alvos = ANOS if "--todos" in args else [a for a in args if not a.startswith("--")
                                            and not a.isdigit()]
    alvos = [a for a in alvos if (RAIZ / a).exists()]
    if not alvos:
        print(__doc__); sys.exit(1)

    total_falhas = 0
    for ano in alvos:
        falhas, avisos, nomes, publicados, notas = fechar_ano(ano, bimestre, bloco, publicar)
        total_falhas += len(falhas)
        print(f"\n{'=' * 70}\n  {ano}\n{'=' * 70}")
        if falhas:
            print(f"\n  ✗ NÃO PODE SER IMPRESSA — {len(falhas)} falha(s):")
            for f in falhas:
                print(f"    ✗ {f}")
        else:
            print("\n  ✓ pronta para impressão")
        if avisos:
            print(f"\n  avisos ({len(avisos)}):")
            for a in avisos:
                print(f"    ~ {a}")
        if publicados:
            print(f"\n  ✓ {len(publicados)} PDF(s) copiados para {publicados[0].parent}")
        (RAIZ / ano / "_FECHAMENTO.md").write_text(
            relatorio(ano, falhas, avisos, nomes, publicados, bimestre, bloco, notas), encoding="utf-8")
        print(f"\n  relatório em {ano}/_FECHAMENTO.md")

    print(f"\n{'=' * 70}\n  {len(alvos)} ano(s) · {total_falhas} falha(s) no total\n")
    sys.exit(1 if total_falhas else 0)
