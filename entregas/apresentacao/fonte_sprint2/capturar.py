"""Percorre o projeto inteiro no site local (US1 a US10) e tira os prints de cada critério de aceite.

Pré-requisito: banco no ar (docker compose up -d db) e o site rodando por `python servidor_demo.py`.
Cria um administrador e uma cliente de demonstração, importa o catálogo do provedor configurado no .env
e guarda as consultas ao banco em evidencias.json. No fim, apaga o administrador de demonstração.
"""
import json
import pathlib
import secrets
import sys

import pymysql
from dotenv import dotenv_values
from playwright.sync_api import sync_playwright
from werkzeug.security import generate_password_hash

B = 'http://127.0.0.1:5050'
PASTA = pathlib.Path(__file__).parent
IMG = PASTA / 'img'
IMG.mkdir(exist_ok=True)
ADMIN = {'email': 'apresentacao@modular.local', 'senha': secrets.token_urlsafe(12)}
CLIENTE = {'nome': 'Marina Demo', 'email': 'marina.demo@exemplo.com', 'senha': 'perfume2026'}
MARCAS = sys.argv[1:] or ['Casa Demo', 'Atelier Exemplo']
# perfil fresco: iniciante, dia a dia e calor, cítricos e brisa do mar, leve, unissex, durante o dia
RESPOSTAS = [1, 4, 7, 9, 13, 15, 19, 22, 26, 28, 32, 35, 38]
MENSAGEM = 'Quero um perfume fresco para usar no trabalho, no calor.'


def banco(sql, params=()):
    con = pymysql.connect(host='127.0.0.1', port=3307, user='modular', password='modular_dev',
                          database='modular_perfumes', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
    try:
        with con.cursor() as cur:
            cur.execute(sql, params)
            linhas = cur.fetchall()
        con.commit()
        return linhas
    finally:
        con.close()


def foto(pg, nome, alvo=None, altura=800):
    caminho = str(IMG / f'{nome}.png')
    if alvo:
        pg.locator(alvo).first.screenshot(path=caminho)
    else:
        pg.screenshot(path=caminho, clip={'x': 0, 'y': 0, 'width': 1280, 'height': altura})


def entrar(pg, email, senha, destino):
    pg.goto(B + '/login')
    pg.fill('#email', email)
    pg.fill('#senha', senha)
    pg.click('button:has-text("Entrar")')
    pg.wait_for_url(destino)


def sair(pg):
    pg.goto(B + '/')
    if pg.locator('button:has-text("Sair")').count():
        pg.click('button:has-text("Sair")')


def perfume(nome):
    return banco('SELECT id FROM perfume WHERE nome = %s', (nome,))[0]['id']


# ---------------------------------------------------------------- preparação
banco('DELETE FROM usuario WHERE email IN (%s, %s)', (CLIENTE['email'], ADMIN['email']))
banco("INSERT INTO usuario (nome, email, senha_hash, perfil) VALUES ('Apresentação', %s, %s, 'ADMIN')",
      (ADMIN['email'], generate_password_hash(ADMIN['senha'], method='pbkdf2:sha256')))
ev = {'marcas': MARCAS}

with sync_playwright() as p:
    nav = p.chromium.launch()
    pg = nav.new_page(viewport={'width': 1280, 'height': 800}, device_scale_factor=2)
    pg.on('dialog', lambda d: d.accept())

    # ---------------------------------------------------------------- administrador
    entrar(pg, ADMIN['email'], ADMIN['senha'], '**/admin/')
    foto(pg, 'admin_inicio', altura=620)

    # US5 — importar o catálogo
    for marca in MARCAS:
        pg.goto(B + '/admin/catalogo')
        pg.fill('#marca', marca)
        pg.fill('#limite', '50')
        pg.click('button:has-text("Importar catálogo")')
        pg.wait_for_url('**/admin/catalogo')
    pg.wait_for_load_state('networkidle'); pg.wait_for_timeout(800)
    foto(pg, 'us5_catalogo', altura=900)

    # US4 — lista de perguntas, já com o botão Pesos da US6
    pg.goto(B + '/admin/perguntas')
    foto(pg, 'us4_lista', altura=800)

    # US6 — pesos: CA1 (salva), CA2 (peso inválido), CA3 (alternativa toda em zero)
    q3 = banco("SELECT id FROM pergunta WHERE enunciado LIKE 'Quais destes cheiros agradam%%'")[0]['id']
    q6 = banco("SELECT id FROM pergunta WHERE enunciado LIKE 'Para quem%%'")[0]['id']
    pg.goto(B + f'/admin/perguntas/{q3}/pesos')
    foto(pg, 'us6_tela', altura=900)
    pg.click('button:has-text("Salvar pesos")'); pg.wait_for_timeout(500)
    foto(pg, 'us6_ca1', altura=360)
    campo = pg.locator('input[type=number]').first
    original = campo.input_value()
    campo.evaluate('c => { c.removeAttribute("min"); c.removeAttribute("max"); }')
    campo.fill('-3')
    pg.click('button:has-text("Salvar pesos")'); pg.wait_for_timeout(500)
    foto(pg, 'us6_ca2', altura=420)
    ev['pesos_depois_ca2'] = banco(
        'SELECT COUNT(*) AS pesos, SUM(ap.peso < 0) AS negativos FROM alternativa_peso ap '
        'JOIN alternativa a ON a.id = ap.alternativa_id WHERE a.pergunta_id = %s', (q3,))
    pg.goto(B + f'/admin/perguntas/{q6}/pesos')
    pg.click('button:has-text("Salvar pesos")'); pg.wait_for_timeout(500)
    foto(pg, 'us6_ca3', altura=520)
    ev['pesos'] = banco(
        'SELECT a.texto AS alternativa, f.nome AS familia, ap.peso FROM alternativa_peso ap '
        'JOIN alternativa a ON a.id = ap.alternativa_id JOIN familia_olfativa f ON f.id = ap.familia_id '
        'WHERE a.pergunta_id = %s ORDER BY a.ordem, ap.peso DESC LIMIT 8', (q3,))
    ev['pesos_q6'] = banco(
        'SELECT a.texto AS alternativa, COUNT(ap.familia_id) AS familias_com_peso FROM alternativa a '
        'LEFT JOIN alternativa_peso ap ON ap.alternativa_id = a.id WHERE a.pergunta_id = %s GROUP BY a.id, a.texto',
        (q6,))
    sair(pg)

    # ---------------------------------------------------------------- visitante (sem login)
    pg.goto(B + '/perfumes/'); pg.wait_for_load_state('networkidle'); pg.wait_for_timeout(800)
    foto(pg, 'vitrine', altura=900)
    brisa = perfume('Brisa de Bergamota') if 'Casa Demo' in MARCAS else None
    alvo = brisa or banco('SELECT id FROM perfume WHERE visivel = 1 ORDER BY avaliacao DESC LIMIT 1')[0]['id']
    pg.goto(B + f'/perfumes/{alvo}'); pg.wait_for_load_state('networkidle')
    foto(pg, 'us7_ca3', altura=800)
    oculto = banco('SELECT id FROM perfume WHERE visivel = 1 AND id <> %s ORDER BY id LIMIT 1', (alvo,))[0]['id']
    banco('UPDATE perfume SET visivel = 0 WHERE id = %s', (oculto,))
    pg.goto(B + f'/perfumes/{oculto}')
    foto(pg, 'us7_ca2', altura=420)
    banco('UPDATE perfume SET visivel = 1 WHERE id = %s', (oculto,))

    # ---------------------------------------------------------------- cliente
    pg.goto(B + '/cadastro')
    pg.fill('#nome', CLIENTE['nome']); pg.fill('#email', CLIENTE['email']); pg.fill('#senha', CLIENTE['senha'])
    pg.check('#aceite')
    foto(pg, 'us1_formulario', '.card')
    pg.click('button:has-text("Criar conta")'); pg.wait_for_url('**/questionario/')
    foto(pg, 'us3_questionario', altura=800)
    # US9 CA3: antes de concluir o questionário, o consultor manda de volta para ele
    pg.goto(B + '/consultor/'); pg.wait_for_url('**/questionario/')
    ev['us9_ca3_url'] = pg.url
    for alt in RESPOSTAS:
        pg.check(f'#alt-{alt}')
    pg.click('button:has-text("Concluir")'); pg.wait_for_url('**/inicio')
    foto(pg, 'us3_perfil', altura=700)

    # US7 CA1 — ficha com o botão da sacola
    pg.goto(B + f'/perfumes/{alvo}'); pg.wait_for_load_state('networkidle')
    foto(pg, 'us7_ca1', altura=800)

    # US8 e US9 — conversa com o consultor e cartões de recomendação
    pg.goto(B + '/consultor/')
    foto(pg, 'us8_vazio', altura=640)
    pg.fill('#texto', MENSAGEM)
    pg.click('#form-chat button')
    pg.wait_for_selector('#recs form', timeout=180000)
    pg.wait_for_timeout(1200)
    foto(pg, 'us8_us9_conversa', altura=800)
    ev['mensagens'] = banco(
        "SELECT m.id, m.papel, LEFT(JSON_UNQUOTE(JSON_EXTRACT(m.conteudo_json, '$.texto')), 60) AS texto, m.modelo "
        'FROM mensagem m JOIN conversa c ON c.id = m.conversa_id JOIN usuario u ON u.id = c.usuario_id '
        'WHERE u.email = %s ORDER BY m.id', (CLIENTE['email'],))
    ev['recomendacoes'] = banco(
        'SELECT r.posicao, p.nome AS perfume, r.justificativa FROM recomendacao r JOIN conversa c ON c.id = r.conversa_id '
        'JOIN usuario u ON u.id = c.usuario_id JOIN perfume p ON p.id = r.perfume_id WHERE u.email = %s ORDER BY r.id',
        (CLIENTE['email'],))

    # US10 — sacola: CA1 pelo cartão da recomendação, CA2 de novo pela ficha, CA3 remover
    pg.locator('#recs form button').first.click(); pg.wait_for_url('**/sacola/')
    foto(pg, 'us10_ca1', altura=520)
    na_sacola = banco('SELECT p.nome FROM sacola_item s JOIN perfume p ON p.id = s.perfume_id '
                      'JOIN usuario u ON u.id = s.usuario_id WHERE u.email = %s', (CLIENTE['email'],))[0]['nome']
    ev['us10_ca1'] = na_sacola
    pg.goto(B + f'/perfumes/{perfume(na_sacola)}')            # CA2: o MESMO perfume de novo
    pg.click('button:has-text("Adicionar à sacola")'); pg.wait_for_url('**/sacola/')
    foto(pg, 'us10_ca2', altura=520)
    ev['us10_ca2_itens'] = banco('SELECT COUNT(*) AS n FROM sacola_item s JOIN usuario u ON u.id = s.usuario_id '
                                 'WHERE u.email = %s', (CLIENTE['email'],))[0]['n']
    outro = next((r['perfume'] for r in ev['recomendacoes'] if r['perfume'] != na_sacola), None)
    if outro:
        pg.goto(B + f'/perfumes/{perfume(outro)}')
        pg.click('button:has-text("Adicionar à sacola")'); pg.wait_for_url('**/sacola/')
    pg.locator('button:has-text("Remover")').last.click(); pg.wait_for_url('**/sacola/')
    foto(pg, 'us10_ca3', altura=520)
    ev['sacola'] = banco(
        'SELECT p.nome AS perfume, s.adicionado_em FROM sacola_item s JOIN perfume p ON p.id = s.perfume_id '
        'JOIN usuario u ON u.id = s.usuario_id WHERE u.email = %s', (CLIENTE['email'],))

    # US2 — login de volta cai no perfil
    sair(pg)
    entrar(pg, CLIENTE['email'], CLIENTE['senha'], '**/inicio')
    nav.close()

# ---------------------------------------------------------------- evidências do banco
ev['perfil'] = banco(
    'SELECT po.nivel_conhecimento, f.nome AS familia, pf.afinidade FROM perfil_olfativo po '
    'JOIN usuario u ON u.id = po.usuario_id JOIN perfil_familia pf ON pf.perfil_id = po.id '
    'JOIN familia_olfativa f ON f.id = pf.familia_id WHERE u.email = %s ORDER BY pf.afinidade DESC', (CLIENTE['email'],))
ev['logs'] = banco('SELECT id, status, qtd_incluidos, qtd_atualizados, mensagem_erro FROM importacao_catalogo '
                   'ORDER BY id DESC LIMIT 4')
ev['totais'] = banco(
    'SELECT (SELECT COUNT(*) FROM perfume) AS perfumes, (SELECT COUNT(*) FROM perfume_nota) AS notas, '
    '(SELECT COUNT(*) FROM perfume_acorde) AS acordes, (SELECT COUNT(*) FROM marca) AS marcas, '
    "(SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'modular_perfumes') AS tabelas")
ev['provedor'] = dotenv_values(PASTA.parents[2] / '.env').get('CATALOGO_PROVEDOR', 'exemplo')
banco('DELETE FROM usuario WHERE email = %s', (ADMIN['email'],))

(PASTA / 'evidencias.json').write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str), encoding='utf-8')
print('prints:', sorted(x.name for x in IMG.glob('*.png')))
