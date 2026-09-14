# 04 — Regras de negócio

| ID | Regra | Onde se aplica |
|---|---|---|
| RN-01 | O uso da plataforma é **gratuito**, mas toda funcionalidade além da página inicial exige conta e login. | RF-01, RF-02 |
| RN-02 | O e-mail é único entre todos os usuários, de qualquer perfil. | RF-01, RF-30, RF-36 |
| RN-03 | A senha deve ter no mínimo 8 caracteres e é guardada somente como hash (ver RNF-01). | RF-01, RF-05 |
| RN-04 | O cliente só acessa o consultor de IA, as recomendações e a sacola depois de concluir o questionário ativo. | RF-12 |
| RN-05 | Existe **um** questionário ativo por vez. Pergunta que já recebeu resposta não é apagada: é desativada, para preservar os perfis já gerados. | RF-07 |
| RN-06 | Toda pergunta tem pelo menos duas alternativas. Pergunta de escolha única aceita uma resposta; de múltipla escolha, uma ou mais. | RF-07, RF-08, RF-09 |
| RN-07 | Perfume importado é identificado pelo ID da API. Reimportar atualiza o perfume em vez de duplicar, **exceto** nos campos já revisados pelo administrador, que prevalecem sobre a API. | RF-13, RF-19 |
| RN-08 | Perfume oculto não aparece no catálogo, na busca nem nas recomendações. Continua visível na sacola de quem já o adicionou, sinalizado como indisponível. | RF-20, RF-22, RF-27 |
| RN-09 | O agente só pode recomendar perfumes visíveis do catálogo, retornados pelas ferramentas do sistema, e deve justificar cada recomendação. Nunca informa preço ou link que não venha de uma oferta ativa. | RF-22, RF-23 |
| RN-10 | Uma loja só publica ofertas depois de aprovada pelo administrador. Loja bloqueada tem todas as ofertas retiradas do ar. | RF-30, RF-32, RF-35 |
| RN-11 | Cada loja tem no máximo uma oferta por perfume. | RF-32 |
| RN-12 | Ao finalizar a sacola, para cada perfume é aberta a oferta **ativa de menor preço** entre as lojas aprovadas; em caso de empate, a atualizada mais recentemente. | RF-28 |
| RN-13 | Todo redirecionamento para uma loja gera um registro de clique com usuário, oferta, data e hora, e origem (sacola, ficha ou recomendação). | RF-28, RF-34, RF-37 |
| RN-14 | Cada recomendação recebe no máximo uma avaliação, com nota inteira de 1 a 5. | RF-24 |
| RN-15 | Cada cliente tem um limite diário de mensagens ao consultor de IA (valor inicial: 30, configurável pelo administrador), para controlar o custo da IA. | RF-21 |
| RN-16 | O sistema não processa pagamento, não guarda dados de cartão e não intermedia a compra. | Todo o sistema |
| RN-17 | Na exclusão da conta, os dados pessoais (nome, e-mail, conversas, respostas e perfil) são apagados. Cliques e avaliações ficam anonimizados, apenas para os indicadores. | RF-06 |
| RN-18 | O agente não dá orientação médica. Perguntas sobre alergia ou sensibilidade de pele recebem a orientação de procurar um profissional de saúde. | RF-21, RF-25 |
