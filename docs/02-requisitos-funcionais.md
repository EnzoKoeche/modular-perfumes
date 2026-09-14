# 02 — Requisitos funcionais

**Convenções**
- **ID** estável: não se reaproveita ID de requisito removido.
- **Prioridade:** `Sprint 1` (já está na sprint), `Alta` (necessária para o produto fazer sentido: consultor + sacola), `Média` (completa o produto) ou `Baixa`.
- **PBI:** item do Canvas PBB de onde o requisito vem. A rastreabilidade completa está em [11-rastreabilidade.md](11-rastreabilidade.md).
- **CRUD:** C = cadastrar, R = consultar/listar, U = alterar, D = excluir ou desativar.

## Módulo ACS — Acesso e conta

| ID | Requisito | Persona | Prioridade | PBI |
|---|---|---|---|---|
| RF-01 | O sistema deve permitir que um visitante crie uma conta de cliente informando nome, e-mail e senha. | Cliente | Sprint 1 | Realizar o cadastro do cliente |
| RF-02 | O sistema deve autenticar qualquer usuário (cliente, curador, lojista, administrador) por e-mail e senha e abrir uma sessão. | Todas | Sprint 1 | Realizar o login na plataforma |
| RF-03 | O sistema deve permitir encerrar a sessão (logout) a qualquer momento. | Todas | Sprint 1 | Realizar o login na plataforma |
| RF-04 | O sistema deve restringir cada tela e cada operação ao perfil de acesso correspondente (`CLIENTE`, `CURADOR`, `LOJISTA`, `ADMIN`). | Todas | Sprint 1 | Realizar o login na plataforma |
| RF-05 | O sistema deve permitir que o cliente consulte e altere os dados da própria conta e altere a senha. **(R, U)** | Cliente | Média | Manter os dados da conta do cliente |
| RF-06 | O sistema deve permitir que o cliente exclua a própria conta, removendo os dados pessoais conforme a RN-17. **(D)** | Cliente | Média | Manter os dados da conta do cliente |

## Módulo QST — Questionário de perfil olfativo

| ID | Requisito | Persona | Prioridade | PBI |
|---|---|---|---|---|
| RF-07 | O sistema deve permitir que o curador cadastre, liste, altere e desative perguntas do questionário, com enunciado, tipo de resposta (única ou múltipla escolha), ordem e obrigatoriedade. **(CRUD)** | Curador | Sprint 1 | Manter as perguntas do questionário |
| RF-08 | O sistema deve permitir que o curador mantenha as alternativas de cada pergunta e o peso de cada alternativa para cada família olfativa. **(CRUD)** | Curador | Alta | Manter as alternativas e os pesos |
| RF-09 | O sistema deve apresentar ao cliente as perguntas ativas do questionário, na ordem definida, e gravar as respostas à medida que ele avança. | Cliente | Sprint 1 | Responder o questionário de perfil olfativo |
| RF-10 | O sistema deve retomar um questionário não concluído a partir da primeira pergunta sem resposta. | Cliente | Sprint 1 | Responder o questionário de perfil olfativo |
| RF-11 | Ao concluir o questionário, o sistema deve gerar o perfil olfativo do cliente: nível de conhecimento e afinidade com cada família olfativa, calculada pelos pesos das alternativas escolhidas. | Cliente | Sprint 1 | Responder o questionário de perfil olfativo |
| RF-12 | O sistema deve bloquear o consultor de IA, a sacola e as recomendações para o cliente que ainda não concluiu o questionário, redirecionando-o ao questionário. | Cliente | Sprint 1 | Responder o questionário de perfil olfativo |

## Módulo CAT — Catálogo

| ID | Requisito | Persona | Prioridade | PBI |
|---|---|---|---|---|
| RF-13 | O sistema deve importar perfumes da API externa de catálogo (nome, marca, foto, gênero, notas por nível e acordes, conforme o que a API fornecer), gravando ou atualizando cada perfume pelo identificador da API. | Administrador | Sprint 1 | Importar os perfumes pela API de catálogo |
| RF-14 | O sistema deve registrar cada importação em log: início, fim, status, quantidade de perfumes incluídos e atualizados, e mensagem de erro quando houver. | Administrador | Sprint 1 | Importar os perfumes pela API de catálogo |
| RF-15 | O sistema deve permitir que o administrador consulte o log de importações. **(R)** | Administrador | Alta | Consultar o log de importações |
| RF-16 | O sistema deve permitir agendar a sincronização periódica do catálogo (ex.: semanal), respeitando os limites da API. | Administrador | Média | Agendar a sincronização do catálogo |
| RF-17 | O sistema deve exibir a ficha do perfume: foto, nome, marca, gênero, notas de saída, corpo e fundo, acordes e as ofertas ativas. | Cliente | Alta | Consultar a ficha do perfume |
| RF-18 | O sistema deve permitir buscar perfumes do catálogo por nome, marca e família olfativa. | Cliente, Lojista, Curador | Alta | Buscar perfume do catálogo para ofertar |
| RF-19 | O sistema deve permitir que o curador altere os dados de uma ficha importada; o campo alterado passa a prevalecer sobre a API (RN-07). **(U)** | Curador | Média | Revisar a ficha de perfume importada |
| RF-20 | O sistema deve permitir que o curador oculte e reexiba um perfume. Perfume oculto não aparece no catálogo nem pode ser recomendado. **(D lógico)** | Curador | Média | Ocultar ou reexibir perfume |

## Módulo IA — Consultor olfativo

| ID | Requisito | Persona | Prioridade | PBI |
|---|---|---|---|---|
| RF-21 | O sistema deve oferecer ao cliente uma conversa em tempo real com o agente consultor, exibindo a resposta à medida que é gerada (streaming) e guardando o histórico da conversa. | Cliente | Alta | Conversar com o agente consultor |
| RF-22 | O agente deve consultar o perfil olfativo do cliente, buscar perfumes no catálogo e consultar ofertas por meio de ferramentas do sistema, sem inventar perfume, preço ou link. | Cliente | Alta | Receber as recomendações personalizadas |
| RF-23 | O sistema deve registrar cada perfume recomendado na conversa, com a posição e a justificativa, e exibi-lo como cartão com foto, botão "ver ficha" e botão "adicionar à sacola". | Cliente | Alta | Receber as recomendações personalizadas |
| RF-24 | O sistema deve permitir que o cliente avalie uma recomendação com nota de 1 a 5 e comentário opcional. **(C)** | Cliente | Média | Avaliar a recomendação recebida |
| RF-25 | O sistema deve permitir que o curador mantenha as diretrizes do agente (regras, limites e tom de voz), aplicadas às conversas seguintes. **(CRUD)** | Curador | Média | Manter as diretrizes do agente |
| RF-26 | O sistema deve permitir que o curador consulte as avaliações das recomendações, com filtro por nota e período. **(R)** | Curador | Média | Consultar as avaliações das recomendações |

## Módulo SAC — Sacola e redirecionamento

| ID | Requisito | Persona | Prioridade | PBI |
|---|---|---|---|---|
| RF-27 | O sistema deve permitir que o cliente adicione e remova perfumes da sacola e liste o que está nela. **(C, R, D)** | Cliente | Alta | Adicionar e remover perfumes da sacola |
| RF-28 | Ao finalizar a sacola, o sistema deve levar o cliente, em uma aba nova para cada perfume, à página da oferta escolhida pela RN-12, registrando um clique por redirecionamento. A página de finalização lista também um botão "Ir para a loja" por perfume, porque navegadores bloqueiam várias abas abertas por um único clique (ver R-05). | Cliente | Alta | Finalizar a sacola abrindo as lojas |
| RF-29 | Quando um perfume da sacola não tiver oferta ativa, o sistema deve informar "sem loja disponível no momento" e mantê-lo na sacola. | Cliente | Alta | Finalizar a sacola abrindo as lojas |

## Módulo LOJ — Lojista parceiro

| ID | Requisito | Persona | Prioridade | PBI |
|---|---|---|---|---|
| RF-30 | O sistema deve permitir que um lojista solicite o cadastro informando os dados de acesso e os da loja (nome, CNPJ, site); a loja nasce com o status "pendente". **(C)** | Lojista | Média | Solicitar o cadastro da loja parceira |
| RF-31 | O sistema deve permitir que o lojista consulte e altere os dados da própria loja. **(R, U)** | Lojista | Média | Manter os dados da loja |
| RF-32 | O sistema deve permitir que o lojista cadastre, liste, altere e exclua ofertas, cada uma ligando um perfume do catálogo a um link de produto e a um preço. **(CRUD)** | Lojista | Alta | Manter as ofertas da loja |
| RF-33 | O sistema deve permitir que o lojista pause e reative uma oferta sem excluí-la. | Lojista | Média | Pausar ou reativar uma oferta |
| RF-34 | O sistema deve mostrar ao lojista o total de cliques por oferta em um período. **(R)** | Lojista | Média | Consultar os cliques por oferta |

## Módulo ADM — Administração

| ID | Requisito | Persona | Prioridade | PBI |
|---|---|---|---|---|
| RF-35 | O sistema deve permitir que o administrador aprove ou bloqueie uma loja parceira, registrando quem fez e quando. | Administrador | Média | Aprovar ou bloquear loja parceira |
| RF-36 | O sistema deve permitir que o administrador cadastre, liste, altere e desative usuários de qualquer perfil. **(CRUD)** | Administrador | Média | Manter os usuários da plataforma |
| RF-37 | O sistema deve exibir indicadores de uso: cadastros, questionários concluídos, conversas, mensagens e tokens consumidos pela IA, recomendações e cliques por loja, por período. | Administrador | Baixa | Consultar os indicadores de uso |

## Resumo de CRUD por entidade

| Entidade | Quem mantém | C | R | U | D |
|---|---|---|---|---|---|
| Usuário (conta) | Cliente (a própria) / Administrador (todas) | RF-01, RF-36 | RF-05, RF-36 | RF-05, RF-36 | RF-06, RF-36 |
| Pergunta do questionário | Curador | RF-07 | RF-07 | RF-07 | RF-07 (desativa) |
| Alternativa e peso | Curador | RF-08 | RF-08 | RF-08 | RF-08 |
| Perfume | Administrador (importa) / Curador (revisa) | RF-13 | RF-17, RF-18 | RF-19 | RF-20 (oculta) |
| Diretriz do agente | Curador | RF-25 | RF-25 | RF-25 | RF-25 |
| Loja | Lojista / Administrador | RF-30 | RF-31 | RF-31, RF-35 | RF-35 (bloqueia) |
| Oferta | Lojista | RF-32 | RF-32 | RF-32, RF-33 | RF-32 |
| Item da sacola | Cliente | RF-27 | RF-27 | — | RF-27 |
| Avaliação de recomendação | Cliente | RF-24 | RF-26 | — | — |
