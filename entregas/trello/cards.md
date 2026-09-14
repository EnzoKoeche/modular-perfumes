# Trello — Modular Perfumes (1ª Sprint)

Guia para montar o quadro conforme a tarefa **Gestão de Projeto + Controle de Versão (1ª Sprint)**.

## O que a tarefa cobra nos cards

| Exigência do enunciado | Como atender no quadro |
|---|---|
| Card de PBI com etiqueta **PBI** + User Story + Critério de Aceite | Os 5 cards da Sprint 1 abaixo têm a etiqueta `PBI`. A descrição traz COMO/POSSO/PARA e os critérios de aceite. |
| Card com etiqueta de **Sprint 1** ou **Sprint 2** | Etiqueta `Sprint 1` nos 5 cards da sprint; etiqueta `Sprint 2` nos cards sugeridos para a próxima sprint. |
| **Responsável(eis)** | Em cada card, "Membros": adicionar quem faz. Todos os integrantes precisam aparecer em pelo menos um card. |
| **Data de entrega** | Em cada card, "Datas": entrega da Sprint 1 até **19/09/2026** (a apresentação é em 20/09). |
| **Checklists** | Checklist "Critérios de aceite" (CA1, CA2, CA3) e checklist "Tarefas" (ex.: tela, rota, banco, teste). |
| **Evolução do card/tarefa** | Mover os cards entre as listas conforme o trabalho anda, marcar itens do checklist e comentar. O histórico de atividade do card mostra a evolução. |

Depois, para a entrega: deixar o quadro **público** (Menu → Visibilidade → Público), copiar o link e tirar um print em alta resolução do quadro inteiro.

## Listas (nessa ordem)

```
Product Backlog
Sprint 1 Backlog
Em Desenvolvimento
Em Teste
Concluído
```

## Etiquetas

`PBI` (azul) · `Sprint 1` (vermelho) · `Sprint 2` (laranja) · `Cliente` (verde) · `Lojista` (roxo) · `Administrador` (preto)

## Lista "Sprint 1 Backlog" — títulos

**Dica:** colar várias linhas de uma vez em "Adicionar um cartão" oferece "Criar N cartões".

```
US1 – Realizar o cadastro do cliente
US2 – Realizar o login na plataforma
US3 – Responder o questionário de perfil olfativo
US4 – Manter as perguntas do questionário
US5 – Importar os perfumes pela API de catálogo
```

### Descrição de cada card (colar em "Descrição")

**US1 – Realizar o cadastro do cliente** · etiquetas: `PBI`, `Sprint 1`, `Cliente`
```
COMO: Cliente
POSSO: realizar o cadastro na plataforma, informando nome, e-mail e senha.
PARA: ter acesso grátis com login ao consultor olfativo.

CA1 (fluxo principal) — DADO QUE estou na página de cadastro, QUANDO informo nome, e-mail válido e senha com no mínimo 8 caracteres e aciono "Criar conta", ENTÃO o sistema grava a conta com o perfil "cliente", guarda a senha criptografada e me leva ao questionário de perfil olfativo.
CA2 (exceção) — DADO QUE estou na página de cadastro, QUANDO informo um e-mail que já possui conta e aciono "Criar conta", ENTÃO o sistema não cria a conta e exibe a mensagem "Este e-mail já está cadastrado".
CA3 (exceção) — DADO QUE estou na página de cadastro, QUANDO deixo um campo obrigatório vazio ou informo senha com menos de 8 caracteres e aciono "Criar conta", ENTÃO o sistema não envia o formulário e indica o campo que precisa ser corrigido.
```

**US2 – Realizar o login na plataforma** · etiquetas: `PBI`, `Sprint 1`, `Cliente`
```
COMO: Cliente
POSSO: realizar o login na plataforma com e-mail e senha.
PARA: acessar meu perfil olfativo salvo.

CA1 (fluxo principal) — DADO QUE tenho uma conta ativa e já concluí o questionário de perfil, QUANDO informo e-mail e senha corretos e aciono "Entrar", ENTÃO o sistema abre a sessão e me leva à minha página inicial, com o meu perfil olfativo.
CA2 (exceção) — DADO QUE estou na tela de login, QUANDO informo e-mail ou senha incorretos e aciono "Entrar", ENTÃO o sistema exibe "E-mail ou senha inválidos", sem indicar qual dos dois está errado.
CA3 (fluxo alternativo) — DADO QUE ainda não concluí o questionário de perfil, QUANDO faço login com sucesso, ENTÃO o sistema me leva direto ao questionário e bloqueia o consultor de IA até eu concluí-lo.
```

**US3 – Responder o questionário de perfil olfativo** · etiquetas: `PBI`, `Sprint 1`, `Cliente`
```
COMO: Cliente
POSSO: responder o questionário de perfil olfativo.
PARA: ter o meu perfil olfativo salvo e receber recomendações que combinem comigo.

CA1 (fluxo principal) — DADO QUE estou autenticado e existe um questionário ativo, QUANDO respondo todas as perguntas obrigatórias e aciono "Concluir", ENTÃO o sistema grava minhas respostas, gera meu perfil olfativo e libera o acesso ao consultor.
CA2 (exceção) — DADO QUE estou respondendo o questionário, QUANDO aciono "Concluir" com alguma pergunta obrigatória sem resposta, ENTÃO o sistema não conclui o questionário e destaca as perguntas pendentes.
CA3 (fluxo alternativo) — DADO QUE saí da plataforma no meio do questionário, QUANDO faço login novamente, ENTÃO o sistema retoma o questionário a partir da primeira pergunta sem resposta.
```

**US4 – Manter as perguntas do questionário** · etiquetas: `PBI`, `Sprint 1`, `Administrador`
```
COMO: Administrador
POSSO: cadastrar, consultar, alterar e excluir as perguntas do questionário de perfil.
PARA: ter perguntas editáveis que revelem o perfil olfativo de cada cliente.

CA1 (fluxo principal) — DADO QUE estou na gestão do questionário, QUANDO informo o enunciado, o tipo de resposta (única ou múltipla escolha) e ao menos duas alternativas e aciono "Salvar", ENTÃO o sistema grava a pergunta como ativa e a exibe na lista, na ordem definida, com as opções "Alterar" e "Excluir".
CA2 (exceção) — DADO QUE estou cadastrando ou alterando uma pergunta, QUANDO deixo o enunciado vazio ou informo menos de duas alternativas e aciono "Salvar", ENTÃO o sistema não grava a pergunta e exibe "Informe o enunciado e pelo menos duas alternativas".
CA3 (fluxo alternativo) — DADO QUE a pergunta já foi respondida por algum cliente, QUANDO aciono "Excluir", ENTÃO o sistema mantém as respostas existentes, desativa a pergunta e deixa de exibi-la para novos clientes.
```

**US5 – Importar os perfumes pela API de catálogo** · etiquetas: `PBI`, `Sprint 1`, `Administrador`
```
COMO: Administrador
POSSO: importar os perfumes da API externa de catálogo.
PARA: ter a importação automática do catálogo, com foto, notas e acordes, sem cadastro manual.

CA1 (fluxo principal) — DADO QUE a chave de acesso da API está configurada, QUANDO aciono "Importar catálogo", ENTÃO o sistema grava os perfumes com nome, marca, foto, notas e acordes e registra no log a data, a quantidade importada e o status "concluída".
CA2 (exceção) — DADO QUE a API está fora do ar ou recusa a chave de acesso, QUANDO aciono "Importar catálogo", ENTÃO o sistema mantém o catálogo atual e registra no log o status "falhou" com a mensagem de erro.
CA3 (fluxo alternativo) — DADO QUE um perfume já existe no catálogo, QUANDO a importação traz esse mesmo perfume, ENTÃO o sistema atualiza os dados usando o identificador da API, sem duplicar o perfume.
```

### Checklist "Tarefas" sugerido (por card)

```
Tela
Rota e regra no servidor
Gravação e leitura no banco
Teste dos critérios de aceite
```

## Lista "Product Backlog" — títulos

Estes 23 PBIs levam a etiqueta `PBI` e a da persona. Os **5 primeiros** também levam `Sprint 2`.

```
Manter as alternativas e os pesos
Consultar a ficha do perfume
Conversar com o agente consultor
Receber as recomendações personalizadas
Adicionar e remover perfumes da sacola
Buscar perfume do catálogo para ofertar
Solicitar o cadastro da loja parceira
Aprovar ou bloquear loja parceira
Manter as ofertas da loja
Finalizar a sacola abrindo as lojas
Consultar o log de importações
Manter os dados da conta do cliente
Manter os usuários da plataforma
Manter os dados da loja
Pausar ou reativar uma oferta
Avaliar a recomendação recebida
Manter as diretrizes do agente
Revisar a ficha de perfume importada
Ocultar ou reexibir perfume
Consultar as avaliações das recomendações
Consultar os cliques por oferta
Agendar a sincronização do catálogo
Consultar os indicadores de uso
```

**Etiqueta de persona:**
- **Cliente:** ficha, conversar, recomendações, sacola (adicionar/remover e finalizar), dados da conta, avaliar.
- **Lojista:** buscar perfume, cadastro da loja, ofertas, dados da loja, pausar, cliques.
- **Administrador:** alternativas e pesos, aprovar loja, log, usuários, diretrizes, revisar ficha, ocultar, avaliações, sincronização, indicadores.

Depois de criar, cole o link público do quadro no lugar de `[COLAR O LINK DO QUADRO]`, no fim do Artefato 5 da especificação.
