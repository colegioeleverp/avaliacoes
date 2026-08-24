#!/usr/bin/env python3
"""Gera o PDF da Avaliação Teste (AT) de cada turma a partir do AT.md.

Layout: cabeçalho oficial (logo, título, Ano/Série + Turma, Nota,
orientações) e questões em duas colunas, A4.

Coloque este script na raiz da pasta AVALIACAO, com o logo-eleve.png
ao lado dele.

Uso:  _at-para-pdf.py "6º Ano" ["7º Ano" ...]
      _at-para-pdf.py --todos               só a AT regular de cada ano
      _at-para-pdf.py --todos-adaptadas     a regular MAIS as versões por perfil
"""
import base64, html, re, subprocess, sys, tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
from _ambiente import comando_chrome
LOGO = RAIZ / "logo-eleve.png"
TEMPO = "1h20"

CSS = """
@page { size: A4 portrait; margin: 9mm; }
* { box-sizing: border-box; }
body { font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; color: #2D2D2D;
       font-size: 10pt; line-height: 1.45; margin: 0; }
.cab { display: grid; grid-template-columns: auto 1fr auto 96px; gap: 8px 12px; align-items: stretch; }
.cab img { grid-column: 1; grid-row: 1 / span 2; width: 64px; height: 64px; object-fit: contain; align-self: center; }
.titulo { grid-column: 2 / span 2; grid-row: 1; border: 1.5px solid #4A4A4A; border-radius: 14px 14px 14px 4px;
          padding: 10px 18px; display: flex; align-items: baseline; justify-content: space-between; gap: 12px; }
.titulo b { font-size: 19pt; font-weight: 800; letter-spacing: -0.02em; }
.titulo span { font-size: 10.5pt; font-weight: 500; color: #848484; }
.nome { grid-column: 2; grid-row: 2; border: 1.5px solid #4A4A4A; border-radius: 4px 10px 10px 10px;
        padding: 7px 14px; font-size: 10pt; font-weight: 700; display: flex; align-items: center; }
.serie { grid-column: 3; grid-row: 2; border: 1.5px solid #4A4A4A; border-radius: 10px;
         padding: 5px 12px; display: flex; align-items: center; gap: 8px; }
.serie .rotulo { font-size: 8.5pt; font-weight: 700; }
.serie .valor { font-size: 13pt; font-weight: 800; }
.serie .turma { font-size: 8.5pt; font-weight: 700; border-left: 1.5px solid #4A4A4A; padding-left: 8px; }
.serie .linha { display: inline-block; width: 44px; border-bottom: 1.5px solid #4A4A4A; height: 16px; }
.nota { grid-column: 4; grid-row: 1 / span 2; display: flex; flex-direction: column; gap: 2px; }
.nota .rotulo { font-size: 10pt; font-weight: 700; }
.nota .caixa { border: 1.5px solid #4A4A4A; border-radius: 10px 14px 14px 14px; flex: 1; min-height: 84px; }
.orient { display: grid; grid-template-columns: 1fr 1.2fr; gap: 10px; margin-top: 10px; }
.orient .tag { border: 1.5px solid #4A4A4A; border-radius: 8px; padding: 4px 12px;
               font-size: 9.5pt; font-weight: 700; width: fit-content; }
.orient ul { margin: 8px 0 0; padding-left: 16px; font-size: 9pt; line-height: 1.4; }
.divisor { border-bottom: 2px solid #2D2D2D; margin: 12px 0 16px; }
.colunas { column-count: 2; column-gap: 26px; column-rule: 1px solid #E4E4E4; }
.apoio-bloco { break-inside: avoid; margin: 0 0 14px; }
.apoio-bloco p { margin: 0 0 4px; font-size: 8.6pt; }
table.apoio { border-collapse: collapse; margin: 5px 0 7px; font-size: 8pt; }
table.apoio th, table.apoio td { border: 0.6px solid #C9C9C9; padding: 2px 5px; text-align: center; }
.secao { break-after: avoid; font-size: 11.5pt; font-weight: 800; border-bottom: 2px solid #2D2D2D;
         padding-bottom: 3px; margin: 18px 0 12px; }
.colunas > .secao:first-child { margin-top: 0; }
.q { break-inside: avoid; margin: 0 0 16px; }
.q .num { font-weight: 700; margin-bottom: 4px; }
.q p { line-height: 1.28; margin: 0 0 6px; }
.citacao { border-left: 3px solid #C9C9C9; background: #F8F9FA; padding: 6px 10px;
           margin: 0 0 6px; font-style: italic; break-inside: avoid; }
.citacao p { margin: 0 0 6px; } .citacao p:last-child { margin: 0; }
.opcoes { display: grid; gap: 3px; }
pre { font-family: "SF Mono", Menlo, monospace; font-size: 8.5pt; line-height: 1.4;
      background: #F8F9FA; padding: 6px 10px; margin: 0 0 6px; break-inside: avoid; white-space: pre; }
"""

def inline(t: str) -> str:
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*(?!\s)([^*\n]+?)(?<!\s)\*(?!\*)", r"<em>\1</em>", t)
    return t

def parse(md: str):
    """Extrai série, bimestre e a lista de seções [(disciplina, [questões])]."""
    serie = re.search(r"^# .*?—\s*(.+)$", md, re.M)
    serie = serie.group(1).strip() if serie else ""
    serie_curta = re.sub(r"\s*(Ano|Série)\s*$", "", serie).strip()
    bim = re.search(r">\s*\*\*(\d+º Bimestre)", md)
    bimestre = bim.group(1) if bim else ""
    secoes, disciplina, questao, apoio = [], None, None, None
    linhas, i = md.split("\n"), 0
    while i < len(linhas):
        l = linhas[i]
        if l.startswith("## "):
            titulo = l[3:].strip()
            if titulo.lower().startswith("tabela de apoio"):   # 08-ADAPTACAO §3.1.1, perfil DISCALC
                apoio_ls, i = [], i + 1
                while i < len(linhas) and not linhas[i].startswith("## "):
                    apoio_ls.append(linhas[i]); i += 1
                apoio = (titulo, apoio_ls)
                continue
            disciplina = (titulo, [])
            secoes.append(disciplina)
        elif l.startswith("### QUESTÃO"):
            if disciplina is None:   # questao antes de qualquer "## Disciplina"
                raise SystemExit(f"{l.strip()} aparece antes do primeiro bloco '## <Disciplina>'. "
                                 "A folha precisa abrir por disciplina.")
            questao = {"num": l.replace("###", "").replace("QUESTÃO", "").strip(), "partes": [], "opcoes": []}
            disciplina[1].append(questao)
        elif questao is not None:
            if l.startswith("```"):          # gráfico em texto
                bloco = []
                i += 1
                while i < len(linhas) and not linhas[i].startswith("```"):
                    bloco.append(linhas[i]); i += 1
                questao["partes"].append("<pre>" + html.escape("\n".join(bloco)) + "</pre>")
            elif l.startswith(">"):          # citação (pode ter vários parágrafos)
                par, pars = [], []
                while i < len(linhas) and linhas[i].startswith(">"):
                    txt = linhas[i].lstrip("> ").rstrip()
                    if txt.startswith("```"):  # gráfico dentro da citação
                        i += 1; bloco = []
                        while i < len(linhas) and not linhas[i].lstrip("> ").startswith("```"):
                            bloco.append(linhas[i].lstrip("> ")); i += 1
                        if par: pars.append(" ".join(par)); par = []
                        pars.append("<pre>" + html.escape("\n".join(bloco)) + "</pre>")
                    elif txt: par.append(txt)
                    else:
                        if par: pars.append(" ".join(par)); par = []
                    i += 1
                if par: pars.append(" ".join(par))
                corpo = "".join(p if p.startswith("<pre>") else f"<p>{inline(p)}</p>" for p in pars)
                questao["partes"].append(f'<div class="citacao">{corpo}</div>')
                continue
            elif re.match(r"^[a-d]\)\s", l):
                questao["opcoes"].append(inline(l.rstrip()))
            elif l.strip() and not l.startswith("---"):
                questao["partes"].append(f"<p>{inline(l.strip())}</p>")
        i += 1
    return serie_curta, bimestre, secoes, apoio

def montar(serie: str, bimestre: str, secoes, apoio=None) -> str:
    logo = base64.b64encode(LOGO.read_bytes()).decode() if LOGO.exists() else ""
    total = sum(len(qs) for _, qs in secoes)
    nomes = [d for d, _ in secoes]
    lista = ", ".join(nomes[:-1]) + " e " + nomes[-1] if len(nomes) > 1 else nomes[0]
    corpo = []
    if apoio:
        titulo, ls = apoio
        html_ap, tab = [], []
        for x in ls + [""]:
            x = x.strip()
            if x.startswith("|"):
                if not re.fullmatch(r"\|[\s:|-]+\|", x): tab.append(x)
                continue
            if tab:
                cel = [[c.strip() for c in r.strip("|").split("|")] for r in tab]
                cab_t = "".join(f"<th>{inline(c)}</th>" for c in cel[0])
                res = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in cel[1:])
                html_ap.append(f'<table class="apoio">{cab_t and "<tr>"+cab_t+"</tr>" or ""}{res}</table>')
                tab = []
            if x and not x.startswith("---"): html_ap.append(f"<p>{inline(x)}</p>")
        corpo.append('<div class="apoio-bloco"><div class="secao">%s</div>%s</div>' % (html.escape(titulo), "".join(html_ap)))
    for disciplina, questoes in secoes:
        corpo.append(f'<div class="secao">{html.escape(disciplina)}</div>')
        for q in questoes:
            ops = "\n".join(f"<div>{o}</div>" for o in q["opcoes"])
            corpo.append(f'<div class="q"><div class="num">QUESTÃO {q["num"]}</div>\n'
                         + "\n".join(q["partes"])
                         + f'\n<div class="opcoes">\n{ops}\n</div>\n</div>')
    return f"""<!doctype html><html lang="pt-BR"><meta charset="utf-8"><style>{CSS}</style><body>
<div class="cab">
  <img src="data:image/png;base64,{logo}" alt="Colégio Eleve">
  <div class="titulo"><b>AVALIAÇÃO TESTE</b><span>{bimestre}</span></div>
  <div class="nome">Nome do aluno(a):</div>
  <div class="serie"><span class="rotulo">Ano/Série:</span><span class="valor">{serie}</span>
    <span class="turma">Turma:</span><span class="linha"></span></div>
  <div class="nota"><div class="rotulo">Nota:</div><div class="caixa"></div></div>
</div>
<div class="orient">
  <div><div class="tag">Orientações para avaliação:</div><ul>
    <li>Esta avaliação contém {total} questões distribuídas nas disciplinas: {lista};</li>
    <li>Atenção ao tempo disponível para a realização da avaliação e o preenchimento do cartão resposta: {TEMPO};</li>
  </ul></div>
  <div><div class="tag">Durante a avaliação:</div><ul>
    <li>Leia atentamente cada questão antes de responder;</li>
    <li>Utilizar caneta esferográfica preta ou azul no cartão resposta;</li>
    <li>Marque apenas uma alternativa, não rasurar;</li>
    <li>Confira a sua prova antes de entregar.</li>
  </ul></div>
</div>
<div class="divisor"></div>
<div class="colunas">
{chr(10).join(corpo)}
</div>
</body></html>"""

def gerar(pasta: Path, nome: str = "AT") -> Path:
    # nome = "AT" ou "AT-<PERFIL>" (08-ADAPTACAO §3.1.1)
    origem = pasta / (nome + ".md")
    destino = pasta / (nome + ".pdf")
    serie, bimestre, secoes, apoio = parse(origem.read_text(encoding="utf-8"))
    pagina = montar(serie, bimestre, secoes, apoio)
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as tmp:
        tmp.write(pagina); caminho = tmp.name
    r = subprocess.run([*comando_chrome(),
                        f"--print-to-pdf={destino}", f"file://{caminho}"],
                       capture_output=True, text=True)
    Path(caminho).unlink(missing_ok=True)
    if not destino.exists(): raise RuntimeError(f"Chrome falhou em {pasta.name}/{nome}: {r.stderr[-400:]}")
    return destino

if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__); sys.exit(1)
    # --todos gera a AT regular; --todos-adaptadas gera tambem as versoes por perfil
    adaptadas = "--todos-adaptadas" in args
    if adaptadas: args = [a for a in args if a != "--todos-adaptadas"] or ["--todos"]
    if args == ["--todos"]:
        pastas = sorted(p.parent for p in RAIZ.glob("*/AT.md"))
    else:
        pastas = [RAIZ / a for a in args]
    for pasta in pastas:
        if not (pasta / "AT.md").exists():
            print(f"  pulado (sem AT.md): {pasta.name}"); continue
        nomes = ["AT"]
        if adaptadas:
            nomes += sorted(f.stem for f in pasta.glob("AT-*.md"))
        for nome in nomes:
            print(f"  {gerar(pasta, nome)}")
