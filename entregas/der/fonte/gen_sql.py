"""Gera o script SQL (MySQL 8) das tabelas da 1ª Sprint a partir de modelo.py.

uso: python3 gen_sql.py ../../sql/modular_perfumes_sprint1.sql
     python3 gen_sql.py ../../sql/modular_perfumes_sprint2.sql sprint2
"""
import re
import sys

from modelo import T, SPRINT1, SPRINT2, FK_REF, ON_DELETE

DEFAULTS = {
    'ativo': '1', 'ativa': '1', 'visivel': '1', 'obrigatoria': '1',
    'tentativas_login': '0', 'qtd_incluidos': '0', 'qtd_atualizados': '0',
    'perfil': "'CLIENTE'", 'origem': "'MANUAL'", 'status': "'EM_ANDAMENTO'",
}
AGORA = {'criado_em', 'importado_em', 'iniciada_em', 'respondida_em', 'gerado_em', 'aceite_termos_em',
         'enviada_em', 'gerada_em', 'ultima_mensagem_em'}
AGORA_ATUALIZA = {'atualizado_em', 'atualizada_em'}
CHECKS = {
    'alternativa_peso': ['CHECK (peso >= 0)'],
    'perfil_familia': ['CHECK (afinidade >= 0)'],
    'importacao_catalogo': ['CHECK (qtd_incluidos >= 0 AND qtd_atualizados >= 0)'],
}
INDICES = {
    'perfume': ['INDEX idx_perfume_visivel_nome (visivel, nome)'],
    'resposta_questionario': ['INDEX idx_resposta_usuario_concluida (usuario_id, concluida_em)'],
    'pergunta': ['INDEX idx_pergunta_questionario_ordem (questionario_id, ordem)'],
}


def sql_tipo(tipo):
    m = re.match(r'ENUM\((.*)\)', tipo)
    if m:
        return 'ENUM(' + ', '.join(f"'{v.strip()}'" for v in m.group(1).split(',')) + ')'
    return re.sub(r'\s*\(1\.\.5\)', '', tipo)


def ordem_dependencias(tabelas, ja_existentes=()):
    feitas, ordem = set(ja_existentes), []
    pendentes = list(tabelas)
    while pendentes:
        for t in pendentes:
            refs = {FK_REF[c] for m, c, _, _ in T[t][1] if 'FK' in m} - {t}
            escopo = set(tabelas) | set(ja_existentes)
            assert refs <= escopo, f'{t} referencia tabela fora do escopo: {refs - escopo}'
            if refs <= feitas:
                ordem.append(t)
                feitas.add(t)
                pendentes.remove(t)
                break
        else:
            raise SystemExit('ciclo de FK em: %s' % pendentes)
    return ordem


def create_table(t):
    cols = T[t][1]
    linhas, pks, fks = [], [], []
    for mark, col, tipo, restr in cols:
        partes = [f'  {col}', sql_tipo(tipo)]
        if restr == 'AUTO_INCREMENT':
            partes += ['NOT NULL', 'AUTO_INCREMENT']
        else:
            partes.append('NOT NULL' if restr == 'NN' else 'NULL')
        if col in DEFAULTS:
            partes.append('DEFAULT ' + DEFAULTS[col])
        if col in AGORA:
            partes.append('DEFAULT CURRENT_TIMESTAMP')
        if col in AGORA_ATUALIZA:
            partes.append('DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')
        if tipo.startswith('TINYINT (1..5)'):
            partes.append(f'CHECK ({col} BETWEEN 1 AND 5)')
        linhas.append(' '.join(partes))
        if 'PK' in mark:
            pks.append(col)
        if 'FK' in mark:
            fks.append(col)
    linhas.append(f'  PRIMARY KEY ({", ".join(pks)})')
    for mark, col, _, _ in cols:
        if re.search(r'(^|,)U($|,)', mark):
            linhas.append(f'  UNIQUE KEY uk_{t}_{col} ({col})')
    composto = [c for m, c, _, _ in cols if 'U¹' in m]
    if composto:
        linhas.append(f'  UNIQUE KEY uk_{t}_{"_".join(composto)} ({", ".join(composto)})')
    linhas += ['  ' + i for i in INDICES.get(t, [])]
    linhas += ['  ' + c for c in CHECKS.get(t, [])]
    for col in fks:
        ref = FK_REF[col]
        acao = ON_DELETE.get((t, col), 'RESTRICT')
        linhas.append(f'  CONSTRAINT fk_{t}_{col} FOREIGN KEY ({col}) REFERENCES {ref} (id) ON DELETE {acao}')
    return (f'CREATE TABLE {t} (\n' + ',\n'.join(linhas) +
            '\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;\n')


if len(sys.argv) > 2 and sys.argv[2] == 'sprint2':
    ordem = ordem_dependencias(SPRINT2, ja_existentes=SPRINT1)
    out = ['''-- =====================================================================
-- MODULAR PERFUMES — Script SQL da 2ª Sprint (consultor de IA)
-- Rodar DEPOIS de modular_perfumes_sprint1.sql. Gerado de entregas/der/fonte/modelo.py.
-- =====================================================================

SET NAMES utf8mb4;
USE modular_perfumes;
''']
    for t in reversed(ordem):
        out.append(f'DROP TABLE IF EXISTS {t};')
    out.append('')
    for t in ordem:
        out.append(create_table(t))
    open(sys.argv[1], 'w').write('\n'.join(out))
    print('ok', sys.argv[1], 'tabelas:', len(ordem))
    sys.exit(0)

ordem = ordem_dependencias(SPRINT1)
out = ["""-- =====================================================================
-- MODULAR PERFUMES — Script SQL do Banco de Dados (1ª Sprint)
-- SGBD: MySQL 8.0 ou superior
-- Gerado a partir de entregas/der/fonte/modelo.py (mesma fonte do DER lógico).
--
-- O script cria o banco, recria as tabelas da 1ª Sprint e faz a carga inicial
-- (famílias olfativas e questionário de perfil). ATENÇÃO: rodar de novo apaga
-- os dados das tabelas da Sprint 1.
-- =====================================================================

-- Garante que acentos sejam lidos corretamente, qualquer que seja o cliente MySQL
SET NAMES utf8mb4;

CREATE DATABASE IF NOT EXISTS modular_perfumes
  DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE modular_perfumes;

SET FOREIGN_KEY_CHECKS = 0;
"""]
for t in reversed(ordem):
    out.append(f'DROP TABLE IF EXISTS {t};')
out.append('SET FOREIGN_KEY_CHECKS = 1;\n')
out.append('-- ---------------------------------------------------------------------')
out.append('-- Tabelas (em ordem de dependência)')
out.append('-- ---------------------------------------------------------------------\n')
for t in ordem:
    out.append(create_table(t))

out.append("""-- ---------------------------------------------------------------------
-- Carga inicial
-- ---------------------------------------------------------------------

INSERT INTO familia_olfativa (id, nome, descricao) VALUES
  (1, 'Floral',            'Flores como rosa, jasmim e flor de laranjeira.'),
  (2, 'Fresco/Cítrico',    'Limão, bergamota, laranja; leve e revigorante.'),
  (3, 'Amadeirado',        'Sândalo, cedro, vetiver e couro.'),
  (4, 'Oriental/Âmbar',    'Especiarias, incenso, âmbar e resinas; intenso.'),
  (5, 'Gourmand',          'Baunilha, caramelo, café e notas doces.'),
  (6, 'Aromático/Fougère', 'Lavanda, ervas e notas verdes.'),
  (7, 'Aquático',          'Notas marinhas e de ar livre.'),
  (8, 'Chypre',            'Bergamota, musgo de carvalho e patchouli; elegante.');

INSERT INTO questionario (id, titulo, ativo) VALUES
  (1, 'Perfil olfativo — versão 1', 1);

-- A pergunta de ordem 1 define o nível de conhecimento do cliente
-- (alternativa de ordem 1 = INICIANTE, 2 = INTERMEDIARIO, 3 = AVANCADO).
-- As demais somam pesos por família olfativa para gerar o perfil.
INSERT INTO pergunta (id, questionario_id, enunciado, tipo, ordem, obrigatoria) VALUES
  (1, 1, 'Quanto você entende de perfumes?',                     'UNICA',    1, 1),
  (2, 1, 'Em que ocasiões você mais usaria o perfume?',          'MULTIPLA', 2, 1),
  (3, 1, 'Quais destes cheiros agradam você?',                   'MULTIPLA', 3, 1),
  (4, 1, 'Como você prefere que o perfume seja?',                'UNICA',    4, 1),
  (5, 1, 'Em que clima você mais vai usar o perfume?',           'UNICA',    5, 1),
  (6, 1, 'Para quem é o perfume?',                               'UNICA',    6, 1),
  (7, 1, 'Que estilo de perfume você procura?',                  'UNICA',    7, 1),
  (8, 1, 'Em que período do dia você mais usaria?',              'UNICA',    8, 1),
  (9, 1, 'Quanto tempo você quer que o perfume dure na pele?',   'UNICA',    9, 1),
  (10, 1, 'Quanto você pretende investir em um perfume?',        'UNICA',   10, 1),
  (11, 1, 'Quais destes cheiros você NÃO gosta?',                'MULTIPLA', 11, 0);

INSERT INTO alternativa (id, pergunta_id, texto, ordem) VALUES
  (1,  1, 'Nada, estou começando',                     1),
  (2,  1, 'Conheço algumas marcas e perfumes',         2),
  (3,  1, 'Sei o que são notas e famílias olfativas',  3),
  (4,  2, 'Dia a dia e trabalho',                      1),
  (5,  2, 'Encontros e noite',                         2),
  (6,  2, 'Eventos formais',                           3),
  (7,  2, 'Esportes e dias de calor',                  4),
  (8,  3, 'Flores, como rosa e jasmim',                1),
  (9,  3, 'Frutas cítricas, como limão e bergamota',   2),
  (10, 3, 'Madeira e couro',                           3),
  (11, 3, 'Baunilha, caramelo e doces',                4),
  (12, 3, 'Especiarias e incenso',                     5),
  (13, 3, 'Brisa do mar e ar livre',                   6),
  (14, 3, 'Ervas e lavanda',                           7),
  (15, 4, 'Leve e discreto',                           1),
  (16, 4, 'Marcante e que fica na pele',               2),
  (17, 4, 'Doce e aconchegante',                       3),
  (18, 4, 'Elegante e sofisticado',                    4),
  (19, 5, 'Calor',                                     1),
  (20, 5, 'Frio',                                      2),
  (21, 5, 'Uso o ano todo',                            3),
  (22, 6, 'Para mim',                                  1),
  (23, 6, 'Para presentear alguém',                    2),
  (24, 7, 'Masculino',                                 1),
  (25, 7, 'Feminino',                                  2),
  (26, 7, 'Unissex',                                   3),
  (27, 7, 'Tanto faz',                                 4),
  (28, 8, 'Durante o dia',                             1),
  (29, 8, 'À noite',                                   2),
  (30, 8, 'Dia e noite',                               3),
  (31, 9, 'Poucas horas, bem suave',                   1),
  (32, 9, 'O dia todo',                                2),
  (33, 9, 'Não faço questão',                          3),
  (34, 10, 'Até R$ 150',                               1),
  (35, 10, 'De R$ 150 a R$ 400',                       2),
  (36, 10, 'De R$ 400 a R$ 800',                       3),
  (37, 10, 'Acima de R$ 800',                          4),
  (38, 11, 'Muito doce',                               1),
  (39, 11, 'Muito floral',                             2),
  (40, 11, 'Madeira ou couro',                         3),
  (41, 11, 'Cítrico ou ácido',                         4),
  (42, 11, 'Especiarias fortes',                       5),
  (43, 11, 'Nenhum destes',                            6);

INSERT INTO alternativa_peso (alternativa_id, familia_id, peso) VALUES
  (4, 2, 2.00), (4, 6, 1.00),
  (5, 4, 2.00), (5, 5, 1.00),
  (6, 3, 2.00), (6, 8, 1.00),
  (7, 7, 2.00), (7, 2, 1.00),
  (8, 1, 3.00),
  (9, 2, 3.00),
  (10, 3, 3.00),
  (11, 5, 3.00),
  (12, 4, 3.00),
  (13, 7, 3.00),
  (14, 6, 3.00),
  (15, 2, 2.00), (15, 7, 2.00),
  (16, 4, 2.00), (16, 3, 2.00),
  (17, 5, 3.00),
  (18, 8, 2.00), (18, 1, 1.00),
  (19, 2, 2.00), (19, 7, 2.00),
  (20, 4, 2.00), (20, 5, 1.00), (20, 3, 1.00),
  (21, 6, 1.00), (21, 1, 1.00),
  (28, 2, 1.00), (28, 1, 1.00),
  (29, 4, 1.00), (29, 5, 1.00),
  (30, 6, 1.00),
  (31, 2, 1.00), (31, 7, 1.00),
  (32, 3, 1.00), (32, 4, 1.00);

-- As perguntas 6, 7, 10 e 11 não somam pesos: o consultor de IA lê essas respostas
-- (para quem é, estilo, orçamento e o que o cliente não gosta) ao recomendar.

-- Administrador: crie a conta pela tela de cadastro (a senha é gravada com hash
-- pela aplicação) e depois promova o perfil:
--   UPDATE usuario SET perfil = 'ADMIN' WHERE email = 'email-do-administrador@exemplo.com';
""")
open(sys.argv[1], 'w').write('\n'.join(out))
print('ok', sys.argv[1], 'tabelas:', len(ordem))
