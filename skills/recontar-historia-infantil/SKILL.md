---
name: recontar-historia-infantil
description: Reconta transcrições literais de histórias inventadas por crianças em histórias infantis organizadas com começo, meio e fim, preservando a voz original. Use quando o usuário colar transcrição de áudio, disser recontar história, organizar história infantil, transformar invenção de criança em livro ou citar o nome da história como ursinho perdido. Não use para criar histórias do zero sem transcrição, para revisão gramatical genérica ou para outros gêneros.
license: CC-BY-4.0
metadata:
  author: marco
  version: 1.0.0
---

# Recontar História Infantil

Transforma transcrição literal de invenção infantil em história organizada com começo, meio e fim, mantendo as ideias e palavras-marca da criança. Responde sempre em PT-BR.

## Instructions

### Step 1: Garimpar os tesouros

Leia a transcrição e liste 5 a 8 tesouros: palavras inventadas, frases engraçadas, nomes, sons e repetições que carregam a voz da criança. Copie cada item literalmente.

Expected output: lista com 5 a 8 itens literais da transcrição prontos para reuso na etapa 3.

### Step 2: Extrair o esqueleto

Preencha os 5 campos usando apenas ideias presentes na transcrição, sem inventar trama nova: quem é o protagonista único, o que ele quer de forma simples e urgente, qual é o conflito central único, quais são as 3 tentativas até o clímax, como o protagonista termina diferente. Se algum campo estiver ausente na transcrição, complete com a opção mais simples compatível com o que a criança disse e marque esse campo com [completei].

Expected output: os 5 campos preenchidos, cada um em 1 frase.

### Step 3: Recontar em começo, meio e fim

Antes de escrever, consulte `references/regras-literatura-infantil.md` para aplicar estrutura, ritmo de leitura em voz alta, refrão repetível, regra das 3 tentativas, solução pela criança e final circular. Escreva 500 a 800 palavras em PT-BR com os 3 blocos rotulados, inclua todos os tesouros da etapa 1 e mantenha 1 protagonista e 1 conflito.

Expected output: história completa nos 3 blocos rotulados contendo todos os tesouros da etapa 1 e 1 refrão repetível.

### Step 4: Entregar no formato

Entregue nesta ordem: título curto no formato Nome mais Problema, história com os blocos Começo, Meio e Fim, seção Preservei listando o que manteve da voz original, seção Ajustei listando 2 a 3 adaptações de clareza. Dê crédito à criança autora.

Expected output: as 5 seções presentes (título, Começo, Meio, Fim, Preservei, Ajustei — título conta como 1 e as demais completam o conjunto).

## Examples

### Example 1: Transcrição bagunçada de áudio

User says: "Tá gravando já. Ursinho perdido. Teve uma família muito distante que morava lá na Inglaterra. Teve um rei, uma rainha e um pequeno de um ano. No Natal ele queria um sinho de pelúcia azul. Perdeu na floresta no piquenique. Um homem pegou e mordeu até rasgar. Ele chorava no colo da mãe todos os dias. Um dia o carteiro trouxe um mapa. Foram com a mãe, acharam o homem, ligaram pra polícia. Viva, o meu está salvo. Enfim."

Actions:

1. Garimpa tesouros: muito muito distante, chorava no colo da mãe todos os dias, Claro filho Bora, Viva o meu está salvo, mordeu mordeu mordeu até rasgar.
2. Extrai o esqueleto: quem é o Pequeno Príncipe, quer o ursinho azul, problema é ursinho perdido e rasgado, tentativas são mapa do carteiro mais ida à floresta mais confronto, mudança é coragem e reencontro.
3. Reconta com refrão cantável e final circular onde o ursinho vai junto a todo piquenique.
4. Entrega título mais 3 blocos mais Preservei mais Ajustei.

Result: História O Ursinho Perdido com começo apresentando família e pedido de Natal, meio com perda mais mordidas mais mapa, fim com resgate e ursinho costurado, seguida das seções Preservei e Ajustei.

## Troubleshooting

### Transcrição curta demais sem meio nem fim

Cause: criança ditou só a ideia inicial. Solution: preencha o esqueleto com a continuação mais simples possível, marque cada campo completado com [completei] e liste esses acréscimos na seção Ajustei.

### Transcrição com vários vilões e subtramas

Cause: criança empolgou e empilhou ideias. Solution: eleja 1 protagonista e 1 conflito do esqueleto, rebaixe o restante a detalhe de cena de uma frase e registre o corte na seção Ajustei.
