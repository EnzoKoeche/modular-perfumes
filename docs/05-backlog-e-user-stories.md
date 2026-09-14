# 05 — Backlog (PBB) e user stories

Canvas PBB em alta resolução: [`entregas/pbb/Modular_Perfumes_Canvas_PBB_Sprint1.png`](../entregas/pbb/Modular_Perfumes_Canvas_PBB_Sprint1.png). Os PBIs com borda vermelha são da Sprint 1.

## Features por persona

| Persona | Features |
|---|---|
| Cliente | Conta e Perfil Olfativo · Consultor Olfativo por IA · Sacola e Compra nas Lojas |
| Lojista Parceiro | Cadastro da Loja · Gestão de Ofertas · Relatório de Cliques |
| Administrador | Questionário de Perfil · Catálogo via API · Gestão da Plataforma |

## Product Backlog (28 PBIs)

A ordem é a sugerida para as sprints. A Sprint 1 monta a base (acesso, questionário e catálogo); a Sprint 2 entrega o valor principal (consultor + sacola); as seguintes completam os papéis de lojista e administrador.

| # | PBI | Persona | Sprint sugerida | RF |
|---|---|---|---|---|
| 1 | Realizar o cadastro do cliente | Cliente | **1** | RF-01 |
| 2 | Realizar o login na plataforma | Todas | **1** | RF-02, RF-03, RF-04 |
| 3 | Manter as perguntas do questionário | Administrador | **1** | RF-07 |
| 4 | Responder o questionário de perfil olfativo | Cliente | **1** | RF-09 a RF-12 |
| 5 | Importar os perfumes pela API de catálogo | Administrador | **1** | RF-13, RF-14 |
| 6 | Manter as alternativas e os pesos | Administrador | 2 | RF-08 |
| 7 | Consultar a ficha do perfume | Cliente | 2 | RF-17 |
| 8 | Conversar com o agente consultor | Cliente | 2 | RF-21 |
| 9 | Receber as recomendações personalizadas | Cliente | 2 | RF-22, RF-23 |
| 10 | Adicionar e remover perfumes da sacola | Cliente | 2 | RF-27 |
| 11 | Buscar perfume do catálogo para ofertar | Lojista | 3 | RF-18 |
| 12 | Solicitar o cadastro da loja parceira | Lojista | 3 | RF-30 |
| 13 | Aprovar ou bloquear loja parceira | Administrador | 3 | RF-35 |
| 14 | Manter as ofertas da loja | Lojista | 3 | RF-32 |
| 15 | Finalizar a sacola abrindo as lojas | Cliente | 3 | RF-28, RF-29 |
| 16 | Consultar o log de importações | Administrador | 3 | RF-15 |
| 17 | Manter os dados da conta do cliente | Cliente | 4 | RF-05, RF-06 |
| 18 | Manter os usuários da plataforma | Administrador | 4 | RF-36 |
| 19 | Manter os dados da loja | Lojista | 4 | RF-31 |
| 20 | Pausar ou reativar uma oferta | Lojista | 4 | RF-33 |
| 21 | Avaliar a recomendação recebida | Cliente | 4 | RF-24 |
| 22 | Manter as diretrizes do agente | Administrador | 4 | RF-25 |
| 23 | Revisar a ficha de perfume importada | Administrador | 5 | RF-19 |
| 24 | Ocultar ou reexibir perfume | Administrador | 5 | RF-20 |
| 25 | Consultar as avaliações das recomendações | Administrador | 5 | RF-26 |
| 26 | Consultar os cliques por oferta | Lojista | 5 | RF-34 |
| 27 | Agendar a sincronização do catálogo | Administrador | 5 | RF-16 |
| 28 | Consultar os indicadores de uso | Administrador | 5 | RF-37 |

> Na Sprint 1 os perfumes entram pela importação da API (PBI 5), então o catálogo não depende de cadastro manual. O PBI 3 dá ao administrador o CRUD das perguntas para que o PBI 4 tenha o que o cliente responder. Até o PBI 6 entrar, as alternativas podem vir de uma carga inicial no banco.

**Objetivo da Sprint 1:** o cliente cria a conta, faz login e responde o questionário de perfil; o administrador monta o questionário; o catálogo é importado da API.

---

## User stories da Sprint 1

Padrão pedido na disciplina: **COMO** (persona do PBB) · **POSSO** (PBI) · **PARA** (benefício da feature). Critérios de aceite: **CA1** = fluxo principal; **CA2** = tratamento de problema (exceção); **CA3** = outro fluxo alternativo ou de exceção.

### US1 — PBI: Realizar o cadastro do cliente

**COMO** Cliente, **POSSO** realizar o cadastro na plataforma, informando nome, e-mail e senha, **PARA** ter acesso grátis com login ao consultor olfativo.

*Feature:* Conta e Perfil Olfativo

| # | Tipo | Dado que | Quando | Então |
|---|---|---|---|---|
| CA1 | fluxo principal | estou na página de cadastro | informo nome, e-mail válido e senha com no mínimo 8 caracteres e aciono "Criar conta" | o sistema grava a conta com o perfil "cliente", guarda a senha criptografada e me leva ao questionário de perfil olfativo. |
| CA2 | exceção | estou na página de cadastro | informo um e-mail que já possui conta e aciono "Criar conta" | o sistema não cria a conta e exibe a mensagem "Este e-mail já está cadastrado". |
| CA3 | exceção | estou na página de cadastro | deixo um campo obrigatório vazio ou informo senha com menos de 8 caracteres e aciono "Criar conta" | o sistema não envia o formulário e indica o campo que precisa ser corrigido. |

### US2 — PBI: Realizar o login na plataforma

**COMO** Cliente, **POSSO** realizar o login na plataforma com e-mail e senha, **PARA** acessar meu perfil olfativo salvo.

*Feature:* Conta e Perfil Olfativo

| # | Tipo | Dado que | Quando | Então |
|---|---|---|---|---|
| CA1 | fluxo principal | tenho uma conta ativa e já concluí o questionário de perfil | informo e-mail e senha corretos e aciono "Entrar" | o sistema abre a sessão e me leva à minha página inicial, com o meu perfil olfativo. |
| CA2 | exceção | estou na tela de login | informo e-mail ou senha incorretos e aciono "Entrar" | o sistema exibe "E-mail ou senha inválidos", sem indicar qual dos dois está errado. |
| CA3 | fluxo alternativo | ainda não concluí o questionário de perfil | faço login com sucesso | o sistema me leva direto ao questionário e bloqueia o consultor de IA até eu concluí-lo. |

### US3 — PBI: Responder o questionário de perfil olfativo

**COMO** Cliente, **POSSO** responder o questionário de perfil olfativo, **PARA** ter o meu perfil olfativo salvo e receber recomendações que combinem comigo.

*Feature:* Conta e Perfil Olfativo

| # | Tipo | Dado que | Quando | Então |
|---|---|---|---|---|
| CA1 | fluxo principal | estou autenticado e existe um questionário ativo | respondo todas as perguntas obrigatórias e aciono "Concluir" | o sistema grava minhas respostas, gera meu perfil olfativo e libera o acesso ao consultor. |
| CA2 | exceção | estou respondendo o questionário | aciono "Concluir" com alguma pergunta obrigatória sem resposta | o sistema não conclui o questionário e destaca as perguntas pendentes. |
| CA3 | fluxo alternativo | saí da plataforma no meio do questionário | faço login novamente | o sistema retoma o questionário a partir da primeira pergunta sem resposta. |

### US4 — PBI: Manter as perguntas do questionário

**COMO** Administrador, **POSSO** cadastrar, consultar, alterar e excluir as perguntas do questionário de perfil, **PARA** ter perguntas editáveis que revelem o perfil olfativo de cada cliente.

*Feature:* Questionário de Perfil

| # | Tipo | Dado que | Quando | Então |
|---|---|---|---|---|
| CA1 | fluxo principal | estou na gestão do questionário | informo o enunciado, o tipo de resposta (única ou múltipla escolha) e ao menos duas alternativas e aciono "Salvar" | o sistema grava a pergunta como ativa e a exibe na lista, na ordem definida, com as opções "Alterar" e "Excluir". |
| CA2 | exceção | estou cadastrando ou alterando uma pergunta | deixo o enunciado vazio ou informo menos de duas alternativas e aciono "Salvar" | o sistema não grava a pergunta e exibe "Informe o enunciado e pelo menos duas alternativas". |
| CA3 | fluxo alternativo | a pergunta já foi respondida por algum cliente | aciono "Excluir" | o sistema mantém as respostas existentes, desativa a pergunta e deixa de exibi-la para novos clientes. |

### US5 — PBI: Importar os perfumes pela API de catálogo

**COMO** Administrador, **POSSO** importar os perfumes da API externa de catálogo, **PARA** ter a importação automática do catálogo, com foto, notas e acordes, sem cadastro manual.

*Feature:* Catálogo via API

| # | Tipo | Dado que | Quando | Então |
|---|---|---|---|---|
| CA1 | fluxo principal | a chave de acesso da API está configurada | aciono "Importar catálogo" | o sistema grava os perfumes com nome, marca, foto, notas e acordes e registra no log a data, a quantidade importada e o status "concluída". |
| CA2 | exceção | a API está fora do ar ou recusa a chave de acesso | aciono "Importar catálogo" | o sistema mantém o catálogo atual e registra no log o status "falhou" com a mensagem de erro. |
| CA3 | fluxo alternativo | um perfume já existe no catálogo | a importação traz esse mesmo perfume | o sistema atualiza os dados usando o identificador da API, sem duplicar o perfume. |

---

## Definition of Done (proposta)

- Os critérios de aceite da história passam em teste manual e, quando houver regra de negócio, em teste automatizado.
- As telas funcionam no celular (RNF-20) e as rotas checam o perfil de acesso no servidor (RNF-03).
- As migrations do banco estão no repositório e o README explica como rodar.
- O card do Trello foi para "Concluído" com o checklist de critérios de aceite marcado.
