# 09 — Riscos e premissas

## Premissas

| ID | Premissa |
|---|---|
| P-01 | A equipe terá uma chave da API da Anthropic com crédito suficiente para desenvolvimento, testes e apresentação. |
| P-02 | A equipe consegue pagar o plano Basic da Fragella (US$ 12/mês) ou o pagamento por uso durante o semestre, e obtém autorização para guardar um recorte do catálogo (ver [08-integracoes.md](08-integracoes.md)). |
| P-03 | Para a apresentação acadêmica, lojas e ofertas podem ser dados de demonstração cadastrados pela equipe como lojistas de teste, com links reais de produtos públicos. |
| P-04 | O público do MVP é pequeno (turma, professores, convidados), então custo e desempenho são controláveis com os limites definidos. |

## Riscos

| ID | Risco | Prob. | Impacto | Resposta |
|---|---|---|---|---|
| R-01 | A API de catálogo muda os termos, sai do ar ou limita demais o plano gratuito. | Média | Alto | Adaptador isolado (RNF-25); dados já importados continuam no banco; plano B de provedor em 08-integracoes. |
| R-02 | Os termos da API não permitem guardar os dados ou as imagens. Os termos da Fragella proíbem guardar "grandes porções" sem permissão do plano. | **Alta** | Alto | Pedir autorização por escrito antes da Sprint 1; importar só um recorte; exibir as imagens pela URL da API, sem copiar; se negado, usar o plano B de 08-integracoes. |
| R-03 | Custo da IA acima do previsto. | Média | Médio | Limite diário por cliente (RN-15), prompt caching, esforço ajustado, registro de tokens (RNF-14); trocar de modelo é decisão da equipe com base nas medições. |
| R-04 | O agente recomenda perfume inexistente ou informa preço errado. | Baixa | Alto | Recomendação só por ferramenta com ID do banco (RN-09, RNF-11); preço e link só de oferta ativa. |
| R-05 | O navegador bloqueia abrir várias abas com um clique na finalização da sacola. | **Alta** | Médio | Página de finalização com um botão por loja (RF-28); "Abrir todas" é conveniência, não o único caminho. |
| R-06 | Tentativas de manipular o agente (prompt injection) pelo chat. | Média | Médio | Diretrizes no prompt de sistema, ferramentas somente de leitura (menos o registro de recomendação) e `usuario_id` sempre vindo da sessão (RNF-12, RNF-03). |
| R-07 | Links de oferta quebrados ou preços desatualizados. | Alta | Médio | Data de atualização na oferta; lojista pausa e edita (RF-32, RF-33); o site informa que preço e estoque são da loja (RNF-28). |
| R-08 | A equipe subestima o esforço: são quatro perfis de acesso com CRUDs. | Média | Alto | Ordem de sprints do backlog (05) prioriza cliente → consultor → sacola; o que for de curador e lojista pode ser simplificado ao fim. |
| R-09 | O questionário não produz um perfil útil para o agente. | Média | Médio | Pesos por família olfativa (RF-08), avaliações das recomendações (RF-26) para calibrar, curador revisa. |
| R-10 | Vazamento de chave de API pelo repositório. | Baixa | Alto | `.env` no `.gitignore`, `.env.example` sem valor, revisão antes de cada push (RNF-04). |
