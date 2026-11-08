"""Diagramas de Atividades (UML) do Modular Perfumes — Artefato 8.

uso: python3 atividades.py && dot -Tpng cliente.dot -o ../Modular_Perfumes_Atividades_Cliente.png
                           && dot -Tpng admin.dot -o ../Modular_Perfumes_Atividades_Admin_Pesos.png
Cada decisão (losango) corresponde a um critério de aceite das user stories.
"""
import pathlib

PASTA = pathlib.Path(__file__).parent
FONTE = 'Helvetica'
COR_SISTEMA, COR_CLIENTE, COR_IA, COR_ADMIN = '#E8F0FB', '#FFF1E6', '#F1EAFE', '#EAF5EA'


def cabecalho(titulo):
    return [
        'digraph G {',
        f'  graph [rankdir=TB, splines=ortho, nodesep=0.45, ranksep=0.42, pad=0.4, dpi=200, fontname="{FONTE}", '
        f'labelloc=t, label=<<FONT POINT-SIZE="22"><B>{titulo}</B></FONT><BR/>'
        f'<FONT POINT-SIZE="13">● início   ◉ fim   ◇ decisão   □ ação (a cor indica quem executa)</FONT><BR/> >];',
        f'  node [fontname="{FONTE}", fontsize=13, shape=box, style="rounded,filled", fillcolor="{COR_SISTEMA}", '
        'color="#5B6B8C", penwidth=1.4, margin="0.18,0.08"];',
        f'  edge [fontname="{FONTE}", fontsize=12, color="#44516B", arrowsize=0.8, penwidth=1.3];',
        '  inicio [shape=circle, label="", width=0.3, style=filled, fillcolor=black];',
    ]


def acao(n, texto, cor=COR_SISTEMA):
    texto = texto.replace('"', '\\"')
    return f'  {n} [label="{texto}", fillcolor="{cor}"];'


def decisao(n, texto):
    return f'  {n} [shape=diamond, style=filled, fillcolor="#FFFBEA", color="#B08900", label="{texto}", fontsize=12, margin="0.05,0.03"];'


def fim(n='fim', texto=''):
    linhas = [f'  {n} [shape=doublecircle, label="", width=0.22, style=filled, fillcolor=black];']
    return linhas


def legenda(itens):
    celulas = ''.join(f'<TD BGCOLOR="{c}" BORDER="1" COLOR="#5B6B8C">  {t}  </TD>' for t, c in itens)
    return [f'  legenda [shape=plaintext, style="", label=<<TABLE BORDER="0" CELLSPACING="6"><TR>{celulas}</TR></TABLE>>];']


# ---------------------------------------------------------------- 8.1 cliente: da conta à sacola
c = cabecalho('ARTEFATO 8.1 — Diagrama de Atividades: Cliente, do cadastro à sacola (US1, US3, US7 a US10)')
c += legenda([('Cliente', COR_CLIENTE), ('Sistema (Flask + MySQL)', COR_SISTEMA), ('Agente de IA (Claude)', COR_IA)])
c += [
    acao('a1', 'Preencher o cadastro\\n(nome, nascimento, e-mail, senha e confirmação)', COR_CLIENTE),
    decisao('d1', 'Campos válidos?\\nsenhas iguais?\\ndata não futura?'),
    acao('e1', 'Destacar o campo e\\nmostrar a mensagem do erro\\n(US1 CA3)'),
    decisao('d2', 'E-mail já\\ncadastrado?'),
    acao('e2', 'Exibir "Este e-mail\\njá está cadastrado"\\n(US1 CA2)'),
    acao('a2', 'Gravar a conta com a senha\\ncriptografada e abrir a sessão (US1 CA1)'),
    acao('a3', 'Responder o questionário\\nde perfil olfativo', COR_CLIENTE),
    decisao('d3', 'Obrigatórias\\nrespondidas?'),
    acao('e3', 'Destacar as perguntas\\npendentes (US3 CA2)'),
    acao('a4', 'Somar os pesos por família\\ne gravar o perfil olfativo (US3 CA1)'),
    acao('a5', 'Enviar mensagem ao consultor', COR_CLIENTE),
    decisao('d4', 'Menos de 30\\nmensagens hoje?'),
    acao('e4', 'Exibir o limite diário,\\nsem chamar a IA (US8 CA3)'),
    acao('a6', 'Ler o perfil, buscar no catálogo\\ne registrar as recomendações', COR_IA),
    decisao('d5', 'API de IA\\ndisponível?'),
    acao('e5', 'Avisar "consultor\\nindisponível" e manter\\no histórico (US8 CA2)'),
    acao('a7', 'Gravar a conversa e mostrar\\nresposta + cartões (US8 e US9 CA1)'),
    acao('a8', 'Abrir a ficha do perfume\\n(pirâmide e acordes, US7)', COR_CLIENTE),
    acao('a9', 'Acionar "Adicionar à sacola"', COR_CLIENTE),
    decisao('d6', 'Perfume já\\nna sacola?'),
    acao('e6', 'Exibir "Este perfume já\\nestá na sua sacola"\\n(US10 CA2)'),
    acao('a10', 'Gravar em sacola_item e exibir\\n"<perfume> entrou na sacola" (US10 CA1)'),
    *fim(),
    '  { rank=same; d1; e1; }', '  { rank=same; d2; e2; }', '  { rank=same; d3; e3; }',
    '  { rank=same; d4; e4; }', '  { rank=same; d5; e5; }', '  { rank=same; d6; e6; }',
    '  legenda -> inicio [style=invis];',
    '  inicio -> a1 -> d1;',
    '  d1 -> e1 [xlabel="não "]; e1 -> a1 [constraint=false];',
    '  d1 -> d2 [xlabel="sim "];',
    '  d2 -> e2 [xlabel="sim "]; e2 -> a1 [constraint=false];',
    '  d2 -> a2 [xlabel="não "]; a2 -> a3 -> d3;',
    '  d3 -> e3 [xlabel="não "]; e3 -> a3 [constraint=false];',
    '  d3 -> a4 [xlabel="sim "]; a4 -> a5 -> d4;',
    '  d4 -> e4 [xlabel="não "]; e4 -> fim [constraint=false];',
    '  d4 -> a6 [xlabel="sim "]; a6 -> d5;',
    '  d5 -> e5 [xlabel="não "]; e5 -> a5 [constraint=false];',
    '  d5 -> a7 [xlabel="sim "]; a7 -> a8 -> a9 -> d6;',
    '  d6 -> e6 [xlabel="sim "]; e6 -> fim [constraint=false];',
    '  d6 -> a10 [xlabel="não "]; a10 -> fim;',
    '}',
]
(PASTA / 'cliente.dot').write_text('\n'.join(c), encoding='utf-8')

# ---------------------------------------------------------------- 8.2 administrador: pesos (US6)
a = cabecalho('ARTEFATO 8.2 — Diagrama de Atividades: Administrador mantém os pesos das alternativas (US6)')
a += legenda([('Administrador', COR_ADMIN), ('Sistema (Flask + MySQL)', COR_SISTEMA)])
a += [
    acao('b1', 'Entrar como administrador', COR_ADMIN),
    acao('b2', 'Abrir "Questionário" e\\nacionar "Pesos" de uma pergunta', COR_ADMIN),
    acao('b3', 'Mostrar a tabela alternativa × família\\ncom os pesos atuais'),
    acao('b4', 'Informar os pesos e\\nacionar "Salvar pesos"', COR_ADMIN),
    decisao('c1', 'Todos inteiros\\nde 0 a 10?'),
    acao('f1', 'Não gravar nada e exibir\\n"Use pesos inteiros de 0 a 10"\\n(US6 CA2)'),
    acao('b5', 'Apagar os pesos da pergunta e\\ngravar os maiores que zero'),
    acao('b6', 'Exibir "Pesos atualizados"\\n(US6 CA1)'),
    decisao('c2', 'Alguma alternativa\\nficou toda em 0?'),
    acao('f2', 'Avisar que a alternativa não soma\\nafinidade com nenhuma família\\n(US6 CA3)'),
    *fim(),
    '  { rank=same; c1; f1; }', '  { rank=same; c2; f2; }',
    '  legenda -> inicio [style=invis];',
    '  inicio -> b1 -> b2 -> b3 -> b4 -> c1;',
    '  c1 -> f1 [xlabel="não "]; f1 -> b4 [constraint=false];',
    '  c1 -> b5 [xlabel="sim "]; b5 -> b6 -> c2;',
    '  c2 -> f2 [xlabel="sim "]; f2 -> fim;',
    '  c2 -> fim [xlabel="não "];',
    '}',
]
(PASTA / 'admin.dot').write_text('\n'.join(a), encoding='utf-8')
print('ok: cliente.dot e admin.dot')
