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
| **Inglês** | **não existe** | ❌ **fora, e confirmado em 19/08/2026: Inglês não tem conteúdo neste pipeline.** Não é pendência a resolver — é ausência definitiva nesta rodada. Registrar e seguir |

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
| ~~Inglês~~ | ~~4~~ | ~~4~~ | ~~4~~ |
| **Produzível** | **26** | **31** | **36** |

O total da prova **não fecha** 30/35/40 nesta rodada, por causa de Inglês. Isso é esperado e vai registrado — não compense inventando questões em outra disciplina.

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

**Disciplinas sem caderno** — Física, Operações e tudo da 3ª série: a checagem #6 não se aplica; registrar "sem caderno correspondente" e seguir.

## 7. O que nunca fazer

- inventar dado, estatística, fonte, lei ou autor. Todo número real vem do capítulo; caso hipotético vem declarado como hipotético
- usar gabarito na folha do aluno
- escrever `Confira você mesmo:` — isso é do caderno
- pedir consulta, internet, outra pessoa ou material além de lápis, caneta e régua
- distrator absurdo, "todas as anteriores", ou dois distratores que caem pelo mesmo motivo
- esquecer os **dois espaços** no fim das alternativas a), b), c) — a última do bloco não leva
