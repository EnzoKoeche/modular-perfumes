# 08 — Integrações externas

> Pesquisa feita em 2026-09-14. Os itens marcados como **não confirmado** não foram verificados na fonte e precisam ser conferidos antes de virar decisão.

## 1. Catálogo de perfumes

### Opções avaliadas

| Fonte | Campos | Acesso e preço | Guardar dados e imagens | Preço ou link de compra |
|---|---|---|---|---|
| **Fragella API** ([site](https://api.fragella.com/), [termos](https://api.fragella.com/terms-of-use.html)) | Foto (JPG/WebP e versão com fundo transparente), notas de saída, corpo e fundo, acordes com percentual, gênero, ano, marca, país, fixação e projeção | Chave no cabeçalho `x-api-key`. Grátis: 20 requisições/mês. Basic: US$ 12/mês (5.000). Pro: US$ 49/mês (20.000). Por uso: US$ 0,005 por requisição + US$ 2 fixos | Os termos proíbem armazenar ou cachear "grandes porções" dos dados para evitar o acesso à API, salvo se o plano permitir. Nada específico sobre imagens | Informa preço e "purchase links"; se incluem lojas brasileiras, **não confirmado** |
| Dataset "Fragrantica.com Fragrance Dataset" no Kaggle ([link](https://www.kaggle.com/datasets/olgagmiufana1/fragrantica-com-fragrance-dataset)) | Notas por nível, acordes, gênero, ano, perfumistas; fotos **não confirmado** | Download grátis | Licença declarada CC BY-NC-SA 4.0, **mas** os dados foram extraídos do Fragrantica, cujos termos proíbem coleta automatizada | Não |
| Dataset Parfumo (TidyTuesday 2024-12-10) ([readme](https://github.com/rfordatascience/tidytuesday/blob/main/data/2024/2024-12-10/readme.md)) | Notas por nível, acordes, marca, ano, concentração, URL do Parfumo | Grátis | Licença **não confirmada** | Não |
| Fragrantica | Não há API pública | — | Termos proíbem coleta automatizada (página retornou 403; informação de busca) | — |
| Open Beauty Facts ([dados](https://world.openbeautyfacts.org/data)) | Cosméticos em geral, **sem** notas olfativas | Sem chave; uso por consulta real, sem raspagem | Dados ODbL/DbCL; fotos CC-BY-SA (atribuição e mesma licença) | Não |
| APIs de fragrância no RapidAPI ("Fragrance API", "FragranceFinder API") | **Não confirmado** | **Não confirmado** | **Não confirmado** | **Não confirmado** |

### Decisão proposta

**Provedor principal: Fragella API.** É a única fonte oficial encontrada com todos os campos que a ficha e o agente usam.

Condições para adotar:
1. **Plano:** as 20 requisições grátis por mês não bastam nem para a primeira importação. O mínimo realista é o **Basic (US$ 12/mês)** ou o pagamento por uso durante o desenvolvimento.
2. **Autorização por escrito:** antes de preencher o banco, pedir por e-mail à Fragella permissão para guardar um recorte do catálogo (algumas centenas de perfumes) em projeto acadêmico sem fins lucrativos, porque a cláusula de "grandes porções" pesa contra a RN-07. A resposta vai para [12-decisoes-pendentes.md](12-decisoes-pendentes.md).
3. **Imagens:** exibir pela URL fornecida pela API (`perfume.imagem_url`), sem copiar o arquivo para o servidor, já que a foto do frasco pertence à marca ou a terceiros (RNF-19).
4. **Recorte:** importar por marcas e famílias de interesse, não o catálogo inteiro, para ficar dentro da cota e da autorização.

**Plano B:** usar um dataset público (Kaggle, CC BY-NC-SA), apenas para uso acadêmico, com crédito, sem fotos. A ficha mostra uma ilustração genérica por família olfativa. O risco de origem do dado (coleta proibida pelo Fragrantica) precisa ser comentado com os professores antes de usar.

### Como a integração entra no sistema

- **Adaptador `CatalogoProvider`** (RNF-25): `listar_pagina(cursor)` e `obter(id_api)`. Trocar Fragella pelo plano B muda só o adaptador.
- **Mapeamento:**
  - ID da Fragella → `perfume.api_id`
  - marca → `marca` (com país)
  - notas por nível → `nota_olfativa` + `perfume_nota`
  - acordes com % → `acorde` + `perfume_acorde.intensidade`
  - fixação e projeção → `perfume.fixacao` e `perfume.projecao`
  - foto → `perfume.imagem_url`
- **Endpoint usado na 1ª Sprint:** `GET https://api.fragella.com/api/v1/brands/{marca}?limit=N`, com cabeçalho `x-api-key`. Uma requisição traz vários perfumes da marca, o que economiza a cota. Os campos lidos são `_id`, `Name`, `Brand`, `Country`, `Gender`, `Year`, `Image URL`, `Longevity`, `Sillage`, `Notes.Top/Middle/Base`, `Main Accords` e `Main Accords Percentage` (texto como "Dominant", por isso `perfume_acorde.intensidade` é VARCHAR).
- **Modo exemplo:** com `CATALOGO_PROVEDOR=exemplo`, o site lê perfumes fictícios de `app/catalogo_exemplo.json`, no mesmo formato, para desenvolver sem gastar cota.
- **Chave:** `FRAGELLA_API_KEY` em variável de ambiente (RNF-04).
- **Cota:** cada importação registra quantas requisições gastou, e a sincronização agendada (RF-16) não passa do limite mensal do plano.

## 2. Links de compra

### Opções avaliadas

| Opção | Buscar por nome devolve URL e preço? | Requisito |
|---|---|---|
| Amazon Creators API (sucessora da Product Advertising API 5) ([docs](https://affiliate-program.amazon.com/creatorsapi/docs)) | Tem busca por palavra-chave; se retorna preço e URL, **não confirmado** | Na documentação do .com: pelo menos 10 vendas qualificadas nos últimos 30 dias. A regra do .com.br **não foi confirmada** |
| Mercado Livre, busca pública `/sites/MLB/search` | Desenvolvedores relatam erro 403 mesmo com token válido; não há comunicado oficial | Na prática, inviável hoje |
| Lomadee, API de Ofertas ([docs](https://developer.socialsoul.com.vc/afiliados/ofertas/v1/)) | A documentação descreve busca de ofertas com link para a loja | Aceita CPF ou CNPJ (fontes secundárias); se funciona em 2026, **não confirmado** |
| Awin | Não pesquisado | — |

### Decisão proposta

**O link de compra não depende de API de terceiros.** Ele vem da **oferta cadastrada pelo lojista parceiro** (RF-32), com URL e preço, e o redirecionamento passa pela rota interna que registra o clique (RN-13).

- **Para a apresentação:** a equipe cria lojistas de teste com links reais de páginas de produto (premissa P-03).
- **Evolução possível** (fora do escopo atual):
  - usar o "purchase link" da Fragella quando existir, como sugestão ao lojista;
  - avaliar a API de Ofertas da Lomadee, a única que aceita CPF.

## 3. API da Anthropic (consultor de IA)

Detalhada em [06-arquitetura.md](06-arquitetura.md#agente-consultor-claude-via-sdk-da-anthropic). Resumo:

- SDK oficial `anthropic` (Python), modelo `claude-opus-5`, Tool Runner, streaming, prompt caching e `fallbacks: "default"`.
- Chave `ANTHROPIC_API_KEY` em variável de ambiente (RNF-04).
- Custo por mensagem registrado a partir de `usage` (RNF-14).
