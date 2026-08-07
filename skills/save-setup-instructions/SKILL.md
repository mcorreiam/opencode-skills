---
name: save-setup-instructions
description: Grava orientações de instalação e configuração no arquivo OPENCODE_SETUP.md, criando-o se não existir (com confirmação). Use quando o usuário pedir para gravar, salvar, registrar ou adicionar orientações/instruções/passos no OPENCODE_SETUP.md ou no arquivo de setup do OpenCode.
compatibility: Requer acesso de escrita ao workspace e ao arquivo OPENCODE_SETUP.md.
metadata:
  target_file: OPENCODE_SETUP.md
  storage: markdown
---

# Save Setup Instructions

Grave orientações de setup do OpenCode no arquivo `OPENCODE_SETUP.md`,
mantendo o formato padronizado do documento.

## Procedimento

1. Localize o arquivo `OPENCODE_SETUP.md`. Procure, nesta ordem, no diretório
   atual, nos diretórios pais até a raiz do workspace e em
   `${HOME}/projects/OPENCODE_SETUP.md`. Leia o arquivo inteiro antes de
   editar; nunca edite com base em leitura parcial.
2. Se o arquivo não existir, pergunte ao usuário se deseja criá-lo. Se ele
   recusar, pare sem criar nada. Se aceitar, crie o arquivo com o cabeçalho
   base abaixo no local escolhido pelo usuário (padrão: raiz do workspace):

       # Setup do OpenCode

       Ao iniciar uma nova instalacao do OpenCode, siga as orientacoes abaixo para configurar o ambiente conforme minhas preferencias.

3. Determine o número da próxima seção analisando os títulos existentes no
   formato `## N. Título`. A nova seção deve receber o próximo número
   sequencial. Se a orientação for sobre um tema já documentado, atualize a
   seção existente em vez de criar uma nova.
4. Se existir uma seção `## Finalizacao`, insira a nova seção imediatamente
   antes dela. Caso contrário, acrescente ao final do arquivo.
5. Escreva a nova seção neste formato:

       ## N. Titulo curto

       Contexto de uma ou duas linhas explicando o que a etapa faz e por que
       e necessaria.

       ```bash
       comando de instalacao ou configuracao
       ```

       Instrucoes de validacao, quando aplicavel:

       ```bash
       comando de verificacao
       ```

       Resultado esperado da validacao.

6. Regras de estilo do documento:
   - Texto em português sem acentos (ex.: `instalacao`, `orientacoes`).
     A única exceção são mensagens literais de saída de ferramentas, que
     devem ser transcritas exatamente como aparecem.
   - Comandos sempre dentro de blocos de código `bash` ou `jsonc`.
   - Todo bloco de código deve ser aberto e fechado corretamente; verifique
     o balanceamento dos delimitadores após editar.
   - Caminhos absolutos dependentes de versão (ex.: versão do Node) devem ser
     resolvidos dinamicamente no comando, nunca fixados.
   - Nunca grave segredos, tokens ou chaves de API no arquivo.

7. Após gravar, releia o arquivo, confirme que a seção foi inserida no local
   correto, que a numeração está sequencial e que não há blocos de código
   abertos sem fechamento. Apresente ao usuário um resumo do que foi gravado.

## Segurança

- Não execute os comandos gravados automaticamente; apenas registre-os no
  arquivo, a menos que o usuário peça explicitamente para executar.
- Não remova nem reescreva seções existentes ao adicionar uma nova, exceto
  quando estiver atualizando a seção correspondente ao tema pedido.
