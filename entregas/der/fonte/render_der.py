"""Renderiza o DER: python3 render_der.py der.dot [sprint1] && dot -Tpng der.dot -o der.png"""
import sys

from modelo import AZUL, LARANJA, VERDE, FONT, T, R, GRUPOS, SPRINT1

# uso: python3 render_der.py saida.dot [sprint1]
if len(sys.argv) > 2 and sys.argv[2] == 'sprint1':
    T = {k: v for k, v in T.items() if k in SPRINT1}
    R = [r for r in R if r[0] in T and r[1] in T]
    GRUPOS = [(g, l, [m for m in ms if m in T]) for g, l, ms in GRUPOS]
    GRUPOS = [g for g in GRUPOS if g[2]]
    TITULO = 'Diagrama de Entidade e Relacionamento (Lógico) — 1ª Sprint'
else:
    TITULO = 'Diagrama de Entidade e Relacionamento (Lógico) — visão completa'

RANKDIR, SPLINES = 'LR', 'spline'


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def node(nome):
    cor, cols = T[nome]
    rows = [f'<TR><TD COLSPAN="3" BGCOLOR="{cor}" ALIGN="CENTER" CELLPADDING="6">'
            f'<FONT COLOR="white" POINT-SIZE="15"><B>{nome}</B></FONT></TD></TR>']
    for mark, col, tipo, restr in cols:
        marca = f'<B>{esc(mark)}</B>' if mark else ' '
        rows.append(
            f'<TR><TD ALIGN="LEFT" WIDTH="46">{marca}</TD>'
            f'<TD ALIGN="LEFT">{esc(col)}</TD>'
            f'<TD ALIGN="LEFT"><FONT COLOR="#444444">{esc(tipo)} {esc(restr)}</FONT></TD></TR>')
    return (f'  {nome} [label=<<TABLE BORDER="1" COLOR="{cor}" CELLBORDER="0" CELLSPACING="0" '
            f'CELLPADDING="3">{"".join(rows)}</TABLE>>];')


out = [
    'digraph DER {',
    f'  graph [rankdir={RANKDIR}, splines={SPLINES}, nodesep=0.55, ranksep=1.1, pad=0.5, dpi=220, '
    f'fontname="{FONT}", bgcolor="white", newrank=true, '
    f'label=<<BR/><FONT POINT-SIZE="26"><B>MODULAR PERFUMES — {TITULO}</B></FONT><BR/>'
    f'<FONT POINT-SIZE="17">PK = Chave Primária   |   FK = Chave Estrangeira   |   U = UNIQUE   |   NN = NOT NULL   |   U¹ = UNIQUE composto   |   '
    f'Pé-de-galinha: traço duplo = exatamente um  ·  traço + círculo = zero ou um  ·  pé + círculo = zero ou muitos</FONT>>, labelloc=b];',
    f'  node [shape=plaintext, fontname="{FONT}", fontsize=13];',
    '  edge [color="#2F4A7A", penwidth=1.6, arrowsize=1.1, dir=both];',
]
for gid, glabel, membros in GRUPOS:
    out.append(f'  subgraph cluster_{gid} {{')
    out.append(f'    label=<<B>{glabel}</B>>; fontsize=18; fontcolor="#555555"; style="rounded,dashed"; '
               f'color="#9A9A9A"; margin=18;')
    for m in membros:
        out.append('  ' + node(m))
    out.append('  }')
for pai, filho, card, anulavel in R:
    tail = 'teeodot' if anulavel else 'teetee'
    head = 'teeodot' if card == '1:1' else 'crowodot'
    out.append(f'  {pai} -> {filho} [arrowtail={tail}, arrowhead={head}];')
out.append('}')

open(sys.argv[1], 'w').write('\n'.join(out))
print('tabelas', len(T), 'relacionamentos', len(R))
