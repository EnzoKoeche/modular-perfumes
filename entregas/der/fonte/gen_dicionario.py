"""Gera docs/07-modelo-de-dados.md: python3 gen_dicionario.py ../../../docs/07-modelo-de-dados.md"""
import sys, runpy
import os
ns = runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'modelo.py'))
T, R, G = ns['T'], ns['R'], ns['GRUPOS']
DESC = {
 'usuario': 'Conta de acesso de qualquer persona. O perfil define o que a pessoa pode fazer (RF-04).',
 'questionario': 'Questionário de perfil olfativo. Só um fica ativo por vez (RN-05).',
 'pergunta': 'Pergunta do questionário, mantida pelo administrador (RF-07). Pergunta respondida é desativada, não apagada.',
 'alternativa': 'Opção de resposta de uma pergunta (RF-08).',
 'alternativa_peso': 'Quanto cada alternativa soma para cada família olfativa no cálculo do perfil (RF-08, RF-11).',
 'resposta_questionario': 'Uma tentativa de resposta do cliente; `concluida_em` nulo significa questionário em andamento (RF-10).',
 'resposta_item': 'Alternativa escolhida em cada pergunta. Múltipla escolha gera várias linhas para a mesma pergunta.',
 'perfil_olfativo': 'Resultado do questionário; um por cliente, recalculado se ele responder de novo (RF-11).',
 'perfil_familia': 'Afinidade do cliente com cada família olfativa, usada pelo agente.',
 'marca': 'Marca do perfume, criada na importação (a Fragella informa o país).',
 'familia_olfativa': 'Famílias usadas no questionário, no perfil e no agrupamento dos acordes.',
 'nota_olfativa': 'Nota (ex.: bergamota, baunilha), criada na importação.',
 'acorde': 'Acorde vindo da API (ex.: amadeirado); `familia_id` liga o acorde a uma família olfativa.',
 'perfume': 'Perfume importado da API (RF-13). `api_id` evita duplicar na reimportação; `campos_revisados` guarda os campos que o administrador alterou e que a API não sobrescreve (RN-07). `imagem_url` aponta para a imagem servida pela API, sem copiar o arquivo (RNF-19, R-02); `fixacao` e `projecao` vêm como texto da API.',
 'perfume_nota': 'Pirâmide olfativa: nota por nível (saída, corpo, fundo).',
 'perfume_acorde': 'Acordes do perfume, com intensidade quando a API informar.',
 'importacao_catalogo': 'Log de cada importação (RF-14, RF-15).',
 'diretriz_agente': 'Regras e orientações do administrador incluídas no prompt de sistema do agente (RF-25).',
 'conversa': 'Conversa do cliente com o consultor de IA (RF-21).',
 'mensagem': 'Turno da conversa com o conteúdo completo da API e o consumo de tokens (RNF-14).',
 'recomendacao': 'Perfume recomendado, registrado pela ferramenta do agente (RF-23, RN-09).',
 'avaliacao_recomendacao': 'Nota de 1 a 5 do cliente para a recomendação; no máximo uma (RN-14).',
 'sacola_item': 'Perfume que o cliente guardou para comprar (RF-27).',
 'loja': 'Loja parceira; um lojista tem uma loja. Aprovação e bloqueio registram quem decidiu (RF-35).',
 'oferta': 'Link e preço de um perfume em uma loja; uma por loja e perfume (RN-11).',
 'clique_oferta': 'Registro de cada redirecionamento para a loja (RN-13). `usuario_id` fica nulo quando a conta é excluída (RN-17).',
}
out = ['# 07 — Modelo de dados (DER lógico)', '',
 'Diagrama da visão completa: [`entregas/der/Modular_Perfumes_DER_Logico_Completo.png`](../entregas/der/Modular_Perfumes_DER_Logico_Completo.png). Fonte: [`entregas/der/fonte/`](../entregas/der/fonte/).', '',
 'Legenda: **PK** chave primária · **FK** chave estrangeira · **U** único · **U¹** único composto `(loja_id, perfume_id)` · **NN** NOT NULL.', '',
 f'Total: **{len(T)} tabelas** e **{len(R)} relacionamentos** (visão completa). Este arquivo é gerado a partir da mesma definição do diagrama e do script SQL, então os três não divergem.', '',
 '**Tabelas da 1ª Sprint** (Artefato 6 e script SQL [`entregas/sql/`](../entregas/sql/)): ' + ', '.join(f'`{t}`' for t in ns['SPRINT1']) + '. DER da Sprint 1: [`entregas/der/Modular_Perfumes_DER_Logico_Sprint1.png`](../entregas/der/Modular_Perfumes_DER_Logico_Sprint1.png).', '']
for gid, glabel, membros in G:
    out += [f'## {glabel.capitalize()}', '']
    for m in membros:
        cor, cols = T[m]
        out += [f'### `{m}`', '', DESC.get(m, ''), '', '| Chave | Coluna | Tipo | Nulo |', '|---|---|---|---|']
        for mark, col, tipo, restr in cols:
            nulo = 'não' if restr in ('NN', 'AUTO_INCREMENT') else 'sim'
            tipo_txt = tipo + (' AUTO_INCREMENT' if restr == 'AUTO_INCREMENT' else '')
            out.append(f'| {mark} | `{col}` | {tipo_txt} | {nulo} |')
        out.append('')
out += ['## Relacionamentos', '', '| Pai | Filho | Cardinalidade | FK no filho pode ser nula? |', '|---|---|---|---|']
for pai, filho, card, anul in R:
    out.append(f'| `{pai}` | `{filho}` | {card} | {"sim" if anul else "não"} |')
out += ['', '## Índices recomendados (além de PK, FK e únicos)', '',
 '- `perfume (visivel, nome)` — listagem e busca do catálogo (RNF-17).',
 '- `oferta (perfume_id, ativa, preco)` — escolha da oferta de menor preço (RN-12).',
 '- `clique_oferta (oferta_id, clicado_em)` — relatório de cliques por período (RF-34).',
 '- `mensagem (conversa_id, enviada_em)` — reconstrução do histórico da conversa.',
 '- `resposta_questionario (usuario_id, concluida_em)` — saber se o cliente já concluiu (RN-04).', '']
open(sys.argv[1], 'w').write('\n'.join(out))
print('ok', len(out), 'linhas')
