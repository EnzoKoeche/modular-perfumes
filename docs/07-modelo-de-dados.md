# 07 — Modelo de dados (DER lógico)

Diagrama da visão completa: [`entregas/der/Modular_Perfumes_DER_Logico_Completo.png`](../entregas/der/Modular_Perfumes_DER_Logico_Completo.png). Fonte: [`entregas/der/fonte/`](../entregas/der/fonte/).

Legenda: **PK** chave primária · **FK** chave estrangeira · **U** único · **U¹** único composto `(loja_id, perfume_id)` · **NN** NOT NULL.

Total: **26 tabelas** e **32 relacionamentos** (visão completa). Este arquivo é gerado a partir da mesma definição do diagrama e do script SQL, então os três não divergem.

**Tabelas da 1ª Sprint** (Artefato 6 e script SQL [`entregas/sql/`](../entregas/sql/)): `usuario`, `questionario`, `pergunta`, `alternativa`, `alternativa_peso`, `familia_olfativa`, `resposta_questionario`, `resposta_item`, `perfil_olfativo`, `perfil_familia`, `marca`, `nota_olfativa`, `acorde`, `perfume`, `perfume_nota`, `perfume_acorde`, `importacao_catalogo`. DER da Sprint 1: [`entregas/der/Modular_Perfumes_DER_Logico_Sprint1.png`](../entregas/der/Modular_Perfumes_DER_Logico_Sprint1.png).

## Acesso

### `usuario`

Conta de acesso de qualquer persona. O perfil define o que a pessoa pode fazer (RF-04).

| Chave | Coluna | Tipo | Nulo |
|---|---|---|---|
| PK | `id` | INT AUTO_INCREMENT | não |
|  | `nome` | VARCHAR(80) | não |
| U | `email` | VARCHAR(120) | não |
|  | `senha_hash` | VARCHAR(255) | não |
|  | `perfil` | ENUM(CLIENTE,LOJISTA,ADMIN) | não |
|  | `ativo` | TINYINT(1) | não |
|  | `tentativas_login` | TINYINT | não |
|  | `bloqueado_ate` | DATETIME | sim |
|  | `aceite_termos_em` | DATETIME | não |
|  | `criado_em` | DATETIME | não |

## Questionário e perfil olfativo

### `questionario`

Questionário de perfil olfativo. Só um fica ativo por vez (RN-05).

| Chave | Coluna | Tipo | Nulo |
|---|---|---|---|
| PK | `id` | INT AUTO_INCREMENT | não |
|  | `titulo` | VARCHAR(120) | não |
|  | `ativo` | TINYINT(1) | não |
|  | `criado_em` | DATETIME | não |

### `pergunta`

Pergunta do questionário, mantida pelo administrador (RF-07). Pergunta respondida é desativada, não apagada.

| Chave | Coluna | Tipo | Nulo |
|---|---|---|---|
| PK | `id` | INT AUTO_INCREMENT | não |
| FK | `questionario_id` | INT | não |
|  | `enunciado` | VARCHAR(255) | não |
|  | `tipo` | ENUM(UNICA,MULTIPLA) | não |
|  | `ordem` | SMALLINT | não |
|  | `obrigatoria` | TINYINT(1) | não |
|  | `ativa` | TINYINT(1) | não |
|  | `atualizada_em` | DATETIME | não |

### `alternativa`

Opção de resposta de uma pergunta (RF-08).

| Chave | Coluna | Tipo | Nulo |
|---|---|---|---|
| PK | `id` | INT AUTO_INCREMENT | não |
| FK | `pergunta_id` | INT | não |
|  | `texto` | VARCHAR(150) | não |
|  | `ordem` | SMALLINT | não |
|  | `ativa` | TINYINT(1) | não |

### `alternativa_peso`

Quanto cada alternativa soma para cada família olfativa no cálculo do perfil (RF-08, RF-11).

| Chave | Coluna | Tipo | Nulo |
|---|---|---|---|
| PK,FK | `alternativa_id` | INT | não |
| PK,FK | `familia_id` | INT | não |
|  | `peso` | DECIMAL(4,2) | não |

### `resposta_questionario`

Uma tentativa de resposta do cliente; `concluida_em` nulo significa questionário em andamento (RF-10).

| Chave | Coluna | Tipo | Nulo |
|---|---|---|---|
| PK | `id` | INT AUTO_INCREMENT | não |
| FK | `usuario_id` | INT | não |
| FK | `questionario_id` | INT | não |
|  | `iniciada_em` | DATETIME | não |
|  | `concluida_em` | DATETIME | sim |

### `resposta_item`

Alternativa escolhida em cada pergunta. Múltipla escolha gera várias linhas para a mesma pergunta.

| Chave | Coluna | Tipo | Nulo |
|---|---|---|---|
| PK,FK | `resposta_id` | INT | não |
| PK,FK | `pergunta_id` | INT | não |
| PK,FK | `alternativa_id` | INT | não |
|  | `respondida_em` | DATETIME | não |

### `perfil_olfativo`

Resultado do questionário; um por cliente, recalculado se ele responder de novo (RF-11).

| Chave | Coluna | Tipo | Nulo |
|---|---|---|---|
| PK | `id` | INT AUTO_INCREMENT | não |
| FK,U | `usuario_id` | INT | não |
| FK | `resposta_id` | INT | não |
|  | `nivel_conhecimento` | ENUM(INICIANTE,INTERMEDIARIO,AVANCADO) | não |
|  | `gerado_em` | DATETIME | não |

### `perfil_familia`

Afinidade do cliente com cada família olfativa, usada pelo agente.

| Chave | Coluna | Tipo | Nulo |
|---|---|---|---|
| PK,FK | `perfil_id` | INT | não |
| PK,FK | `familia_id` | INT | não |
|  | `afinidade` | DECIMAL(5,2) | não |

## Catálogo (importado da api)

### `marca`

Marca do perfume, criada na importação (a Fragella informa o país).

| Chave | Coluna | Tipo | Nulo |
|---|---|---|---|
| PK | `id` | INT AUTO_INCREMENT | não |
| U | `nome` | VARCHAR(80) | não |
|  | `pais` | VARCHAR(60) | sim |

### `familia_olfativa`

Famílias usadas no questionário, no perfil e no agrupamento dos acordes.

| Chave | Coluna | Tipo | Nulo |
|---|---|---|---|
| PK | `id` | INT AUTO_INCREMENT | não |
| U | `nome` | VARCHAR(50) | não |
|  | `descricao` | VARCHAR(255) | sim |

### `nota_olfativa`

Nota (ex.: bergamota, baunilha), criada na importação.

| Chave | Coluna | Tipo | Nulo |
|---|---|---|---|
| PK | `id` | INT AUTO_INCREMENT | não |
| U | `nome` | VARCHAR(80) | não |

### `acorde`

Acorde vindo da API (ex.: amadeirado); `familia_id` liga o acorde a uma família olfativa.

| Chave | Coluna | Tipo | Nulo |
|---|---|---|---|
| PK | `id` | INT AUTO_INCREMENT | não |
| U | `nome` | VARCHAR(60) | não |
| FK | `familia_id` | INT | sim |

### `perfume`

Perfume importado da API (RF-13). `api_id` evita duplicar na reimportação; `campos_revisados` guarda os campos que o administrador alterou e que a API não sobrescreve (RN-07). `imagem_url` aponta para a imagem servida pela API, sem copiar o arquivo (RNF-19, R-02); `fixacao` e `projecao` vêm como texto da API.

| Chave | Coluna | Tipo | Nulo |
|---|---|---|---|
| PK | `id` | INT AUTO_INCREMENT | não |
| U | `api_id` | VARCHAR(64) | não |
| FK | `marca_id` | INT | não |
|  | `nome` | VARCHAR(150) | não |
|  | `genero` | ENUM(MASCULINO,FEMININO,UNISSEX) | sim |
|  | `ano` | SMALLINT | sim |
|  | `imagem_url` | VARCHAR(500) | sim |
|  | `fixacao` | VARCHAR(40) | sim |
|  | `projecao` | VARCHAR(40) | sim |
|  | `descricao` | TEXT | sim |
|  | `visivel` | TINYINT(1) | não |
|  | `campos_revisados` | JSON | sim |
|  | `importado_em` | DATETIME | não |
|  | `atualizado_em` | DATETIME | não |

### `perfume_nota`

Pirâmide olfativa: nota por nível (saída, corpo, fundo).

| Chave | Coluna | Tipo | Nulo |
|---|---|---|---|
| PK,FK | `perfume_id` | INT | não |
| PK,FK | `nota_id` | INT | não |
| PK | `nivel` | ENUM(SAIDA,CORPO,FUNDO) | não |

### `perfume_acorde`

Acordes do perfume, com intensidade quando a API informar.

| Chave | Coluna | Tipo | Nulo |
|---|---|---|---|
| PK,FK | `perfume_id` | INT | não |
| PK,FK | `acorde_id` | INT | não |
|  | `intensidade` | DECIMAL(5,2) | sim |

### `importacao_catalogo`

Log de cada importação (RF-14, RF-15).

| Chave | Coluna | Tipo | Nulo |
|---|---|---|---|
| PK | `id` | INT AUTO_INCREMENT | não |
|  | `origem` | ENUM(MANUAL,AGENDADA) | não |
|  | `status` | ENUM(EM_ANDAMENTO,CONCLUIDA,FALHOU) | não |
|  | `qtd_incluidos` | INT | não |
|  | `qtd_atualizados` | INT | não |
|  | `mensagem_erro` | TEXT | sim |
|  | `iniciada_em` | DATETIME | não |
|  | `finalizada_em` | DATETIME | sim |

## Consultor olfativo por ia

### `diretriz_agente`

Regras e orientações do administrador incluídas no prompt de sistema do agente (RF-25).

| Chave | Coluna | Tipo | Nulo |
|---|---|---|---|
| PK | `id` | INT AUTO_INCREMENT | não |
|  | `titulo` | VARCHAR(120) | não |
|  | `conteudo` | TEXT | não |
|  | `ordem` | SMALLINT | não |
|  | `ativa` | TINYINT(1) | não |
|  | `atualizada_em` | DATETIME | não |

### `conversa`

Conversa do cliente com o consultor de IA (RF-21).

| Chave | Coluna | Tipo | Nulo |
|---|---|---|---|
| PK | `id` | INT AUTO_INCREMENT | não |
| FK | `usuario_id` | INT | não |
|  | `iniciada_em` | DATETIME | não |
|  | `ultima_mensagem_em` | DATETIME | não |

### `mensagem`

Turno da conversa com o conteúdo completo da API e o consumo de tokens (RNF-14).

| Chave | Coluna | Tipo | Nulo |
|---|---|---|---|
| PK | `id` | INT AUTO_INCREMENT | não |
| FK | `conversa_id` | INT | não |
|  | `papel` | ENUM(USUARIO,ASSISTENTE) | não |
|  | `conteudo_json` | JSON | não |
|  | `modelo` | VARCHAR(40) | sim |
|  | `tokens_entrada` | INT | sim |
|  | `tokens_saida` | INT | sim |
|  | `tokens_cache` | INT | sim |
|  | `enviada_em` | DATETIME | não |

### `recomendacao`

Perfume recomendado, registrado pela ferramenta do agente (RF-23, RN-09).

| Chave | Coluna | Tipo | Nulo |
|---|---|---|---|
| PK | `id` | INT AUTO_INCREMENT | não |
| FK | `conversa_id` | INT | não |
| FK | `perfume_id` | INT | não |
|  | `posicao` | TINYINT | não |
|  | `justificativa` | VARCHAR(500) | não |
|  | `gerada_em` | DATETIME | não |

### `avaliacao_recomendacao`

Nota de 1 a 5 do cliente para a recomendação; no máximo uma (RN-14).

| Chave | Coluna | Tipo | Nulo |
|---|---|---|---|
| PK | `id` | INT AUTO_INCREMENT | não |
| FK,U | `recomendacao_id` | INT | não |
|  | `nota` | TINYINT (1..5) | não |
|  | `comentario` | VARCHAR(500) | sim |
|  | `avaliada_em` | DATETIME | não |

## Sacola e lojas parceiras

### `sacola_item`

Perfume que o cliente guardou para comprar (RF-27).

| Chave | Coluna | Tipo | Nulo |
|---|---|---|---|
| PK,FK | `usuario_id` | INT | não |
| PK,FK | `perfume_id` | INT | não |
|  | `adicionado_em` | DATETIME | não |

### `loja`

Loja parceira; um lojista tem uma loja. Aprovação e bloqueio registram quem decidiu (RF-35).

| Chave | Coluna | Tipo | Nulo |
|---|---|---|---|
| PK | `id` | INT AUTO_INCREMENT | não |
| FK,U | `usuario_id` | INT | não |
|  | `nome` | VARCHAR(120) | não |
| U | `cnpj` | CHAR(14) | não |
|  | `site_url` | VARCHAR(255) | não |
|  | `status` | ENUM(PENDENTE,APROVADA,BLOQUEADA) | não |
| FK | `decidido_por` | INT | sim |
|  | `decidido_em` | DATETIME | sim |
|  | `criado_em` | DATETIME | não |

### `oferta`

Link e preço de um perfume em uma loja; uma por loja e perfume (RN-11).

| Chave | Coluna | Tipo | Nulo |
|---|---|---|---|
| PK | `id` | INT AUTO_INCREMENT | não |
| FK,U¹ | `loja_id` | INT | não |
| FK,U¹ | `perfume_id` | INT | não |
|  | `url` | VARCHAR(500) | não |
|  | `preco` | DECIMAL(10,2) | não |
|  | `ativa` | TINYINT(1) | não |
|  | `atualizada_em` | DATETIME | não |

### `clique_oferta`

Registro de cada redirecionamento para a loja (RN-13). `usuario_id` fica nulo quando a conta é excluída (RN-17).

| Chave | Coluna | Tipo | Nulo |
|---|---|---|---|
| PK | `id` | INT AUTO_INCREMENT | não |
| FK | `oferta_id` | INT | não |
| FK | `usuario_id` | INT | sim |
|  | `origem` | ENUM(SACOLA,FICHA,RECOMENDACAO) | não |
|  | `clicado_em` | DATETIME | não |

## Relacionamentos

| Pai | Filho | Cardinalidade | FK no filho pode ser nula? |
|---|---|---|---|
| `questionario` | `pergunta` | 1:N | não |
| `pergunta` | `alternativa` | 1:N | não |
| `alternativa` | `alternativa_peso` | 1:N | não |
| `familia_olfativa` | `alternativa_peso` | 1:N | não |
| `usuario` | `resposta_questionario` | 1:N | não |
| `questionario` | `resposta_questionario` | 1:N | não |
| `resposta_questionario` | `resposta_item` | 1:N | não |
| `pergunta` | `resposta_item` | 1:N | não |
| `alternativa` | `resposta_item` | 1:N | não |
| `usuario` | `perfil_olfativo` | 1:1 | não |
| `resposta_questionario` | `perfil_olfativo` | 1:1 | não |
| `perfil_olfativo` | `perfil_familia` | 1:N | não |
| `familia_olfativa` | `perfil_familia` | 1:N | não |
| `marca` | `perfume` | 1:N | não |
| `perfume` | `perfume_nota` | 1:N | não |
| `nota_olfativa` | `perfume_nota` | 1:N | não |
| `perfume` | `perfume_acorde` | 1:N | não |
| `acorde` | `perfume_acorde` | 1:N | não |
| `familia_olfativa` | `acorde` | 1:N | sim |
| `usuario` | `conversa` | 1:N | não |
| `conversa` | `mensagem` | 1:N | não |
| `conversa` | `recomendacao` | 1:N | não |
| `perfume` | `recomendacao` | 1:N | não |
| `recomendacao` | `avaliacao_recomendacao` | 1:1 | não |
| `usuario` | `sacola_item` | 1:N | não |
| `perfume` | `sacola_item` | 1:N | não |
| `usuario` | `loja` | 1:1 | não |
| `usuario` | `loja` | 1:N | sim |
| `loja` | `oferta` | 1:N | não |
| `perfume` | `oferta` | 1:N | não |
| `oferta` | `clique_oferta` | 1:N | não |
| `usuario` | `clique_oferta` | 1:N | sim |

## Índices recomendados (além de PK, FK e únicos)

- `perfume (visivel, nome)` — listagem e busca do catálogo (RNF-17).
- `oferta (perfume_id, ativa, preco)` — escolha da oferta de menor preço (RN-12).
- `clique_oferta (oferta_id, clicado_em)` — relatório de cliques por período (RF-34).
- `mensagem (conversa_id, enviada_em)` — reconstrução do histórico da conversa.
- `resposta_questionario (usuario_id, concluida_em)` — saber se o cliente já concluiu (RN-04).
