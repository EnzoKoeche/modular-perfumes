# 00 — Visão geral do produto

## O problema

Quem compra perfume pela internet não pode sentir o cheiro antes. A maioria das pessoas também não sabe ler uma ficha olfativa: "notas de saída", "acorde amadeirado" e "família chypre" não dizem nada para quem está começando. O resultado é compra às cegas, arrependimento e devolução. Do outro lado, lojas de perfumaria gastam para atrair visitantes que ainda não sabem o que querem.

## A solução

**Modular Perfumes** é uma plataforma web gratuita, com cadastro e login, em que um **agente de inteligência artificial** atua como consultor olfativo.

1. O cliente cria a conta e responde um **questionário de perfil olfativo**: quem ele é, o que costuma gostar e quanto entende de perfume.
2. Com o perfil pronto, o **consultor de IA** é liberado. Ele conversa com o cliente e recomenda perfumes do catálogo, explicando por que cada um combina com ele.
3. O **catálogo** (foto, marca, notas e acordes) é importado de uma **API externa de fragrâncias**. Ninguém cadastra perfume à mão.
4. O cliente guarda na **sacola** os perfumes de que gostou. Ao **finalizar**, o site abre, em abas separadas, a página da **loja parceira** onde comprar cada um.
5. O site **não vende**: não cobra, não guarda cartão e não entrega. A compra acontece na loja.

## Objetivos (Artefato 1)

| # | Objetivo |
|---|---|
| 1 | Ajudar quem não entende de perfumaria a descobrir os perfumes que combinam com o próprio perfil, por meio de um questionário de perfil olfativo e de um agente de IA que conversa com o cliente antes de recomendar. |
| 2 | Reunir em um único lugar um catálogo completo e confiável — foto, notas olfativas e acordes de cada perfume —, importado de uma API externa e revisado por um curador olfativo. |
| 3 | Levar o cliente até as lojas parceiras onde comprar os perfumes escolhidos, gerando cliques qualificados para os lojistas e reduzindo a compra às cegas e o arrependimento. |

## É / Não é / Faz / Não faz (Artefato 2)

| É | Não é |
|---|---|
| Uma plataforma web gratuita de consultoria olfativa, com cadastro, login e senha. | Uma loja virtual: não vende, não cobra e não entrega perfumes. |
| Um agente de IA que conversa com o cliente e recomenda perfumes a partir do perfil dele. | Um marketplace com pagamento ou intermediação da compra. |
| Um catálogo de perfumes com foto, notas e acordes, importado de uma API externa. | Uma rede social ou fórum de perfumaria. |
| Uma vitrine que leva o cliente às lojas parceiras onde comprar. | Um serviço de saúde: não avalia alergia nem faz recomendação médica. |

| Faz | Não faz |
|---|---|
| Exige cadastro, login e o questionário de perfil olfativo antes de liberar o consultor de IA. | Não processa pagamento nem guarda dados de cartão. |
| Conversa com o cliente e recomenda perfumes, explicando o motivo de cada indicação. | Não entrega nem troca produtos: a compra e o pós-venda são responsabilidade da loja. |
| Mostra a ficha de cada perfume: foto, notas de saída, corpo e fundo, e acordes. | Não garante a percepção do cheiro na pele de cada pessoa. |
| Guarda na sacola os perfumes de que o cliente gostou e, ao finalizar, abre a página da loja de cada um. | Não libera o consultor de IA sem login e sem o questionário respondido. |
| Permite ao curador manter o questionário, ao lojista manter suas ofertas e ao administrador importar o catálogo e gerenciar os usuários. | |

## Visão de produto (Artefato 3)

| Campo | Conteúdo |
|---|---|
| **Cliente-alvo** | Pessoas de 18 a 45 anos que querem comprar perfume pela internet e não sabem qual escolher; iniciantes que não conhecem notas nem famílias olfativas; entusiastas que buscam um perfume novo parecido com os que já gostam; lojas de perfumaria que querem receber clientes já interessados. |
| **Categoria** | Plataforma web gratuita de consultoria olfativa, com agente de inteligência artificial, catálogo integrado a uma API externa e redirecionamento para lojas parceiras. |
| **Benefício-chave** | Descobrir, depois de um questionário e de uma conversa, os perfumes que combinam com o próprio perfil — e ir direto à loja certa para comprar, sem tentativa e erro. |
| **Diferencial** | Ao contrário das lojas e dos sites de resenha, que mostram listas e filtros, o Modular Perfumes primeiro entende quem é o cliente, pelo questionário de perfil, e depois recomenda por meio de um agente de IA, com ficha completa e link para comprar. |
| **Meta-valor** | Aumentar o acerto na escolha do perfume e os cliques qualificados para as lojas parceiras, reduzindo o arrependimento e as devoluções. |

Em uma frase: *para quem quer comprar perfume pela internet e não sabe qual escolher, o Modular Perfumes é um consultor olfativo com IA que entende o seu perfil e leva você direto à loja do perfume certo — ao contrário das lojas, que só mostram listas e filtros.*

## Histórico da visão

| Data | Mudança | Motivo |
|---|---|---|
| 2026-08-31 | Visão entregue: e-commerce de perfumaria com agentes de IA. Personas "Cliente Iniciante", "Cliente Entusiasta" e "Administrador". | Entrega dos artefatos 1–6. |
| 2026-09-14 | O produto passa a ser o **consultor de IA**: questionário de perfil obrigatório, catálogo via API, compra em lojas parceiras por redirecionamento, CRUDs explícitos. Personas: Cliente, Curador Olfativo, Lojista Parceiro e Administrador. | Feedback do professor: as personas eram "cliente, cliente", as features precisavam mudar e o sistema precisa de login e CRUD. |
