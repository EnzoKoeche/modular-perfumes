# Trello — Modular Perfumes (v2)

Quadro: **Modular Perfumes**. Visibilidade: público, ou convide os orientadores. Senão, o link abre "quadro não encontrado" para quem avalia.

**Dica:** no Trello, colar várias linhas de uma vez em "Adicionar um cartão" oferece **"Criar N cartões"**, um por linha. Use os blocos de títulos abaixo assim e depois cole a descrição de cada card da Sprint 1.

**Etiquetas:** `Cliente` (laranja), `Curador` (verde), `Lojista` (azul), `Administrador` (roxo), `Sprint 1` (vermelho).

## Listas (nessa ordem)

```
Product Backlog
Sprint 1 Backlog
Em Desenvolvimento
Em Teste
Concluído
```

## Lista "Sprint 1 Backlog" — títulos

```
US1 – Realizar o cadastro do cliente
US2 – Realizar o login na plataforma
US3 – Responder o questionário de perfil olfativo
US4 – Manter as perguntas do questionário
US5 – Importar os perfumes pela API de catálogo
```

### Descrições

**US1 – Realizar o cadastro do cliente** · Cliente, Sprint 1
```
COMO: visitante não cadastrado
POSSO: criar minha conta informando nome, e-mail e senha.
PARA: ter acesso gratuito ao consultor olfativo.

CA1 — DADO QUE estou na página de cadastro, QUANDO informo nome, e-mail válido e senha com no mínimo 8 caracteres e aciono "Criar conta", ENTÃO o sistema grava a conta com o perfil "cliente", guarda a senha criptografada e me leva ao questionário de perfil olfativo.
CA2 — DADO QUE estou na página de cadastro, QUANDO informo um e-mail que já possui conta e aciono "Criar conta", ENTÃO o sistema não cria a conta e exibe a mensagem "Este e-mail já está cadastrado".
CA3 — DADO QUE estou na página de cadastro, QUANDO deixo um campo obrigatório vazio ou informo senha com menos de 8 caracteres e aciono "Criar conta", ENTÃO o sistema não envia o formulário e indica o campo que precisa ser corrigido.
```

**US2 – Realizar o login na plataforma** · Cliente, Curador, Lojista, Administrador, Sprint 1
```
COMO: usuário cadastrado (cliente, curador, lojista ou administrador)
POSSO: entrar na plataforma com e-mail e senha.
PARA: acessar as funções do meu perfil de acesso.

CA1 — DADO QUE tenho uma conta ativa, QUANDO informo e-mail e senha corretos e aciono "Entrar", ENTÃO o sistema abre a sessão e me leva à página inicial do meu perfil de acesso.
CA2 — DADO QUE estou na tela de login, QUANDO informo e-mail ou senha incorretos e aciono "Entrar", ENTÃO o sistema exibe "E-mail ou senha inválidos", sem indicar qual dos dois está errado.
CA3 — DADO QUE sou cliente e ainda não concluí o questionário de perfil, QUANDO faço login com sucesso, ENTÃO o sistema me leva direto ao questionário e bloqueia o consultor de IA até eu concluí-lo.
```

**US3 – Responder o questionário de perfil olfativo** · Cliente, Sprint 1
```
COMO: cliente autenticado
POSSO: responder o questionário de perfil olfativo.
PARA: liberar o consultor de IA e receber recomendações que combinem comigo.

CA1 — DADO QUE estou autenticado e existe um questionário ativo, QUANDO respondo todas as perguntas obrigatórias e aciono "Concluir", ENTÃO o sistema grava minhas respostas, gera meu perfil olfativo e libera o acesso ao consultor.
CA2 — DADO QUE estou respondendo o questionário, QUANDO aciono "Concluir" com alguma pergunta obrigatória sem resposta, ENTÃO o sistema não conclui o questionário e destaca as perguntas pendentes.
CA3 — DADO QUE saí da plataforma no meio do questionário, QUANDO faço login novamente, ENTÃO o sistema retoma o questionário a partir da primeira pergunta sem resposta.
```

**US4 – Manter as perguntas do questionário** · Curador, Sprint 1
```
COMO: curador olfativo
POSSO: cadastrar, consultar, alterar e excluir as perguntas do questionário de perfil.
PARA: que o questionário revele bem o perfil olfativo de cada cliente.

CA1 — DADO QUE estou na gestão do questionário, QUANDO informo o enunciado, o tipo de resposta (única ou múltipla escolha) e ao menos duas alternativas e aciono "Salvar", ENTÃO o sistema grava a pergunta como ativa e a exibe na lista, na ordem definida.
CA2 — DADO QUE existe uma pergunta cadastrada, QUANDO altero o enunciado ou as alternativas e aciono "Salvar", ENTÃO o sistema grava a alteração e os próximos clientes passam a ver a versão nova.
CA3 — DADO QUE a pergunta já foi respondida por algum cliente, QUANDO aciono "Excluir", ENTÃO o sistema mantém as respostas existentes, desativa a pergunta e deixa de exibi-la para novos clientes.
```

**US5 – Importar os perfumes pela API de catálogo** · Administrador, Sprint 1
```
COMO: administrador
POSSO: importar os perfumes da API externa de catálogo.
PARA: ter o catálogo completo, com foto, notas e acordes, sem cadastro manual.

CA1 — DADO QUE a chave de acesso da API está configurada, QUANDO aciono "Importar catálogo", ENTÃO o sistema grava os perfumes com nome, marca, foto, notas e acordes e registra no log a data, a quantidade importada e o status "concluída".
CA2 — DADO QUE um perfume já existe no catálogo, QUANDO a importação traz esse mesmo perfume, ENTÃO o sistema atualiza os dados usando o identificador da API, sem duplicar o perfume.
CA3 — DADO QUE a API está fora do ar ou recusa a chave de acesso, QUANDO aciono "Importar catálogo", ENTÃO o sistema mantém o catálogo atual e registra no log o status "falhou" com a mensagem de erro.
```

Coloque os três critérios de cada card também como **checklist "Critérios de aceite"**.

## Lista "Product Backlog" — títulos (23 PBIs, na ordem sugerida)

```
Manter as alternativas e os pesos
Consultar a ficha do perfume
Conversar com o agente consultor
Receber as recomendações personalizadas
Adicionar e remover perfumes da sacola
Buscar perfume do catálogo para ofertar
Solicitar o cadastro da loja parceira
Aprovar ou bloquear loja parceira
Manter as ofertas da loja
Finalizar a sacola abrindo as lojas
Consultar o log de importações
Manter os dados da conta do cliente
Manter os usuários da plataforma
Manter os dados da loja
Pausar ou reativar uma oferta
Avaliar a recomendação recebida
Manter as diretrizes do agente
Revisar a ficha de perfume importada
Ocultar ou reexibir perfume
Consultar as avaliações das recomendações
Consultar os cliques por oferta
Agendar a sincronização do catálogo
Consultar os indicadores de uso
```

**Etiquetas:**
- **Cliente:** ficha, conversar, recomendações, sacola (adicionar/remover e finalizar), dados da conta, avaliar.
- **Curador:** alternativas e pesos, diretrizes, revisar ficha, ocultar, avaliações.
- **Lojista:** buscar perfume, cadastro da loja, ofertas, dados da loja, pausar, cliques.
- **Administrador:** aprovar loja, log de importações, usuários, sincronização, indicadores.

Depois de criar, copie o link do quadro e cole no lugar de `[COLAR O LINK DO QUADRO]` no fim do Artefato 5 da especificação.
