#!/usr/bin/env python3
"""Confere se esta máquina consegue produzir avaliação — e diz o que falta.

Rode uma vez, antes do primeiro trabalho:   python3 AVALIACAO/_diagnostico.py

Não altera nada. Só olha. Cada linha vermelha vem com o que fazer a respeito.
"""
import shutil, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _ambiente as amb

OK, AVISO, FALHA = "✓", "~", "✗"
achados = []


def item(marca, titulo, detalhe="", conserto=""):
    achados.append((marca, titulo, detalhe, conserto))


# ---------------------------------------------------------------- ambiente
v = sys.version_info
item(OK if v >= (3, 9) else FALHA, f"Python {v.major}.{v.minor}",
     conserto="Instale o Python 3.9 ou mais novo." if v < (3, 9) else "")

nav = amb._procura_chrome()
item(OK if nav else FALHA, "Navegador para gerar PDF", nav or "não encontrado",
     "Instale o Google Chrome, ou aponte o caminho com  export ELEVE_CHROME='...'" if not nav else "")

pdc = amb.pandoc(obrigatorio=False)
item(OK if pdc else AVISO, "pandoc (só o PDF dos mapas precisa)", pdc or "não encontrado",
     "Mac: brew install pandoc  ·  Linux: sudo apt-get install -y pandoc" if not pdc else "")

import platform
if platform.system() == "Darwin":
    item(OK, "Fonte da folha impressa", "Helvetica Neue, do próprio sistema")
else:
    tem = False
    if shutil.which("fc-list"):
        r = subprocess.run(["fc-list"], capture_output=True, text=True)
        tem = "helvetica" in r.stdout.lower()
    item(OK if tem else AVISO, "Fonte da folha impressa",
         "Helvetica encontrada" if tem else "Helvetica não instalada — o PDF sai com fonte substituta",
         "O texto fica correto e a paginação costuma bater, mas as letras não são\n"
         "        idênticas às do PDF gerado num Mac. Para a versão que vai à gráfica,\n"
         "        prefira gerar na máquina onde a fonte existe." if not tem else "")

git = shutil.which("git")
item(OK if git else AVISO, "git (histórico e trabalho em equipe)", git or "não encontrado",
     "Instale o git para conseguir puxar e enviar as mudanças da equipe." if not git else "")

# ---------------------------------------------------------------- projeto
raiz = amb.RAIZ_PROJETO
for pasta, papel in [("METODOLOGIA", "as regras"), ("AVALIACAO", "as provas"),
                     ("CADERNO", "o caderno de casa, usado na checagem de sobreposição")]:
    p = raiz / pasta
    item(OK if p.exists() else FALHA, f"{pasta}/ — {papel}", str(p) if p.exists() else "não existe",
         "Você está fora da pasta do projeto, ou o clone veio incompleto." if not p.exists() else "")

cont = amb.conteudo()
item(OK if cont.exists() else FALHA, "Capítulos-fonte (o insumo de toda prova)",
     str(cont) if cont.exists() else "não encontrados",
     "Sem os capítulos não dá para montar matriz nem escrever questão.\n"
     "        Confira se a pasta CONTEUDO/ veio no clone, ou aponte a sua:\n"
     "        export ELEVE_CONTEUDO='/caminho/para/os/conteudos'" if not cont.exists() else "")

drv = amb.drive(obrigatorio=False)
item(OK if drv else AVISO, "Drive de impressão", str(drv) if drv else "não montado nesta máquina",
     "Só faz falta na hora de publicar. Numa sessão na nuvem, peça ao Claude\n"
     "        para publicar pelo conector do Google Drive." if not drv else "")

if git:
    try:
        r = subprocess.run(["git", "-C", str(raiz), "status", "--porcelain"],
                           capture_output=True, text=True, timeout=10)
        if r.returncode == 0:
            sujos = [l for l in r.stdout.splitlines() if l.strip()]
            item(OK if not sujos else AVISO, "Mudanças ainda não registradas no git",
                 "nenhuma" if not sujos else f"{len(sujos)} arquivo(s) alterado(s)",
                 "Não é problema — só lembre de registrar antes de largar o trabalho." if sujos else "")
    except Exception:
        pass

item(OK, "Responsável (vai no registro de fechamento)", amb.quem())

# ---------------------------------------------------------------- saída
print(f"\n{'=' * 68}\n  Diagnóstico do ambiente · {raiz.name}\n{'=' * 68}\n")
for marca, titulo, detalhe, conserto in achados:
    print(f"  {marca} {titulo}")
    if detalhe:
        print(f"      {detalhe}")
    if conserto:
        print(f"      → {conserto}")
print()

falhas = [a for a in achados if a[0] == FALHA]
avisos = [a for a in achados if a[0] == AVISO]
if falhas:
    print(f"  {len(falhas)} coisa(s) faltando — resolva antes de produzir.\n")
    sys.exit(1)
print(f"  Tudo pronto para produzir{f' ({len(avisos)} aviso[s] acima)' if avisos else ''}.\n")
