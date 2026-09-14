"""Monta os slides da apresentação da 1ª Sprint em HTML (16:9) e gera o PDF com o Chromium."""
import html
import json
import pathlib
import sys

from playwright.sync_api import sync_playwright

PASTA = pathlib.Path(__file__).parent
IMG = PASTA / 'img'
REPO = pathlib.Path.home() / 'Documents/pessoal/modular-perfumes'
SAIDA = pathlib.Path(sys.argv[1])
EV = json.loads((PASTA / 'evidencias.json').read_text(encoding='utf-8'))
e = html.escape


def img(caminho, estilo=''):
    return f'<img src="file://{caminho}" style="{estilo}">'


def tabela(linhas, colunas, rotulos=None, destaque=None):
    rotulos = rotulos or colunas
    cab = ''.join(f'<th>{e(r)}</th>' for r in rotulos)
    corpo = ''
    for l in linhas:
        cls = ' class="destaque"' if destaque and destaque(l) else ''
        corpo += f'<tr{cls}>' + ''.join(f'<td>{e(str(l[c]) if l[c] is not None else "NULL")}</td>' for c in colunas) + '</tr>'
    return f'<table class="dados"><thead><tr>{cab}</tr></thead><tbody>{corpo}</tbody></table>'


def slide(conteudo, secao='', numero=None, escuro=False):
    rodape = '' if escuro else (
        f'<div class="rodape"><span class="mono">MODULAR PERFUMES · 1ª SPRINT</span>'
        f'<span class="mono">{e(secao)}</span><span class="mono">{numero:02d}</span></div>')
    return f'<section class="slide{" escuro" if escuro else ""}">{conteudo}{rodape}</section>'


PERSONAS = [
    ('Cliente', ['Responde o questionário de perfil', 'Conversa com o consultor de IA'],
     ['Achar perfumes que combinem comigo', 'Comprar sem errar']),
    ('Lojista Parceiro', ['Cadastra a loja e as ofertas', 'Acompanha os cliques recebidos'],
     ['Receber clientes interessados', 'Ofertas sempre corretas']),
    ('Administrador', ['Monta o questionário de perfil', 'Importa o catálogo e aprova lojistas'],
     ['Catálogo completo e confiável', 'Plataforma segura e bem configurada']),
]
FEATURES = [
    ('Cliente', 'Conta e Perfil Olfativo', ['Recomendação genérica', 'Não sabe do que gosta'],
     ['Acesso grátis com login', 'Perfil olfativo salvo'], 'US1 · US2 · US3'),
    ('Lojista Parceiro', 'Cadastro da Loja', ['Loja sem visibilidade', 'Parceiro não verificado'],
     ['Loja aprovada', 'Dados sempre atuais'], 'próximas sprints'),
    ('Administrador', 'Questionário de Perfil', ['Perguntas genéricas', 'Perfil mal definido'],
     ['Perguntas editáveis', 'Pesos por família'], 'US4'),
    ('Administrador', 'Catálogo via API', ['Cadastro manual lento', 'Ficha incompleta'],
     ['Importação automática', 'Ficha revisada'], 'US5'),
]
US = [
    ('US1', 'Realizar o cadastro do cliente', 'Cliente', 'realizar o cadastro na plataforma, informando nome, e-mail e senha',
     'ter acesso grátis com login ao consultor olfativo',
     ('estou na página de cadastro', 'informo nome, e-mail válido e senha com 8+ caracteres e aciono "Criar conta"',
      'grava a conta com perfil "cliente", senha criptografada, e me leva ao questionário'),
     ('estou na página de cadastro', 'informo um e-mail que já possui conta', 'não cria a conta e exibe "Este e-mail já está cadastrado"')),
    ('US2', 'Realizar o login na plataforma', 'Cliente', 'realizar o login na plataforma com e-mail e senha',
     'acessar meu perfil olfativo salvo',
     ('tenho conta ativa e já concluí o questionário', 'informo e-mail e senha corretos e aciono "Entrar"',
      'abre a sessão e me leva à página inicial com o meu perfil olfativo'),
     ('estou na tela de login', 'informo e-mail ou senha incorretos', 'exibe "E-mail ou senha inválidos", sem dizer qual está errado')),
    ('US3', 'Responder o questionário de perfil olfativo', 'Cliente', 'responder o questionário de perfil olfativo',
     'ter o meu perfil olfativo salvo e receber recomendações que combinem comigo',
     ('estou autenticado e existe um questionário ativo', 'respondo as perguntas obrigatórias e aciono "Concluir"',
      'grava as respostas, gera o perfil olfativo e libera o consultor'),
     ('estou respondendo o questionário', 'aciono "Concluir" com pergunta obrigatória sem resposta',
      'não conclui e destaca as perguntas pendentes')),
    ('US4', 'Manter as perguntas do questionário', 'Administrador', 'cadastrar, consultar, alterar e excluir as perguntas do questionário',
     'ter perguntas editáveis que revelem o perfil olfativo de cada cliente',
     ('estou na gestão do questionário', 'informo enunciado, tipo e ao menos duas alternativas e aciono "Salvar"',
      'grava a pergunta como ativa e a exibe na lista, na ordem definida'),
     ('estou cadastrando ou alterando uma pergunta', 'deixo o enunciado vazio ou informo menos de duas alternativas',
      'não grava e exibe "Informe o enunciado e pelo menos duas alternativas"')),
    ('US5', 'Importar os perfumes pela API de catálogo', 'Administrador', 'importar os perfumes da API externa de catálogo',
     'ter a importação automática do catálogo, com foto, notas e acordes, sem cadastro manual',
     ('a chave de acesso da API está configurada', 'aciono "Importar catálogo"',
      'grava os perfumes com nome, marca, foto, notas e acordes e registra no log "concluída"'),
     ('a API está fora do ar ou recusa a chave', 'aciono "Importar catálogo"',
      'mantém o catálogo atual e registra no log "falhou" com a mensagem de erro')),
]


def cartao_us(u):
    cod, pbi, persona, posso, para, ca1, ca2 = u

    def ca(rotulo, tipo, c):
        return (f'<div class="ca"><div class="ca-rotulo"><span class="mono">{rotulo}</span><span>{tipo}</span></div>'
                f'<p><b>DADO QUE</b> {e(c[0])}<br><b>QUANDO</b> {e(c[1])}<br><b>ENTÃO</b> {e(c[2])}</p></div>')
    return (f'<div class="card us"><div class="us-topo"><span class="selo">{cod}</span><span class="mono pbi">PBI</span>'
            f'<h3>{e(pbi)}</h3></div>'
            f'<p class="historia"><b>COMO</b> {e(persona)} · <b>POSSO</b> {e(posso)} · <b>PARA</b> {e(para)}</p>'
            f'{ca("CA1", "fluxo principal", ca1)}{ca("CA2", "exceção", ca2)}</div>')


slides = []
n = 0


def add(conteudo, secao='', escuro=False):
    global n
    n += 1
    slides.append(slide(conteudo, secao, n, escuro))


# 1 — capa
add(f'''<div class="capa">
  <div class="chips"><span class="chip">EXPERIÊNCIA CRIATIVA · PUCPR</span><span class="chip">1ª SPRINT</span></div>
  <h1>Modular <span class="grad">Perfumes</span></h1>
  <p class="sub">Consultor olfativo com inteligência artificial</p>
  <div class="equipe"><div><span class="mono">EQUIPE</span><p>Enzo Koeche Castagna · Angelo · André Lagos</p></div>
  <div><span class="mono">ORIENTADORES</span><p>Profa. Cristina Verçosa P. B. de Souza · Prof. Giulio Domenico Bordin · Profa. Rosilene Fernandes</p></div></div>
</div>''', escuro=True)

# 2 — roteiro
add('''<div class="topo"><span class="chip">ROTEIRO</span><h2>O que vamos mostrar em 5 minutos</h2></div>
<div class="grade3">
  <div class="card passo"><span class="num mono">01</span><h3>Canvas PBB</h3><p>Três personas, uma feature por persona e os PBIs da 1ª Sprint.</p><span class="tempo mono">1 MIN</span></div>
  <div class="card passo"><span class="num mono">02</span><h3>User Stories</h3><p>Uma história por PBI, com critérios de aceite de fluxo principal e de exceção.</p><span class="tempo mono">1 MIN</span></div>
  <div class="card passo"><span class="num mono">03</span><h3>Implementação</h3><p>Cada PBI funcionando no site, com a base de dados preenchida e recuperada.</p><span class="tempo mono">3 MIN</span></div>
</div>
<p class="nota-rodape">O produto: plataforma gratuita, com login, em que o cliente responde um questionário de perfil olfativo e um agente de IA recomenda perfumes de um catálogo importado de API externa; a compra acontece nas lojas parceiras.</p>''', 'ROTEIRO')

# 3 — canvas
add(f'''<div class="topo"><span class="chip">[1] CANVAS PBB</span><h2>Product Backlog Building</h2></div>
<div class="figura">{img(REPO / "entregas/pbb/Modular_Perfumes_Canvas_PBB_Sprint1.png", "width:100%;border-radius:12px;border:1px solid #e6e8ec")}</div>
<p class="legenda">PBIs com borda vermelha = 1ª Sprint.</p>''', '[1] CANVAS PBB')

# 4 — personas
cards = ''
for nome, faz, espera in PERSONAS:
    cards += (f'<div class="card persona"><h3>{e(nome)}</h3><span class="mono rot">O QUE FAZ</span>'
              + ''.join(f'<p class="item faz">{e(x)}</p>' for x in faz)
              + '<span class="mono rot">O QUE ESPERA</span>' + ''.join(f'<p class="item espera">{e(x)}</p>' for x in espera)
              + '</div>')
add(f'''<div class="topo"><span class="chip">[1] CANVAS PBB</span><h2>Três personas, com papéis diferentes</h2></div>
<div class="grade3">{cards}</div>''', '[1] CANVAS PBB')

# 5 — features
cards = ''
for persona, nome, probs, bens, onde in FEATURES:
    cards += (f'<div class="card feature"><span class="mono rot">{e(persona.upper())}</span><h3>{e(nome)}</h3>'
              '<div class="duas"><div><span class="mono rot">PROBLEMAS / NECESSIDADES</span>'
              + ''.join(f'<p class="item prob">{e(x)}</p>' for x in probs)
              + '</div><div><span class="mono rot">RESULTADOS / BENEFÍCIOS</span>'
              + ''.join(f'<p class="item ben">{e(x)}</p>' for x in bens)
              + f'</div></div><span class="onde mono">{e(onde)}</span></div>')
add(f'''<div class="topo"><span class="chip">[1] CANVAS PBB</span><h2>Uma feature para cada persona</h2></div>
<div class="grade4">{cards}</div>''', '[1] CANVAS PBB')

# 6 — PBIs da sprint
linhas = ''.join(f'<tr><td><span class="selo">{u[0]}</span></td><td><b>{e(u[1])}</b></td><td>{e(u[2])}</td><td>{e(f)}</td></tr>'
                 for u, f in zip(US, ['Conta e Perfil Olfativo'] * 3 + ['Questionário de Perfil', 'Catálogo via API']))
add(f'''<div class="topo"><span class="chip">[1] CANVAS PBB</span><h2>PBIs implementados na 1ª Sprint</h2></div>
<table class="dados grande"><thead><tr><th></th><th>PBI</th><th>Persona</th><th>Feature</th></tr></thead><tbody>{linhas}</tbody></table>
<p class="nota-rodape">Objetivo da sprint: o cliente cria a conta, faz login e responde o questionário; o administrador monta o questionário e importa o catálogo.</p>''', '[1] CANVAS PBB')

# 7 e 8 — user stories
add(f'''<div class="topo"><span class="chip">[2] USER STORIES</span><h2>Cliente</h2></div>
<div class="grade3">{"".join(cartao_us(u) for u in US[:3])}</div>''', '[2] USER STORIES')
add(f'''<div class="topo"><span class="chip">[2] USER STORIES</span><h2>Administrador</h2></div>
<div class="grade2">{"".join(cartao_us(u) for u in US[3:])}</div>''', '[2] USER STORIES')

# 9 — implementação: stack e modelo
add(f'''<div class="topo"><span class="chip">[3] IMPLEMENTAÇÃO</span><h2>Como foi construído</h2></div>
<div class="lado">
  <div class="card">
    <span class="mono rot">TECNOLOGIAS</span>
    <p class="item">Python + Flask (páginas HTML com Jinja)</p><p class="item">HTML, CSS e Bootstrap 5</p>
    <p class="item">MySQL 8 com SQL escrito à mão</p><p class="item">API externa de catálogo: Fragella</p>
    <span class="mono rot">QUALIDADE</span>
    <p class="item">27 testes automáticos: um por critério de aceite</p><p class="item">Senha com hash, CSRF e acesso checado no servidor</p>
    <p class="item">Código versionado no GitHub; tarefas no Trello</p>
  </div>
  <div class="card figura-card"><span class="mono rot">MODELO LÓGICO DA 1ª SPRINT (17 TABELAS)</span>
    {img(REPO / "entregas/der/Modular_Perfumes_DER_Logico_Sprint1.png", "width:100%;margin-top:10px")}</div>
</div>''', '[3] IMPLEMENTAÇÃO')

# 10 — US1
u = [x for x in EV['usuario'] if x['email'] == 'marina.demo@exemplo.com']
add(f'''<div class="topo"><span class="chip">[3] US1 · CADASTRO</span><h2>Cadastro do cliente</h2></div>
<div class="grade3 prints">
  <div class="print"><span class="mono rot">FORMULÁRIO</span>{img(IMG / "us1_formulario.png")}</div>
  <div class="print"><span class="mono rot ok">CA1 · CONTA CRIADA → QUESTIONÁRIO</span>{img(IMG / "us1_ca1.png")}</div>
  <div class="print"><span class="mono rot erro">CA2 · E-MAIL JÁ CADASTRADO</span>{img(IMG / "us1_ca2.png")}</div>
</div>
<div class="banco"><span class="mono rot">BANCO · SELECT id, nome, email, perfil, senha_hash FROM usuario</span>
{tabela(u, ["id", "nome", "email", "perfil", "senha_hash", "criado_em"], ["id", "nome", "email", "perfil", "senha_hash (início)", "criado_em"])}</div>''', '[3] IMPLEMENTAÇÃO')

# 11 — US2
add(f'''<div class="topo"><span class="chip">[3] US2 · LOGIN</span><h2>Login na plataforma</h2></div>
<div class="grade2 prints">
  <div class="print"><span class="mono rot erro">CA2 · E-MAIL OU SENHA INVÁLIDOS</span>{img(IMG / "us2_ca2.png", "max-height:560px;width:auto")}</div>
  <div class="print"><span class="mono rot ok">CA1 · SESSÃO ABERTA, PERFIL DO CLIENTE</span>{img(IMG / "us2_ca1.png")}
    <p class="obs">Sem questionário concluído, o login leva direto ao questionário (CA3). Cada tela checa o perfil de acesso no servidor.</p></div>
</div>''', '[3] IMPLEMENTAÇÃO')

# 12 — US3
parcial = EV['resposta_parcial'][0]
r = EV['resposta'][0]
add(f'''<div class="topo"><span class="chip">[3] US3 · QUESTIONÁRIO</span><h2>Questionário de perfil olfativo</h2></div>
<div class="lado">
  <div class="print"><span class="mono rot erro">CA2 · OBRIGATÓRIAS PENDENTES FICAM DESTACADAS</span>{img(IMG / "us3_ca2.png")}</div>
  <div class="banco coluna">
    <div class="print"><span class="mono rot ok">CA1 · PERFIL GERADO</span>{img(IMG / "us3_ca1.png")}</div>
    <span class="mono rot">BANCO · RESPOSTA DA MARINA</span>
    {tabela([{"momento": "após CA2", "perguntas": parcial["perguntas_respondidas"], "concluida_em": parcial["concluida_em"]},
             {"momento": "após CA1", "perguntas": r["perguntas_respondidas"], "concluida_em": r["concluida_em"]}],
            ["momento", "perguntas", "concluida_em"], ["momento", "perguntas respondidas", "concluida_em"])}
    <span class="mono rot">BANCO · perfil_familia (afinidade = soma dos pesos)</span>
    {tabela(EV["perfil"][:4], ["familia", "afinidade"])}
  </div>
</div>''', '[3] IMPLEMENTAÇÃO')

# 13 — US4
pergunta_desativada = next(q for q in EV["perguntas"] if q["ativa"] == 0)
pergunta_nova = next(q for q in EV["perguntas"] if q["respostas"] == 0)
add(f'''<div class="topo"><span class="chip">[3] US4 · PERGUNTAS</span><h2>Manter as perguntas do questionário</h2></div>
<div class="lado">
  <div class="print"><span class="mono rot ok">CA1 · PERGUNTA CADASTRADA NA LISTA · CA3 · RESPONDIDA É DESATIVADA</span>{img(IMG / "us4_ca3.png")}</div>
  <div class="banco coluna">
    <div class="print"><span class="mono rot erro">CA2 · MENOS DE DUAS ALTERNATIVAS</span>{img(IMG / "us4_ca2.png")}</div>
    <span class="mono rot">BANCO · pergunta (trecho)</span>
    {tabela(EV["perguntas"], ["id", "enunciado", "ativa", "respostas"], destaque=lambda l: l["id"] >= 11)}
    <p class="obs">A pergunta {pergunta_desativada["id"]} tinha resposta: foi desativada, não apagada. A {pergunta_nova["id"]} foi criada pelo administrador na tela (CA1).</p>
  </div>
</div>''', '[3] IMPLEMENTAÇÃO')

# 14 — US5
logs = [{**l, 'mensagem_erro': l['mensagem_erro'] or ''} for l in EV['logs']]
add(f'''<div class="topo"><span class="chip">[3] US5 · CATÁLOGO</span><h2>Importar os perfumes pela API</h2></div>
<div class="lado">
  <div class="print grande-print"><span class="mono rot ok">CA1 · PERFUMES IMPORTADOS COM FOTO, NOTAS E ACORDES</span>{img(IMG / "us5_catalogo.png")}</div>
  <div class="banco coluna">
    <span class="mono rot">BANCO · importacao_catalogo (log)</span>
    {tabela(logs, ["id", "status", "qtd_incluidos", "qtd_atualizados", "mensagem_erro"], ["id", "status", "incluídos", "atualizados", "mensagem"], destaque=lambda l: l["status"] == "FALHOU")}
    <p class="obs"><b>CA2</b>: sem chave, o log registra "falhou" e o catálogo é mantido. <b>CA3</b>: reimportar atualiza pelo id da API, sem duplicar (0 incluídos, 50 atualizados).</p>
    <span class="mono rot">BANCO · perfumes por marca</span>
    {tabela(EV["perfumes"], ["marca", "perfumes", "com_foto", "de", "ate", "media"], ["marca", "perfumes", "com foto", "de", "até", "nota média"])}
  </div>
</div>''', '[3] IMPLEMENTAÇÃO')

# 15 — base de dados
t = EV['totais'][0]
add(f'''<div class="topo"><span class="chip">[3] BASE DE DADOS</span><h2>Preenchida pelo site e recuperada nas telas</h2></div>
<div class="grade4 numeros">
  <div class="card"><span class="mono rot">PERFUMES</span><p class="grande">{t["perfumes"]}</p><p class="obs">vindos da API, com foto</p></div>
  <div class="card"><span class="mono rot">NOTAS OLFATIVAS</span><p class="grande">{t["notas"]}</p><p class="obs">pirâmide saída/corpo/fundo</p></div>
  <div class="card"><span class="mono rot">ACORDES</span><p class="grande">{t["acordes"]}</p><p class="obs">com intensidade</p></div>
  <div class="card"><span class="mono rot">MARCAS</span><p class="grande">{t["marcas"]}</p><p class="obs">criadas na importação</p></div>
</div>
<div class="grade2">
  <div class="card"><span class="mono rot">GRAVAÇÃO (O QUE O SITE FAZ)</span>
    <pre>INSERT INTO usuario (nome, email, senha_hash, perfil) ...
INSERT INTO resposta_item (resposta_id, pergunta_id, alternativa_id) ...
INSERT INTO perfil_familia (perfil_id, familia_id, afinidade)
  SELECT ..., SUM(ap.peso) FROM resposta_item ri
  JOIN alternativa_peso ap ON ... GROUP BY ap.familia_id</pre></div>
  <div class="card"><span class="mono rot">RECUPERAÇÃO (O QUE A TELA MOSTRA)</span>
    <pre>SELECT f.nome, pf.afinidade FROM perfil_familia pf
JOIN familia_olfativa f ON f.id = pf.familia_id
WHERE pf.perfil_id = %s ORDER BY pf.afinidade DESC;

SELECT * FROM importacao_catalogo ORDER BY id DESC;</pre></div>
</div>
<p class="nota-rodape">Script do banco e consultas de verificação no GitHub: entregas/sql/.</p>''', '[3] IMPLEMENTAÇÃO')

# 16 — encerramento
add('''<div class="capa fim">
  <div class="chips"><span class="chip">1ª SPRINT ENTREGUE</span></div>
  <h1>Obrigado!</h1>
  <p class="sub">Próxima sprint: o <span class="grad">consultor de IA</span> conversa com o cliente e recomenda perfumes do catálogo, e a vitrine mostra os melhores do ano e de cada década.</p>
  <div class="equipe"><div><span class="mono">GITHUB</span><p>github.com/EnzoKoeche/modular-perfumes</p></div>
  <div><span class="mono">TRELLO</span><p>trello.com/b/PN46fipf</p></div></div>
</div>''', escuro=True)

CSS = '''
@page { size: 1920px 1080px; margin: 0; }
* { box-sizing: border-box; }
body { margin: 0; font-family: Inter, system-ui, sans-serif; color: #0c0d12; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.mono { font-family: 'JetBrains Mono', ui-monospace, monospace; letter-spacing: .03em; }
.slide { width: 1920px; height: 1080px; padding: 72px 96px 90px; position: relative; overflow: hidden; background: #f6f7f9; page-break-after: always; }
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
.topo { margin-bottom: 36px; }
.topo h2 { font-size: 58px; letter-spacing: -.03em; margin: 14px 0 0; }
.card { background: #fff; border: 1px solid #e6e8ec; border-radius: 22px; padding: 30px 34px; box-shadow: 0 1px 2px rgba(16,24,40,.04); }
.grade2 { display: grid; grid-template-columns: 1fr 1fr; gap: 28px; }
.grade3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 28px; }
.grade4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; }
.lado { display: grid; grid-template-columns: 1.25fr 1fr; gap: 32px; align-items: start; }
h3 { font-size: 30px; margin: 6px 0 14px; letter-spacing: -.01em; }
.rot { display: block; font-size: 14px; color: #667085; margin: 14px 0 8px; font-weight: 600; }
.rot.ok { color: #047857; } .rot.erro { color: #b42318; }
.item { font-size: 23px; margin: 8px 0; padding: 12px 16px; border-radius: 12px; background: #f6f7f9; }
.item.faz, .item.prob { background: #1f2027; color: #fff; }
.item.espera, .item.ben { background: linear-gradient(135deg, #7c3aed, #06b6d4); color: #fff; }
.passo { position: relative; min-height: 360px; }
.passo .num { font-size: 22px; color: #7c3aed; font-weight: 600; }
.passo h3 { font-size: 40px; margin-top: 18px; } .passo p { font-size: 26px; color: #475467; line-height: 1.45; }
.tempo { position: absolute; bottom: 28px; left: 34px; font-size: 18px; color: #06b6d4; font-weight: 600; }
.nota-rodape { font-size: 24px; color: #475467; margin-top: 32px; line-height: 1.45; max-width: 1600px; }
.figura { text-align: center; } .legenda { color: #b42318; font-size: 22px; margin-top: 10px; font-weight: 600; }
.feature h3 { font-size: 28px; } .feature .duas { display: grid; grid-template-columns: 1fr; gap: 0; }
.feature .item { font-size: 20px; padding: 10px 14px; }
.onde { display: inline-block; margin-top: 16px; font-size: 15px; color: #7c3aed; font-weight: 600; }
.selo { display: inline-block; padding: 4px 12px; border-radius: 8px; background: #0c0d12; color: #fff; font: 700 18px 'JetBrains Mono', monospace; }
.pbi { margin-left: 8px; font-size: 14px; color: #7c3aed; font-weight: 700; }
.us h3 { font-size: 26px; margin: 12px 0 10px; }
.historia { font-size: 19px; line-height: 1.45; color: #344054; margin: 0 0 12px; }
.ca { border-top: 1px solid #e6e8ec; padding-top: 12px; margin-top: 12px; }
.ca-rotulo { display: flex; gap: 10px; align-items: center; font-size: 15px; color: #667085; }
.ca-rotulo .mono { font-weight: 700; color: #0c0d12; }
.ca p { font-size: 18px; line-height: 1.5; margin: 6px 0 0; color: #344054; }
.ca b { font-family: 'JetBrains Mono', monospace; font-size: 14px; color: #7c3aed; }
.grade2 .us .historia { font-size: 21px; } .grade2 .us .ca p { font-size: 20px; }
table.dados { width: 100%; border-collapse: collapse; background: #fff; border: 1px solid #e6e8ec; border-radius: 14px; overflow: hidden; font-size: 17px; }
table.dados th { text-align: left; font: 600 14px 'JetBrains Mono', monospace; color: #667085; background: #f9fafb; padding: 10px 12px; border-bottom: 1px solid #e6e8ec; }
table.dados td { padding: 9px 12px; border-bottom: 1px solid #f0f1f3; }
table.dados tr.destaque td { background: #f3efff; }
table.dados.grande { font-size: 28px; } table.dados.grande td { padding: 22px 18px; } table.dados.grande th { font-size: 16px; padding: 14px 18px; }
.prints .print, .print { background: #fff; border: 1px solid #e6e8ec; border-radius: 18px; padding: 12px 14px 16px; }
.print img { width: 100%; border-radius: 10px; border: 1px solid #eef0f3; display: block; }
.print .rot { margin-top: 4px; }
.grande-print img { max-height: 800px; object-fit: cover; object-position: top; }
.banco { margin-top: 24px; } .banco.coluna { margin-top: 0; }
.obs { font-size: 18px; color: #475467; line-height: 1.45; margin: 10px 0; }
.trio { display: grid; grid-template-columns: 1fr 1fr 0.9fr; gap: 26px; align-items: start; }
.trio .print img { max-height: 780px; object-fit: cover; object-position: top; }
.lado > .print img { max-height: 820px; object-fit: cover; object-position: top; }
.banco.coluna > .print { margin-bottom: 18px; }
.banco.coluna > .print img { max-height: 330px; object-fit: cover; object-position: top; }
.grade3.prints .print img { height: 470px; object-fit: cover; object-position: top; }
.banco table.dados { font-size: 16px; }
.numeros .grande { font-size: 76px; font-weight: 700; margin: 4px 0; letter-spacing: -.03em; }
pre { font-size: 18px; line-height: 1.5; background: #0b0b12; color: #e2e8f0; padding: 20px 22px; border-radius: 14px; margin: 8px 0 0; white-space: pre-wrap; }
.rodape { position: absolute; left: 96px; right: 96px; bottom: 34px; display: flex; justify-content: space-between; font-size: 14px; color: #98a2b3; }
.figura-card img { border-radius: 10px; }
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
    # miniaturas para conferência
    for i in range(len(slides)):
        pg.set_viewport_size({'width': 1920, 'height': 1080})
        pg.evaluate(f'window.scrollTo(0, {i * 1080})')
        pg.screenshot(path=str(PASTA / f'slide_{i + 1:02d}.png'))
    nav.close()
print('slides:', len(slides), '->', SAIDA)
