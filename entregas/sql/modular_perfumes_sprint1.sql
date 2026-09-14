-- =====================================================================
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

DROP TABLE IF EXISTS importacao_catalogo;
DROP TABLE IF EXISTS perfume_acorde;
DROP TABLE IF EXISTS perfume_nota;
DROP TABLE IF EXISTS perfume;
DROP TABLE IF EXISTS acorde;
DROP TABLE IF EXISTS nota_olfativa;
DROP TABLE IF EXISTS marca;
DROP TABLE IF EXISTS perfil_familia;
DROP TABLE IF EXISTS perfil_olfativo;
DROP TABLE IF EXISTS resposta_item;
DROP TABLE IF EXISTS resposta_questionario;
DROP TABLE IF EXISTS alternativa_peso;
DROP TABLE IF EXISTS familia_olfativa;
DROP TABLE IF EXISTS alternativa;
DROP TABLE IF EXISTS pergunta;
DROP TABLE IF EXISTS questionario;
DROP TABLE IF EXISTS usuario;
SET FOREIGN_KEY_CHECKS = 1;

-- ---------------------------------------------------------------------
-- Tabelas (em ordem de dependência)
-- ---------------------------------------------------------------------

CREATE TABLE usuario (
  id INT NOT NULL AUTO_INCREMENT,
  nome VARCHAR(80) NOT NULL,
  email VARCHAR(120) NOT NULL,
  senha_hash VARCHAR(255) NOT NULL,
  perfil ENUM('CLIENTE', 'LOJISTA', 'ADMIN') NOT NULL DEFAULT 'CLIENTE',
  ativo TINYINT(1) NOT NULL DEFAULT 1,
  tentativas_login TINYINT NOT NULL DEFAULT 0,
  bloqueado_ate DATETIME NULL,
  aceite_termos_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_usuario_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE questionario (
  id INT NOT NULL AUTO_INCREMENT,
  titulo VARCHAR(120) NOT NULL,
  ativo TINYINT(1) NOT NULL DEFAULT 1,
  criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE pergunta (
  id INT NOT NULL AUTO_INCREMENT,
  questionario_id INT NOT NULL,
  enunciado VARCHAR(255) NOT NULL,
  tipo ENUM('UNICA', 'MULTIPLA') NOT NULL,
  ordem SMALLINT NOT NULL,
  obrigatoria TINYINT(1) NOT NULL DEFAULT 1,
  ativa TINYINT(1) NOT NULL DEFAULT 1,
  atualizada_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  INDEX idx_pergunta_questionario_ordem (questionario_id, ordem),
  CONSTRAINT fk_pergunta_questionario_id FOREIGN KEY (questionario_id) REFERENCES questionario (id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE alternativa (
  id INT NOT NULL AUTO_INCREMENT,
  pergunta_id INT NOT NULL,
  texto VARCHAR(150) NOT NULL,
  ordem SMALLINT NOT NULL,
  ativa TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (id),
  CONSTRAINT fk_alternativa_pergunta_id FOREIGN KEY (pergunta_id) REFERENCES pergunta (id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE familia_olfativa (
  id INT NOT NULL AUTO_INCREMENT,
  nome VARCHAR(50) NOT NULL,
  descricao VARCHAR(255) NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_familia_olfativa_nome (nome)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE alternativa_peso (
  alternativa_id INT NOT NULL,
  familia_id INT NOT NULL,
  peso DECIMAL(4,2) NOT NULL,
  PRIMARY KEY (alternativa_id, familia_id),
  CHECK (peso >= 0),
  CONSTRAINT fk_alternativa_peso_alternativa_id FOREIGN KEY (alternativa_id) REFERENCES alternativa (id) ON DELETE CASCADE,
  CONSTRAINT fk_alternativa_peso_familia_id FOREIGN KEY (familia_id) REFERENCES familia_olfativa (id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE resposta_questionario (
  id INT NOT NULL AUTO_INCREMENT,
  usuario_id INT NOT NULL,
  questionario_id INT NOT NULL,
  iniciada_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  concluida_em DATETIME NULL,
  PRIMARY KEY (id),
  INDEX idx_resposta_usuario_concluida (usuario_id, concluida_em),
  CONSTRAINT fk_resposta_questionario_usuario_id FOREIGN KEY (usuario_id) REFERENCES usuario (id) ON DELETE CASCADE,
  CONSTRAINT fk_resposta_questionario_questionario_id FOREIGN KEY (questionario_id) REFERENCES questionario (id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE resposta_item (
  resposta_id INT NOT NULL,
  pergunta_id INT NOT NULL,
  alternativa_id INT NOT NULL,
  respondida_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (resposta_id, pergunta_id, alternativa_id),
  CONSTRAINT fk_resposta_item_resposta_id FOREIGN KEY (resposta_id) REFERENCES resposta_questionario (id) ON DELETE CASCADE,
  CONSTRAINT fk_resposta_item_pergunta_id FOREIGN KEY (pergunta_id) REFERENCES pergunta (id) ON DELETE RESTRICT,
  CONSTRAINT fk_resposta_item_alternativa_id FOREIGN KEY (alternativa_id) REFERENCES alternativa (id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE perfil_olfativo (
  id INT NOT NULL AUTO_INCREMENT,
  usuario_id INT NOT NULL,
  resposta_id INT NOT NULL,
  nivel_conhecimento ENUM('INICIANTE', 'INTERMEDIARIO', 'AVANCADO') NOT NULL,
  gerado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_perfil_olfativo_usuario_id (usuario_id),
  CONSTRAINT fk_perfil_olfativo_usuario_id FOREIGN KEY (usuario_id) REFERENCES usuario (id) ON DELETE CASCADE,
  CONSTRAINT fk_perfil_olfativo_resposta_id FOREIGN KEY (resposta_id) REFERENCES resposta_questionario (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE perfil_familia (
  perfil_id INT NOT NULL,
  familia_id INT NOT NULL,
  afinidade DECIMAL(5,2) NOT NULL,
  PRIMARY KEY (perfil_id, familia_id),
  CHECK (afinidade >= 0),
  CONSTRAINT fk_perfil_familia_perfil_id FOREIGN KEY (perfil_id) REFERENCES perfil_olfativo (id) ON DELETE CASCADE,
  CONSTRAINT fk_perfil_familia_familia_id FOREIGN KEY (familia_id) REFERENCES familia_olfativa (id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE marca (
  id INT NOT NULL AUTO_INCREMENT,
  nome VARCHAR(80) NOT NULL,
  pais VARCHAR(60) NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_marca_nome (nome)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE nota_olfativa (
  id INT NOT NULL AUTO_INCREMENT,
  nome VARCHAR(80) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_nota_olfativa_nome (nome)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE acorde (
  id INT NOT NULL AUTO_INCREMENT,
  nome VARCHAR(60) NOT NULL,
  familia_id INT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_acorde_nome (nome),
  CONSTRAINT fk_acorde_familia_id FOREIGN KEY (familia_id) REFERENCES familia_olfativa (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE perfume (
  id INT NOT NULL AUTO_INCREMENT,
  api_id VARCHAR(64) NOT NULL,
  marca_id INT NOT NULL,
  nome VARCHAR(150) NOT NULL,
  genero ENUM('MASCULINO', 'FEMININO', 'UNISSEX') NULL,
  ano SMALLINT NULL,
  imagem_url VARCHAR(500) NULL,
  fixacao VARCHAR(40) NULL,
  projecao VARCHAR(40) NULL,
  concentracao VARCHAR(40) NULL,
  avaliacao DECIMAL(4,2) NULL,
  popularidade VARCHAR(30) NULL,
  descricao TEXT NULL,
  visivel TINYINT(1) NOT NULL DEFAULT 1,
  campos_revisados JSON NULL,
  importado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  atualizado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_perfume_api_id (api_id),
  INDEX idx_perfume_visivel_nome (visivel, nome),
  CONSTRAINT fk_perfume_marca_id FOREIGN KEY (marca_id) REFERENCES marca (id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE perfume_nota (
  perfume_id INT NOT NULL,
  nota_id INT NOT NULL,
  nivel ENUM('SAIDA', 'CORPO', 'FUNDO') NOT NULL,
  PRIMARY KEY (perfume_id, nota_id, nivel),
  CONSTRAINT fk_perfume_nota_perfume_id FOREIGN KEY (perfume_id) REFERENCES perfume (id) ON DELETE CASCADE,
  CONSTRAINT fk_perfume_nota_nota_id FOREIGN KEY (nota_id) REFERENCES nota_olfativa (id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE perfume_acorde (
  perfume_id INT NOT NULL,
  acorde_id INT NOT NULL,
  intensidade VARCHAR(20) NULL,
  PRIMARY KEY (perfume_id, acorde_id),
  CONSTRAINT fk_perfume_acorde_perfume_id FOREIGN KEY (perfume_id) REFERENCES perfume (id) ON DELETE CASCADE,
  CONSTRAINT fk_perfume_acorde_acorde_id FOREIGN KEY (acorde_id) REFERENCES acorde (id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE importacao_catalogo (
  id INT NOT NULL AUTO_INCREMENT,
  origem ENUM('MANUAL', 'AGENDADA') NOT NULL DEFAULT 'MANUAL',
  status ENUM('EM_ANDAMENTO', 'CONCLUIDA', 'FALHOU') NOT NULL DEFAULT 'EM_ANDAMENTO',
  qtd_incluidos INT NOT NULL DEFAULT 0,
  qtd_atualizados INT NOT NULL DEFAULT 0,
  mensagem_erro TEXT NULL,
  iniciada_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  finalizada_em DATETIME NULL,
  PRIMARY KEY (id),
  CHECK (qtd_incluidos >= 0 AND qtd_atualizados >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ---------------------------------------------------------------------
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
