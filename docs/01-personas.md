# 01 — Personas

São quatro personas com **papéis diferentes no sistema**, e não variações do mesmo cliente. Cada uma tem um perfil de acesso próprio (`usuario.perfil`) e as suas próprias telas e CRUDs.

| Persona | Perfil de acesso | Em uma frase |
|---|---|---|
| Cliente | `CLIENTE` | Quer descobrir perfumes que combinam com ele e comprar sem errar. |
| Curador Olfativo | `CURADOR` | Garante que o questionário, as fichas e o agente falem a verdade sobre perfumes. |
| Lojista Parceiro | `LOJISTA` | Quer que clientes interessados cheguem à loja dele. |
| Administrador | `ADMIN` | Mantém a plataforma funcionando: catálogo, usuários e indicadores. |

---

## Cliente

**Quem é.** Pessoa de 18 a 45 anos que compra pela internet. Pode ser iniciante (escolhe pela marca ou pelo frasco e não sabe o que é uma nota de saída) ou entusiasta (já tem perfumes favoritos e procura algo parecido). O questionário de perfil registra esse nível de conhecimento, e o agente ajusta a linguagem a partir dele.

**O que faz no sistema.**
- Cria a conta e faz login.
- Responde o questionário de perfil olfativo, sem o qual o consultor não é liberado.
- Conversa com o consultor de IA e recebe recomendações explicadas.
- Consulta a ficha do perfume (foto, notas e acordes).
- Guarda na sacola os perfumes de que gostou e finaliza, sendo levado às lojas.
- Avalia as recomendações.

**O que espera.** Achar perfumes que combinem com ele, entender o motivo da indicação em linguagem simples e não errar na compra.

**Dores.** Recomendação genérica, igual para todo mundo; não entende notas nem acordes; compra às cegas; informação espalhada em vários sites.

---

## Curador Olfativo

**Quem é.** Pessoa que entende de perfumaria: consultor de perfumaria, vendedor experiente ou entusiasta avançado convidado pela equipe. É a "voz técnica" da plataforma.

**O que faz no sistema.**
- Mantém as perguntas do questionário de perfil (CRUD).
- Mantém as alternativas de cada pergunta e os pesos que ligam cada alternativa às famílias olfativas.
- Revisa as fichas importadas da API, corrigindo ou completando dados, e oculta perfumes fora do padrão.
- Mantém as diretrizes do agente consultor: regras, limites e tom de voz.
- Consulta as avaliações que os clientes deram às recomendações.

**O que espera.** Um questionário que revele de fato o perfil do cliente, um catálogo confiável e recomendações em que ele próprio confiaria.

**Dores.** Perguntas genéricas geram perfil mal definido; fichas incompletas vindas da API; a IA sai do assunto ou responde de forma inconsistente.

---

## Lojista Parceiro

**Quem é.** Dono ou responsável pelo e-commerce de uma loja de perfumaria que vende pela internet.

**O que faz no sistema.**
- Solicita o cadastro da loja, que depois é aprovado pelo administrador.
- Mantém os dados da loja.
- Busca perfumes do catálogo e mantém as ofertas (CRUD): link da página do produto e preço.
- Pausa e reativa ofertas.
- Consulta quantos cliques cada oferta recebeu.

**O que espera.** Receber clientes que já decidiram o que querem e manter as ofertas sempre corretas.

**Dores.** A loja não chega a quem já quer comprar; link quebrado e preço desatualizado queimam a reputação; não consegue medir o retorno.

---

## Administrador

**Quem é.** Integrante da equipe responsável pela operação da plataforma.

**O que faz no sistema.**
- Importa o catálogo pela API externa, agenda a sincronização e consulta o log de importações.
- Aprova ou bloqueia lojas parceiras.
- Mantém os usuários da plataforma (CRUD), inclusive criando contas de curador e de outros administradores.
- Consulta os indicadores de uso: cadastros, questionários concluídos, conversas, consumo da IA e cliques nas lojas.

**O que espera.** Catálogo completo e atualizado sem trabalho manual, e plataforma segura e estável.

**Dores.** Cadastro manual lento e sem foto; acesso sem controle; lojista falso; custo de IA invisível; decisões sem dados.
