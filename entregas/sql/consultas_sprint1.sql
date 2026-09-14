-- =====================================================================
-- MODULAR PERFUMES — Consultas de verificação da 1ª Sprint
-- Mostram que a base foi preenchida e é recuperada conforme cada user story.
-- Rodar depois de modular_perfumes_sprint1.sql e de usar o sistema.
-- =====================================================================
USE modular_perfumes;

-- US1 / US2 — contas cadastradas (a senha aparece só como hash)
SELECT id, nome, email, perfil, ativo, LEFT(senha_hash, 12) AS inicio_do_hash, criado_em
FROM usuario
ORDER BY criado_em DESC;

-- US4 — questionário ativo com perguntas e alternativas, na ordem
SELECT q.titulo, p.ordem, p.enunciado, p.tipo, p.obrigatoria, p.ativa, a.ordem AS alt, a.texto
FROM questionario q
JOIN pergunta p     ON p.questionario_id = q.id
JOIN alternativa a  ON a.pergunta_id = p.id AND a.ativa = 1
WHERE q.ativo = 1
ORDER BY p.ordem, a.ordem;

-- US3 — situação do questionário de cada cliente (concluído ou em andamento)
SELECT u.email, r.id AS resposta_id, r.iniciada_em, r.concluida_em,
       CASE WHEN r.concluida_em IS NULL THEN 'EM ANDAMENTO' ELSE 'CONCLUÍDO' END AS situacao,
       COUNT(DISTINCT ri.pergunta_id) AS perguntas_respondidas
FROM usuario u
JOIN resposta_questionario r ON r.usuario_id = u.id
LEFT JOIN resposta_item ri   ON ri.resposta_id = r.id
GROUP BY u.email, r.id, r.iniciada_em, r.concluida_em
ORDER BY r.iniciada_em DESC;

-- US3 — perfil olfativo gerado: nível e afinidade por família
SELECT u.email, po.nivel_conhecimento, f.nome AS familia, pf.afinidade
FROM perfil_olfativo po
JOIN usuario u         ON u.id = po.usuario_id
JOIN perfil_familia pf ON pf.perfil_id = po.id
JOIN familia_olfativa f ON f.id = pf.familia_id
ORDER BY u.email, pf.afinidade DESC;

-- US3 — conferência do cálculo: soma dos pesos das alternativas escolhidas
SELECT r.usuario_id, f.nome AS familia, SUM(ap.peso) AS soma_pesos
FROM resposta_questionario r
JOIN resposta_item ri    ON ri.resposta_id = r.id
JOIN alternativa_peso ap ON ap.alternativa_id = ri.alternativa_id
JOIN familia_olfativa f  ON f.id = ap.familia_id
WHERE r.concluida_em IS NOT NULL
GROUP BY r.usuario_id, f.nome
ORDER BY r.usuario_id, soma_pesos DESC;

-- US5 — log das importações do catálogo
SELECT id, origem, status, qtd_incluidos, qtd_atualizados, iniciada_em, finalizada_em, mensagem_erro
FROM importacao_catalogo
ORDER BY iniciada_em DESC;

-- US5 — perfumes importados, com marca e quantidade de notas e acordes
SELECT p.id, p.api_id, p.nome, m.nome AS marca, p.genero, p.ano,
       COUNT(DISTINCT pn.nota_id)  AS notas,
       COUNT(DISTINCT pa.acorde_id) AS acordes,
       p.importado_em, p.atualizado_em
FROM perfume p
JOIN marca m ON m.id = p.marca_id
LEFT JOIN perfume_nota pn   ON pn.perfume_id = p.id
LEFT JOIN perfume_acorde pa ON pa.perfume_id = p.id
GROUP BY p.id, p.api_id, p.nome, m.nome, p.genero, p.ano, p.importado_em, p.atualizado_em
ORDER BY p.nome;

-- US5 — pirâmide olfativa de um perfume (troque o id)
SELECT p.nome, pn.nivel, n.nome AS nota
FROM perfume p
JOIN perfume_nota pn  ON pn.perfume_id = p.id
JOIN nota_olfativa n  ON n.id = pn.nota_id
WHERE p.id = 1
ORDER BY FIELD(pn.nivel, 'SAIDA', 'CORPO', 'FUNDO'), n.nome;
