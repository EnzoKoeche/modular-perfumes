# Modular Perfumes

Plataforma web gratuita de **consultoria olfativa com IA**. O cliente cria a conta e responde um questionário de perfil olfativo. Depois, conversa com um agente de inteligência artificial (Claude, via SDK da Anthropic), que recomenda perfumes de um catálogo importado de uma API externa. Os perfumes de que ele gostou vão para uma sacola, e a finalização leva o cliente às lojas parceiras onde comprar. O site não vende nem processa pagamento.

Projeto da disciplina **Experiência Criativa – Projetando Soluções Computacionais** (Bacharelado em Engenharia de Software, PUCPR).
**Equipe:** Enzo Koeche Castagna · Angelo · André Lagos.

> **Status:** 1ª Sprint implementada (5 user stories). Especificação v3 (2026-09-14) alinhada aos enunciados da disciplina: três personas, user stories no padrão da rubrica, DER e script SQL da 1ª Sprint.

## Rodar o site localmente (1ª Sprint)

Pré-requisitos: Python 3.9+, Docker.

```bash
# 1. banco MySQL com as tabelas e a carga inicial (scripts da 1ª e da 2ª Sprint)
docker compose up -d db

# 2. ambiente Python
python3 -m venv .venv
source .venv/bin/activate          # no Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt   # site + pytest
cp .env.example .env               # ajuste SECRET_KEY

# 3. criar um administrador (pede a senha)
flask --app app criar-admin admin@exemplo.com "Administrador"

# 4. subir o site em http://127.0.0.1:5050
flask --app app run --port 5050 --debug

# testes automáticos (critérios de aceite, vitrine e consultor com a IA simulada), com o banco do passo 1 no ar
pytest
```

| Onde fica cada user story | Rota | Código |
|---|---|---|
| US1 — cadastro do cliente | `/cadastro` | `app/auth.py` |
| US2 — login | `/login` | `app/auth.py` |
| US3 — questionário de perfil olfativo | `/questionario/` | `app/questionario.py` |
| US4 — manter perguntas (admin) | `/admin/perguntas` | `app/admin.py` |
| US5 — importar catálogo (admin) | `/admin/catalogo` | `app/admin.py` e `app/catalogo.py` |
| Vitrine: melhores do ano, clássicos por década, lista e ficha (antecipado da Sprint 2) | `/perfumes/` | `app/vitrine.py` |
| Consultor de IA com ferramentas no banco (antecipado da Sprint 2; exige `ANTHROPIC_API_KEY`) | `/consultor/` | `app/consultor.py` |

No modo `CATALOGO_PROVEDOR=exemplo` (padrão), a importação usa perfumes fictícios das marcas *Casa Demo* e *Atelier Exemplo*. Para a API real, use `CATALOGO_PROVEDOR=fragella` e preencha `FRAGELLA_API_KEY` no `.env`.

## Documentação

| # | Documento | Conteúdo |
|---|---|---|
| 00 | [Visão geral](docs/00-visao-geral.md) | Problema, solução, objetivos, é/não é/faz/não faz, visão de produto, histórico da visão |
| 01 | [Personas](docs/01-personas.md) | Cliente, Lojista Parceiro, Administrador |
| 02 | [Requisitos funcionais](docs/02-requisitos-funcionais.md) | 37 RFs por módulo, prioridade, PBI de origem e resumo de CRUD por entidade |
| 03 | [Requisitos não funcionais](docs/03-requisitos-nao-funcionais.md) | Segurança, LGPD, IA, desempenho, usabilidade, manutenção |
| 04 | [Regras de negócio](docs/04-regras-de-negocio.md) | 18 regras |
| 05 | [Backlog e user stories](docs/05-backlog-e-user-stories.md) | Features, 28 PBIs em ordem de sprint, user stories da Sprint 1 e Definition of Done |
| 06 | [Arquitetura e agente de IA](docs/06-arquitetura.md) | Stack proposta, componentes, Tool Runner, ferramentas, cache, custos, falhas |
| 07 | [Modelo de dados](docs/07-modelo-de-dados.md) | Dicionário de dados das 26 tabelas (17 na 1ª Sprint) |
| 08 | [Integrações](docs/08-integracoes.md) | API de catálogo (Fragella e plano B), links de compra, API da Anthropic |
| 09 | [Riscos e premissas](docs/09-riscos-e-premissas.md) | |
| 10 | [Glossário](docs/10-glossario.md) | |
| 11 | [Rastreabilidade](docs/11-rastreabilidade.md) | Objetivo → feature → PBI → RF/RN/RNF → tabelas |
| 12 | [Decisões pendentes](docs/12-decisoes-pendentes.md) | O que ainda precisa ser decidido e por quem |

## Entregas da 1ª Sprint

| Tarefa (prazo) | Item pedido | Onde está |
|---|---|---|
| **Especificação (1ª Sprint)** — 14/09 | 1. Especificação no template (artefatos 1 a 6) | [`entregas/especificacao/Modular_Perfumes_Especificacao_do_Projeto.docx`](entregas/especificacao/) |
| | 2. Imagem de alta resolução do Canvas PBB (PBIs da 1ª Sprint em vermelho) | [`entregas/pbb/Modular_Perfumes_Canvas_PBB_Sprint1.png`](entregas/pbb/Modular_Perfumes_Canvas_PBB_Sprint1.png) |
| | 3. Script SQL do banco de dados | [`entregas/sql/modular_perfumes_sprint1.sql`](entregas/sql/modular_perfumes_sprint1.sql), com as consultas de verificação em [`consultas_sprint1.sql`](entregas/sql/consultas_sprint1.sql). A 2ª Sprint acrescenta [`modular_perfumes_sprint2.sql`](entregas/sql/modular_perfumes_sprint2.sql). |
| **Gestão de Projeto + Controle de Versão** — 14/09 | 1. Link público do Trello + print | Quadro: https://trello.com/b/6aa8142cf99507d054887fdb · guia dos cards: [`entregas/trello/cards.md`](entregas/trello/cards.md) |
| | 2. Link público do GitHub + print de Insights → Contributors | Este repositório |
| **1ª Sprint do Produto (Apresentação)** — 20/09 | PDF do PPT da apresentação | [`entregas/apresentacao/Modular_Perfumes_Apresentacao_Sprint1.pdf`](entregas/apresentacao/Modular_Perfumes_Apresentacao_Sprint1.pdf) (gerado por `entregas/apresentacao/fonte/`) |

Imagens de apoio:
- DER lógico da 1ª Sprint (Artefato 6): [`entregas/der/Modular_Perfumes_DER_Logico_Sprint1.png`](entregas/der/Modular_Perfumes_DER_Logico_Sprint1.png)
- DER da visão completa: [`entregas/der/Modular_Perfumes_DER_Logico_Completo.png`](entregas/der/Modular_Perfumes_DER_Logico_Completo.png)

O **Artefato 7 (modelo orientado a objetos)** só é exigido se a equipe usar orientação a objetos na programação, por isso ainda não está na especificação.

Ao abrir o `.docx` no Word, responda **"Sim"** à pergunta sobre atualizar os campos. Isso atualiza o sumário e o índice de ilustrações.

## Regenerar as imagens

As imagens são geradas por código, para que mudanças no backlog ou no modelo não dependam de redesenho à mão.

```bash
cd entregas/der/fonte
# DER lógico (requer Graphviz: brew install graphviz)
python3 render_der.py der_logico_sprint1.dot sprint1 && dot -Tpng der_logico_sprint1.dot -o ../Modular_Perfumes_DER_Logico_Sprint1.png
python3 render_der.py der_logico.dot && dot -Tpng der_logico.dot -o ../Modular_Perfumes_DER_Logico_Completo.png
# dicionário de dados e script SQL (mesma fonte: modelo.py)
python3 gen_dicionario.py ../../../docs/07-modelo-de-dados.md
python3 gen_sql.py ../../sql/modular_perfumes_sprint1.sql

# Canvas PBB (requer Pillow; usa a fonte Helvetica do macOS)
cd ../../pbb/fonte
python3 pbb.py ../Modular_Perfumes_Canvas_PBB_Sprint1.png
```

Para mudar uma tabela, edite `entregas/der/fonte/modelo.py` (a lista `SPRINT1` define o recorte da sprint) e rode os geradores. Para mudar personas, features ou PBIs, edite o bloco de conteúdo no topo de `entregas/pbb/fonte/pbb.py`.
