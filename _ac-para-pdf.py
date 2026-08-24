#!/usr/bin/env python3
"""Gera o PDF da Avaliação de Conteúdo (AC) a partir do AC-<Disciplina>.md.

Cabeçalho oficial da AC: logo, título, caixa da disciplina, nome do aluno,
ano/série, número da avaliação, nota, bimestre e orientações.
Corpo em coluna única, com espaço pautado para o aluno escrever —
proporcional ao valor da questão (o markdown não traz campo de resposta;
quem cria o espaço é esta diagramação, como manda o 07 §6.1).

Uso:  _ac-para-pdf.py "6º Ano/AC-Ciências.md" [...]
      _ac-para-pdf.py --todos
      _ac-para-pdf.py --todos --avaliacao 2
"""
import base64, html, re, subprocess, sys, tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
from _ambiente import comando_chrome
LOGO = RAIZ / "logo-eleve.png"
TEMPO = {"4º Ano": "1h40", "5º Ano": "1h20"}   # da coordenacao; o resto usa o padrao
TEMPO_PADRAO = "1h20"
LIMITE_FOLHA = 8      # a partir daqui a questao vai para a folha a parte, em vez de pauta

CSS = """
@page { size: A4 portrait; margin: 9mm 11mm 10mm 11mm; }
* { box-sizing: border-box; }
body { font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; color: #2D2D2D;
       font-size: 10pt; line-height: 1.38; margin: 0; }
.cab { display: grid; grid-template-columns: 56px 1fr 152px 96px; gap: 7px 10px; }
.cab img { grid-column: 1; grid-row: 1 / span 2; width: 52px; height: 52px; object-fit: contain; align-self: center; }
.titulo { grid-column: 2; grid-row: 1; border: 1.5px solid #4A4A4A; border-radius: 12px 12px 12px 4px;
          padding: 7px 16px; font-size: 15.5pt; font-weight: 800; letter-spacing: -0.02em; }
.disc { grid-column: 3; grid-row: 1; border: 1.5px solid #4A4A4A; border-radius: 12px; padding: 6px 8px;
        font-size: 11pt; font-weight: 800; text-align: center; text-transform: uppercase;
        display: flex; align-items: center; justify-content: center; line-height: 1.1; }
.nome { grid-column: 2; grid-row: 2; border: 1.5px solid #4A4A4A; border-radius: 4px 10px 10px 10px;
        padding: 6px 14px; font-size: 9.5pt; font-weight: 700; display: flex; align-items: center; }
.ident { grid-column: 3; grid-row: 2; display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
.ident .cx { border: 1.5px solid #4A4A4A; border-radius: 9px; padding: 3px 4px; text-align: center; }
.ident .rot { font-size: 6.8pt; font-weight: 700; color: #4A4A4A; display: block; line-height: 1.2; }
.ident .val { font-size: 12pt; font-weight: 800; line-height: 1.1; }
.nota { grid-column: 4; grid-row: 1 / span 2; display: flex; flex-direction: column; gap: 2px; }
.nota .rot { font-size: 9.5pt; font-weight: 700; }
.nota .caixa { border: 1.5px solid #4A4A4A; border-radius: 9px 12px 12px 12px; flex: 1; min-height: 68px; }
.orient { display: grid; grid-template-columns: 1fr 1.45fr auto; gap: 12px; margin-top: 7px; align-items: start; }
.orient .tag { border: 1.5px solid #4A4A4A; border-radius: 8px; padding: 3px 11px;
               font-size: 9pt; font-weight: 700; width: fit-content; }
.orient ul { margin: 6px 0 0; padding-left: 15px; font-size: 8.5pt; line-height: 1.35; }
.bim { font-size: 11.5pt; font-weight: 800; white-space: nowrap; padding-top: 3px; }
.divisor { border-bottom: 2px solid #2D2D2D; margin: 9px 0 11px; }
.colunas { column-count: 2; column-gap: 19px; column-rule: 1px solid #E4E4E4; }
.base { break-inside: avoid; margin: 0 0 10px; }
.base-tit { font-weight: 800; text-align: center; margin-bottom: 8px; font-size: 10.5pt; }
.base p { margin: 0 0 4px; text-align: justify; }
.base ul { margin: 0 0 6px; padding-left: 16px; }
.colunas > .q:last-child, .colunas > .q.fechada:last-child { column-span: all; break-inside: auto; }
.colunas > .q.curta:last-child { column-span: all; break-inside: avoid; }
.colunas > .q:last-child .pauta div { height: 8.4mm; }
.q { break-inside: avoid-page; margin: 0 0 28px; }
.q.fechada { break-inside: avoid; }
.q .num { font-weight: 800; font-size: 10pt; margin-bottom: 5px; }
.q .num span { font-weight: 600; color: #848484; }
.q p { margin: 0 0 5px; }
.citacao { border-left: 3px solid #C9C9C9; background: #F8F9FA; padding: 5px 10px;
           margin: 0 0 5px; font-style: italic; break-inside: avoid; }
.citacao p:last-child { margin: 0; }
.sub { margin: 0 0 5px; }
.opcoes { display: grid; gap: 3px; margin: 0 0 5px; }
.assoc2 { display: grid; grid-template-columns: 1fr 1.35fr; gap: 10px; margin: 0 0 7px; break-inside: avoid; }
.ct { font-weight: 700; font-size: 8.5pt; border-bottom: 1px solid #D8DCDE; padding-bottom: 2px; margin-bottom: 4px; }
.ci { margin: 0 0 4px; font-size: 9.3pt; line-height: 1.3; }
table.assoc { width: 100%; border-collapse: collapse; font-size: 9pt; margin: 0 0 7px; break-inside: avoid; }
table.assoc th { background: #F2F4F5; text-align: left; padding: 3px 5px; border: 1px solid #D8DCDE; font-size: 8pt; }
table.assoc td { padding: 3px 5px; border: 1px solid #E4E4E4; vertical-align: top; }
.vf { margin: 0 0 4px; padding-left: 2px; }
.col { margin: 0 0 2px; padding-left: 6px; }
.aparte { border: 1.2px solid #4A4A4A; border-radius: 8px; padding: 5px 10px; margin: 5px 0 9px;
          font-size: 9.5pt; font-weight: 700; text-align: center; }
.pauta { margin: 3px 0 8px; }
.pauta div { border-bottom: 1px solid #C9C9C9; height: 6.9mm; }
"""

def inline(t: str) -> str:
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*(?!\s)([^*\n]+?)(?<!\s)\*(?!\*)", r"<em>\1</em>", t)
    return t

def parse(md: str):
    h1 = re.search(r"^#\s+(.+?)\s+—\s+(.+)$", md, re.M)
    disciplina, ano = (h1.group(1).strip(), h1.group(2).strip()) if h1 else ("", "")
    bim = re.search(r"(\d+º Bimestre)", md)
    bimestre = bim.group(1) if bim else ""
    # texto-base: tudo entre o primeiro "## " e a primeira "### QUESTAO"
    base = ""
    m0 = re.search(r"^##\s+(.+)$", md, re.M)
    if m0:
        ini = m0.start()
        mq = re.search(r"^###\s+QUESTÃO", md[ini:], re.M)
        bruto = md[ini:ini + mq.start()] if mq else md[ini:]
        linhas_b = bruto.split("\n")
        titulo = linhas_b[0][3:].strip()
        corpo, tab = [], []
        for l in linhas_b[1:] + [""]:
            l = l.strip()
            if l.startswith("|"):                       # tabela markdown no bloco base
                if not re.fullmatch(r"\|[\s:|-]+\|", l): tab.append(l)
                continue
            if tab:                                     # fecha a tabela acumulada
                cel = [[c.strip() for c in r.strip("|").split("|")] for r in tab]
                cab = "".join(f"<th>{inline(c)}</th>" for c in cel[0])
                res = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in cel[1:])
                corpo.append(f'<table class="assoc"><tr>{cab}</tr>{res}</table>')
                tab = []
            if not l or l.startswith("---"): continue
            if l.startswith("- ") or l.startswith("* "):
                corpo.append(f"<li>{inline(l[2:])}</li>")
            else:
                corpo.append(f"<p>{inline(l)}</p>")
        html_corpo = "".join(corpo).replace("<li>", "<ul><li>", 1)
        if "<li>" in html_corpo: html_corpo = html_corpo.replace("</li><p>", "</li></ul><p>")
        if html_corpo.count("<ul>") > html_corpo.count("</ul>"): html_corpo += "</ul>"
        base = f'<div class="base"><div class="base-tit">{inline(titulo)}</div>{html_corpo}</div>'

    questoes, q = [], None
    linhas, i = md.split("\n"), 0
    while i < len(linhas):
        l = linhas[i]
        m = re.match(r"^###\s+QUESTÃO\s+(\d+)\s*·?\s*\(?([\d,]+)?\)?", l)
        if m:
            q = {"num": m.group(1), "valor": m.group(2) or "", "partes": [], "itens": [], "fechado": False}
            questoes.append(q)
        elif q is not None:
            if l.startswith(">"):
                pars, par = [], []
                while i < len(linhas) and linhas[i].startswith(">"):
                    txt = linhas[i].lstrip("> ").rstrip()
                    if txt: par.append(txt)
                    elif par: pars.append(" ".join(par)); par = []
                    i += 1
                if par: pars.append(" ".join(par))
                q["partes"].append('<div class="citacao">' + "".join(f"<p>{inline(p)}</p>" for p in pars) + "</div>")
                continue
            elif l.lstrip().startswith("|"):                   # tabela markdown (associacao, dados)
                linhas_tab = []
                while i < len(linhas) and linhas[i].lstrip().startswith("|"):
                    linhas_tab.append(linhas[i].strip()); i += 1
                celulas = [[c.strip() for c in r.strip("|").split("|")] for r in linhas_tab]
                celulas = [c for c in celulas if not all(set(x) <= set("-: ") for x in c)]
                if celulas and len(celulas[0]) == 2 and "coluna" in " ".join(celulas[0]).lower():
                    a = [r[0] for r in celulas[1:]]
                    b = [r[1] for r in celulas[1:]]
                    esq = "".join(f'<div class="ci">{inline(x)}</div>' for x in a)
                    dir_ = "".join(f'<div class="ci">(&nbsp;&nbsp;&nbsp;&nbsp;) {inline(x)}</div>' for x in b)
                    q["partes"].append(
                        f'<div class="assoc2"><div><div class="ct">{inline(celulas[0][0])}</div>{esq}</div>'
                        f'<div><div class="ct">{inline(celulas[0][1])}</div>{dir_}</div></div>')
                    q["fechado"] = True
                elif celulas:
                    cab = "".join(f"<th>{inline(c)}</th>" for c in celulas[0])
                    corpo_t = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>"
                                      for r in celulas[1:])
                    q["partes"].append(f'<table class="assoc"><tr>{cab}</tr>{corpo_t}</table>')
                continue
            elif re.match(r"^[a-z]\)\s", l):
                q["itens"].append(l.rstrip())
            elif re.match(r"^\(\s*\)", l):                      # verdadeiro ou falso
                q["fechado"] = True
                q["partes"].append(f'<div class="vf">{inline(l.strip())}</div>')
            elif re.match(r"^\d+\.\s", l):                      # item numerado (V/F ou coluna A)
                mrot = re.match(r"^(\d+\.)\s+(.*)$", l.strip())
                q["fechado"] = True
                q["partes"].append(f'<div class="col"><b>{mrot.group(1)}</b> {inline(mrot.group(2))}</div>')
            elif l.strip() and not l.startswith("---") and not l.startswith("#"):
                q["partes"].append(f"<p>{inline(l.strip())}</p>")
        i += 1
    return disciplina, ano, bimestre, questoes, base

NUM = {"duas":2,"três":3,"tres":3,"quatro":4,"cinco":5,"seis":6,"sete":7,"oito":8,"nove":9,
       "dez":10,"onze":11,"doze":12,"quinze":15,"vinte":20}

def linhas_pedidas(texto: str):
    """Se o comando pede um tamanho, e ele que manda — nao o valor da questao."""
    t = re.sub(r"<[^>]+>", " ", texto).lower()
    def n(x):
        return int(x) if x.isdigit() else NUM.get(x)
    m = re.search(r"(\w+)\s+a\s+(\w+)\s+linhas", t)
    if m and n(m.group(2)): return n(m.group(2)) + 1
    m = re.search(r"(?:de|até|em)\s+(\w+)\s+linhas", t)
    if m and n(m.group(1)): return n(m.group(1)) + 1
    m = re.search(r"(\w+)\s+a\s+(\w+)\s+frases", t)
    if m and n(m.group(2)): return n(m.group(2)) * 2
    return None

def pauta(n: int) -> str:
    """Pauta na propria folha; acima do limite, manda para a folha a parte."""
    if n >= LIMITE_FOLHA:
        return '<div class="aparte">Responda em uma folha à parte.</div>'
    return '<div class="pauta">' + "".join("<div></div>" for _ in range(max(2, n))) + "</div>"

def agrupar_colunas(q):
    """Associacao escrita em duas listas: junta Coluna A e Coluna B lado a lado."""
    partes = q["partes"]
    if any("assoc2" in x for x in partes): return
    kb = next((k for k, x in enumerate(partes) if "Coluna B" in x), None)
    ka = next((k for k, x in enumerate(partes) if "Coluna A" in x), None)
    if ka is None or kb is None or kb <= ka: return
    marca = lambda xs: [x.replace('class="col"', 'class="ci"').replace('class="vf"', 'class="ci"') for x in xs
                        if 'class="col"' in x or 'class="vf"' in x]
    a, b = marca(partes[ka + 1:kb]), marca(partes[kb + 1:])
    if not (a and b): return
    tit = lambda x: re.sub(r"<[^>]+>", "", x).strip()
    q["partes"] = partes[:ka] + [
        f'<div class="assoc2"><div><div class="ct">{tit(partes[ka])}</div>{"".join(a)}</div>'
        f'<div><div class="ct">{tit(partes[kb])}</div>{"".join(b)}</div></div>']
    q["fechado"] = True

def montar(disciplina, ano, bimestre, questoes, base="", avaliacao="", tempo="") -> str:
    logo = base64.b64encode(LOGO.read_bytes()).decode() if LOGO.exists() else ""
    ano_curto = re.sub(r"\s*(Ano|Série)\s*$", "", ano).strip()
    corpo = []
    # a producao final e a ULTIMA questao valendo 2,0 ou mais. Numa prova de pesos
    # iguais (a adaptada do 08) todas valem 2,0, e "vale 2,0" sozinho nao a identifica.
    ultima = questoes[-1]["num"] if questoes else None
    for q in questoes:
        agrupar_colunas(q)
        val = f' <span>({q["valor"]})</span>' if q["valor"] else ""
        cls = "q fechada" if (q["fechado"] or q["itens"]) else "q"
        bloco = [f'<div class="{cls}"><div class="num">QUESTÃO {q["num"]}{val}</div>', *q["partes"]]
        pontos = float(q["valor"].replace(",", ".")) if q["valor"] else 2.0
        itens = q["itens"]
        letras = [x[0] for x in itens]
        # verdadeiro-ou-falso escrito com letras em vez de "( )": e fechado, nao leva pauta
        enunciado = " ".join(q["partes"]).lower()
        vf = ("erdadeir" in enunciado and "als" in enunciado) or ("<strong>v</strong>" in enunciado and "<strong>f</strong>" in enunciado)
        if any(x in enunciado for x in ("coluna a", "associe", "ligue cada", "corresponde a uma",
                                        "complete as", "dentro dos parênteses")):
            q["fechado"] = True

        if vf and not itens:   # V/F escrito com numeros
            bloco = [b.replace('<div class="col"><b>', '<div class="vf"><b>')
                      .replace('</b> ', '</b> (&nbsp;&nbsp;&nbsp;&nbsp;) ', 1) if 'class="col"' in b else b
                     for b in bloco]
            corpo.append("\n".join(bloco) + "</div>")
            continue
        if vf and itens:
            bloco.append("".join(f'<div class="vf">(&nbsp;&nbsp;&nbsp;&nbsp;) {inline(x[3:])}</div>' for x in itens))
            corpo.append("\n".join(bloco) + "</div>")
            continue
        # alternativas de objetiva: exatamente a-d, questao leve, e nenhum item e pergunta
        alternativa = (letras == ["a", "b", "c", "d"] and pontos <= 1.0
                       and not any(x.rstrip().endswith("?") for x in itens))
        if alternativa:
            bloco.append('<div class="opcoes">' + "".join(f"<div>{inline(x)}</div>" for x in itens) + "</div>")
        elif itens and pontos >= 2.0 and q["num"] == ultima:   # producao final com subitens: folha a parte
            for x in itens:
                bloco.append(f'<div class="sub">{inline(x)}</div>')
            bloco.append('<div class="aparte">Responda em uma folha à parte.</div>')
        elif itens and q["fechado"]:      # completar: o aluno escreve na propria lacuna
            for x in itens:
                bloco.append('<div class="sub">%s</div>' % inline(x))
        elif itens:
            por_sub = max(2, round(pontos * 3 / len(itens)))
            for x in itens:
                bloco.append(f'<div class="sub">{inline(x)}</div>{pauta(por_sub)}')
        elif not q["fechado"]:
            pedido = linhas_pedidas(" ".join(q["partes"]))
            n = pedido or round(pontos * 3)
            if pontos >= 2.0 and q["num"] == ultima: n = max(n, LIMITE_FOLHA)   # a producao final e sempre a parte
            bloco.append(pauta(n))
        html_q = "\n".join(bloco)
        if q["num"] == ultima and 'class="pauta"' not in html_q and 'class="aparte"' not in html_q:
            html_q = html_q.replace('<div class="q fechada">', '<div class="q fechada curta">', 1)
        corpo.append(html_q + "</div>")
    tem_aparte = any('class="aparte"' in c for c in corpo)
    item_aparte = ("\n    <li>As questões indicadas devem ser respondidas em uma folha à parte, "
                   "com o número da questão;</li>") if tem_aparte else ""
    return f"""<!doctype html><html lang="pt-BR"><meta charset="utf-8"><style>{CSS}</style><body>
<div class="cab">
  <img src="data:image/png;base64,{logo}" alt="Colégio Eleve">
  <div class="titulo">AVALIAÇÃO DE CONTEÚDO</div>
  <div class="disc">{html.escape(disciplina)}</div>
  <div class="nome">Nome do aluno(a):</div>
  <div class="ident">
    <div class="cx"><span class="rot">Ano/Série:</span><span class="val">{ano_curto}</span></div>
    <div class="cx"><span class="rot">Avaliação:</span><span class="val">{avaliacao or "&nbsp;"}</span></div>
  </div>
  <div class="nota"><div class="rot">Nota:</div><div class="caixa"></div></div>
</div>
<div class="orient">
  <div><div class="tag">Orientações para avaliação:</div><ul>
    <li>Esta avaliação tem o valor total de 10 pontos;</li>
    <li>Atenção ao tempo disponível para a realização da avaliação de {tempo};</li>{item_aparte}
  </ul></div>
  <div><div class="tag">Durante a avaliação:</div><ul>
    <li>Leia atentamente cada questão antes de responder;</li>
    <li>Os erros ortográficos cometidos serão sinalizados e descontados na nota final;</li>
    <li>Utilizar caneta esferográfica preta ou azul;</li>
    <li>Questões objetivas: marque apenas uma alternativa, não rasurar;</li>
    <li>Confira a sua prova antes de entregar.</li>
  </ul></div>
  <div class="bim">{bimestre}</div>
</div>
<div class="divisor"></div>
<div class="colunas">
{base}
{chr(10).join(corpo)}
</div>
</body></html>"""

def gerar(origem: Path, avaliacao="") -> Path:
    destino = origem.with_suffix(".pdf")
    if not avaliacao:
        m = re.match(r"AC(\d+)-", origem.name)
        avaliacao = m.group(1) if m else ""
    # a prova pode estar numa subpasta do ano (ex.: "4º Ano/ADAPTADAS")
    tempo = next((TEMPO[p.name] for p in origem.parents if p.name in TEMPO), TEMPO_PADRAO)
    pagina = montar(*parse(origem.read_text(encoding="utf-8")), avaliacao=avaliacao, tempo=tempo)
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as tmp:
        tmp.write(pagina); caminho = tmp.name
    r = subprocess.run([*comando_chrome(),
                        f"--print-to-pdf={destino}", f"file://{caminho}"], capture_output=True, text=True)
    Path(caminho).unlink(missing_ok=True)
    if not destino.exists(): raise RuntimeError(f"Chrome falhou em {origem.name}: {r.stderr[-400:]}")
    return destino

if __name__ == "__main__":
    args = sys.argv[1:]
    aval = ""
    if "--avaliacao" in args:
        k = args.index("--avaliacao"); aval = args[k + 1]; del args[k:k + 2]
    if not args: print(__doc__); sys.exit(1)
    alvos = sorted(RAIZ.glob("*/AC*-*.md")) if args == ["--todos"] else [Path(a) for a in args]
    for a in alvos:
        d = gerar(a, aval)
        print(f"  {d.parent.name}/{d.name}")
    print(f"\n{len(alvos)} PDF(s)")
