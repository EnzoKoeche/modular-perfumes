# 03 — Requisitos não funcionais

Os valores numéricos são **metas de projeto** para um trabalho acadêmico. Servem para orientar decisões e testes, não são SLA.

## Segurança

| ID | Requisito | Como verificar |
|---|---|---|
| RNF-01 | Senhas são guardadas apenas como hash com algoritmo próprio para senha (bcrypt ou Argon2). Nenhuma senha em texto puro, nem em log. | Inspecionar a tabela `usuario` e os logs depois de um cadastro. |
| RNF-02 | A sessão usa cookie `HttpOnly`, `Secure` (em produção) e `SameSite=Lax`. Formulários que alteram dados têm proteção CSRF. | Inspecionar os cabeçalhos no navegador; tentar um POST sem token. |
| RNF-03 | Toda rota verifica o perfil de acesso no **servidor**. Esconder o botão na tela não basta. | Chamar a rota de outro perfil diretamente pela URL e esperar 403. |
| RNF-04 | As chaves da API da Anthropic e da API de catálogo ficam só no servidor, em variável de ambiente. Nunca vão para o front-end nem para o repositório (`.env` no `.gitignore`, `.env.example` sem valores). | Buscar as chaves no bundle do front e no histórico do git. |
| RNF-05 | Após 5 tentativas de login erradas seguidas para o mesmo e-mail, novas tentativas ficam bloqueadas por 15 minutos. | Teste automatizado. |
| RNF-06 | Links de oferta aceitam somente `https://` e abrem com `rel="noopener noreferrer"`. | Tentar cadastrar `javascript:`; inspecionar o HTML. |

## Privacidade (LGPD)

| ID | Requisito |
|---|---|
| RNF-07 | Coletar só o necessário: nome, e-mail e senha no cadastro; as respostas do questionário são dados de preferência, não dados sensíveis. |
| RNF-08 | O cadastro exibe e registra o aceite dos termos de uso e da política de privacidade, informando que as conversas são processadas por um provedor de IA externo. |
| RNF-09 | A exclusão de conta cumpre a RN-17 em até 1 dia. |
| RNF-10 | As mensagens enviadas ao modelo de IA levam o perfil olfativo e a conversa, nunca e-mail ou senha. |

## IA — qualidade, segurança e custo

| ID | Requisito |
|---|---|
| RNF-11 | O agente só recomenda perfumes que as ferramentas retornaram (RN-09). As recomendações exibidas na tela vêm do registro estruturado da ferramenta, não do texto livre do modelo. |
| RNF-12 | Instruções do cliente para mudar as regras do agente ("ignore suas instruções", "finja que é outro sistema") não alteram as diretrizes. As diretrizes vão no *system prompt*; o texto do cliente vai sempre como mensagem de usuário. |
| RNF-13 | O início da resposta do agente aparece em até 5 segundos na maioria das mensagens (streaming). |
| RNF-14 | Cada mensagem registra os tokens de entrada, de saída e lidos do cache, para o indicador de custo (RF-37). |
| RNF-15 | O *system prompt* e as definições de ferramentas são estáveis entre mensagens, para aproveitar o *prompt caching*. Nada variável, como data, hora ou ID, vai antes do ponto de cache. |
| RNF-16 | Se a API de IA falhar ou estourar o limite, o cliente vê "O consultor está indisponível agora, tente em alguns minutos" e o resto do site continua funcionando. |

## Desempenho e disponibilidade

| ID | Requisito |
|---|---|
| RNF-17 | Páginas de catálogo, ficha e sacola respondem em até 2 segundos com até 10 mil perfumes cadastrados (consultas com índice e paginação de 20 itens). |
| RNF-18 | A importação do catálogo roda em segundo plano e não trava o site. Se falhar, o catálogo anterior continua valendo (RF-14). |
| RNF-19 | As fotos dos perfumes são exibidas com carregamento preguiçoso (`loading="lazy"`), respeitando os termos de uso da API quanto a cache e hospedagem de imagem. |

## Usabilidade e acessibilidade

| ID | Requisito |
|---|---|
| RNF-20 | Layout responsivo: todas as telas funcionam em celular a partir de 360 px de largura. |
| RNF-21 | Contraste de texto no nível AA (WCAG 2.1), campos com rótulo e navegação por teclado nos formulários. |
| RNF-22 | Mensagens de erro dizem o que aconteceu e como corrigir, sem código técnico. |

## Manutenibilidade e qualidade

| ID | Requisito |
|---|---|
| RNF-23 | Código versionado no GitHub, com README de instalação, `.env.example` e migrations do banco. |
| RNF-24 | Testes automatizados para as regras de negócio (RN-04, RN-05, RN-07, RN-11, RN-12) e para os CRUDs principais. |
| RNF-25 | As integrações externas (API de catálogo e API de IA) ficam atrás de uma camada própria, para trocar de provedor sem mexer nas telas. |
| RNF-26 | Logs de aplicação sem dados pessoais: registram IDs, nunca nome, e-mail ou conteúdo da conversa. |

## Legais e de terceiros

| ID | Requisito |
|---|---|
| RNF-27 | Os termos de uso da API de catálogo são respeitados: atribuição exigida, limite de chamadas e regras sobre armazenar dados e imagens. Os detalhes do provedor escolhido estão em [08-integracoes.md](08-integracoes.md). |
| RNF-28 | O site informa que os preços e a disponibilidade são das lojas e podem mudar, e que a compra é feita na loja. |
