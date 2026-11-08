"""Monta a apresentação da 2ª Sprint (o projeto inteiro, US1 a US10) em HTML 16:9 e gera o PDF com o Chromium.

Uso:  python montar.py ../Modular_Perfumes_Apresentacao_Sprint2.pdf
Antes: python capturar.py (gera img/ e evidencias.json).
"""
import html
import json
import pathlib
import subprocess
import sys

from dotenv import dotenv_values
from playwright.sync_api import sync_playwright

PASTA = pathlib.Path(__file__).parent
REPO = PASTA.parents[2]
IMG = PASTA / 'img'
SAIDA = pathlib.Path(sys.argv[1]).resolve()
EV = json.loads((PASTA / 'evidencias.json').read_text(encoding='utf-8'))
ENV = dotenv_values(REPO / '.env')
IA_REAL = bool(ENV.get('ANTHROPIC_API_KEY'))
CATALOGO_REAL = EV.get('provedor') == 'fragella'
e = html.escape
SPRINT = '2ª SPRINT'


def git(*args):
    return subprocess.run(['git', *args], cwd=REPO, capture_output=True, text=True).stdout.strip()


def contar_testes():
    saida = subprocess.run([str(REPO / '.venv/bin/python'), '-m', 'pytest', '--collect-only', '-q'],
                           cwd=REPO, capture_output=True, text=True).stdout
    return sum(1 for linha in saida.splitlines() if '::' in linha)


TESTES = contar_testes()
COMMITS = [l.strip().split('\t') for l in git('shortlog', '-sn', 'HEAD').splitlines() if l.strip()]


def img(nome, estilo=''):
    return f'<img src="file://{IMG / (nome + ".png")}" style="{estilo}">'


def tabela(linhas, colunas, rotulos=None, destaque=None):
    rotulos = rotulos or colunas
    cab = ''.join(f'<th>{e(r)}</th>' for r in rotulos)
    corpo = ''
    for l in linhas:
        cls = ' class="destaque"' if destaque and destaque(l) else ''
        corpo += f'<tr{cls}>' + ''.join(
            f'<td>{e(str(l[c])) if l[c] is not None else "NULL"}</td>' for c in colunas) + '</tr>'
    return f'<table class="dados"><thead><tr>{cab}</tr></thead><tbody>{corpo}</tbody></table>'


slides = []


def add(conteudo, secao='', escuro=False):
    n = len(slides) + 1
    rodape = '' if escuro else (
        f'<div class="rodape"><span class="mono">MODULAR PERFUMES · {SPRINT}</span>'
        f'<span class="mono">{e(secao)}</span><span class="mono">{n:02d}</span></div>')
    slides.append(f'<section class="slide{" escuro" if escuro else ""}">{conteudo}{rodape}</section>')


def topo(chip, titulo, sub=''):
    s = f'<p class="subtitulo">{sub}</p>' if sub else ''
    return f'<div class="topo"><span class="chip">{e(chip)}</span><h2>{titulo}</h2>{s}</div>'


def ca(rotulo, tipo, dado, quando, entao):
    return (f'<div class="ca"><div class="ca-rotulo"><span class="mono">{rotulo}</span><span>{tipo}</span></div>'
            f'<p><b>DADO QUE</b> {e(dado)}<br><b>QUANDO</b> {e(quando)}<br><b>ENTÃO</b> {e(entao)}</p></div>')


def cartao_us(u):
    return (f'<div class="card us"><div class="us-topo"><span class="selo">{u["cod"]}</span>'
            f'<span class="mono pbi">PBI {u["pbi"]} · {e(u["dono"])}</span><h3>{e(u["nome"])}</h3></div>'
            f'<p class="historia"><b>COMO</b> {e(u["persona"])} · <b>POSSO</b> {e(u["posso"])} · <b>PARA</b> {e(u["para"])}</p>'
            + ''.join(ca(f'CA{i + 1}', t, *c) for i, (t, c) in enumerate(u['cas'])) + '</div>')


# ---------------------------------------------------------------- conteúdo (fonte: docs/05-backlog-e-user-stories.md)

PERSONAS = [
    ('Cliente', 'CLIENTE', ['Responde o questionário de perfil', 'Conversa com o consultor de IA'],
     ['Achar perfumes que combinem comigo', 'Comprar sem errar'],
     ['Conta e Perfil Olfativo', 'Consultor Olfativo por IA', 'Sacola e Compra nas Lojas']),
    ('Lojista Parceiro', 'LOJISTA', ['Cadastra a loja e as ofertas', 'Acompanha os cliques recebidos'],
     ['Receber clientes interessados', 'Ofertas sempre corretas'],
     ['Cadastro da Loja', 'Gestão de Ofertas', 'Relatório de Cliques']),
    ('Administrador', 'ADMIN', ['Monta o questionário de perfil', 'Importa o catálogo e aprova lojistas'],
     ['Catálogo completo e confiável', 'Plataforma segura e bem configurada'],
     ['Questionário de Perfil', 'Catálogo via API', 'Gestão da Plataforma']),
]

PBIS = [  # (número, PBI, persona, sprint)
    (1, 'Realizar o cadastro do cliente', 'Cliente', 1), (2, 'Realizar o login na plataforma', 'Todas', 1),
    (3, 'Manter as perguntas do questionário', 'Administrador', 1),
    (4, 'Responder o questionário de perfil olfativo', 'Cliente', 1),
    (5, 'Importar os perfumes pela API de catálogo', 'Administrador', 1),
    (6, 'Manter as alternativas e os pesos', 'Administrador', 2), (7, 'Consultar a ficha do perfume', 'Cliente', 2),
    (8, 'Conversar com o agente consultor', 'Cliente', 2), (9, 'Receber as recomendações personalizadas', 'Cliente', 2),
    (10, 'Adicionar e remover perfumes da sacola', 'Cliente', 2),
    (11, 'Buscar perfume do catálogo para ofertar', 'Lojista', 3), (12, 'Solicitar o cadastro da loja parceira', 'Lojista', 3),
    (13, 'Aprovar ou bloquear loja parceira', 'Administrador', 3), (14, 'Manter as ofertas da loja', 'Lojista', 3),
    (15, 'Finalizar a sacola abrindo as lojas', 'Cliente', 3), (16, 'Consultar o log de importações', 'Administrador', 3),
    (17, 'Manter os dados da conta do cliente', 'Cliente', 4), (18, 'Manter os usuários da plataforma', 'Administrador', 4),
    (19, 'Manter os dados da loja', 'Lojista', 4), (20, 'Pausar ou reativar uma oferta', 'Lojista', 4),
    (21, 'Avaliar a recomendação recebida', 'Cliente', 4), (22, 'Manter as diretrizes do agente', 'Administrador', 4),
    (23, 'Revisar a ficha de perfume importada', 'Administrador', 5), (24, 'Ocultar ou reexibir perfume', 'Administrador', 5),
    (25, 'Consultar as avaliações das recomendações', 'Administrador', 5),
    (26, 'Consultar os cliques por oferta', 'Lojista', 5), (27, 'Agendar a sincronização do catálogo', 'Administrador', 5),
    (28, 'Consultar os indicadores de uso', 'Administrador', 5),
]

US2 = [
    {'cod': 'US6', 'pbi': 6, 'dono': 'André Lagos', 'nome': 'Manter as alternativas e os pesos', 'persona': 'Administrador',
     'feature': 'Questionário de Perfil',
     'posso': 'definir o peso de cada alternativa do questionário para cada família olfativa',
     'para': 'ter um perfil olfativo calculado com regras que eu mesmo ajusto',
     'cas': [('fluxo principal', ('abro "Pesos" de uma pergunta', 'informo pesos inteiros de 0 a 10 e aciono "Salvar pesos"',
                                  'grava os pesos e exibe "Pesos atualizados"')),
             ('exceção', ('estou editando os pesos', 'informo peso negativo, maior que 10 ou que não é número',
                          'não grava nada e exibe "Use pesos inteiros de 0 a 10"')),
             ('fluxo alternativo', ('deixo todos os pesos de uma alternativa em 0', 'aciono "Salvar pesos"',
                                    'grava e avisa que a alternativa não soma afinidade com nenhuma família'))]},
    {'cod': 'US7', 'pbi': 7, 'dono': 'Enzo', 'nome': 'Consultar a ficha do perfume', 'persona': 'Cliente',
     'feature': 'Consultor Olfativo por IA',
     'posso': 'consultar a ficha completa de um perfume', 'para': 'conhecer a pirâmide olfativa e os acordes antes de decidir',
     'cas': [('fluxo principal', ('o perfume está visível no catálogo', 'abro a ficha pela vitrine ou por uma recomendação',
                                  'exibe foto, marca, gênero, ano, notas de saída, corpo e fundo, acordes e "Adicionar à sacola"')),
             ('exceção', ('o perfume não existe ou está oculto', 'acesso o endereço da ficha',
                          'exibe "Perfume não encontrado." com o código 404')),
             ('fluxo alternativo', ('não estou logado', 'abro a ficha',
                                    'troca o botão da sacola por "Criar conta e descobrir se combina com você"'))]},
    {'cod': 'US8', 'pbi': 8, 'dono': 'Enzo', 'nome': 'Conversar com o agente consultor', 'persona': 'Cliente',
     'feature': 'Consultor Olfativo por IA',
     'posso': 'conversar com o agente consultor de IA',
     'para': 'tirar dúvidas sobre perfumes em linguagem natural, levando em conta o meu perfil',
     'cas': [('fluxo principal', ('concluí o questionário de perfil', 'envio uma mensagem ao consultor',
                                  'mostra a resposta do agente e guarda a conversa no histórico')),
             ('exceção', ('a chave da IA não está configurada ou o serviço caiu', 'envio uma mensagem',
                          'avisa que o consultor está indisponível, sem perder o histórico')),
             ('exceção', ('já enviei 30 mensagens hoje (RN-15)', 'envio mais uma',
                          'não chama a IA e exibe a mensagem de limite diário'))]},
    {'cod': 'US9', 'pbi': 9, 'dono': 'Enzo', 'nome': 'Receber as recomendações personalizadas', 'persona': 'Cliente',
     'feature': 'Consultor Olfativo por IA',
     'posso': 'receber recomendações de perfumes do catálogo com a justificativa de cada uma',
     'para': 'saber quais perfumes combinam com o meu perfil e por quê',
     'cas': [('fluxo principal', ('o agente recomenda um perfume na conversa', 'a resposta chega',
                                  'registra a recomendação com posição e justificativa e exibe o cartão')),
             ('exceção', ('o agente tenta recomendar perfume inexistente ou oculto', 'a ferramenta de registro é chamada',
                          'recusa o registro e o cartão não aparece')),
             ('fluxo alternativo', ('ainda não concluí o questionário', 'abro o consultor',
                                    'me leva ao questionário (RN-04)'))]},
    {'cod': 'US10', 'pbi': 10, 'dono': 'Enzo', 'nome': 'Adicionar e remover perfumes da sacola', 'persona': 'Cliente',
     'feature': 'Sacola e Compra nas Lojas',
     'posso': 'adicionar, listar e remover perfumes da minha sacola',
     'para': 'juntar os perfumes que quero comprar nas lojas parceiras',
     'cas': [('fluxo principal', ('concluí o questionário e o perfume está visível', 'aciono "Adicionar à sacola"',
                                  'o perfume entra na sacola, com "<perfume> entrou na sacola."')),
             ('exceção', ('o perfume já está na sacola', 'aciono "Adicionar à sacola" de novo',
                          'não duplica e exibe "Este perfume já está na sua sacola."')),
             ('fluxo alternativo', ('tenho um perfume na sacola', 'aciono "Remover"',
                                    'o perfume sai e o sistema exibe "Perfume removido da sacola."'))]},
]

TESTES_POR_CA = [  # (US, CA1, CA2, CA3) -> nome do teste automático
    ('US6', 'test_ca1_grava_pesos_e_exibe_mensagem', 'test_ca2_peso_invalido_nao_grava_nada',
     'test_ca3_alternativa_so_com_zeros_grava_e_avisa'),
    ('US7', 'test_ficha_mostra_piramide_e_acordes', 'test_us7_ca2_ficha_de_perfume_oculto_da_404',
     'test_us7_ca3_visitante_ve_convite_para_criar_conta'),
    ('US8', 'test_consultor_responde_registra_recomendacao_e_tokens', 'test_consultor_sem_chave_responde_indisponivel',
     'test_us8_ca3_limite_diario_nao_chama_a_ia'),
    ('US9', 'test_consultor_responde_registra_recomendacao_e_tokens', 'test_ferramentas_leem_perfil_e_catalogo',
     'test_consultor_bloqueado_sem_questionario'),
    ('US10', 'test_ca1_adiciona_e_lista_na_sacola', 'test_ca2_mesmo_perfume_nao_duplica', 'test_ca3_remove_da_sacola'),
]

# ---------------------------------------------------------------- 1. abertura

add(f'''<div class="capa">
  <div class="chips"><span class="chip">EXPERIÊNCIA CRIATIVA · PUCPR</span><span class="chip">{SPRINT}</span><span class="chip">PROJETO COMPLETO</span></div>
  <h1>Modular <span class="grad">Perfumes</span></h1>
  <p class="sub">Consultor olfativo com inteligência artificial: do questionário à sacola</p>
  <div class="equipe"><div><span class="mono">EQUIPE</span><p>Enzo Koeche Castagna · Angelo · André Lagos</p></div>
  <div><span class="mono">ORIENTADORES</span><p>Profa. Cristina Verçosa P. B. de Souza · Prof. Giulio Domenico Bordin · Profa. Rosilene Fernandes</p></div></div>
</div>''', escuro=True)

add(topo('ROTEIRO', 'O que vamos mostrar') + '''
<div class="grade4">
  <div class="card passo"><span class="num mono">01</span><h3>O produto</h3><p>Problema, solução e como o cliente usa o site, do começo ao fim.</p><span class="tempo mono">PÁG. 3–5</span></div>
  <div class="card passo"><span class="num mono">02</span><h3>Canvas PBB</h3><p>Três personas, nove features e os 28 PBIs divididos em sprints.</p><span class="tempo mono">PÁG. 6–9</span></div>
  <div class="card passo"><span class="num mono">03</span><h3>User Stories</h3><p>As cinco histórias da 2ª Sprint, cada uma com três critérios de aceite.</p><span class="tempo mono">PÁG. 10–12</span></div>
  <div class="card passo"><span class="num mono">04</span><h3>Implementação</h3><p>Como funciona por dentro, cada critério no site e no banco, testes e processo.</p><span class="tempo mono">PÁG. 13–26</span></div>
</div>
<p class="nota-rodape">Na 1ª Sprint entregamos a base (conta, questionário e catálogo). Nesta 2ª Sprint entregamos o valor principal: o administrador ajusta os pesos do questionário, e o cliente vê a ficha do perfume, conversa com o consultor de IA, recebe recomendações e monta a sacola.</p>''', 'ROTEIRO')

# ---------------------------------------------------------------- 2. o produto

add(topo('[1] O PRODUTO', 'Comprar perfume pela internet é comprar às cegas') + '''
<div class="grade2">
  <div class="card"><span class="mono rot">O PROBLEMA</span>
    <p class="item faz">Não dá para sentir o cheiro antes de comprar.</p>
    <p class="item faz">"Notas de saída" e "acorde amadeirado" não dizem nada para quem está começando.</p>
    <p class="item faz">Resultado: compra errada, arrependimento e devolução.</p>
    <p class="item faz">Lojas gastam para atrair visitantes que ainda não sabem o que querem.</p></div>
  <div class="card"><span class="mono rot">A SOLUÇÃO</span>
    <p class="item espera">Plataforma web gratuita, com cadastro e login.</p>
    <p class="item espera">Um questionário descobre o perfil olfativo do cliente.</p>
    <p class="item espera">Um agente de IA conversa com ele e recomenda perfumes do catálogo, explicando o porquê.</p>
    <p class="item espera">A compra acontece na loja parceira: o site não vende nem cobra.</p></div>
</div>
<p class="nota-rodape"><b>Em uma frase:</b> para quem quer comprar perfume pela internet e não sabe qual escolher, o Modular Perfumes é um consultor olfativo com IA que entende o seu perfil e leva você direto à loja do perfume certo.</p>''', '[1] O PRODUTO')

passos = [('1', 'Cria a conta', 'US1 · US2', 'Nome, e-mail e senha. Login com sessão segura.', 'S1'),
          ('2', 'Responde o questionário', 'US3 · US4 · US6', '11 perguntas. Os pesos de cada resposta geram o perfil olfativo.', 'S1 · S2'),
          ('3', 'Conversa com o consultor', 'US8 · US9', 'O agente de IA lê o perfil, busca no catálogo e recomenda com justificativa.', 'S2'),
          ('4', 'Vê a ficha do perfume', 'US5 · US7', 'Pirâmide olfativa e acordes, vindos da API de catálogo.', 'S1 · S2'),
          ('5', 'Guarda na sacola', 'US10', 'Junta os perfumes de que gostou para comprar nas lojas parceiras.', 'S2')]
add(topo('[1] O PRODUTO', 'Como o cliente usa o site, em cinco passos') + '<div class="fluxo">' + ''.join(
    f'<div class="card etapa"><span class="num mono">{n}</span><h3>{e(t)}</h3><p>{e(d)}</p>'
    f'<span class="onde mono">{e(u)}</span><span class="sprint-tag mono">{s}</span></div>' for n, t, u, d, s in passos)
    + '</div><p class="nota-rodape">Os passos 1 a 5 já funcionam. O próximo passo, <b>finalizar a sacola abrindo a loja de cada perfume</b> (PBI 15), depende das lojas parceiras e entra na 3ª Sprint.</p>',
    '[1] O PRODUTO')

add(topo('[1] O PRODUTO', 'O que é e o que não é') + '''
<div class="grade2">
  <div class="card"><span class="mono rot ok">É / FAZ</span>
    <p class="item">Plataforma gratuita de consultoria olfativa, com login</p>
    <p class="item">Agente de IA que recomenda a partir do perfil e explica o motivo</p>
    <p class="item">Catálogo com foto, notas e acordes, importado de API externa</p>
    <p class="item">Sacola que leva o cliente às lojas parceiras</p></div>
  <div class="card"><span class="mono rot erro">NÃO É / NÃO FAZ</span>
    <p class="item">Loja virtual: não vende, não cobra e não entrega</p>
    <p class="item">Não guarda dados de cartão nem intermedia a compra</p>
    <p class="item">Não libera o consultor sem login e sem o questionário respondido</p>
    <p class="item">Não dá orientação médica (alergia ou pele: procurar um profissional)</p></div>
</div>''', '[1] O PRODUTO')

# ---------------------------------------------------------------- 3. canvas PBB

cards = ''
for nome, perfil, faz, espera, feats in PERSONAS:
    cards += (f'<div class="card persona"><h3>{e(nome)}</h3><span class="mono perfil">perfil {perfil}</span>'
              '<span class="mono rot">O QUE FAZ</span>' + ''.join(f'<p class="item faz">{e(x)}</p>' for x in faz)
              + '<span class="mono rot">O QUE ESPERA</span>' + ''.join(f'<p class="item espera">{e(x)}</p>' for x in espera)
              + '<span class="mono rot">FEATURES</span>' + ''.join(f'<p class="feat">{e(x)}</p>' for x in feats) + '</div>')
add(topo('[2] CANVAS PBB', 'Três personas, cada uma com um papel no sistema') + f'<div class="grade3">{cards}</div>',
    '[2] CANVAS PBB')

add(topo('[2] CANVAS PBB', 'Product Backlog Building', 'O Canvas entregue na 1ª Sprint. As features e os PBIs não mudaram: a 2ª Sprint seguiu a ordem do backlog.')
    + f'<div class="figura"><img src="file://{REPO / "entregas/pbb/Modular_Perfumes_Canvas_PBB_Sprint1.png"}" style="max-height:760px;max-width:100%;border-radius:12px;border:1px solid #e6e8ec"></div>',
    '[2] CANVAS PBB')


def linha_pbi(n, nome, persona, sprint):
    cls = {1: 's1', 2: 's2'}.get(sprint, 'sx')
    estado = {1: 'entregue', 2: 'entregue'}.get(sprint, 'planejado')
    return (f'<tr class="{cls}"><td class="mono">{n:02d}</td><td>{e(nome)}</td><td>{e(persona)}</td>'
            f'<td><span class="tag {cls}">Sprint {sprint}</span></td><td class="mono">{estado}</td></tr>')


meia = len(PBIS) // 2
add(topo('[2] CANVAS PBB', 'Product Backlog: 28 PBIs em ordem de sprint') + '<div class="grade2 backlog">'
    + ''.join('<table class="dados pbis"><thead><tr><th>#</th><th>PBI</th><th>Persona</th><th>Sprint</th><th>Estado</th></tr></thead><tbody>'
              + ''.join(linha_pbi(*p) for p in parte) + '</tbody></table>' for parte in (PBIS[:meia], PBIS[meia:]))
    + '</div><p class="nota-rodape"><b>10 de 28 PBIs entregues.</b> A ordem vem do valor: primeiro a base (acesso, questionário e catálogo), depois o consultor e a sacola, e por fim os papéis de lojista e administrador.</p>',
    '[2] CANVAS PBB')

add(topo('[2] CANVAS PBB', 'PBIs implementados na 2ª Sprint') + '<table class="dados grande"><thead><tr><th></th><th>PBI</th><th>Persona</th><th>Feature</th><th>Responsável</th></tr></thead><tbody>'
    + ''.join(f'<tr><td><span class="selo">{u["cod"]}</span></td><td><b>{e(u["nome"])}</b></td><td>{e(u["persona"])}</td>'
              f'<td>{e(u["feature"])}</td><td>{e(u["dono"])}</td></tr>' for u in US2)
    + '</tbody></table><p class="nota-rodape"><b>Objetivo da sprint:</b> o cliente consulta a ficha do perfume, conversa com o agente consultor, recebe recomendações e monta a sacola; o administrador ajusta os pesos das alternativas.</p>',
    '[2] CANVAS PBB')

# ---------------------------------------------------------------- 4. user stories

add(topo('[3] USER STORIES', 'Administrador e ficha do perfume') + f'<div class="grade2">{cartao_us(US2[0])}{cartao_us(US2[1])}</div>',
    '[3] USER STORIES')
add(topo('[3] USER STORIES', 'Consultor de IA') + f'<div class="grade2">{cartao_us(US2[2])}{cartao_us(US2[3])}</div>',
    '[3] USER STORIES')
add(topo('[3] USER STORIES', 'Sacola, e como lemos uma user story') + f'''<div class="grade2">{cartao_us(US2[4])}
  <div class="card didatico"><span class="mono rot">COMO LER</span>
    <p><b class="mono">COMO</b> quem usa (a persona do Canvas)</p>
    <p><b class="mono">POSSO</b> o que ela faz (o PBI)</p>
    <p><b class="mono">PARA</b> o benefício (vem da feature)</p>
    <span class="mono rot">CRITÉRIOS DE ACEITE</span>
    <p><b class="mono">CA1</b> o fluxo principal, quando tudo dá certo</p>
    <p><b class="mono">CA2</b> o tratamento de um problema (exceção)</p>
    <p><b class="mono">CA3</b> outro caminho possível ou outra exceção</p>
    <p class="obs">Cada critério é escrito em <b>DADO QUE · QUANDO · ENTÃO</b> e vira um teste automático (pág. 22).</p></div>
</div>''', '[3] USER STORIES')

# ---------------------------------------------------------------- 5. como funciona por dentro

add(topo('[4] COMO FUNCIONA', 'Arquitetura: um site Flask, um banco MySQL e duas APIs externas') + '''
<div class="arq">
  <div class="caixa nav"><span class="mono rot">NAVEGADOR</span><p>Páginas HTML (Jinja2) com Bootstrap 5</p><p class="obs">o chat chama o servidor por fetch/JSON</p></div>
  <div class="seta">→</div>
  <div class="caixa srv"><span class="mono rot">SERVIDOR FLASK (PYTHON)</span>
    <div class="mods">
      <span>auth.py<small>US1 · US2</small></span><span>questionario.py<small>US3</small></span><span>admin.py<small>US4 · US5 · US6</small></span>
      <span>vitrine.py<small>US7</small></span><span>consultor.py<small>US8 · US9</small></span><span>sacola.py<small>US10</small></span>
      <span>catalogo.py<small>adaptador da API</small></span><span>db.py<small>SQL à mão (PyMySQL)</small></span></div>
    <p class="obs">Cada rota confere o perfil (CLIENTE, LOJISTA, ADMIN) no servidor, com CSRF em todo formulário.</p></div>
  <div class="seta">→</div>
  <div class="pilha">
    <div class="caixa db"><span class="mono rot">MYSQL 8</span><p>21 tabelas</p><p class="obs">17 da 1ª Sprint + 4 da 2ª</p></div>
    <div class="caixa ext"><span class="mono rot">API DA ANTHROPIC</span><p>Claude (consultor)</p></div>
    <div class="caixa ext"><span class="mono rot">API DE CATÁLOGO</span><p>Fragella (perfumes)</p></div>
  </div>
</div>
<p class="nota-rodape">As chaves das APIs ficam só no servidor, no arquivo <span class="mono">.env</span>, que não vai para o GitHub. Trocar o provedor de catálogo muda só o adaptador <span class="mono">catalogo.py</span>.</p>''',
    '[4] COMO FUNCIONA')

perfil = EV['perfil'][:5]
add(topo('[4] COMO FUNCIONA', 'Do questionário ao perfil: a soma dos pesos (US3 + US6)') + f'''
<div class="lado">
  <div class="card didatico">
    <span class="mono rot">A IDEIA</span>
    <p>Cada alternativa do questionário vale pontos para uma ou mais <b>famílias olfativas</b> (floral, cítrico, amadeirado...). Quem define esses pontos é o administrador, na tela de pesos da <b>US6</b>.</p>
    <span class="mono rot">EXEMPLO</span>
    <div class="conta"><span>"Frutas cítricas"</span><span class="mono">→ Fresco/Cítrico +3</span></div>
    <div class="conta"><span>"Brisa do mar"</span><span class="mono">→ Aquático +3</span></div>
    <div class="conta"><span>"Leve e discreto"</span><span class="mono">→ Fresco/Cítrico +…</span></div>
    <p>Ao concluir o questionário, o sistema <b>soma os pontos por família</b>. As famílias com mais pontos são as que mais combinam com o cliente, e é isso que o consultor de IA lê depois.</p>
    <pre>INSERT INTO perfil_familia (perfil_id, familia_id, afinidade)
SELECT %s, ap.familia_id, SUM(ap.peso)
FROM resposta_item ri
JOIN alternativa_peso ap ON ap.alternativa_id = ri.alternativa_id
WHERE ri.resposta_id = %s GROUP BY ap.familia_id;</pre></div>
  <div class="banco coluna">
    <div class="print"><span class="mono rot ok">PERFIL DA CLIENTE DE DEMONSTRAÇÃO</span>{img("us3_perfil")}</div>
    <span class="mono rot">BANCO · perfil_familia (afinidade = soma dos pesos)</span>
    {tabela(perfil, ["familia", "afinidade"])}
  </div>
</div>''', '[4] COMO FUNCIONA')

add(topo('[4] COMO FUNCIONA', 'O agente de IA: o modelo conversa, o sistema confere') + '''
<div class="lado">
  <div class="ciclo">
    <div class="no cli"><span class="mono rot">1 · CLIENTE</span><p>"Quero um perfume fresco para o trabalho"</p></div>
    <div class="no srv"><span class="mono rot">2 · SERVIDOR</span><p>Confere login, questionário e o limite de 30 mensagens por dia</p></div>
    <div class="no ia"><span class="mono rot">3 · CLAUDE (TOOL RUNNER)</span><p>Decide quais ferramentas chamar, quantas vezes precisar</p></div>
    <div class="no db"><span class="mono rot">4 · FERRAMENTAS → MYSQL</span><p>Leem o perfil e o catálogo; registram cada recomendação</p></div>
    <div class="no cli"><span class="mono rot">5 · TELA</span><p>Texto da resposta + um cartão por perfume registrado</p></div>
  </div>
  <div class="card">
    <span class="mono rot">AS 5 FERRAMENTAS DO AGENTE</span>
    <p class="ferr"><span class="mono">obter_perfil_olfativo</span> nível, afinidades e respostas</p>
    <p class="ferr"><span class="mono">listar_acordes</span> acordes que existem no catálogo</p>
    <p class="ferr"><span class="mono">buscar_perfumes</span> por acorde, nome, nota e gênero</p>
    <p class="ferr"><span class="mono">obter_ficha_perfume</span> pirâmide olfativa e acordes</p>
    <p class="ferr"><span class="mono">registrar_recomendacao</span> grava o perfume e a justificativa</p>
    <span class="mono rot">POR QUE É SEGURO</span>
    <p class="item">O modelo nunca escolhe de quem é o perfil: o id do cliente vem da sessão.</p>
    <p class="item">Só vira cartão o que passou por <span class="mono">registrar_recomendacao</span>, que recusa perfume inexistente ou oculto (US9 CA2).</p>
    <p class="item">Pedidos como "ignore suas regras" não mudam o prompt de sistema.</p>
  </div>
</div>''', '[4] COMO FUNCIONA')

# ---------------------------------------------------------------- 6. implementação, US a US

pesos_ca2 = EV['pesos_depois_ca2'][0]
add(topo('[4] US6 · PESOS', 'Manter as alternativas e os pesos') + f'''
<div class="lado">
  <div class="print"><span class="mono rot">TELA DE PESOS · UMA LINHA POR ALTERNATIVA, UMA COLUNA POR FAMÍLIA</span>{img("us6_tela")}</div>
  <div class="banco coluna us6">
    <div class="print"><span class="mono rot ok">CA1 · PESOS ATUALIZADOS</span>{img("us6_ca1")}</div>
    <div class="print"><span class="mono rot erro">CA2 · PESO −3: NADA É GRAVADO</span>{img("us6_ca2")}</div>
    <div class="print"><span class="mono rot aviso">CA3 · ALTERNATIVA TODA EM ZERO: GRAVA E AVISA</span>{img("us6_ca3")}</div>
    <p class="obs">Banco depois do CA2: {pesos_ca2["pesos"]} pesos na pergunta, {pesos_ca2["negativos"]} negativos. O botão <b>Pesos</b> fica na lista de perguntas da US4.</p>
  </div>
</div>''', '[4] IMPLEMENTAÇÃO')

add(topo('[4] US7 · FICHA', 'Consultar a ficha do perfume') + f'''
<div class="grade2 us7">
  <div class="print"><span class="mono rot ok">CA1 · FICHA COMPLETA, COM "ADICIONAR À SACOLA"</span>{img("us7_ca1")}</div>
  <div class="print"><span class="mono rot ok">CA3 · VISITANTE SEM LOGIN: CONVITE PARA CRIAR CONTA</span>{img("us7_ca3")}</div>
</div>
<div class="grade2 us7b">
    <div class="print"><span class="mono rot erro">CA2 · PERFUME OCULTO: 404</span>{img("us7_ca2")}</div>
    <p class="obs"><b>Pirâmide olfativa:</b> notas de <b>saída</b> (o primeiro cheiro), de <b>corpo</b> (o meio) e de <b>fundo</b> (o que fica na pele). <b>Acordes</b> são a impressão geral, com a intensidade que vem da API.</p>
</div>''', '[4] IMPLEMENTAÇÃO')

aviso_ia = '' if IA_REAL else (
    '<p class="aviso-demo"><b>Sobre este print:</b> o consultor rodou com o <b>modelo simulado</b> dos testes automáticos, porque este computador '
    'não tem a chave da API da Anthropic. As ferramentas rodaram de verdade no banco (perfil, busca e registro); só o texto da resposta é fixo. '
    'Na apresentação ao vivo, com a <span class="mono">ANTHROPIC_API_KEY</span> no <span class="mono">.env</span>, quem responde é o Claude.</p>')
add(topo('[4] US8 · US9 · CONSULTOR', 'Conversa e recomendações personalizadas') + f'''
<div class="lado">
  <div class="print"><span class="mono rot ok">US8 CA1 · RESPOSTA NA TELA · US9 CA1 · CARTÕES REGISTRADOS PELA FERRAMENTA</span>{img("us8_us9_conversa")}</div>
  <div class="banco coluna">
    <span class="mono rot">BANCO · mensagem (histórico da conversa)</span>
    {tabela(EV["mensagens"], ["id", "papel", "texto"])}
    <span class="mono rot">BANCO · recomendacao</span>
    {tabela(EV["recomendacoes"], ["posicao", "perfume", "justificativa"])}
    <p class="obs"><b>US8 CA2:</b> sem a chave ou com a API fora do ar, o cliente vê "O consultor está indisponível agora" e o histórico fica. <b>US8 CA3:</b> na 31ª mensagem do dia, a IA nem é chamada. <b>US9 CA3:</b> sem questionário, o consultor manda para o questionário.</p>
    {aviso_ia}
  </div>
</div>''', '[4] IMPLEMENTAÇÃO')

add(topo('[4] US10 · SACOLA', 'Adicionar e remover perfumes da sacola') + f'''
<div class="grade2 sacola">
  <div class="coluna-prints">
    <div class="print"><span class="mono rot ok">CA1 · ENTROU NA SACOLA (PELO CARTÃO DA RECOMENDAÇÃO)</span>{img("us10_ca1")}</div>
    <div class="print"><span class="mono rot aviso">CA2 · O MESMO PERFUME DE NOVO: NÃO DUPLICA</span>{img("us10_ca2")}</div>
  </div>
  <div class="coluna-prints">
    <div class="print"><span class="mono rot ok">CA3 · REMOVIDO DA SACOLA</span>{img("us10_ca3")}</div>
    <span class="mono rot">BANCO · sacola_item (depois do CA3)</span>{tabela(EV["sacola"], ["perfume", "adicionado_em"])}
    <p class="obs">Depois do CA2, a sacola continuou com {EV["us10_ca2_itens"]} item. A sacola é uma tabela simples: <b>um cliente + um perfume</b>, com a chave primária nos dois campos, então o próprio banco impede a duplicata. Perfume oculto não entra na sacola (RN-08).</p>
  </div>
</div>''', '[4] IMPLEMENTAÇÃO')

add(topo('[4] 1ª SPRINT · RECAPITULANDO', 'A base que a 2ª Sprint usa') + f'''
<div class="grade2 prints mini">
  <div class="print"><span class="mono rot">US1 · CADASTRO</span>{img("us1_formulario")}</div>
  <div class="print"><span class="mono rot">US3 · QUESTIONÁRIO</span>{img("us3_questionario")}</div>
  <div class="print"><span class="mono rot">US4 · PERGUNTAS (COM O BOTÃO PESOS)</span>{img("us4_lista")}</div>
  <div class="print"><span class="mono rot">US5 · CATÁLOGO IMPORTADO</span>{img("us5_catalogo")}</div>
</div>
<p class="nota-rodape">US1 a US5 foram apresentadas na 1ª Sprint, com prints e consultas ao banco de cada critério de aceite. Elas continuam cobertas por {TESTES - 20} dos {TESTES} testes automáticos.</p>''',
    '[4] IMPLEMENTAÇÃO')

# ---------------------------------------------------------------- 7. banco, qualidade, processo

t = EV['totais'][0]
nota_catalogo = ('' if CATALOGO_REAL else
                 '<p class="aviso-demo">Os prints usam o <b>catálogo de exemplo</b> (perfumes fictícios, sem foto), para não gastar a cota da API. '
                 'Na 1ª Sprint importamos 350 perfumes reais da Fragella, com foto, de 7 marcas.</p>')
add(topo('[4] BANCO DE DADOS', 'Quatro tabelas novas na 2ª Sprint') + f'''
<div class="lado">
  <div class="tabelas-novas">
    <div class="tb"><h4>conversa</h4><p>id · <u>usuario_id</u> · iniciada_em · ultima_mensagem_em</p><span class="obs">uma conversa do cliente com o consultor</span></div>
    <div class="tb"><h4>mensagem</h4><p>id · <u>conversa_id</u> · papel · conteudo_json · tokens_entrada · tokens_saida · tokens_cache</p><span class="obs">cada fala, com os tokens gastos (custo da IA)</span></div>
    <div class="tb"><h4>recomendacao</h4><p>id · <u>conversa_id</u> · <u>perfume_id</u> · posicao · justificativa</p><span class="obs">só a ferramenta do agente grava aqui</span></div>
    <div class="tb"><h4>sacola_item</h4><p><u>usuario_id</u> · <u>perfume_id</u> · adicionado_em</p><span class="obs">chave primária dupla: sem duplicatas</span></div>
  </div>
  <div class="banco coluna">
    <div class="grade2 numeros">
      <div class="card"><span class="mono rot">TABELAS</span><p class="grande">{t["tabelas"]}</p></div>
      <div class="card"><span class="mono rot">PERFUMES NO BANCO</span><p class="grande">{t["perfumes"]}</p></div>
    </div>
    <span class="mono rot">COMO A TELA RECUPERA AS RECOMENDAÇÕES</span>
    <pre>SELECT r.posicao, r.justificativa, p.nome, m.nome AS marca
FROM recomendacao r
JOIN perfume p ON p.id = r.perfume_id
JOIN marca m   ON m.id = p.marca_id
WHERE r.conversa_id = %s ORDER BY r.id;</pre>
    <p class="obs">Script oficial: <span class="mono">entregas/sql/modular_perfumes_sprint2.sql</span>. Excluir a conta apaga em cascata conversas, mensagens e sacola (LGPD).</p>
    {nota_catalogo}
  </div>
</div>''', '[4] IMPLEMENTAÇÃO')

linhas = ''.join(f'<tr><td><span class="selo">{u}</span></td>' + ''.join(f'<td class="mono teste">{e(x)}</td>' for x in cas) + '</tr>'
                 for u, *cas in TESTES_POR_CA)
add(topo('[4] QUALIDADE', f'{TESTES} testes automáticos: cada critério de aceite tem o seu') + f'''
<table class="dados testes"><thead><tr><th></th><th>CA1</th><th>CA2</th><th>CA3</th></tr></thead><tbody>{linhas}</tbody></table>
<div class="grade3 qualidade">
  <div class="card"><span class="mono rot">COMO RODAM</span><p>Com <span class="mono">pytest</span>, num banco MySQL de teste recriado a cada rodada pelos scripts oficiais. Não mexem nos dados de desenvolvimento.</p></div>
  <div class="card"><span class="mono rot">E A IA?</span><p>Nos testes, o Claude é substituído por um dublê. As ferramentas rodam de verdade no banco: o teste prova o que o sistema faz com a resposta, sem gastar a API.</p></div>
  <div class="card"><span class="mono rot">SEGURANÇA</span><p>Senha com hash PBKDF2, bloqueio após 5 tentativas, CSRF nos formulários e perfil de acesso conferido no servidor.</p></div>
</div>''', '[4] QUALIDADE')

autores = ''.join(f'<div class="card"><span class="mono rot">{e(nome.upper())}</span><p class="grande">{n}</p><p class="obs">commits</p></div>'
                  for n, nome in COMMITS)
add(topo('[4] PROCESSO', 'Scrum no Trello, código no GitHub') + f'''
<div class="colunas-trello">
  <div class="col"><span class="mono">PRODUCT BACKLOG</span><p>os 28 PBIs</p></div><div class="seta">→</div>
  <div class="col"><span class="mono">SPRINT BACKLOG</span><p>os PBIs da sprint, com responsável e prazo</p></div><div class="seta">→</div>
  <div class="col"><span class="mono">EM DESENVOLVIMENTO</span><p>comentário "comecei"</p></div><div class="seta">→</div>
  <div class="col"><span class="mono">EM TESTE</span><p>testes passando</p></div><div class="seta">→</div>
  <div class="col ok"><span class="mono">CONCLUÍDO</span><p>critérios marcados + link do commit</p></div>
</div>
<div class="lado processo">
  <div class="card"><span class="mono rot">REGRAS DO TIME</span>
    <p class="item">Commits pequenos, um passo por commit, com a US na mensagem ("US6: tela de pesos...").</p>
    <p class="item">Antes do push, todos os testes verdes.</p>
    <p class="item">Cada card tem checklist de tarefas e de critérios de aceite.</p>
    <p class="item">Documentos das entregas (DER, SQL, PDF) são gerados por código, em <span class="mono">entregas/*/fonte</span>.</p></div>
  <div class="grade2 numeros">{autores}</div>
</div>''', '[4] PROCESSO')

add(topo('[4] RASTREABILIDADE', 'Do objetivo ao teste: um exemplo completo (US6)') + '''
<div class="trilha">
  <div class="elo"><span class="mono rot">OBJETIVO 1</span><p>Ajudar quem não entende de perfumaria a descobrir o que combina com o próprio perfil</p></div>
  <div class="elo"><span class="mono rot">PERSONA · FEATURE</span><p>Administrador · Questionário de Perfil</p></div>
  <div class="elo"><span class="mono rot">PBI 6 · US6</span><p>Manter as alternativas e os pesos</p></div>
  <div class="elo"><span class="mono rot">REQUISITO</span><p>RF-08: manter alternativas e o peso de cada uma por família (CRUD)</p></div>
  <div class="elo"><span class="mono rot">TABELAS</span><p>alternativa · alternativa_peso · familia_olfativa</p></div>
  <div class="elo"><span class="mono rot">CÓDIGO</span><p>admin.py, rota /admin/perguntas/&lt;id&gt;/pesos · admin/pesos.html</p></div>
  <div class="elo ok"><span class="mono rot">TESTES</span><p>tests/test_pesos.py: um teste por critério de aceite</p></div>
</div>
<p class="nota-rodape">A tabela completa (objetivo → feature → PBI → RF/RN/RNF → tabelas) está em <span class="mono">docs/11-rastreabilidade.md</span>, no GitHub.</p>''',
    '[4] RASTREABILIDADE')

prox = {3: [p for p in PBIS if p[3] == 3], 4: [p for p in PBIS if p[3] == 4], 5: [p for p in PBIS if p[3] == 5]}
objetivos = {3: 'Lojas parceiras: cadastro, aprovação e ofertas; a sacola passa a abrir a loja de cada perfume.',
             4: 'Contas e cadastros completos; avaliação das recomendações e diretrizes do agente.',
             5: 'Curadoria do catálogo, sincronização agendada e indicadores para o administrador.'}
add(topo('PRÓXIMOS PASSOS', 'O que vem nas próximas sprints') + '<div class="grade3">' + ''.join(
    f'<div class="card"><span class="mono rot">SPRINT {s}</span><p class="obj">{e(objetivos[s])}</p>'
    + ''.join(f'<p class="pbi-item"><span class="mono">{n:02d}</span> {e(nome)}</p>' for n, nome, _, _ in prox[s]) + '</div>'
    for s in (3, 4, 5)) + '</div><p class="nota-rodape">Também na fila: a resposta do consultor aparecer aos poucos, enquanto é gerada (streaming, RF-21). Hoje ela chega inteira.</p>',
    'PRÓXIMOS PASSOS')

add(topo('GLOSSÁRIO', 'Os termos que aparecem na apresentação') + '''
<div class="grade2 glossario">
  <div class="card"><span class="mono rot">PERFUMARIA</span>
    <p><b>Família olfativa</b> grupo de perfumes parecidos: floral, cítrico, amadeirado, oriental, aquático...</p>
    <p><b>Notas de saída, corpo e fundo</b> a pirâmide: o que se sente primeiro, no meio e o que fica na pele.</p>
    <p><b>Acorde</b> a impressão geral que a mistura de notas causa ("amadeirado", "cítrico").</p>
    <p><b>Perfil olfativo</b> nível de conhecimento do cliente + afinidade com cada família.</p></div>
  <div class="card"><span class="mono rot">TÉCNICOS</span>
    <p><b>PBB / PBI</b> Product Backlog Building, a técnica do Canvas; PBI é cada item do backlog.</p>
    <p><b>Critério de aceite</b> a condição, em DADO QUE · QUANDO · ENTÃO, que prova que a história funciona.</p>
    <p><b>Agente e ferramentas</b> o modelo de IA decide; as ferramentas são funções do nosso sistema que ele pode chamar.</p>
    <p><b>Tool Runner</b> recurso do SDK da Anthropic que repete "chamar o modelo → rodar a ferramenta" até a resposta final.</p></div>
</div>''', 'GLOSSÁRIO')

add('''<div class="capa fim">
  <div class="chips"><span class="chip">2ª SPRINT ENTREGUE</span><span class="chip">10 DE 28 PBIs</span></div>
  <h1>Obrigado!</h1>
  <p class="sub">Próxima sprint: as <span class="grad">lojas parceiras</span> entram, e finalizar a sacola leva o cliente à loja de cada perfume.</p>
  <div class="equipe"><div><span class="mono">GITHUB</span><p>github.com/EnzoKoeche/modular-perfumes</p></div>
  <div><span class="mono">TRELLO</span><p>trello.com/b/PN46fipf</p></div></div>
</div>''', escuro=True)

# ---------------------------------------------------------------- apêndice: roteiro de fala

blocos = [
    ('Abertura e produto', 'págs. 1–5', '2 min', 'Problema (comprar às cegas), solução e os cinco passos do cliente. Feche dizendo o que esta sprint entrega.'),
    ('Canvas PBB e backlog', 'págs. 6–9', '1,5 min', 'Personas com papéis diferentes, os 28 PBIs e por que o consultor e a sacola vieram agora (valor principal).'),
    ('User stories', 'págs. 10–12', '1,5 min', 'Leia uma história inteira em voz alta (a US6 ou a US9) e mostre que CA1, CA2 e CA3 viraram testes.'),
    ('Como funciona e US6', 'págs. 13–15, 16', '2 min', 'Perfil = soma dos pesos; o agente só recomenda o que a ferramenta registrou. Depois os três critérios da US6.'),
    ('US7 a US10 no site', 'págs. 17–20', '2 min', 'Ficha, conversa, cartões e sacola, mostrando o banco ao lado de cada tela. Se der, demonstre ao vivo.'),
    ('Qualidade, processo e próximos', 'págs. 21–27', '1 min', 'Os testes por critério, o fluxo do Trello e o que vem na Sprint 3. Agradecer.'),
]
add(topo('APÊNDICE', 'Roteiro de fala sugerido (cerca de 10 minutos)', 'Sugestão para dividir entre os três. Ajustem quem fala o quê; o importante é cada um apresentar uma parte.')
    + '<table class="dados roteiro"><thead><tr><th>Bloco</th><th>Páginas</th><th>Tempo</th><th>O que dizer</th><th>Quem</th></tr></thead><tbody>'
    + ''.join(f'<tr><td><b>{e(b)}</b></td><td class="mono">{e(p)}</td><td class="mono">{e(t)}</td><td>{e(d)}</td><td class="quem"></td></tr>'
              for b, p, t, d in blocos)
    + '</tbody></table><p class="nota-rodape"><b>Dica para a demonstração ao vivo:</b> deixe o banco e o site no ar antes (<span class="mono">docker compose up -d db</span> e <span class="mono">flask --app app run --port 5050</span>), já logado como cliente com o questionário respondido, e outra aba como administrador na tela de pesos.</p>',
    'APÊNDICE')

# ---------------------------------------------------------------- estilo e PDF

CSS = '''
@page { size: 1920px 1080px; margin: 0; }
* { box-sizing: border-box; }
body { margin: 0; font-family: Inter, system-ui, sans-serif; color: #0c0d12; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.mono { font-family: 'JetBrains Mono', ui-monospace, monospace; letter-spacing: .03em; }
.slide { width: 1920px; height: 1080px; padding: 64px 96px 90px; position: relative; overflow: hidden; background: #f6f7f9; page-break-after: always; }
.slide.escuro { background: #0b0b12; color: #fff; }
.slide.escuro::before { content: ''; position: absolute; inset: 0; opacity: .5;
  background-image: linear-gradient(rgba(255,255,255,.05) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.05) 1px, transparent 1px);
  background-size: 48px 48px; mask-image: radial-gradient(ellipse at 30% 50%, #000 30%, transparent 75%); }
.slide.escuro::after { content: ''; position: absolute; width: 900px; height: 900px; right: -250px; top: -300px;
  background: radial-gradient(circle, rgba(124,58,237,.55), rgba(6,182,212,.25) 45%, transparent 70%); }
.slide > * { position: relative; z-index: 1; }
.grad { background: linear-gradient(135deg, #a78bfa, #22d3ee); -webkit-background-clip: text; background-clip: text; color: transparent; }
.chip { display: inline-block; padding: 6px 14px; border-radius: 999px; border: 1px solid #e6e8ec; background: #fff; font: 600 15px 'JetBrains Mono', monospace; color: #667085; letter-spacing: .04em; }
.escuro .chip { background: rgba(255,255,255,.06); border-color: rgba(255,255,255,.18); color: #cbd5e1; }
.capa { position: absolute; left: 120px; right: 120px; top: 50%; transform: translateY(-50%); }
.capa h1 { font-size: 150px; letter-spacing: -.04em; margin: 28px 0 10px; line-height: 1; }
.capa .sub { font-size: 40px; color: #cbd5e1; margin: 0 0 80px; max-width: 1400px; line-height: 1.3; }
.capa.fim h1 { font-size: 120px; }
.chips { display: flex; gap: 12px; }
.equipe { display: flex; gap: 90px; }
.equipe .mono { color: #94a3b8; font-size: 16px; }
.equipe p { font-size: 26px; margin: 8px 0 0; color: #e2e8f0; }
.topo { margin-bottom: 30px; }
.topo h2 { font-size: 54px; letter-spacing: -.03em; margin: 14px 0 0; }
.subtitulo { font-size: 22px; color: #475467; margin: 10px 0 0; }
.card { background: #fff; border: 1px solid #e6e8ec; border-radius: 22px; padding: 28px 32px; box-shadow: 0 1px 2px rgba(16,24,40,.04); }
.grade2 { display: grid; grid-template-columns: 1fr 1fr; gap: 28px; }
.grade3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 28px; }
.grade4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; }
.lado { display: grid; grid-template-columns: 1.25fr 1fr; gap: 32px; align-items: start; }
h3 { font-size: 30px; margin: 6px 0 14px; letter-spacing: -.01em; }
.rot { display: block; font-size: 14px; color: #667085; margin: 14px 0 8px; font-weight: 600; }
.rot.ok { color: #047857; } .rot.erro { color: #b42318; } .rot.aviso { color: #b54708; }
.item { font-size: 22px; margin: 8px 0; padding: 12px 16px; border-radius: 12px; background: #f6f7f9; line-height: 1.35; }
.item.faz, .item.prob { background: #1f2027; color: #fff; }
.item.espera, .item.ben { background: linear-gradient(135deg, #7c3aed, #06b6d4); color: #fff; }
.passo { position: relative; min-height: 380px; }
.passo .num, .etapa .num { font-size: 22px; color: #7c3aed; font-weight: 600; }
.passo h3 { font-size: 38px; margin-top: 18px; } .passo p { font-size: 25px; color: #475467; line-height: 1.45; }
.tempo { position: absolute; bottom: 28px; left: 32px; font-size: 18px; color: #06b6d4; font-weight: 600; }
.nota-rodape { font-size: 23px; color: #475467; margin-top: 28px; line-height: 1.45; max-width: 1650px; }
.figura { text-align: center; }
.fluxo { display: grid; grid-template-columns: repeat(5, 1fr); gap: 22px; }
.etapa { position: relative; min-height: 470px; padding-top: 30px; }
.etapa h3 { font-size: 30px; margin-top: 16px; } .etapa p { font-size: 22px; color: #475467; line-height: 1.45; }
.etapa .onde { position: absolute; bottom: 64px; left: 32px; }
.sprint-tag { position: absolute; bottom: 26px; left: 32px; font-size: 15px; color: #667085; }
.onde { display: inline-block; margin-top: 16px; font-size: 16px; color: #7c3aed; font-weight: 600; }
.persona h3 { margin-bottom: 0; } .perfil { font-size: 14px; color: #7c3aed; }
.persona .item { font-size: 20px; padding: 10px 14px; }
.feat { font-size: 20px; margin: 6px 0; padding: 8px 14px; border: 1px dashed #c4b5fd; border-radius: 10px; color: #5b21b6; }
.selo { display: inline-block; padding: 4px 12px; border-radius: 8px; background: #0c0d12; color: #fff; font: 700 18px 'JetBrains Mono', monospace; }
.pbi { margin-left: 8px; font-size: 14px; color: #7c3aed; font-weight: 700; }
.us h3 { font-size: 26px; margin: 12px 0 10px; }
.historia { font-size: 19px; line-height: 1.45; color: #344054; margin: 0 0 8px; }
.ca { border-top: 1px solid #e6e8ec; padding-top: 10px; margin-top: 10px; }
.ca-rotulo { display: flex; gap: 10px; align-items: center; font-size: 15px; color: #667085; }
.ca-rotulo .mono { font-weight: 700; color: #0c0d12; }
.ca p { font-size: 18px; line-height: 1.45; margin: 4px 0 0; color: #344054; }
.ca b { font-family: 'JetBrains Mono', monospace; font-size: 14px; color: #7c3aed; }
.didatico p { font-size: 21px; line-height: 1.5; color: #344054; margin: 8px 0; }
.didatico b.mono { color: #7c3aed; font-size: 18px; margin-right: 6px; }
table.dados { width: 100%; border-collapse: collapse; background: #fff; border: 1px solid #e6e8ec; border-radius: 14px; overflow: hidden; font-size: 17px; }
table.dados th { text-align: left; font: 600 14px 'JetBrains Mono', monospace; color: #667085; background: #f9fafb; padding: 10px 12px; border-bottom: 1px solid #e6e8ec; }
table.dados td { padding: 9px 12px; border-bottom: 1px solid #f0f1f3; vertical-align: top; }
table.dados tr.destaque td { background: #f3efff; }
table.dados.grande { font-size: 27px; } table.dados.grande td { padding: 22px 18px; } table.dados.grande th { font-size: 16px; padding: 14px 18px; }
table.pbis { font-size: 19px; } table.pbis td { padding: 9px 12px; }
table.pbis tr.s1 td, table.pbis tr.s2 td { background: #faf8ff; }
.tag { display: inline-block; padding: 3px 10px; border-radius: 999px; font: 600 14px 'JetBrains Mono', monospace; background: #f2f4f7; color: #667085; }
.tag.s1 { background: #0c0d12; color: #fff; } .tag.s2 { background: linear-gradient(135deg, #7c3aed, #06b6d4); color: #fff; }
.print { background: #fff; border: 1px solid #e6e8ec; border-radius: 18px; padding: 12px 14px 16px; }
.print img { width: 100%; border-radius: 10px; border: 1px solid #eef0f3; display: block; }
.print .rot { margin-top: 4px; }
.banco { margin-top: 22px; } .banco.coluna { margin-top: 0; }
.banco.coluna > .print { margin-bottom: 14px; }
.obs { font-size: 18px; color: #475467; line-height: 1.45; margin: 10px 0; }
.lado > .print img { max-height: 800px; object-fit: cover; object-position: top; }
.banco.coluna > .print img { max-height: 250px; object-fit: cover; object-position: top; }
.trio { display: grid; grid-template-columns: 1fr 1fr 0.8fr; gap: 26px; align-items: start; }
.trio > .print img { max-height: 760px; object-fit: cover; object-position: top; }
.grade3.prints .print img { height: 330px; object-fit: cover; object-position: top; }
.mini .print img { height: 600px; object-fit: cover; object-position: top; }
.banco table.dados { font-size: 16px; }
.numeros .grande { font-size: 70px; font-weight: 700; margin: 0; letter-spacing: -.03em; line-height: 1.1; }
.numeros .card { padding: 20px 26px; }
pre { font-size: 17px; line-height: 1.5; background: #0b0b12; color: #e2e8f0; padding: 18px 22px; border-radius: 14px; margin: 8px 0 0; white-space: pre-wrap; }
.rodape { position: absolute; left: 96px; right: 96px; bottom: 34px; display: flex; justify-content: space-between; font-size: 14px; color: #98a2b3; }
.aviso-demo { font-size: 17px; line-height: 1.45; background: #fffaeb; border: 1px solid #fedf89; color: #7a2e0e; border-radius: 12px; padding: 12px 16px; margin: 12px 0 0; }
.conta { display: flex; justify-content: space-between; font-size: 20px; padding: 10px 16px; margin: 6px 0; background: #f6f7f9; border-radius: 10px; }
.conta .mono { color: #7c3aed; font-weight: 600; }
.arq { display: grid; grid-template-columns: 0.8fr 60px 2fr 60px 0.9fr; align-items: center; gap: 10px; margin-top: 10px; }
.caixa { background: #fff; border: 1px solid #e6e8ec; border-radius: 20px; padding: 22px 26px; }
.caixa p { font-size: 22px; margin: 6px 0; } .caixa .rot { margin-top: 0; }
.caixa.srv { border: 2px solid #c4b5fd; }
.mods { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 10px 0; }
.mods span { font: 600 18px 'JetBrains Mono', monospace; background: #f6f7f9; border-radius: 12px; padding: 14px; }
.mods small { display: block; font: 500 14px Inter, sans-serif; color: #7c3aed; margin-top: 6px; }
.seta { font-size: 46px; color: #98a2b3; text-align: center; }
.pilha { display: flex; flex-direction: column; gap: 14px; }
.caixa.db { border-left: 6px solid #0c0d12; } .caixa.ext { border-left: 6px solid #06b6d4; }
.ciclo { display: flex; flex-direction: column; gap: 14px; }
.no { background: #fff; border: 1px solid #e6e8ec; border-radius: 18px; padding: 16px 24px; border-left: 6px solid #e6e8ec; }
.no p { font-size: 22px; margin: 0; } .no .rot { margin: 0 0 6px; }
.no.cli { border-left-color: #0c0d12; } .no.srv { border-left-color: #7c3aed; } .no.ia { border-left-color: #a78bfa; } .no.db { border-left-color: #06b6d4; }
.ferr { font-size: 19px; margin: 8px 0; color: #344054; } .ferr .mono { display: inline-block; min-width: 290px; color: #7c3aed; font-weight: 600; font-size: 17px; }
.tabelas-novas { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.tb { background: #fff; border: 1px solid #e6e8ec; border-radius: 18px; padding: 22px 24px; border-top: 6px solid #7c3aed; }
.tb h4 { font: 700 24px 'JetBrains Mono', monospace; margin: 0 0 10px; }
.tb p { font: 500 17px 'JetBrains Mono', monospace; color: #344054; line-height: 1.6; margin: 0 0 8px; }
table.testes { font-size: 17px; } table.testes td.teste { font-size: 15px; color: #344054; }
.qualidade { margin-top: 26px; } .qualidade p { font-size: 20px; line-height: 1.45; color: #344054; margin: 0; }
.colunas-trello { display: grid; grid-template-columns: 1fr 40px 1fr 40px 1fr 40px 1fr 40px 1fr; align-items: center; margin-bottom: 30px; }
.col { background: #fff; border: 1px solid #e6e8ec; border-radius: 16px; padding: 18px; min-height: 130px; }
.col .mono { font-size: 15px; font-weight: 700; color: #7c3aed; } .col p { font-size: 19px; color: #475467; margin: 8px 0 0; }
.col.ok { border: 2px solid #12b76a; } .col.ok .mono { color: #047857; }
.colunas-trello .seta { font-size: 30px; }
.processo .item { font-size: 20px; }
.trilha { display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); gap: 14px; margin-top: 20px; }
.elo { background: #fff; border: 1px solid #e6e8ec; border-radius: 18px; padding: 20px; min-height: 330px; position: relative; border-top: 6px solid #a78bfa; }
.elo p { font-size: 21px; line-height: 1.4; margin: 0; } .elo.ok { border-top-color: #12b76a; }
.obj { font-size: 20px; color: #344054; line-height: 1.45; margin: 0 0 14px; }
.pbi-item { font-size: 20px; margin: 8px 0; padding: 10px 14px; background: #f6f7f9; border-radius: 10px; }
.pbi-item .mono { color: #7c3aed; font-weight: 700; margin-right: 8px; }
.glossario p { font-size: 21px; line-height: 1.5; color: #344054; margin: 12px 0; } .glossario b { color: #0c0d12; }

table.pbis { font-size: 17px; } table.pbis td { padding: 6px 10px; } table.pbis th { padding: 7px 10px; }
.tag { white-space: nowrap; }
.backlog + .nota-rodape { margin-top: 18px; }
.us6 > .print img { max-height: 170px !important; }
.us6 > .print { padding: 8px 12px 10px; margin-bottom: 10px !important; } .us6 .rot { margin: 2px 0 6px; }
.us7 .print img { height: 400px; object-fit: cover; object-position: top; }
.us7b { margin-top: 24px; align-items: start; } .us7b .print img { max-height: 230px; object-fit: cover; object-position: top; }
.us7b .obs { font-size: 23px; }
.sacola .print img { height: 290px !important; object-fit: cover; object-position: top; }
.coluna-prints { display: flex; flex-direction: column; gap: 18px; }
.sacola .obs { font-size: 21px; }
.mini .print img { height: 270px !important; object-fit: cover; object-position: top; }
.item { font-size: 25px; }
.passo p { font-size: 28px; } .passo h3 { font-size: 42px; }
.historia { font-size: 22px; } .ca p { font-size: 21px; } .ca b { font-size: 16px; } .ca-rotulo { font-size: 17px; }
.didatico p { font-size: 24px; }
.glossario p { font-size: 26px; margin: 18px 0; }
.pbi-item { font-size: 23px; } .obj { font-size: 23px; }
.qualidade p { font-size: 24px; }
table.testes { font-size: 19px; table-layout: fixed; } table.testes th:first-child { width: 90px; } table.testes td.teste { word-break: break-all; } table.testes td { padding: 14px 12px; } table.testes td.teste { font-size: 17px; }
.tb p { font-size: 20px; } .tb h4 { font-size: 28px; } .tb .obs { font-size: 20px; }
.processo .item { font-size: 23px; } .col p { font-size: 21px; } .col { min-height: 150px; }
.elo { min-height: 420px; } .elo p { font-size: 23px; overflow-wrap: anywhere; }
.etapa p { font-size: 24px; } .etapa h3 { font-size: 32px; } .etapa { min-height: 520px; }
.nota-rodape { font-size: 25px; }
.caixa p { font-size: 25px; } .mods span { font-size: 20px; } .mods small { font-size: 16px; }
.no p { font-size: 25px; } .ferr { font-size: 21px; } .ferr .mono { font-size: 19px; min-width: 320px; }
.conta { font-size: 22px; }
table.roteiro { font-size: 20px; } table.roteiro td { padding: 16px 14px; } table.roteiro td.quem { min-width: 220px; border-left: 1px dashed #d0d5dd; }
'''

documento = f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600;700&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>{"".join(slides)}</body></html>'''
(PASTA / 'slides.html').write_text(documento, encoding='utf-8')

with sync_playwright() as p:
    nav = p.chromium.launch()
    pg = nav.new_page(viewport={'width': 1920, 'height': 1080})
    pg.goto(f'file://{PASTA / "slides.html"}')
    pg.wait_for_load_state('networkidle')
    pg.evaluate('document.fonts.ready')
    pg.wait_for_timeout(800)
    pg.pdf(path=str(SAIDA), width='1920px', height='1080px', print_background=True,
           margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'})
    for i in range(len(slides)):
        pg.evaluate(f'window.scrollTo(0, {i * 1080})')
        pg.screenshot(path=str(PASTA / f'slide_{i + 1:02d}.png'))
    nav.close()
print('slides:', len(slides), '->', SAIDA)
