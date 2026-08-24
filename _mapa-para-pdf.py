#!/usr/bin/env python3
"""Gera o PDF do mapa de avaliação para o professor.

Corta o que é de gestão: cabeçalho de metadados, "Como ler este mapa",
"Cobertura do bloco/capítulo" e "O que este mapa mostra".
Mantém as tabelas de nível por capítulo e os parágrafos de "Por quê".

Uso:  _mapa-para-pdf.py "<caminho do _MAPA-*.md>" [...]
      _mapa-para-pdf.py --todos
"""
import html, re, subprocess, sys, tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
from _ambiente import comando_chrome, pandoc
CORTAR = ("como ler este mapa", "cobertura do bloco", "cobertura do capítulo",
          "o que este mapa mostra")

CSS = """
@page { size: A4 portrait; margin: 16mm 14mm 18mm 14mm;
        @bottom-right { content: counter(page); } }
* { box-sizing: border-box; }
body { font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
       color: #3a3a3a; font-size: 10pt; line-height: 1.5; margin: 0; }
h1 { font-size: 17pt; color: #2D2D2D; margin: 0 0 2mm 0; letter-spacing: -.2px; }
.regua { height: 3px; background: #FF6F3D; width: 46mm; margin: 0 0 7mm 0; border-radius: 2px; }
h2 { font-size: 12pt; color: #2D2D2D; margin: 9mm 0 3mm 0; padding-bottom: 1.5mm;
     border-bottom: 1px solid #e6e6e6; page-break-after: avoid; }
h3 { font-size: 10.5pt; color: #2D2D2D; margin: 6mm 0 2mm 0; page-break-after: avoid; }
table { width: 100%; border-collapse: collapse; font-size: 7.8pt; line-height: 1.35;
        margin: 0 0 4mm 0; page-break-inside: avoid; }
th { background: #f4f6f7; color: #2D2D2D; font-size: 7.2pt; text-transform: uppercase;
     letter-spacing: .4px; text-align: left; padding: 2mm 1.8mm; border-bottom: 1.5px solid #d8dcde; }
td { padding: 2mm 1.8mm; border-bottom: 1px solid #ededed; vertical-align: top; }
tr:nth-child(even) td { background: #fbfcfc; }
td:first-child { font-weight: 600; color: #2D2D2D; width: 17%; }
p { margin: 0 0 3mm 0; }
p.meta { background: #f2fbfb; border-left: 3px solid #1AC2C2; padding: 3mm 4mm;
         margin: 0 0 1.5mm 0; font-size: 10pt; color: #2f4f4f; page-break-after: avoid; }
p.avalia { background: #fff8f5; border-left: 3px solid #FF6F3D; padding: 3mm 4mm;
           margin: 0 0 4mm 0; font-size: 10pt; color: #5a4038; page-break-after: avoid; }
td:first-child { width: 22%; }
div.porque { background: #fff8f5; border-left: 3px solid #FF6F3D; padding: 4mm 4.5mm 1.5mm 4.5mm;
             margin: 3mm 0 5mm 0; font-size: 9.6pt; page-break-inside: avoid; }
div.porque p { margin: 0 0 2.5mm 0; }
blockquote { border-left: 2px solid #1AC2C2; margin: 3mm 0; padding: 0 0 0 4mm; color: #555; }
strong { color: #2D2D2D; }
em { color: #4a4a4a; }
code { font-family: "SF Mono", Menlo, monospace; font-size: 8.5pt; background: #f4f6f7;
       padding: .4mm 1mm; border-radius: 2px; }
ul { margin: 0 0 3mm 0; padding-left: 5mm; }
"""

def filtrar(md: str) -> str:
    linhas, fora, vistos_h2, saida = md.split("\n"), False, False, []
    for l in linhas:
        if l.startswith("## "):
            vistos_h2 = True
            fora = l[3:].strip().lower().rstrip(".").startswith(CORTAR)
            if fora: continue
        if fora: continue
        # cabecalho de metadados: citacoes antes do primeiro ##
        if not vistos_h2 and l.startswith(">"): continue
        saida.append(l)
    t = "\n".join(saida)
    # carga horaria e dado de planejamento da coordenacao: fora do titulo do capitulo
    t = re.sub(r"^(#{2,3} .*?)(?: ·)? ?\(?\d+ aulas\)?\s*$", r"\1", t, flags=re.M)
    return re.sub(r"\n{3,}", "\n\n", t).strip() + "\n"

COLUNAS_FORA = ("treinou no caderno", "foi medido", "treinou", "medido")

def enxugar_tabelas(md: str) -> str:
    """Remove das tabelas as colunas que dizem ONDE se mede, e nao O QUE se aprende."""
    saida, bloco = [], []
    def despejar():
        if not bloco: return
        celulas = [[c.strip() for c in l.strip().strip("|").split("|")] for l in bloco]
        cab = [c.lower().strip("* ") for c in celulas[0]]
        fora = [i for i, c in enumerate(cab) if any(c.startswith(f) for f in COLUNAS_FORA)]
        for orig, cs in zip(bloco, celulas):
            if fora and len(cs) == len(cab):
                cs = [c for i, c in enumerate(cs) if i not in fora]
                saida.append("| " + " | ".join(cs) + " |")
            else:
                saida.append(orig)
        bloco.clear()
    for l in md.split("\n"):
        if l.lstrip().startswith("|"): bloco.append(l)
        else: despejar(); saida.append(l)
    despejar()
    return "\n".join(saida)

def para_html(md: str) -> str:
    frag = subprocess.run([pandoc(), "-f", "markdown", "-t", "html", "--wrap=none"],
                          input=md, capture_output=True, text=True, check=True).stdout
    # agrupa o bloco "Por quê" inteiro — do primeiro paragrafo ate o proximo titulo
    def agrupar(m):
        return '<div class="porque">' + m.group(0) + "</div>"
    frag = re.sub(r"<p><strong>Por quê\.</strong>.*?(?=<h[123]|\Z)", agrupar, frag, flags=re.S)
    frag = frag.replace("<p><strong>O aluno precisa aprender:</strong>",
                        '<p class="meta"><strong>O aluno precisa aprender:</strong>')
    frag = frag.replace("<p><strong>A avaliação vai verificar se ele:</strong>",
                        '<p class="avalia"><strong>A avaliação vai verificar se ele:</strong>')
    frag = re.sub(r"(<h1[^>]*>.*?</h1>)", r'\1<div class="regua"></div>', frag, count=1, flags=re.S)
    return f"<!doctype html><html lang=pt-BR><meta charset=utf-8><style>{CSS}</style><body>{frag}</body></html>"

def gerar(origem: Path) -> Path:
    destino = origem.with_suffix(".pdf")
    pagina = para_html(enxugar_tabelas(filtrar(origem.read_text(encoding="utf-8"))))
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as tmp:
        tmp.write(pagina); caminho = tmp.name
    r = subprocess.run([*comando_chrome(),
                        f"--print-to-pdf={destino}", f"file://{caminho}"],
                       capture_output=True, text=True)
    Path(caminho).unlink(missing_ok=True)
    if not destino.exists(): raise RuntimeError(f"Chrome falhou em {origem.name}: {r.stderr[-400:]}")
    return destino

if __name__ == "__main__":
    args = sys.argv[1:]
    alvos = sorted(RAIZ.glob("*/_MAPA-*.md")) if args == ["--todos"] else [Path(a) for a in args]
    for a in alvos:
        d = gerar(a)
        print(f"  {d.parent.name}/{d.name}  ({d.stat().st_size//1024} KB)")
    print(f"\n{len(alvos)} PDF(s)")
