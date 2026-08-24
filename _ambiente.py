#!/usr/bin/env python3
"""Resolve o que muda de uma máquina para outra: navegador, pandoc e Drive.

Os scripts desta pasta nasceram num Mac só, com o caminho do Chrome escrito
à mão. Este módulo existe para que qualquer pessoa da equipe rode os mesmos
scripts sem editar código — no próprio computador (Mac, Windows ou Linux) ou
numa sessão do Cowork na nuvem.

Nada aqui decide conteúdo. Só descobre onde as ferramentas estão.

Ordem de resolução do navegador (o primeiro que existir vence):
  1. a variável de ambiente ELEVE_CHROME, se você quiser mandar num caminho
  2. Chrome ou Chromium instalado no sistema
  3. o Chromium que já vem no container do Cowork

Pasta do Drive de impressão:
  1. a variável de ambiente ELEVE_DRIVE
  2. o Google Drive Desktop montado, de qualquer conta @colegioeleve.com.br
"""
import os, shutil, subprocess, sys
from pathlib import Path

RAIZ_AVALIACAO = Path(__file__).resolve().parent
RAIZ_PROJETO = RAIZ_AVALIACAO.parent

# ---------------------------------------------------------------- navegador

CANDIDATOS_CHROME = [
    # macOS
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    # Linux e container do Cowork
    "/opt/pw-browsers/chromium",
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    # Windows
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]

GLOBS_CHROME = [
    ("/opt/pw-browsers", "chromium*/chrome-linux/chrome"),
    ("/opt/pw-browsers", "chromium*/chrome"),
]


def _procura_chrome():
    if os.environ.get("ELEVE_CHROME"):
        p = Path(os.environ["ELEVE_CHROME"])
        if p.exists():
            return str(p)
        _erro(f"ELEVE_CHROME aponta para {p}, que não existe.")
    for c in CANDIDATOS_CHROME:
        if Path(c).exists():
            return c
    for base, padrao in GLOBS_CHROME:
        b = Path(base)
        if b.exists():
            for achado in sorted(b.glob(padrao)):
                return str(achado)
    for nome in ("google-chrome", "chromium", "chromium-browser", "chrome"):
        achado = shutil.which(nome)
        if achado:
            return achado
    return None


def chrome():
    """O executável do navegador que gera os PDFs. Erra explicando o que fazer."""
    achado = _procura_chrome()
    if achado:
        return achado
    _erro(
        "Não encontrei o Chrome nesta máquina, e é ele que imprime o PDF.\n"
        "  · No Mac ou no Windows: instale o Google Chrome e rode de novo.\n"
        "  · Se ele está instalado num lugar fora do comum, aponte o caminho:\n"
        "      export ELEVE_CHROME='/caminho/para/o/chrome'\n"
        "  · Numa sessão do Cowork na nuvem o Chromium já vem instalado —\n"
        "    se este erro apareceu lá, rode  python3 AVALIACAO/_diagnostico.py"
    )


def comando_chrome(*extras):
    """A chamada do navegador já com as opções de impressão e as travas do ambiente.

    O --no-sandbox só entra quando o script roda como root num Linux, que é o
    caso do container do Cowork. Sem ele o Chromium recusa a abrir por lá.
    """
    cmd = [chrome(), "--headless=new", "--disable-gpu", "--no-pdf-header-footer"]
    if os.name == "posix" and sys.platform.startswith("linux") and os.geteuid() == 0:
        cmd.append("--no-sandbox")
    return cmd + list(extras)


# ------------------------------------------------------------------- pandoc

def pandoc(obrigatorio=True):
    """O conversor de markdown que o gerador de mapas usa."""
    achado = shutil.which("pandoc") or os.environ.get("ELEVE_PANDOC")
    if achado and Path(shutil.which(achado) or achado).exists():
        return achado
    if not obrigatorio:
        return None
    _erro(
        "O pandoc não está instalado, e é ele que converte o mapa em PDF.\n"
        "  · Mac:     brew install pandoc\n"
        "  · Linux:   sudo apt-get install -y pandoc\n"
        "  · Windows: winget install --id JohnMacFarlane.Pandoc\n"
        "Só o gerador de mapas precisa dele. Os outros scripts rodam sem."
    )


# -------------------------------------------------------------------- Drive

RAIZ_DRIVE_REL = "Drives compartilhados/Conteudos - Colégio Eleve/Avaliações"


def drive(obrigatorio=True):
    """A pasta de impressão no Drive compartilhado, como pasta local."""
    if os.environ.get("ELEVE_DRIVE"):
        p = Path(os.environ["ELEVE_DRIVE"]).expanduser()
        if p.exists():
            return p
        if obrigatorio:
            _erro(f"ELEVE_DRIVE aponta para {p}, que não existe.")
        return None
    base = Path.home() / "Library/CloudStorage"
    if base.exists():
        for conta in sorted(base.glob("GoogleDrive-*@colegioeleve.com.br")):
            alvo = conta / RAIZ_DRIVE_REL
            if alvo.exists():
                return alvo
    if not obrigatorio:
        return None
    _erro(
        "Não achei a pasta do Drive de impressão nesta máquina.\n"
        "  · Se você usa o Google Drive para Desktop, abra-o e espere sincronizar.\n"
        "  · Se a pasta está em outro lugar, aponte o caminho:\n"
        f"      export ELEVE_DRIVE='.../{RAIZ_DRIVE_REL}'\n"
        "  · Numa sessão do Cowork na nuvem não existe Drive montado: peça ao\n"
        "    Claude para publicar pelo conector do Google Drive."
    )


# ------------------------------------------------------------------- pessoa

def quem():
    """Quem está fechando a prova — vai para o _FECHAMENTO.md do ano."""
    for chave in ("ELEVE_RESPONSAVEL", "GIT_AUTHOR_NAME"):
        if os.environ.get(chave):
            return os.environ[chave]
    try:
        r = subprocess.run(["git", "-C", str(RAIZ_PROJETO), "config", "user.name"],
                           capture_output=True, text=True, timeout=5)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    except Exception:
        pass
    return os.environ.get("USER") or os.environ.get("USERNAME") or "não identificado"


# -------------------------------------------------------------------- geral

def _erro(msg):
    print(f"\n  ✗ {msg}\n", file=sys.stderr)
    sys.exit(2)


def conteudo(disciplina=None, ano=None):
    """A pasta dos capítulos-fonte. Dentro do projeto, ou fora dele por variável."""
    if os.environ.get("ELEVE_CONTEUDO"):
        base = Path(os.environ["ELEVE_CONTEUDO"]).expanduser()
    elif (RAIZ_PROJETO / "CONTEUDO").exists():
        base = RAIZ_PROJETO / "CONTEUDO"
    else:
        base = Path.home() / "conteudos-segundo-semestre"
    if disciplina:
        base = base / disciplina
    if ano:
        base = base / ano
    return base


if __name__ == "__main__":
    print(f"navegador : {_procura_chrome() or 'NÃO ENCONTRADO'}")
    print(f"pandoc    : {pandoc(obrigatorio=False) or 'NÃO ENCONTRADO'}")
    print(f"drive     : {drive(obrigatorio=False) or 'não montado'}")
    print(f"conteúdo  : {conteudo()}  {'(existe)' if conteudo().exists() else '(NÃO EXISTE)'}")
    print(f"responsável: {quem()}")
