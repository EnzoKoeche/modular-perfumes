"""Definição do DER lógico v2 do Modular Perfumes: tabelas, relacionamentos e grupos."""
AZUL, LARANJA, VERDE = '#1F3864', '#A64500', '#385723'
FONT = 'Helvetica'

# (nome, cor, [(marcador, coluna, tipo, restrição)])
T = {}


def tabela(nome, cor, cols):
    T[nome] = (cor, cols)


PK = ('PK', 'id', 'INT', 'AUTO_INCREMENT')

# ---------------------------------------------------------------- acesso
tabela('usuario', LARANJA, [
    PK,
    ('', 'nome', 'VARCHAR(80)', 'NN'),
    ('U', 'email', 'VARCHAR(120)', 'NN'),
    ('', 'senha_hash', 'VARCHAR(255)', 'NN'),
    ('', 'perfil', 'ENUM(CLIENTE,LOJISTA,ADMIN)', 'NN'),
    ('', 'ativo', 'TINYINT(1)', 'NN'),
    ('', 'tentativas_login', 'TINYINT', 'NN'),
    ('', 'bloqueado_ate', 'DATETIME', 'NULL'),
    ('', 'aceite_termos_em', 'DATETIME', 'NN'),
    ('', 'criado_em', 'DATETIME', 'NN'),
])

# ---------------------------------------------------------------- questionário e perfil
tabela('questionario', AZUL, [
    PK,
    ('', 'titulo', 'VARCHAR(120)', 'NN'),
    ('', 'ativo', 'TINYINT(1)', 'NN'),
    ('', 'criado_em', 'DATETIME', 'NN'),
])
tabela('pergunta', AZUL, [
    PK,
    ('FK', 'questionario_id', 'INT', 'NN'),
    ('', 'enunciado', 'VARCHAR(255)', 'NN'),
    ('', 'tipo', 'ENUM(UNICA,MULTIPLA)', 'NN'),
    ('', 'ordem', 'SMALLINT', 'NN'),
    ('', 'obrigatoria', 'TINYINT(1)', 'NN'),
    ('', 'ativa', 'TINYINT(1)', 'NN'),
    ('', 'atualizada_em', 'DATETIME', 'NN'),
])
tabela('alternativa', AZUL, [
    PK,
    ('FK', 'pergunta_id', 'INT', 'NN'),
    ('', 'texto', 'VARCHAR(150)', 'NN'),
    ('', 'ordem', 'SMALLINT', 'NN'),
    ('', 'ativa', 'TINYINT(1)', 'NN'),
])
tabela('alternativa_peso', VERDE, [
    ('PK,FK', 'alternativa_id', 'INT', 'NN'),
    ('PK,FK', 'familia_id', 'INT', 'NN'),
    ('', 'peso', 'DECIMAL(4,2)', 'NN'),
])
tabela('resposta_questionario', LARANJA, [
    PK,
    ('FK', 'usuario_id', 'INT', 'NN'),
    ('FK', 'questionario_id', 'INT', 'NN'),
    ('', 'iniciada_em', 'DATETIME', 'NN'),
    ('', 'concluida_em', 'DATETIME', 'NULL'),
])
tabela('resposta_item', VERDE, [
    ('PK,FK', 'resposta_id', 'INT', 'NN'),
    ('PK,FK', 'pergunta_id', 'INT', 'NN'),
    ('PK,FK', 'alternativa_id', 'INT', 'NN'),
    ('', 'respondida_em', 'DATETIME', 'NN'),
])
tabela('perfil_olfativo', LARANJA, [
    PK,
    ('FK,U', 'usuario_id', 'INT', 'NN'),
    ('FK', 'resposta_id', 'INT', 'NN'),
    ('', 'nivel_conhecimento', 'ENUM(INICIANTE,INTERMEDIARIO,AVANCADO)', 'NN'),
    ('', 'gerado_em', 'DATETIME', 'NN'),
])
tabela('perfil_familia', VERDE, [
    ('PK,FK', 'perfil_id', 'INT', 'NN'),
    ('PK,FK', 'familia_id', 'INT', 'NN'),
    ('', 'afinidade', 'DECIMAL(5,2)', 'NN'),
])

# ---------------------------------------------------------------- catálogo
tabela('marca', AZUL, [
    PK,
    ('U', 'nome', 'VARCHAR(80)', 'NN'),
    ('', 'pais', 'VARCHAR(60)', 'NULL'),
])
tabela('familia_olfativa', AZUL, [
    PK,
    ('U', 'nome', 'VARCHAR(50)', 'NN'),
    ('', 'descricao', 'VARCHAR(255)', 'NULL'),
])
tabela('nota_olfativa', AZUL, [
    PK,
    ('U', 'nome', 'VARCHAR(80)', 'NN'),
])
tabela('acorde', AZUL, [
    PK,
    ('U', 'nome', 'VARCHAR(60)', 'NN'),
    ('FK', 'familia_id', 'INT', 'NULL'),
])
tabela('perfume', LARANJA, [
    PK,
    ('U', 'api_id', 'VARCHAR(64)', 'NN'),
    ('FK', 'marca_id', 'INT', 'NN'),
    ('', 'nome', 'VARCHAR(150)', 'NN'),
    ('', 'genero', 'ENUM(MASCULINO,FEMININO,UNISSEX)', 'NULL'),
    ('', 'ano', 'SMALLINT', 'NULL'),
    ('', 'imagem_url', 'VARCHAR(500)', 'NULL'),
    ('', 'fixacao', 'VARCHAR(40)', 'NULL'),
    ('', 'projecao', 'VARCHAR(40)', 'NULL'),
    ('', 'concentracao', 'VARCHAR(40)', 'NULL'),
    ('', 'avaliacao', 'DECIMAL(4,2)', 'NULL'),
    ('', 'popularidade', 'VARCHAR(30)', 'NULL'),
    ('', 'descricao', 'TEXT', 'NULL'),
    ('', 'visivel', 'TINYINT(1)', 'NN'),
    ('', 'campos_revisados', 'JSON', 'NULL'),
    ('', 'importado_em', 'DATETIME', 'NN'),
    ('', 'atualizado_em', 'DATETIME', 'NN'),
])
tabela('perfume_nota', VERDE, [
    ('PK,FK', 'perfume_id', 'INT', 'NN'),
    ('PK,FK', 'nota_id', 'INT', 'NN'),
    ('PK', 'nivel', 'ENUM(SAIDA,CORPO,FUNDO)', 'NN'),
])
tabela('perfume_acorde', VERDE, [
    ('PK,FK', 'perfume_id', 'INT', 'NN'),
    ('PK,FK', 'acorde_id', 'INT', 'NN'),
    ('', 'intensidade', 'VARCHAR(20)', 'NULL'),
])
tabela('importacao_catalogo', AZUL, [
    PK,
    ('', 'origem', 'ENUM(MANUAL,AGENDADA)', 'NN'),
    ('', 'status', 'ENUM(EM_ANDAMENTO,CONCLUIDA,FALHOU)', 'NN'),
    ('', 'qtd_incluidos', 'INT', 'NN'),
    ('', 'qtd_atualizados', 'INT', 'NN'),
    ('', 'mensagem_erro', 'TEXT', 'NULL'),
    ('', 'iniciada_em', 'DATETIME', 'NN'),
    ('', 'finalizada_em', 'DATETIME', 'NULL'),
])

# ---------------------------------------------------------------- consultor IA
tabela('diretriz_agente', AZUL, [
    PK,
    ('', 'titulo', 'VARCHAR(120)', 'NN'),
    ('', 'conteudo', 'TEXT', 'NN'),
    ('', 'ordem', 'SMALLINT', 'NN'),
    ('', 'ativa', 'TINYINT(1)', 'NN'),
    ('', 'atualizada_em', 'DATETIME', 'NN'),
])
tabela('conversa', LARANJA, [
    PK,
    ('FK', 'usuario_id', 'INT', 'NN'),
    ('', 'iniciada_em', 'DATETIME', 'NN'),
    ('', 'ultima_mensagem_em', 'DATETIME', 'NN'),
])
tabela('mensagem', AZUL, [
    PK,
    ('FK', 'conversa_id', 'INT', 'NN'),
    ('', 'papel', 'ENUM(USUARIO,ASSISTENTE)', 'NN'),
    ('', 'conteudo_json', 'JSON', 'NN'),
    ('', 'modelo', 'VARCHAR(40)', 'NULL'),
    ('', 'tokens_entrada', 'INT', 'NULL'),
    ('', 'tokens_saida', 'INT', 'NULL'),
    ('', 'tokens_cache', 'INT', 'NULL'),
    ('', 'enviada_em', 'DATETIME', 'NN'),
])
tabela('recomendacao', LARANJA, [
    PK,
    ('FK', 'conversa_id', 'INT', 'NN'),
    ('FK', 'perfume_id', 'INT', 'NN'),
    ('', 'posicao', 'TINYINT', 'NN'),
    ('', 'justificativa', 'VARCHAR(500)', 'NN'),
    ('', 'gerada_em', 'DATETIME', 'NN'),
])
tabela('avaliacao_recomendacao', AZUL, [
    PK,
    ('FK,U', 'recomendacao_id', 'INT', 'NN'),
    ('', 'nota', 'TINYINT (1..5)', 'NN'),
    ('', 'comentario', 'VARCHAR(500)', 'NULL'),
    ('', 'avaliada_em', 'DATETIME', 'NN'),
])

# ---------------------------------------------------------------- sacola e lojas
tabela('sacola_item', VERDE, [
    ('PK,FK', 'usuario_id', 'INT', 'NN'),
    ('PK,FK', 'perfume_id', 'INT', 'NN'),
    ('', 'adicionado_em', 'DATETIME', 'NN'),
])
tabela('loja', LARANJA, [
    PK,
    ('FK,U', 'usuario_id', 'INT', 'NN'),
    ('', 'nome', 'VARCHAR(120)', 'NN'),
    ('U', 'cnpj', 'CHAR(14)', 'NN'),
    ('', 'site_url', 'VARCHAR(255)', 'NN'),
    ('', 'status', 'ENUM(PENDENTE,APROVADA,BLOQUEADA)', 'NN'),
    ('FK', 'decidido_por', 'INT', 'NULL'),
    ('', 'decidido_em', 'DATETIME', 'NULL'),
    ('', 'criado_em', 'DATETIME', 'NN'),
])
tabela('oferta', LARANJA, [
    PK,
    ('FK,U¹', 'loja_id', 'INT', 'NN'),
    ('FK,U¹', 'perfume_id', 'INT', 'NN'),
    ('', 'url', 'VARCHAR(500)', 'NN'),
    ('', 'preco', 'DECIMAL(10,2)', 'NN'),
    ('', 'ativa', 'TINYINT(1)', 'NN'),
    ('', 'atualizada_em', 'DATETIME', 'NN'),
])
tabela('clique_oferta', AZUL, [
    PK,
    ('FK', 'oferta_id', 'INT', 'NN'),
    ('FK', 'usuario_id', 'INT', 'NULL'),
    ('', 'origem', 'ENUM(SACOLA,FICHA,RECOMENDACAO)', 'NN'),
    ('', 'clicado_em', 'DATETIME', 'NN'),
])

# (pai, filho, cardinalidade, fk anulável?)
R = [
    ('questionario', 'pergunta', '1:N', False),
    ('pergunta', 'alternativa', '1:N', False),
    ('alternativa', 'alternativa_peso', '1:N', False),
    ('familia_olfativa', 'alternativa_peso', '1:N', False),
    ('usuario', 'resposta_questionario', '1:N', False),
    ('questionario', 'resposta_questionario', '1:N', False),
    ('resposta_questionario', 'resposta_item', '1:N', False),
    ('pergunta', 'resposta_item', '1:N', False),
    ('alternativa', 'resposta_item', '1:N', False),
    ('usuario', 'perfil_olfativo', '1:1', False),
    ('resposta_questionario', 'perfil_olfativo', '1:1', False),
    ('perfil_olfativo', 'perfil_familia', '1:N', False),
    ('familia_olfativa', 'perfil_familia', '1:N', False),
    ('marca', 'perfume', '1:N', False),
    ('perfume', 'perfume_nota', '1:N', False),
    ('nota_olfativa', 'perfume_nota', '1:N', False),
    ('perfume', 'perfume_acorde', '1:N', False),
    ('acorde', 'perfume_acorde', '1:N', False),
    ('familia_olfativa', 'acorde', '1:N', True),
    ('usuario', 'conversa', '1:N', False),
    ('conversa', 'mensagem', '1:N', False),
    ('conversa', 'recomendacao', '1:N', False),
    ('perfume', 'recomendacao', '1:N', False),
    ('recomendacao', 'avaliacao_recomendacao', '1:1', False),
    ('usuario', 'sacola_item', '1:N', False),
    ('perfume', 'sacola_item', '1:N', False),
    ('usuario', 'loja', '1:1', False),
    ('usuario', 'loja', '1:N', True),
    ('loja', 'oferta', '1:N', False),
    ('perfume', 'oferta', '1:N', False),
    ('oferta', 'clique_oferta', '1:N', False),
    ('usuario', 'clique_oferta', '1:N', True),
]

GRUPOS = [
    ('acesso', 'ACESSO', ['usuario']),
    ('questionario', 'QUESTIONÁRIO E PERFIL OLFATIVO',
     ['questionario', 'pergunta', 'alternativa', 'alternativa_peso', 'resposta_questionario',
      'resposta_item', 'perfil_olfativo', 'perfil_familia']),
    ('catalogo', 'CATÁLOGO (IMPORTADO DA API)',
     ['marca', 'familia_olfativa', 'nota_olfativa', 'acorde', 'perfume', 'perfume_nota',
      'perfume_acorde', 'importacao_catalogo']),
    ('ia', 'CONSULTOR OLFATIVO POR IA',
     ['diretriz_agente', 'conversa', 'mensagem', 'recomendacao', 'avaliacao_recomendacao']),
    ('sacola', 'SACOLA E LOJAS PARCEIRAS', ['sacola_item', 'loja', 'oferta', 'clique_oferta']),
]


# ---------------------------------------------------------------- escopo da Sprint 1
# Tabelas que as user stories da 1ª Sprint gravam ou leem (cadastro, login, questionário,
# perguntas e importação do catálogo). `alternativa_peso` e `familia_olfativa` entram porque
# gerar o perfil olfativo (US3) usa os pesos, que vêm da carga inicial do script SQL.
SPRINT1 = [
    'usuario',
    'questionario', 'pergunta', 'alternativa', 'alternativa_peso', 'familia_olfativa',
    'resposta_questionario', 'resposta_item', 'perfil_olfativo', 'perfil_familia',
    'marca', 'nota_olfativa', 'acorde', 'perfume', 'perfume_nota', 'perfume_acorde',
    'importacao_catalogo',
]

# Tabelas que entram na 2ª Sprint (consultor de IA), criadas por um script próprio
SPRINT2 = ['conversa', 'mensagem', 'recomendacao']

# coluna FK -> tabela referenciada
FK_REF = {
    'usuario_id': 'usuario', 'questionario_id': 'questionario', 'pergunta_id': 'pergunta',
    'alternativa_id': 'alternativa', 'familia_id': 'familia_olfativa', 'resposta_id': 'resposta_questionario',
    'perfil_id': 'perfil_olfativo', 'marca_id': 'marca', 'nota_id': 'nota_olfativa', 'acorde_id': 'acorde',
    'perfume_id': 'perfume', 'conversa_id': 'conversa', 'recomendacao_id': 'recomendacao',
    'loja_id': 'loja', 'oferta_id': 'oferta', 'decidido_por': 'usuario',
}

# (tabela, coluna) com ON DELETE diferente de RESTRICT
ON_DELETE = {
    ('alternativa_peso', 'alternativa_id'): 'CASCADE',
    ('resposta_questionario', 'usuario_id'): 'CASCADE',   # RN-17: excluir conta apaga respostas
    ('resposta_item', 'resposta_id'): 'CASCADE',
    ('perfil_olfativo', 'usuario_id'): 'CASCADE',         # RN-17
    ('perfil_olfativo', 'resposta_id'): 'CASCADE',
    ('perfil_familia', 'perfil_id'): 'CASCADE',
    ('perfume_nota', 'perfume_id'): 'CASCADE',
    ('perfume_acorde', 'perfume_id'): 'CASCADE',
    ('acorde', 'familia_id'): 'SET NULL',
    ('conversa', 'usuario_id'): 'CASCADE',
    ('mensagem', 'conversa_id'): 'CASCADE',
    ('recomendacao', 'conversa_id'): 'CASCADE',
    ('avaliacao_recomendacao', 'recomendacao_id'): 'CASCADE',
    ('sacola_item', 'usuario_id'): 'CASCADE',
    ('clique_oferta', 'usuario_id'): 'SET NULL',          # RN-17: clique fica anonimizado
    ('loja', 'decidido_por'): 'SET NULL',
    ('oferta', 'loja_id'): 'CASCADE',
}
