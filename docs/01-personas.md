# 01 — Personas

São **três personas** com **papéis diferentes no sistema**, e não variações do mesmo cliente. Cada uma tem um perfil de acesso próprio (`usuario.perfil`), as suas próprias telas e os seus CRUDs.

| Persona | Perfil de acesso | Em uma frase |
|---|---|---|
| Cliente | `CLIENTE` | Quer descobrir perfumes que combinam com ele e comprar sem errar. |
| Lojista Parceiro | `LOJISTA` | Quer que clientes interessados cheguem à loja dele. |
| Administrador | `ADMIN` | Mantém a plataforma: questionário, catálogo, lojas, usuários e regras do consultor. |

No Canvas PBB, cada persona tem dois itens "o que faz" e dois "o que espera", e três features, cada uma com dois problemas e dois benefícios.

---

## Cliente

**Quem é.** Pessoa de 18 a 45 anos que compra pela internet. Pode ser iniciante (escolhe pela marca ou pelo frasco e não sabe o que é uma nota de saída) ou entusiasta (já tem perfumes favoritos e procura algo parecido). O questionário de perfil registra esse nível de conhecimento, e o agente ajusta a linguagem a partir dele.

| O que faz | O que espera |
|---|---|
| Responde o questionário de perfil | Achar perfumes que combinem comigo |
| Conversa com o consultor de IA | Comprar sem errar |

**Features:** Conta e Perfil Olfativo · Consultor Olfativo por IA · Sacola e Compra nas Lojas.

**No sistema:**
- cria a conta e faz login;
- responde o questionário de perfil;
- conversa com o consultor e recebe recomendações explicadas;
- consulta a ficha do perfume;
- guarda perfumes na sacola e finaliza, sendo levado às lojas;
- avalia as recomendações.

---

## Lojista Parceiro

**Quem é.** Dono ou responsável pelo e-commerce de uma loja de perfumaria que vende pela internet.

| O que faz | O que espera |
|---|---|
| Cadastra a loja e as ofertas | Receber clientes interessados |
| Acompanha os cliques recebidos | Ofertas sempre corretas |

**Features:** Cadastro da Loja · Gestão de Ofertas · Relatório de Cliques.

**No sistema:**
- solicita o cadastro da loja, que depois é aprovado pelo administrador;
- mantém os dados da loja;
- busca perfumes do catálogo e mantém as ofertas (CRUD), com link do produto e preço;
- pausa e reativa ofertas;
- consulta os cliques por oferta.

---

## Administrador

**Quem é.** Integrante da equipe responsável pela operação da plataforma. Também é quem entende de perfumaria: define o questionário e as regras do consultor de IA.

| O que faz | O que espera |
|---|---|
| Monta o questionário de perfil | Catálogo completo e confiável |
| Importa o catálogo e aprova lojistas | Plataforma segura e bem configurada |

**Features:** Questionário de Perfil · Catálogo via API · Gestão da Plataforma.

**No sistema:**
- mantém as perguntas do questionário e as alternativas, com os pesos por família olfativa (CRUD);
- importa o catálogo pela API, agenda a sincronização e consulta o log;
- revisa e oculta fichas de perfume;
- aprova ou bloqueia lojas parceiras e mantém os usuários (CRUD);
- mantém as diretrizes do agente, consulta as avaliações das recomendações e os indicadores de uso.
