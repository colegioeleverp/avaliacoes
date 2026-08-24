# Briefing de produção — AT · 3º Bimestre · Bloco 1

> Decisões de execução válidas para **todos os anos** desta rodada. Um agente por ano.
> A regra está em [`../METODOLOGIA/07-AVALIACAO.md`](../METODOLOGIA/07-AVALIACAO.md). Este arquivo só resolve o que a regra deixa em aberto na hora de percorrer as disciplinas.

## 1. Escopo desta rodada

**Só a AT.** A Avaliação de Conteúdo não entra agora.
Anos: **6º · 7º · 8º · 9º · 1ª série · 2ª série · 3ª série**.

## 2. De que pasta sai cada bloco da tabela da coordenação

| Linha da tabela da AT | Conteúdo em `~/conteudos-segundo-semestre/` | Observação |
|---|---|---|
| Português | `Português/` | — |
| **Operações** | **`Operações/`** | **confirmado pela coordenação em 19/08/2026.** o nome em uso é **Operações**; *Operações* era o rótulo antigo da tabela da coordenação |
| Geometria e Física | `Geometria/` **+** `Física/` | duas pastas, um bloco só. Dividir as questões entre as duas e registrar a divisão |
| Matemática Financeira | `Matemática Financeira/` | — |
| Ciências / Biologia | `Ciências/` (6º–8º) · `Biologia/` (9º e EM) | — |
| Estudos Sociais | `Estudos Sociais/` (6º–9º) · no EM: `História/` + `Geografia/` + `Filosofia/` + `Sociologia/` | no EM são 4 pastas para um bloco. Distribuir as questões e registrar a divisão |
| Química | `Química/` — só 9º e EM | não existe no 6º–8º, como a própria tabela indica |
| **Inglês** | **`Inglês - Ok/`, no Drive** | ✅ **dentro, desde 24/08/2026. A linha anterior desta tabela estava errada.** Ela dizia *"Inglês não tem conteúdo neste pipeline — ausência definitiva nesta rodada"*, e essa afirmação atravessou a rodada inteira sem ser conferida contra o Drive. A pasta `Inglês - Ok` foi criada em **14/08/2026**, cinco dias **antes** da decisão de 19/08, e traz capítulo-fonte e caderno de atividades do 1º ano à 2ª série do Ensino Médio. **É a terceira vez que a mesma classe de erro aparece nesta rodada** — Operações e Física em 22/08, Inglês agora —, e as três vezes o padrão foi o mesmo: declarar ausência sem abrir o Drive. **Exceção: a 3ª série não tem conteúdo de Inglês**, e a ausência dela é real, conferida arquivo a arquivo |

Arquivo-fonte: `<Disciplina>/<Ano>/bl1_<Disciplina>_<ano>.md`. Ele traz os capítulos do bloco e **o número de aulas de cada um** no cabeçalho — é dali que sai a distribuição do §3.3.

## 3. Quantas questões por bloco

Da tabela da coordenação, em `_PARAMETROS/`:

| Disciplina | 6º–8º | 9º | EM |
|---|:---:|:---:|:---:|
| Português | 5 | 5 | 6 |
| Operações | 5 | 5 | 6 |
| Geometria e Física | 4 | 5 | 5 |
| Matemática Financeira | 2 | 2 | 3 |
| Ciências / Biologia | 5 | 5 | 6 |
| Estudos Sociais | 5 | 5 | 6 |
| Química | — | 4 | 4 |
| Inglês | 4 | 4 | 4 |
| **Produzível** | **30** | **35** | **40** |

**O total fecha 30/35/40 desde 24/08/2026**, quando o bloco de Inglês entrou no 6º, 7º, 8º e 9º ano. Até essa data a prova saía com 26/31/36, por causa da premissa falsa registrada no §2.

⚠️ **A 3ª série continua em 36 de 40, e essa ausência é real.** Não existe conteúdo de Inglês da 3ª série no Drive — nem capítulo, nem caderno —, conferido em 24/08/2026. **A 1ª e a 2ª série têm o conteúdo e ainda não receberam o bloco**: ficaram fora do escopo da rodada de 24/08, que cobriu só o EF2. É pendência aberta, não ausência.

## 4. Questão de interpretação (`07` §4.1)

| Faixa | Por bloco de disciplina |
|---|:---:|
| 6º–8º | **1** |
| 9º | **1** |
| 1ª–3ª série | **2** |

Exceção: bloco de **2 questões** (Matemática Financeira no 6º–8º e no 9º) leva **1**, nunca 2.

## 5. Onde escrever

```
AVALIACAO/<Ano>/
├── AT.md                     ← a prova, blocos na ordem da tabela do §3
├── _ORGANIZACAO.md           ← matriz, gabarito, conferência das 11 checagens
└── _MAPA-<Disciplina>.md     ← um por disciplina produzida
```

**Numeração contínua** na prova inteira, atravessando as disciplinas: o bloco seguinte começa onde o anterior parou.

## 6. Cruzamento obrigatório com o caderno

A checagem #6 se faz **contra a folha**, questão a questão, em `~/ATIVIDADES/CADERNO/<Disciplina>/<Ano>.md`. É no `_MAPA` que ela se registra.

**Disciplinas sem caderno** — ~~Física, Operações~~ e tudo da 3ª série: a checagem #6 não se aplica; registrar "sem caderno correspondente" e seguir.

⚠️ **Corrigido em 22/08 e de novo em 24/08.** Operações e Física **têm** caderno, no Drive, e Inglês também — nos nove anos, menos a 3ª série. A frase riscada acima é o registro do erro, mantida à vista de propósito: **três premissas de ausência foram declaradas nesta rodada sem que ninguém abrisse o Drive, e as três estavam erradas.** Antes de escrever "não existe conteúdo" em qualquer linha deste briefing, procure a pasta.

## 7. O que nunca fazer

- inventar dado, estatística, fonte, lei ou autor. Todo número real vem do capítulo; caso hipotético vem declarado como hipotético
- usar gabarito na folha do aluno
- escrever `Confira você mesmo:` — isso é do caderno
- pedir consulta, internet, outra pessoa ou material além de lápis, caneta e régua
- distrator absurdo, "todas as anteriores", ou dois distratores que caem pelo mesmo motivo
- esquecer os **dois espaços** no fim das alternativas a), b), c) — a última do bloco não leva
