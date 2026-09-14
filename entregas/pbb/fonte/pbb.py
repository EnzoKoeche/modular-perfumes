"""Canvas PBB (Product Backlog Building) do Modular Perfumes — versão 3 (três personas)."""
import sys

from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
HELV = '/System/Library/Fonts/Helvetica.ttc'

# ------------------------------------------------------------------ conteúdo
PRODUTO = 'Modular Perfumes'

PROBLEMAS = [
    'Cliente não sabe qual perfume combina com ele',
    'Não entende notas, acordes e famílias olfativas',
    'Compra às cegas pela internet, sem sentir o cheiro',
    'Informação de perfume espalhada em vários sites',
    'Recomendação genérica, igual para todo mundo',
    'Arrependimento e devolução depois da compra',
    'Loja não chega a quem já quer comprar',
    'Cadastrar catálogo à mão é lento e incompleto',
]
EXPECTATIVAS = [
    'Recomendação a partir do meu perfil olfativo',
    'Linguagem simples, sem jargão de perfumaria',
    'Ficha com foto, notas e acordes de cada perfume',
    'Juntar os que gostei e ir direto à loja',
    'Acesso gratuito com login e senha',
    'Consultor de IA disponível a qualquer hora',
    'Lojista recebe cliente já interessado',
    'Catálogo completo vindo de API externa',
]

# persona: nome, (faz, faz), (espera, espera), features, pbis
# feature: (título, (problema, problema), (benefício, benefício))
# pbi: (texto, sprint1?)
PERSONAS = [
    dict(
        nome='Cliente',
        faz=('Responde o questionário de perfil', 'Conversa com o consultor de IA'),
        espera=('Achar perfumes que combinem comigo', 'Comprar sem errar'),
        features=[
            ('Conta e Perfil Olfativo', ('Recomendação genérica', 'Não sabe do que gosta'),
             ('Acesso grátis com login', 'Perfil olfativo salvo')),
            ('Consultor Olfativo por IA', ('Não entende as notas', 'Compra às cegas'),
             ('Recomendação explicada', 'Linguagem simples')),
            ('Sacola e Compra nas Lojas', ('Informação espalhada', 'Muitas lojas e abas'),
             ('Favoritos num só lugar', 'Vai direto à loja')),
        ],
        pbis=[
            ('Realizar o cadastro do cliente', True), ('Realizar o login na plataforma', True),
            ('Responder o questionário de perfil olfativo', True), ('Manter os dados da conta do cliente', False),
            ('Conversar com o agente consultor', False), ('Receber as recomendações personalizadas', False),
            ('Consultar a ficha do perfume', False), ('Avaliar a recomendação recebida', False),
            ('Adicionar e remover perfumes da sacola', False), ('Finalizar a sacola abrindo as lojas', False),
        ],
    ),
    dict(
        nome='Lojista Parceiro',
        faz=('Cadastra a loja e as ofertas', 'Acompanha os cliques recebidos'),
        espera=('Receber clientes interessados', 'Ofertas sempre corretas'),
        features=[
            ('Cadastro da Loja', ('Loja sem visibilidade', 'Parceiro não verificado'),
             ('Loja aprovada', 'Dados sempre atuais')),
            ('Gestão de Ofertas', ('Link quebrado', 'Preço desatualizado'),
             ('Oferta por perfume', 'Pausar e reativar')),
            ('Relatório de Cliques', ('Não mede o retorno', 'Público errado'),
             ('Cliques por oferta', 'Cliente já interessado')),
        ],
        pbis=[
            ('Solicitar o cadastro da loja parceira', False), ('Manter os dados da loja', False),
            ('Buscar perfume do catálogo para ofertar', False), ('Manter as ofertas da loja', False),
            ('Pausar ou reativar uma oferta', False), ('Consultar os cliques por oferta', False),
        ],
    ),
    dict(
        nome='Administrador',
        faz=('Monta o questionário de perfil', 'Importa o catálogo e aprova lojistas'),
        espera=('Catálogo completo e confiável', 'Plataforma segura e bem configurada'),
        features=[
            ('Questionário de Perfil', ('Perguntas genéricas', 'Perfil mal definido'),
             ('Perguntas editáveis', 'Pesos por família')),
            ('Catálogo via API', ('Cadastro manual lento', 'Ficha incompleta'),
             ('Importação automática', 'Ficha revisada')),
            ('Gestão da Plataforma', ('Lojista falso', 'IA sai do assunto'),
             ('Lojas aprovadas', 'Regras do consultor')),
        ],
        pbis=[
            ('Manter as perguntas do questionário', True), ('Importar os perfumes pela API de catálogo', True),
            ('Manter as alternativas e os pesos', False), ('Consultar o log de importações', False),
            ('Agendar a sincronização do catálogo', False), ('Revisar a ficha de perfume importada', False),
            ('Ocultar ou reexibir perfume', False), ('Aprovar ou bloquear loja parceira', False),
            ('Manter os usuários da plataforma', False), ('Manter as diretrizes do agente', False),
            ('Consultar as avaliações das recomendações', False), ('Consultar os indicadores de uso', False),
        ],
    ),
]

EQUIPE = 'Equipe: Enzo Koeche Castagna • Angelo • André Lagos — Engenharia de Software / PUCPR'

# ------------------------------------------------------------------ estilo
PRETO, CINZA_ESC, LARANJA, VERMELHO = '#111111', '#2E2E2E', '#EF7B22', '#D32F2F'
CINZA_BORDA, CINZA_TXT = '#8A8A8A', '#555555'
W = 6000
M = 90


def font(size, bold=False):
    return ImageFont.truetype(HELV, size, index=1 if bold else 0)


def wrap(draw, text, fnt, maxw):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if draw.textlength(t, font=fnt) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_box(draw, box, text, size, bold=False, fill='white', max_size=None, pad=18, spacing=1.18):
    x0, y0, x1, y1 = box
    s = max_size or size
    while s >= 14:
        fnt = font(s, bold)
        lines = wrap(draw, text, fnt, (x1 - x0) - 2 * pad)
        lh = s * spacing
        too_wide = any(draw.textlength(l, font=fnt) > (x1 - x0) - 2 * pad for l in lines)
        if len(lines) * lh <= (y1 - y0) - 2 * pad * 0.6 and not too_wide:
            break
        s -= 2
    total = len(lines) * lh
    y = y0 + ((y1 - y0) - total) / 2 + (lh - s) / 2 - s * 0.08
    for l in lines:
        tw = draw.textlength(l, font=fnt)
        draw.text((x0 + ((x1 - x0) - tw) / 2, y), l, font=fnt, fill=fill)
        y += lh


def rbox(draw, box, fill, outline=None, width=0, r=10, shadow=True):
    if shadow:
        x0, y0, x1, y1 = box
        draw.rounded_rectangle((x0 + 5, y0 + 6, x1 + 5, y1 + 6), r, fill='#D9D9D9')
    draw.rounded_rectangle(box, r, fill=fill, outline=outline, width=width)


def dashed_v(draw, x, y0, y1, color='#BBBBBB', dash=14, gap=12, w=3):
    y = y0
    while y < y1:
        draw.line((x, y, x, min(y + dash, y1)), fill=color, width=w)
        y += dash + gap


def dashed_rect(draw, box, color, dash=26, gap=16, w=5):
    x0, y0, x1, y1 = box
    for a, b, c, d in ((x0, y0, x1, y0), (x0, y1, x1, y1)):
        x = a
        while x < c:
            draw.line((x, b, min(x + dash, c), d), fill=color, width=w)
            x += dash + gap
    for a, b, c, d in ((x0, y0, x0, y1), (x1, y0, x1, y1)):
        y = b
        while y < d:
            draw.line((a, y, c, min(y + dash, d)), fill=color, width=w)
            y += dash + gap


# ------------------------------------------------------------------ layout
N = len(PERSONAS)
LEFT_W = 1180
FRAME_T = 330
SEC_LABEL = 78

MINI_H, GAP = 132, 18
PBI_POR_LINHA = 3
BIG_W = 0  # calculado
PERS_H = MINI_H * 2 + GAP
FEAT_BLOCK_H = MINI_H * 2 + GAP
FEAT_GAP = 34
PBI_H, PBI_GAP = 160, 24
max_feats = max(len(p['features']) for p in PERSONAS)
max_pbi_rows = max(-(-len(p['pbis']) // PBI_POR_LINHA) for p in PERSONAS)

right_x0 = M + LEFT_W
right_x1 = W - M
col_w = (right_x1 - right_x0) / N
inner_pad = 34
MINI_W = round(col_w * 0.25)
BIG_W = col_w - 2 * inner_pad - 2 * MINI_W - 2 * GAP

pers_y0 = FRAME_T
pers_h = SEC_LABEL + PERS_H + 50
feat_y0 = pers_y0 + pers_h
feat_h = SEC_LABEL + max_feats * FEAT_BLOCK_H + (max_feats - 1) * FEAT_GAP + 50
pbi_y0 = feat_y0 + feat_h
legend_h = 120
pbi_h = SEC_LABEL + max_pbi_rows * PBI_H + (max_pbi_rows - 1) * PBI_GAP + 40 + legend_h + 40
FRAME_B = pbi_y0 + pbi_h
H = FRAME_B + 130

img = Image.new('RGB', (W, H), 'white')
d = ImageDraw.Draw(img)

# cabeçalho
d.text((M, 80), 'PRODUCT BACKLOG BUILDING', font=font(118, True), fill=PRETO)
tw = d.textlength('PBB Canvas', font=font(60, True))
title_w = d.textlength('PRODUCT BACKLOG BUILDING', font=font(118, True))
d.text((M + title_w - tw, 212), 'PBB Canvas', font=font(60, True), fill='#9A9A9A')
pn_x0 = M + title_w + 90
d.rectangle((pn_x0, 70, W - M, 280), outline=PRETO, width=8)
d.text((pn_x0 + 40, 100), 'PRODUCT NAME:', font=font(40, True), fill=PRETO)
d.rectangle((pn_x0 + 420, 100, W - M - 40, 250), fill=CINZA_ESC)
text_box(d, (pn_x0 + 420, 100, W - M - 40, 250), PRODUTO, 92, True)

# moldura
d.rectangle((M, FRAME_T, W - M, FRAME_B), outline=PRETO, width=10)
d.line((right_x0, FRAME_T, right_x0, FRAME_B), fill=PRETO, width=10)
d.line((right_x0, feat_y0, W - M, feat_y0), fill=PRETO, width=6)
d.line((right_x0, pbi_y0, W - M, pbi_y0), fill=PRETO, width=6)
d.line((M, pbi_y0, right_x0, pbi_y0), fill=PRETO, width=10)

# painel esquerdo: problemas e expectativas
label_w = 110


def vertical_label(text, box):
    x0, y0, x1, y1 = box
    fnt = font(46, True)
    tw = int(d.textlength(text, font=fnt)) + 20
    tmp = Image.new('RGBA', (tw, 70), (255, 255, 255, 0))
    ImageDraw.Draw(tmp).text((10, 8), ' '.join(text), font=fnt, fill=PRETO) if False else \
        ImageDraw.Draw(tmp).text((10, 8), text, font=fnt, fill=PRETO)
    rot = tmp.rotate(90, expand=True)
    img.paste(rot, (int(x0 + (x1 - x0 - rot.width) / 2), int(y0 + (y1 - y0 - rot.height) / 2)), rot)


def grid_left(items, y0, y1, fill, label):
    d.line((M + label_w, y0, M + label_w, y1), fill=PRETO, width=6)
    vertical_label(label, (M, y0, M + label_w, y1))
    gx0, gx1 = M + label_w + 40, right_x0 - 40
    gy0, gy1 = y0 + 40, y1 - 40
    rows = (len(items) + 1) // 2
    cw = (gx1 - gx0 - 30) / 2
    ch = (gy1 - gy0 - (rows - 1) * 30) / rows
    for i, it in enumerate(items):
        r, c = divmod(i, 2)
        bx = gx0 + c * (cw + 30)
        by = gy0 + r * (ch + 30)
        box = (bx, by, bx + cw, by + ch)
        rbox(d, box, fill)
        text_box(d, box, it, 44, False, max_size=44)


grid_left(PROBLEMAS, FRAME_T, pbi_y0, CINZA_ESC, 'PROBLEMS')
grid_left(EXPECTATIVAS, pbi_y0, FRAME_B, LARANJA, 'EXPECTATIONS')

# rótulos das seções da direita
for y, t in ((pers_y0, 'PERSONAS'), (feat_y0, 'FEATURES'), (pbi_y0, 'PBI: PRODUCT BACKLOG ITENS')):
    d.text((right_x0 + 40, y + 24), t, font=font(44, True), fill=PRETO)

for i, p in enumerate(PERSONAS):
    cx0 = right_x0 + i * col_w
    if i > 0:
        dashed_v(d, cx0, FRAME_T + 20, FRAME_B - legend_h - 60)
    x = cx0 + inner_pad
    # personas
    y = pers_y0 + SEC_LABEL + 10
    for k, t in enumerate(p['faz']):
        b = (x, y + k * (MINI_H + GAP), x + MINI_W, y + k * (MINI_H + GAP) + MINI_H)
        rbox(d, b, LARANJA, shadow=False)
        text_box(d, b, t, 34, max_size=34, pad=12)
    b = (x + MINI_W + GAP, y, x + MINI_W + GAP + BIG_W, y + PERS_H)
    rbox(d, b, CINZA_ESC)
    text_box(d, b, p['nome'], 64, True, max_size=64)
    for k, t in enumerate(p['espera']):
        bx = x + MINI_W + GAP + BIG_W + GAP
        b = (bx, y + k * (MINI_H + GAP), bx + MINI_W, y + k * (MINI_H + GAP) + MINI_H)
        rbox(d, b, LARANJA, shadow=False)
        text_box(d, b, t, 34, max_size=34, pad=12)
    # features
    y = feat_y0 + SEC_LABEL + 10
    for f, (titulo, probs, bens) in enumerate(p['features']):
        fy = y + f * (FEAT_BLOCK_H + FEAT_GAP)
        for k, t in enumerate(probs):
            b = (x, fy + k * (MINI_H + GAP), x + MINI_W, fy + k * (MINI_H + GAP) + MINI_H)
            rbox(d, b, CINZA_ESC, shadow=False)
            text_box(d, b, t, 34, max_size=34, pad=12)
        b = (x + MINI_W + GAP, fy, x + MINI_W + GAP + BIG_W, fy + FEAT_BLOCK_H)
        rbox(d, b, LARANJA)
        text_box(d, b, titulo, 54, True, max_size=54)
        for k, t in enumerate(bens):
            bx = x + MINI_W + GAP + BIG_W + GAP
            b = (bx, fy + k * (MINI_H + GAP), bx + MINI_W, fy + k * (MINI_H + GAP) + MINI_H)
            rbox(d, b, CINZA_ESC, shadow=False)
            text_box(d, b, t, 34, max_size=34, pad=12)
    # PBIs
    y = pbi_y0 + SEC_LABEL + 20
    pw = (col_w - 2 * inner_pad - (PBI_POR_LINHA - 1) * PBI_GAP) / PBI_POR_LINHA
    for k, (t, s1) in enumerate(p['pbis']):
        r, c = divmod(k, PBI_POR_LINHA)
        bx = x + c * (pw + PBI_GAP)
        by = y + r * (PBI_H + PBI_GAP)
        b = (bx, by, bx + pw, by + PBI_H)
        if s1:
            d.rounded_rectangle((bx - 9, by - 9, bx + pw + 9, by + PBI_H + 9), 12, outline=VERMELHO, width=9)
        rbox(d, b, 'white', outline=CINZA_BORDA, width=3, r=6)
        text_box(d, b, t, 38, fill=PRETO, max_size=38, pad=20)

# legenda da Sprint 1
sprint = [t for p in PERSONAS for (t, s1) in p['pbis'] if s1]
lb = (right_x0 + 40, FRAME_B - legend_h - 40, W - M - 40, FRAME_B - 40)
dashed_rect(d, lb, VERMELHO)
text_box(d, lb, 'SPRINT 1 — PBIs destacados em vermelho: ' + ' • '.join(sprint), 40, True, fill=VERMELHO,
         max_size=40)

# rodapé
d.text((M, FRAME_B + 40), EQUIPE, font=font(36), fill=CINZA_TXT)
cred1 = 'PRODUCT BACKLOG BUILDING (PBB Canvas) by '
cred2 = 'Fábio Aguiar (@fabyogr)'
w1 = d.textlength(cred1, font=font(36))
w2 = d.textlength(cred2, font=font(36, True))
d.text((W - M - w1 - w2, FRAME_B + 40), cred1, font=font(36), fill=CINZA_TXT)
d.text((W - M - w2, FRAME_B + 40), cred2, font=font(36, True), fill=PRETO)

img.save(OUT, dpi=(300, 300))
print(OUT, img.size)
