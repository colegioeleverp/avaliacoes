# Briefing de produção — MODELO

> **O que é isto.** Toda rodada de produção começa com um briefing. A regra está na
> [`METODOLOGIA/07-AVALIACAO.md`](../METODOLOGIA/07-AVALIACAO.md) e não se discute aqui; o briefing
> só resolve **o que a regra deixa em aberto nesta rodada específica** — quais anos, quantas questões,
> de que pasta sai cada bloco, o que fica de fora e por quê.
>
> **Como usar.** Copie este arquivo para `_PRODUCAO-<INSTRUMENTO>-<Bloco>.md`, preencha tudo que
> está entre `⟨ ⟩` e apague as instruções em itálico. O briefing preenchido é o que o agente lê
> antes de produzir — e é ele que, meses depois, explica por que a prova ficou como ficou.
>
> **Não comece a produzir com um `⟨ ⟩` em aberto.** Cada um deles é uma decisão que, se você
> adivinhar, alguém vai ter de desfazer depois. O exemplo real e completo é
> [`_PRODUCAO-AT-Bloco1.md`](_PRODUCAO-AT-Bloco1.md) — abra ao lado deste.

---

## 0. Antes de preencher: o que exige a coordenação

Estas seis perguntas **não se respondem aqui**. Se a rodada esbarrar em alguma, pare e leve à
coordenação — a lista viva está em [`07` §9](../METODOLOGIA/07-AVALIACAO.md#9-lacunas-declaradas).

| Pergunta | Só siga se |
|---|---|
| Quais disciplinas fazem AC nesta série? | houver resposta escrita; não infira pela rodada anterior |
| Quantas questões tem a AC? | os 5 × 10,0 valem enquanto ninguém disser outra coisa |
| A adaptação neurodivergente segue o desenho do [`08`](../METODOLOGIA/08-ADAPTACAO.md)? | a ratificação de §9 tiver saído, ou você registrar que produziu sob a regra em ajuste |
| Peso da prova na nota | `05` §2 reserva 30% para "prova" sem separar AT de AC |
| Inglês entra? | houver conteúdo produzido — hoje não há |
| Recuperação e segunda chamada | estão fora do escopo desta versão da metodologia |

**Regra geral:** ausência de resposta não vira invenção. Registra-se a ausência, produz-se o que dá,
e o que faltou fica nomeado no `_ORGANIZACAO.md` do ano.

---

## 1. Escopo desta rodada

| | |
|---|---|
| **Instrumento** | ⟨AT · AC · AC1 · AC2 — *um por rodada; não misture*⟩ |
| **Bimestre e bloco** | ⟨3º bimestre · Bloco 2⟩ |
| **Anos** | ⟨6º · 7º · 8º · 9º · 1ª · 2ª · 3ª série⟩ |
| **Disciplinas** | ⟨todas as da tabela, ou a lista⟩ |
| **Fora desta rodada** | ⟨o que não entra, e por quê⟩ |
| **Versões adaptadas** | ⟨sim, os 4 perfis · ou só os perfis que existem no ano — ver `_PARAMETROS/perfis-por-ano.md`⟩ |
| **Responsável** | ⟨quem está tocando⟩ |
| **Data de início** | ⟨dd/mm/aaaa⟩ |

*Um agente por ano é o arranjo que funcionou no Bloco 1. Um agente para tudo perde o fio na terceira
disciplina; um por disciplina desperdiça a leitura do bloco inteiro.*

## 2. De que pasta sai cada bloco

*O insumo é `CONTEUDO/<Disciplina>/<Ano>/bl<N>_<Disciplina>_<ano>.md`, e é dele que sai o número de
aulas de cada capítulo — que é o que decide a distribuição do §3. Preencha a linha de cada disciplina
que entra, e diga o que fazer quando um bloco da prova vem de mais de uma pasta.*

| Linha da tabela | Pasta em `CONTEUDO/` | Observação |
|---|---|---|
| ⟨Português⟩ | ⟨`Português/`⟩ | ⟨—⟩ |
| ⟨…⟩ | ⟨…⟩ | ⟨…⟩ |

**Bloco que vem de duas pastas** — como *Geometria e Física* no 6º–9º, ou *Estudos Sociais* no EM
(História + Geografia + Filosofia + Sociologia): dividir as questões pela carga de aulas e
**registrar a divisão** no `_ORGANIZACAO.md`. Divisão não registrada é divisão que ninguém consegue
auditar depois.

## 3. Quantas questões por bloco

*Da tabela da coordenação, em [`_PARAMETROS/`](_PARAMETROS/). Copie os números; não recalcule.*

| Disciplina | ⟨6º–8º⟩ | ⟨9º⟩ | ⟨EM⟩ |
|---|:---:|:---:|:---:|
| ⟨…⟩ | | | |
| **Produzível** | | | |

**Se o total não fechar** o volume previsto (30 · 35 · 40), isso é esperado quando uma disciplina
não tem conteúdo. **Não compense inventando questão em outra disciplina** — registre a diferença.

## 4. Questão de interpretação

*`07` §4.1. Bloco de 2 questões leva 1, nunca 2.*

| Faixa | Por bloco |
|---|:---:|
| ⟨6º–8º⟩ | ⟨1⟩ |
| ⟨9º⟩ | ⟨1⟩ |
| ⟨EM⟩ | ⟨2⟩ |

## 5. Onde escrever

```
AVALIACAO/<Ano>/
├── ⟨AT.md · AC-<Disciplina>.md no EF2/EM · AC1-<Disciplina>.md no 4º e 5º⟩   ← a prova
├── ⟨AT-<PERFIL>.md⟩                     ← as versões adaptadas, se a rodada as inclui
├── _ORGANIZACAO.md                      ← matriz, gabarito, checagens, registro das decisões
└── _MAPA-<Disciplina>.md                ← um por disciplina produzida
```

**Numeração:** ⟨contínua na prova inteira, atravessando as disciplinas (AT) · reiniciando por prova (AC)⟩.

## 6. Cruzamento obrigatório com o caderno

A checagem #6 se faz **contra a folha**, questão a questão, em `CADERNO/<Disciplina>/<Ano>.md` —
e, em **Operações e Física**, em `CADERNO/_DO-DRIVE/<Disciplina>/<Ano>.md`, exportado do Drive em
24/08/2026. Registra-se no `_MAPA`. Mesmo conteúdo, outro caminho — se a prova refizer o exercício da casa,
ela mede a memória do treino, não o aprendizado.

⟨**Disciplinas sem caderno nesta rodada:** … — registrar "sem caderno correspondente" e seguir.
Cuidado: em 22/08/2026 descobriu-se que Operações e Física *tinham* caderno, no Drive, e a
premissa contrária tinha atravessado a rodada inteira. Confirme antes de declarar ausência.⟩

## 7. O que nunca fazer

*Vale para toda rodada. Não edite esta lista — ela é cópia do `07` §8.*

- inventar dado, estatística, fonte, lei ou autor. Todo número real vem do capítulo; caso hipotético vem declarado como hipotético
- usar gabarito na folha do aluno
- escrever `Confira você mesmo:` — isso é do caderno
- pedir consulta, internet, outra pessoa ou material além de lápis, caneta e régua
- distrator absurdo, "todas as anteriores", ou dois distratores que caem pelo mesmo motivo
- esquecer os **dois espaços** no fim das alternativas a), b), c) — a última do bloco não leva

## 8. Fechamento da rodada

Nesta ordem, e nenhuma etapa é opcional:

```bash
python3 AVALIACAO/_validar-at.py "AVALIACAO/<Ano>"      # só onde existe AT.md
python3 AVALIACAO/_validar-ac.py "AVALIACAO/<Ano>"      # onde há AC
python3 AVALIACAO/_validar-mapas.py "AVALIACAO/<Ano>"   # sempre
python3 AVALIACAO/_at-para-pdf.py --todos-adaptadas     # ou _ac-para-pdf.py --todos
python3 AVALIACAO/_mapa-para-pdf.py --todos && python3 AVALIACAO/_organizar-por-disciplina.py
python3 AVALIACAO/_fechar.py --todos --bloco ⟨N⟩       # o portão: 0 falhas ou não imprime
python3 AVALIACAO/_fechar.py --todos --bloco ⟨N⟩ --publicar
```

E registre no `_ORGANIZACAO.md` de cada ano: o que ficou de fora, as divisões de bloco, as exceções
de trava e a data. **Exceção registrada é aceitável; exceção silenciosa não.**
