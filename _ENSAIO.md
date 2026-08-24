# O ensaio — o primeiro trabalho de quem chega

> Para o Felipe conduzir, uma vez com cada pessoa nova. Dura uma tarde.
> **A regra do ensaio: você não digita nada e não responde nada que a pasta já responda.**
> Cada vez que você precisar explicar algo que não está escrito em lugar nenhum, isso é um defeito
> do projeto — anote e conserte depois. É essa a medida que o ensaio produz.

## Por que um ensaio, e não uma explicação

Explicar leva vinte minutos e não prova nada. O que prova é a pessoa chegando ao PDF sozinha. Os
sete pontos abaixo são onde a experiência diz que ela vai travar — se travar em algum, o conserto é
no projeto, não na pessoa.

## A tarefa

**Refazer a AC de Ciências do 5º ano tirando o último capítulo**, como se o professor não o tivesse
concluído. É um trabalho real, pequeno, reversível (o git desfaz), e passa por tudo: mapa, matriz,
questão, gabarito, versões adaptadas, validação, PDF.

Se preferir uma tarefa sem consequência nenhuma, mande fazer numa branch: `git checkout -b ensaio`.

## O roteiro, e o que observar em cada passo

| # | O que ela faz | Onde costuma travar | O que isso significa se travar |
|---|---|---|---|
| 1 | clona, abre no Cowork, roda `_diagnostico.py` | falta Chrome ou pandoc; não sabe o que é Terminal | o `SETUP-EQUIPE.md` §5 está incompleto para o perfil dela |
| 2 | lê o `GUIA-EQUIPE.md` e diz, com as próprias palavras, o que vai fazer | não distingue AT de AC | o guia abre com "o que tem aqui" e devia abrir com a diferença entre as duas provas |
| 3 | pede a mudança ao Claude em português comum | escreve um comando em vez de uma frase | ela está tentando programar — mostre o exemplo do guia e deixe repetir |
| 4 | confere o que a prova deixa de medir, no `_MAPA` | vai direto ao `.md` da prova | falta destaque para "peça a revisão pelo mapa" |
| 5 | acompanha o Claude mexer nos quatro arquivos | acha que só a questão mudou | é o erro mais caro da pasta — veja se a rota 2 preveniu |
| 6 | roda o fechamento e lê o resultado | não sabe o que fazer com um aviso | a diferença entre falha e aviso precisa estar clara |
| 7 | registra no git e diz o que mudou | esquece, ou escreve "atualização" | combine a frase: *o que mudou e por quê* |

## Três perguntas ao final — para ela, não sobre ela

1. **Em que momento você quase me chamou?** É o ponto exato onde falta documentação.
2. **O que você fez sem ter certeza de estar certo?** É onde falta um portão, não uma explicação.
3. **O que você não faria sozinha na segunda-feira?** Se sobrar alguma coisa, ela ainda não está
   autônoma — e o que falta é nomeável.

## O critério

A pessoa está pronta quando **fecha uma prova com 0 falhas sem você ter tocado no teclado**. Não é
quando ela entende a metodologia: entender vem com a quinta prova. É quando ela sabe **onde parar e
perguntar** — e a lista do que é decisão da coordenação está no `GUIA-EQUIPE.md` exatamente para isso.

## Depois

Anote no `_ORGANIZACAO.md` do ano o que foi feito no ensaio (mesmo que descartado) e desfaça o que
não vai valer:

```bash
git checkout main && git branch -D ensaio     # se usou branch
```
