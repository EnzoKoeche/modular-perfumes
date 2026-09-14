"""Gera o script SQL (MySQL 8) das tabelas da 1ª Sprint a partir de modelo.py.

uso: python3 gen_sql.py ../../sql/modular_perfumes_sprint1.sql
"""
import re
import sys

from modelo import T, SPRINT1, FK_REF, ON_DELETE

DEFAULTS = {
    'ativo': '1', 'ativa': '1', 'visivel': '1', 'obrigatoria': '1',
    'tentativas_login': '0', 'qtd_incluidos': '0', 'qtd_atualizados': '0',
    'perfil': "'CLIENTE'", 'origem': "'MANUAL'", 'status': "'EM_ANDAMENTO'",
}
AGORA = {'criado_em', 'importado_em', 'iniciada_em', 'respondida_em', 'gerado_em', 'aceite_termos_em'}
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


def ordem_dependencias(tabelas):
    feitas, ordem = set(), []
    pendentes = list(tabelas)
    while pendentes:
        for t in pendentes:
            refs = {FK_REF[c] for m, c, _, _ in T[t][1] if 'FK' in m} - {t}
            assert refs <= set(tabelas), f'{t} referencia tabela fora do escopo: {refs - set(tabelas)}'
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
  (5, 1, 'Em que clima você mais vai usar o perfume?',           'UNICA',    5, 1);

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
  (21, 5, 'Uso o ano todo',                            3);

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
  (21, 6, 1.00), (21, 1, 1.00);

-- Administrador: crie a conta pela tela de cadastro (a senha é gravada com hash
-- pela aplicação) e depois promova o perfil:
--   UPDATE usuario SET perfil = 'ADMIN' WHERE email = 'email-do-administrador@exemplo.com';
""")
open(sys.argv[1], 'w').write('\n'.join(out))
print('ok', sys.argv[1], 'tabelas:', len(ordem))
