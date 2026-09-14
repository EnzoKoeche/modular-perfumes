# 11 — Rastreabilidade

Liga cada objetivo de negócio às features, aos PBIs, aos requisitos e às tabelas que o sustentam. Serve para responder, em qualquer mudança, "o que mais precisa mudar junto?".

## Objetivos → features

| Objetivo | Features que atendem |
|---|---|
| **O1** — Descobrir perfumes que combinam com o perfil (questionário + agente) | Conta e Perfil Olfativo · Questionário de Perfil · Consultor Olfativo por IA · Diretrizes do Agente IA |
| **O2** — Catálogo completo e confiável, importado e revisado | Catálogo via API · Curadoria do Catálogo |
| **O3** — Levar o cliente às lojas parceiras | Sacola e Compra nas Lojas · Cadastro da Loja · Gestão de Ofertas · Relatório de Cliques |
| Suporte a todos | Gestão de Usuários · Indicadores da Plataforma |

## PBI → requisitos → tabelas

| PBI | Obj. | RF | RN / RNF | Tabelas |
|---|---|---|---|---|
| Realizar o cadastro do cliente | O1 | RF-01 | RN-01, RN-02, RN-03, RNF-01, RNF-08 | `usuario` |
| Realizar o login na plataforma | O1 | RF-02, RF-03, RF-04 | RNF-02, RNF-03, RNF-05 | `usuario` |
| Manter os dados da conta do cliente | O1 | RF-05, RF-06 | RN-17, RNF-09 | `usuario`, `clique_oferta` |
| Responder o questionário de perfil olfativo | O1 | RF-09, RF-10, RF-11, RF-12 | RN-04, RN-06 | `resposta_questionario`, `resposta_item`, `perfil_olfativo`, `perfil_familia` |
| Manter as perguntas do questionário | O1 | RF-07 | RN-05, RN-06 | `questionario`, `pergunta`, `alternativa` |
| Manter as alternativas e os pesos | O1 | RF-08 | RN-06 | `alternativa`, `alternativa_peso`, `familia_olfativa` |
| Conversar com o agente consultor | O1 | RF-21 | RN-15, RN-18, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16 | `conversa`, `mensagem` |
| Receber as recomendações personalizadas | O1 | RF-22, RF-23 | RN-09, RNF-11 | `recomendacao`, `perfume`, `perfil_familia`, `oferta` |
| Avaliar a recomendação recebida | O1 | RF-24 | RN-14 | `avaliacao_recomendacao` |
| Manter as diretrizes do agente | O1 | RF-25 | RNF-12 | `diretriz_agente` |
| Consultar as avaliações das recomendações | O1 | RF-26 | — | `avaliacao_recomendacao`, `recomendacao` |
| Importar os perfumes pela API de catálogo | O2 | RF-13, RF-14 | RN-07, RNF-18, RNF-25, RNF-27 | `perfume`, `marca`, `nota_olfativa`, `perfume_nota`, `acorde`, `perfume_acorde`, `importacao_catalogo` |
| Consultar o log de importações | O2 | RF-15 | — | `importacao_catalogo` |
| Agendar a sincronização do catálogo | O2 | RF-16 | RNF-27 | `importacao_catalogo` |
| Consultar a ficha do perfume | O2 | RF-17 | RNF-19 | `perfume`, `perfume_nota`, `perfume_acorde`, `oferta` |
| Revisar a ficha de perfume importada | O2 | RF-19 | RN-07 | `perfume` (`campos_revisados`) |
| Ocultar ou reexibir perfume | O2 | RF-20 | RN-08 | `perfume` (`visivel`) |
| Buscar perfume do catálogo para ofertar | O2, O3 | RF-18 | RNF-17 | `perfume`, `marca`, `acorde` |
| Adicionar e remover perfumes da sacola | O3 | RF-27 | RN-08 | `sacola_item` |
| Finalizar a sacola abrindo as lojas | O3 | RF-28, RF-29 | RN-12, RN-13, RNF-06, R-05 | `sacola_item`, `oferta`, `loja`, `clique_oferta` |
| Solicitar o cadastro da loja parceira | O3 | RF-30 | RN-02, RN-10 | `usuario`, `loja` |
| Manter os dados da loja | O3 | RF-31 | — | `loja` |
| Manter as ofertas da loja | O3 | RF-32 | RN-10, RN-11, RNF-06, RNF-28 | `oferta` |
| Pausar ou reativar uma oferta | O3 | RF-33 | — | `oferta` (`ativa`) |
| Consultar os cliques por oferta | O3 | RF-34 | RN-13 | `clique_oferta` |
| Aprovar ou bloquear loja parceira | O3 | RF-35 | RN-10 | `loja` (`status`, `decidido_por`) |
| Manter os usuários da plataforma | — | RF-36 | RN-02 | `usuario` |
| Consultar os indicadores de uso | — | RF-37 | RNF-14 | `usuario`, `perfil_olfativo`, `conversa`, `mensagem`, `recomendacao`, `clique_oferta` |

## Tabelas → onde são usadas

Toda tabela do DER aparece em pelo menos um PBI acima. Se uma tabela nova entrar no modelo sem PBI correspondente, é sinal de escopo não combinado.
