-- =====================================================================
-- MODULAR PERFUMES — Ajuste da 1ª Sprint feito na 2ª: data de nascimento no cadastro
-- Só para bancos criados ANTES deste ajuste (quem sobe o banco do zero já recebe a coluna
-- pelo modular_perfumes_sprint1.sql). Rodar uma vez:
--   docker compose exec -T db mysql -umodular -pmodular_dev modular_perfumes < entregas/sql/ajuste_sprint2_data_nascimento.sql
-- =====================================================================
ALTER TABLE usuario ADD COLUMN data_nascimento DATE NULL AFTER email;
