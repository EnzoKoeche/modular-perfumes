# Modular Perfumes

Plataforma web gratuita de **consultoria olfativa com IA**. O cliente cria a conta e responde um questionário de perfil olfativo. Depois, conversa com um agente de inteligência artificial (Claude, via SDK da Anthropic), que recomenda perfumes de um catálogo importado de uma API externa. Os perfumes de que ele gostou vão para uma sacola, e a finalização leva o cliente às lojas parceiras onde comprar. O site não vende nem processa pagamento.

Projeto da disciplina **Experiência Criativa – Projetando Soluções Computacionais** (Bacharelado em Engenharia de Software, PUCPR).
**Equipe:** Enzo Koeche Castagna · Angelo · André Lagos.

> **Status:** especificação e engenharia de requisitos (v2, 2026-09-14, após feedback do professor). O código começa na Sprint 1.

## Documentação

| # | Documento | Conteúdo |
|---|---|---|
| 00 | [Visão geral](docs/00-visao-geral.md) | Problema, solução, objetivos, é/não é/faz/não faz, visão de produto, histórico da visão |
| 01 | [Personas](docs/01-personas.md) | Cliente, Curador Olfativo, Lojista Parceiro, Administrador |
| 02 | [Requisitos funcionais](docs/02-requisitos-funcionais.md) | 37 RFs por módulo, prioridade, PBI de origem e resumo de CRUD por entidade |
| 03 | [Requisitos não funcionais](docs/03-requisitos-nao-funcionais.md) | Segurança, LGPD, IA, desempenho, usabilidade, manutenção |
| 04 | [Regras de negócio](docs/04-regras-de-negocio.md) | 18 regras |
| 05 | [Backlog e user stories](docs/05-backlog-e-user-stories.md) | Features, 28 PBIs em ordem de sprint, user stories da Sprint 1 e Definition of Done |
| 06 | [Arquitetura e agente de IA](docs/06-arquitetura.md) | Stack proposta, componentes, Tool Runner, ferramentas, cache, custos, falhas |
| 07 | [Modelo de dados](docs/07-modelo-de-dados.md) | Dicionário de dados das 26 tabelas do DER lógico |
| 08 | [Integrações](docs/08-integracoes.md) | API de catálogo (Fragella e plano B), links de compra, API da Anthropic |
| 09 | [Riscos e premissas](docs/09-riscos-e-premissas.md) | |
| 10 | [Glossário](docs/10-glossario.md) | |
| 11 | [Rastreabilidade](docs/11-rastreabilidade.md) | Objetivo → feature → PBI → RF/RN/RNF → tabelas |
| 12 | [Decisões pendentes](docs/12-decisoes-pendentes.md) | O que ainda precisa ser decidido e por quem |

## Entregas da disciplina

| Arquivo | O que é |
|---|---|
| [`entregas/especificacao/Modular_Perfumes_Especificacao_do_Projeto.docx`](entregas/especificacao/) | Especificação no template da PUCPR: artefatos 1 a 5, link do Trello e Artefato 6 (DER lógico) |
| [`entregas/pbb/Modular_Perfumes_Canvas_PBB_Sprint1.png`](entregas/pbb/Modular_Perfumes_Canvas_PBB_Sprint1.png) | Canvas PBB em alta resolução, com os PBIs da Sprint 1 em vermelho |
| [`entregas/der/Modular_Perfumes_DER_Logico.png`](entregas/der/Modular_Perfumes_DER_Logico.png) | DER lógico em alta resolução |
| [`entregas/trello/cards.md`](entregas/trello/cards.md) | Listas e cards para montar o quadro do Trello |

Ao abrir o `.docx` no Word, responda **"Sim"** à pergunta sobre atualizar os campos. Isso atualiza o sumário e o índice de ilustrações.

## Regenerar as imagens

As imagens são geradas por código, para que mudanças no backlog ou no modelo não dependam de redesenho à mão.

```bash
# DER lógico e dicionário de dados (requer Graphviz: brew install graphviz)
cd entregas/der/fonte
python3 render_der.py der_logico.dot && dot -Tpng der_logico.dot -o ../Modular_Perfumes_DER_Logico.png
python3 gen_dicionario.py ../../../docs/07-modelo-de-dados.md

# Canvas PBB (requer Pillow; usa a fonte Helvetica do macOS)
cd ../../pbb/fonte
python3 pbb.py ../Modular_Perfumes_Canvas_PBB_Sprint1.png
```

Para mudar uma tabela, edite `entregas/der/fonte/modelo.py`. Para mudar personas, features ou PBIs, edite o bloco de conteúdo no topo de `entregas/pbb/fonte/pbb.py`.
