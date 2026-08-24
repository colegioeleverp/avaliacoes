# Briefing — reescrita dos mapas para o professor (v2)

> Aprovado em 19/08/2026. **Amostra calibradora:** `7º Ano/_MAPA-Estudos Sociais.md`.

## O que muda em cada `_MAPA-<Disciplina>.md`

**1 · Sai o bloco "Por quê" inteiro.** Ele explicava decisões de produção — por que a questão caiu naquele instrumento, o que se ganhou e se perdeu. Isso é leitura de coordenação e já está no `_ORGANIZACAO.md`. Apagar, não encurtar.

**2 · Entram duas linhas logo abaixo do título de cada capítulo**, nesta ordem e com estes rótulos **exatos**:

```markdown
## Capítulo N — <título>

**O aluno precisa aprender:** <uma frase>

**A avaliação vai verificar se ele:** <uma frase>

| Assunto | Reconhecer | Aplicar | Analisar | Treinou no caderno | Foi medido |
```

**3 · Sai a carga horária do título do capítulo.** Nada de `· 6 aulas` nem `(5 aulas)`. O dado continua no `_ORGANIZACAO.md`, que é onde a matriz o usa.

## Como escrever as duas frases

| Linha | O que é | Como se escreve |
|---|---|---|
| **O aluno precisa aprender** | o objetivo do capítulo, em uma frase | o que o aluno sai sabendo, não a lista de tópicos. Linguagem de conversa, não de ementa |
| **A avaliação vai verificar se ele** | o que as questões **daquele capítulo realmente cobram** | leia a matriz e o gabarito no `_ORGANIZACAO.md` do ano, veja quais questões caíram sobre aquele capítulo e em que profundidade, e descreva a tarefa concreta |

**A segunda linha nunca é promessa genérica.** *"…se compreendeu o conteúdo"* não diz nada. Escreve-se o que a questão pede: *"…explica que o predomínio das estradas vem de uma decisão de governo dos anos 1950 e não de o caminhão ser mais barato"*.

**Capítulo sem questão na prova existe, e se declara:** `**A avaliação vai verificar se ele:** este capítulo não é cobrado na prova deste bloco — ele é trabalhado no caderno de casa.` Não invente cobrança que não existe.

### As três do mapa aprovado, como calibre

> **O aluno precisa aprender:** que moradia, transporte e enchente não atingem a cidade por igual: atingem sempre os mesmos bairros, e há uma razão para isso.
>
> **A avaliação vai verificar se ele:** lê o caso de dois bairros de um mesmo município e explica como a distância até o centro vira desigualdade de oportunidade — e, principalmente, se percebe o que aquele caso **não** permite concluir.

## O que NÃO tocar

- as **tabelas** de Reconhecer / Aplicar / Analisar — nem o conteúdo, nem as colunas, nem a estrela dos essenciais
- as seções **Cobertura** e **O que este mapa mostra** — são de coordenação e ficam no arquivo
- o `AT.md`, o `_ORGANIZACAO.md` e qualquer questão

## Linguagem

**Nenhum código no texto corrido.** Nada de `N1`, `A5`, `OBJ`, `INT`, "rubrica", "matriz", "essencial", "banda". Escreve-se "questão de alternativas", "questão escrita", "o degrau de cima", "o que decide a nota". O professor lê isto; o vocabulário técnico mora no `_ORGANIZACAO.md`.

Na seção **Como ler este mapa**, ajuste o parágrafo de abertura para mencionar as duas linhas novas, como está na amostra.

## Não gerar PDF

Os PDFs saem depois, de uma vez, com `_mapa-para-pdf.py --todos`.
