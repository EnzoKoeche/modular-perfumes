-- =====================================================================
-- MODULAR PERFUMES — Script SQL da 2ª Sprint (consultor de IA)
-- Rodar DEPOIS de modular_perfumes_sprint1.sql. Gerado de entregas/der/fonte/modelo.py.
-- =====================================================================

SET NAMES utf8mb4;
USE modular_perfumes;

DROP TABLE IF EXISTS recomendacao;
DROP TABLE IF EXISTS mensagem;
DROP TABLE IF EXISTS conversa;

CREATE TABLE conversa (
  id INT NOT NULL AUTO_INCREMENT,
  usuario_id INT NOT NULL,
  iniciada_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  ultima_mensagem_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  CONSTRAINT fk_conversa_usuario_id FOREIGN KEY (usuario_id) REFERENCES usuario (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE mensagem (
  id INT NOT NULL AUTO_INCREMENT,
  conversa_id INT NOT NULL,
  papel ENUM('USUARIO', 'ASSISTENTE') NOT NULL,
  conteudo_json JSON NOT NULL,
  modelo VARCHAR(40) NULL,
  tokens_entrada INT NULL,
  tokens_saida INT NULL,
  tokens_cache INT NULL,
  enviada_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  CONSTRAINT fk_mensagem_conversa_id FOREIGN KEY (conversa_id) REFERENCES conversa (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE recomendacao (
  id INT NOT NULL AUTO_INCREMENT,
  conversa_id INT NOT NULL,
  perfume_id INT NOT NULL,
  posicao TINYINT NOT NULL,
  justificativa VARCHAR(500) NOT NULL,
  gerada_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  CONSTRAINT fk_recomendacao_conversa_id FOREIGN KEY (conversa_id) REFERENCES conversa (id) ON DELETE CASCADE,
  CONSTRAINT fk_recomendacao_perfume_id FOREIGN KEY (perfume_id) REFERENCES perfume (id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
