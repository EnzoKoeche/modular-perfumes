# Modular Perfumes — como preparar a máquina e rodar

Projeto da disciplina **Experiência Criativa** (PUCPR): plataforma de consultoria olfativa com IA.
Python + Flask + Jinja2 + Bootstrap 5 + MySQL 8 (SQL escrito à mão, com PyMySQL).

Este arquivo é o passo a passo para deixar o projeto rodando **exatamente igual** em outra máquina.
Serve tanto para uma pessoa quanto para um assistente de código (Claude Code): siga na ordem e
confira o resultado de cada passo antes de ir para o próximo.

---

## 1. O que precisa estar instalado

| Programa | Para quê | Como conferir |
|---|---|---|
| **Git** | baixar o repositório | `git --version` |
| **Python 3.9 ou mais novo** | rodar o site | `python3 --version` |
| **Docker Desktop** | subir o banco MySQL | `docker --version` (e o app **aberto**) |
| **VS Code** (opcional) | editar o código | `code --version` |

No macOS, com [Homebrew](https://brew.sh): `brew install --cask docker visual-studio-code`
No Windows: baixe Docker Desktop, Python e VS Code dos sites oficiais e marque *"Add Python to PATH"*.

> O Docker Desktop precisa estar **aberto** (ícone da baleia na barra) antes de qualquer comando `docker`.

---

## 2. Baixar o projeto

```bash
git clone https://github.com/EnzoKoeche/modular-perfumes.git
cd modular-perfumes
```

## 3. Subir o banco de dados

O `docker-compose.yml` cria um MySQL 8.4 na porta **3307** e, na primeira subida, roda sozinho os
scripts `entregas/sql/modular_perfumes_sprint1.sql` e `..._sprint2.sql`, que criam as 20 tabelas e a
carga inicial (famílias olfativas + o questionário com 11 perguntas).

```bash
docker compose up -d db
docker compose ps          # espere aparecer "healthy" (uns 15 segundos)
```

## 4. Preparar o Python

```bash
python3 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt  # site + pytest
```

## 5. Criar o arquivo `.env`

```bash
cp .env.example .env                 # Windows: copy .env.example .env
```

Depois abra o `.env` e ajuste:

| Variável | O que pôr |
|---|---|
| `SECRET_KEY` | qualquer texto longo e aleatório (assina a sessão) |
| `CATALOGO_PROVEDOR` | `exemplo` para desenvolver sem gastar cota da API; `fragella` para importar o catálogo real |
| `FRAGELLA_API_KEY` | só é usada quando o provedor é `fragella` |
| `ANTHROPIC_API_KEY` | **chave pessoal de quem for testar o consultor de IA.** Sem ela o site funciona normalmente; só o chat do consultor mostra o aviso "não configurado" |

O `.env` está no `.gitignore` e **nunca** deve ser enviado ao GitHub.

## 6. Criar o usuário administrador

```bash
flask --app app criar-admin admin@modular.local "Administrador"
# ele pergunta a senha duas vezes (mínimo 8 caracteres)
```

## 7. Subir o site

```bash
flask --app app run --port 5050 --debug
```

Abra **http://127.0.0.1:5050**. A porta 5000 no macOS é usada pelo AirPlay, por isso 5050.

## 8. Conferir que está tudo certo

```bash
pytest -q       # esperado: 27 passed
```

Os testes recriam um banco separado (`modular_perfumes_teste`) a partir dos scripts SQL, então
**não apagam** os dados que você tiver no banco de desenvolvimento.

---

## 9. Ver o banco pelo navegador (opcional, bom para apresentar)

```bash
docker run -d --name modular-adminer --network modular-perfumes_default \
  -e ADMINER_DEFAULT_SERVER=db -p 8080:8080 adminer
```

Abra **http://127.0.0.1:8080** e entre com: sistema `MySQL` · servidor `db` · usuário `modular` ·
senha `modular_dev` · base `modular_perfumes`. (Para desligar: `docker stop modular-adminer`.)

---

## 10. Roteiro de demonstração (a 1ª Sprint inteira)

1. **US1 — cadastro:** `/cadastro`, criar conta → cai no questionário.
2. **US3 — questionário:** responder as 11 perguntas → o perfil olfativo é gerado em `/inicio`.
3. **US2 — login:** sair e entrar de novo → volta direto ao perfil.
4. **US4 — CRUD do admin:** entrar como admin → *Questionário* → criar, alterar e excluir pergunta.
   Pergunta que já tem resposta é **desativada**, não apagada (regra RN-05).
5. **US5 — catálogo:** *Catálogo* → importar uma marca → o log registra incluídos e atualizados.
6. **Extras da Sprint 2:** vitrine em `/perfumes/` e o consultor de IA em `/consultor/`.

---

## 11. Mapa do código

| O quê | Onde |
|---|---|
| Cadastro, login, controle de acesso | `app/auth.py` |
| Questionário e geração do perfil | `app/questionario.py` |
| Área do administrador (perguntas, importação) | `app/admin.py` |
| Integração com a API de catálogo | `app/catalogo.py` |
| Vitrine e ficha do perfume | `app/vitrine.py` |
| Consultor de IA (ferramentas + chamada ao modelo) | `app/consultor.py` |
| Telas (Jinja2) | `app/templates/` |
| CSS próprio | `public/static/css/estilo.css` |
| Banco: script oficial e dicionário | `entregas/sql/` e `docs/07-modelo-de-dados.md` |
| Documentação completa (requisitos, backlog, arquitetura) | `docs/00` a `docs/12` |

---

## 12. Regras para quem for mexer (inclusive assistentes de código)

- **Mudança mínima:** não reformatar nem "limpar de passagem" arquivos que não são o objetivo da tarefa.
- **Nunca commitar** `.env`, chaves de API, `.venv/` nem dados baixados da API.
- **Os testes acompanham as regras:** se mudar uma regra de negócio (tamanho de senha, número de
  tentativas, limite do consultor), ajuste o teste correspondente em `tests/` e rode `pytest -q`.
- **Banco é gerado por script:** ao criar ou alterar tabela, atualize também
  `entregas/sql/modular_perfumes_sprint1.sql` e `docs/07-modelo-de-dados.md`. A fonte única do modelo
  é `entregas/der/fonte/modelo.py`, que gera o DER, o dicionário e o SQL.
- **Documentos das entregas** (`.docx`, PNG do Canvas, PDF da apresentação) são **gerados por código**,
  em `entregas/*/fonte/`. Edite a fonte e regere, não o arquivo final.
- **IDs são estáveis:** RF-xx, RN-xx, US-x e PBI não são renumerados.

---

## 13. Se der errado

| Sintoma | Causa e solução |
|---|---|
| `Can't connect to MySQL server` | Docker Desktop fechado ou banco no ar ainda: `docker compose up -d db` e espere `healthy`. |
| `Port 5050 is in use` | Já existe um site rodando. macOS/Linux: `kill $(lsof -ti tcp:5050)`. |
| `Access denied for user` | O `.env` não bate com o `docker-compose.yml` (usuário `modular`, senha `modular_dev`, porta 3307). |
| Acentos aparecem como `vocÃª` | O banco foi criado por um script antigo: `docker compose down -v` e suba de novo (apaga os dados e recria). |
| "O consultor está indisponível" | Falta `ANTHROPIC_API_KEY` no `.env`, ou o limite de 30 mensagens por dia foi atingido. |
| `pytest` não encontra o banco | Os testes usam o usuário `root` com a senha `root_dev` na porta 3307 — é o padrão do compose. |
