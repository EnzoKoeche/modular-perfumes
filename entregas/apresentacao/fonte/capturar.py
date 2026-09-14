"""Percorre as user stories da 1ª Sprint no site local e tira prints de cada critério de aceite."""
import json
import pathlib
import sys

import pymysql
from playwright.sync_api import sync_playwright

B = 'http://127.0.0.1:5050'
PASTA = pathlib.Path(__file__).parent
IMG = PASTA / 'img'
SENHA_ADMIN = sys.argv[1]
CLIENTE = {'nome': 'Marina Demo', 'email': 'marina.demo@exemplo.com', 'senha': 'perfume2026'}
RESPOSTAS = {1: [1], 2: [4, 5], 3: [8, 11], 4: [17], 5: [20], 6: [22], 7: [25], 8: [29], 9: [32], 10: [35], 11: [40]}


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


def print_(pg, nome, alvo=None, altura=None):
    caminho = str(IMG / f'{nome}.png')
    if alvo:
        pg.locator(alvo).first.screenshot(path=caminho)
    else:
        pg.screenshot(path=caminho, clip={'x': 0, 'y': 0, 'width': 1280, 'height': altura or 800})


def sair(pg):
    pg.goto(B + '/')
    if pg.locator('button:has-text("Sair")').count():
        pg.click('button:has-text("Sair")')


def responder(pg, perguntas):
    for p in perguntas:
        for alt in RESPOSTAS[p]:
            pg.check(f'#alt-{alt}')


# limpa demonstrações anteriores
banco("DELETE FROM usuario WHERE email = %s", (CLIENTE['email'],))
banco("DELETE a FROM alternativa a JOIN pergunta p ON p.id = a.pergunta_id WHERE p.enunciado LIKE 'No trabalho, você prefere%%'")
banco("DELETE FROM pergunta WHERE enunciado LIKE 'No trabalho, você prefere%%'")

evidencias = {}
with sync_playwright() as p:
    nav = p.chromium.launch()
    pg = nav.new_page(viewport={'width': 1280, 'height': 800}, device_scale_factor=2)
    pg.on('dialog', lambda d: d.accept())

    # US1 — cadastro
    pg.goto(B + '/cadastro')
    pg.fill('#nome', CLIENTE['nome']); pg.fill('#email', CLIENTE['email']); pg.fill('#senha', CLIENTE['senha'])
    pg.check('#aceite')
    print_(pg, 'us1_formulario', '.card')
    pg.click('button:has-text("Criar conta")'); pg.wait_for_url('**/questionario/')
    print_(pg, 'us1_ca1', altura=520)

    # US3 — questionário: CA2 (obrigatória sem resposta) e CA1 (conclui e gera perfil)
    responder(pg, [1, 2, 3, 4, 5])
    pg.click('button:has-text("Concluir")'); pg.wait_for_timeout(900)
    pg.locator('.pergunta-pendente').first.scroll_into_view_if_needed(); pg.wait_for_timeout(300)
    pg.screenshot(path=str(IMG / 'us3_ca2.png'))
    evidencias['resposta_parcial'] = banco(
        "SELECT r.id, r.concluida_em, COUNT(DISTINCT ri.pergunta_id) AS perguntas_respondidas FROM resposta_questionario r "
        "JOIN usuario u ON u.id = r.usuario_id LEFT JOIN resposta_item ri ON ri.resposta_id = r.id "
        "WHERE u.email = %s GROUP BY r.id, r.concluida_em", (CLIENTE['email'],))
    responder(pg, [6, 7, 8, 9, 10, 11])
    pg.click('button:has-text("Concluir")'); pg.wait_for_url('**/inicio')
    print_(pg, 'us3_ca1', altura=640)

    # US1 — CA2: e-mail já cadastrado
    sair(pg)
    pg.goto(B + '/cadastro')
    pg.fill('#nome', 'Marina de Novo'); pg.fill('#email', CLIENTE['email']); pg.fill('#senha', 'outra-senha-1')
    pg.check('#aceite'); pg.click('button:has-text("Criar conta")'); pg.wait_for_timeout(500)
    print_(pg, 'us1_ca2', '.card')

    # US2 — CA2 (senha errada) e CA1 (login com questionário concluído)
    pg.goto(B + '/login')
    pg.fill('#email', CLIENTE['email']); pg.fill('#senha', 'senha-errada')
    pg.click('button:has-text("Entrar")'); pg.wait_for_timeout(400)
    print_(pg, 'us2_ca2', '.card')
    pg.fill('#email', CLIENTE['email']); pg.fill('#senha', CLIENTE['senha'])
    pg.click('button:has-text("Entrar")'); pg.wait_for_url('**/inicio')
    print_(pg, 'us2_ca1', altura=400)
    sair(pg)

    # US4 — perguntas (administrador)
    pg.goto(B + '/login')
    pg.fill('#email', 'admin@modular.local'); pg.fill('#senha', SENHA_ADMIN)
    pg.click('button:has-text("Entrar")'); pg.wait_for_url('**/admin/')
    pg.goto(B + '/admin/perguntas/nova')
    pg.fill('#enunciado', 'No trabalho, você prefere perfumes discretos ou marcantes?')
    pg.fill('#alternativas', 'Discretos')
    pg.click('button:has-text("Salvar")'); pg.wait_for_timeout(500)
    print_(pg, 'us4_ca2', altura=560)
    pg.fill('#alternativas', 'Discretos\nMarcantes\nDepende do dia')
    pg.click('button:has-text("Salvar")'); pg.wait_for_url('**/admin/perguntas')
    print_(pg, 'us4_ca1', altura=800)
    linha = pg.locator('tr', has_text='Quais destes cheiros você NÃO gosta?')
    linha.locator('button:has-text("Excluir")').click(); pg.wait_for_url('**/admin/perguntas')
    pg.wait_for_timeout(300)
    print_(pg, 'us4_ca3', altura=800)
    evidencias['perguntas'] = banco(
        "SELECT p.id, p.ordem, p.enunciado, p.tipo, p.ativa, "
        "(SELECT COUNT(*) FROM alternativa a WHERE a.pergunta_id = p.id AND a.ativa = 1) AS alternativas, "
        "(SELECT COUNT(*) FROM resposta_item ri WHERE ri.pergunta_id = p.id) AS respostas "
        "FROM pergunta p WHERE p.id >= 9 ORDER BY p.ordem")

    # US5 — catálogo
    pg.goto(B + '/admin/catalogo'); pg.wait_for_load_state('networkidle'); pg.wait_for_timeout(1200)
    print_(pg, 'us5_catalogo', altura=900)
    pg.goto(B + '/perfumes/'); pg.wait_for_load_state('networkidle'); pg.wait_for_timeout(1200)
    print_(pg, 'extra_vitrine', altura=800)
    nav.close()

# evidências do banco para os slides (antes de desfazer a demonstração)
evidencias['usuario'] = banco(
    "SELECT id, nome, email, perfil, LEFT(senha_hash, 22) AS senha_hash, criado_em FROM usuario ORDER BY id")
evidencias['resposta'] = banco(
    "SELECT r.id, r.iniciada_em, r.concluida_em, COUNT(DISTINCT ri.pergunta_id) AS perguntas_respondidas, "
    "COUNT(*) AS itens FROM resposta_questionario r JOIN usuario u ON u.id = r.usuario_id "
    "JOIN resposta_item ri ON ri.resposta_id = r.id WHERE u.email = %s GROUP BY r.id, r.iniciada_em, r.concluida_em",
    (CLIENTE['email'],))
evidencias['perfil'] = banco(
    "SELECT po.nivel_conhecimento, f.nome AS familia, pf.afinidade FROM perfil_olfativo po "
    "JOIN usuario u ON u.id = po.usuario_id JOIN perfil_familia pf ON pf.perfil_id = po.id "
    "JOIN familia_olfativa f ON f.id = pf.familia_id WHERE u.email = %s ORDER BY pf.afinidade DESC",
    (CLIENTE['email'],))
evidencias['logs'] = banco(
    "SELECT id, status, qtd_incluidos, qtd_atualizados, mensagem_erro, iniciada_em FROM importacao_catalogo "
    "ORDER BY id DESC LIMIT 4")
evidencias['perfumes'] = banco(
    "SELECT m.nome AS marca, COUNT(*) AS perfumes, SUM(p.imagem_url IS NOT NULL) AS com_foto, "
    "MIN(p.ano) AS de, MAX(p.ano) AS ate, ROUND(AVG(p.avaliacao), 2) AS media FROM perfume p "
    "JOIN marca m ON m.id = p.marca_id GROUP BY m.nome ORDER BY perfumes DESC, m.nome")
evidencias['totais'] = banco(
    "SELECT (SELECT COUNT(*) FROM perfume) AS perfumes, (SELECT COUNT(*) FROM perfume_nota) AS notas, "
    "(SELECT COUNT(*) FROM perfume_acorde) AS acordes, (SELECT COUNT(*) FROM marca) AS marcas")

# desfaz a demonstração no admin: reativa a pergunta 11 e remove a pergunta criada (sem respostas)
banco("UPDATE pergunta SET ativa = 1 WHERE enunciado = 'Quais destes cheiros você NÃO gosta?'")
banco("DELETE a FROM alternativa a JOIN pergunta p ON p.id = a.pergunta_id WHERE p.enunciado LIKE 'No trabalho, você prefere%%'")
banco("DELETE FROM pergunta WHERE enunciado LIKE 'No trabalho, você prefere%%'")

(PASTA / 'evidencias.json').write_text(json.dumps(evidencias, ensure_ascii=False, indent=1, default=str), encoding='utf-8')
print('prints:', sorted(x.name for x in IMG.glob('*.png')))
