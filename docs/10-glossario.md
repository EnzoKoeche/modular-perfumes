# 10 — Glossário

| Termo | Significado neste projeto |
|---|---|
| **Acorde** | Impressão olfativa dominante resultante da combinação de notas, ex.: "amadeirado", "cítrico", "baunilhado". |
| **Agente / consultor de IA** | Conversa com o cliente usando um modelo Claude, da Anthropic, e ferramentas do sistema para consultar perfil, catálogo e ofertas. |
| **API de catálogo** | Serviço externo de onde vêm os dados dos perfumes (nome, marca, foto, notas, acordes). |
| **Curador olfativo** | Persona que mantém o questionário, revisa fichas e define as diretrizes do agente. |
| **Diretriz do agente** | Regra ou orientação escrita pelo curador e incluída no prompt de sistema do agente. |
| **Família olfativa** | Grupo de perfumes com características parecidas, ex.: floral, oriental/âmbar, amadeirado, fresco/cítrico, fougère, chypre. |
| **Ficha do perfume** | Página com foto, marca, notas por nível, acordes e ofertas de um perfume. |
| **Finalizar a sacola** | Ação que leva o cliente às lojas de cada perfume da sacola. Não é pagamento. |
| **Lojista parceiro** | Persona que representa uma loja e mantém ofertas com link e preço. |
| **Notas de saída, corpo e fundo** | Níveis da pirâmide olfativa: o que se sente primeiro (saída), no meio (corpo ou coração) e o que fica por mais tempo (fundo). |
| **Oferta** | Ligação entre um perfume do catálogo e a página do produto em uma loja, com preço. |
| **PBB** | *Product Backlog Building*, técnica de Fábio Aguiar para montar o backlog a partir de personas, problemas, expectativas e features. |
| **PBI** | *Product Backlog Item*, item do backlog, que vira uma ou mais user stories. |
| **Perfil olfativo** | Resultado do questionário: nível de conhecimento do cliente e afinidade dele com cada família olfativa. |
| **Prompt caching** | Recurso da API da Anthropic que reaproveita a parte inicial repetida de uma requisição, reduzindo custo e latência. |
| **Sacola** | Lista de perfumes de que o cliente gostou e quer comprar. Não é carrinho de compra: não há pagamento. |
| **Streaming** | Exibir a resposta do agente aos poucos, enquanto é gerada. |
| **Tool Runner** | Recurso do SDK da Anthropic que executa automaticamente o ciclo de chamadas de ferramenta do agente. |
