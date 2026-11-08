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



def linha_pbi(n, nome, persona, sprint):
    cls = {1: 's1', 2: 's2'}.get(sprint, 'sx')
    estado = 'entregue' if sprint <= 2 else 'planejado'
    return (f'<tr class="{cls}"><td class="mono">{n:02d}</td><td>{e(nome)}</td><td>{e(persona)}</td>'
            f'<td><span class="tag {cls}">Sprint {sprint}</span></td><td class="mono">{estado}</td></tr>')

TESTES_POR_CA.insert(0, ('US1', 'test_us1_ca1_cadastro_grava_cliente_com_hash_e_leva_ao_questionario',
                         'test_us1_ca2_email_ja_cadastrado', 'test_us1_ca3_senhas_que_nao_conferem · …_data_de_nascimento_no_futuro'))

# roteiro da demonstração ao vivo por história: (passos, consulta ao banco)
DEMO = {
    'US1': (['Sair da conta e abrir "Criar conta"',
             'CA3: data 01/01/2999 e senhas diferentes → o formulário não é enviado',
             'CA1: corrigir e criar a conta → cai no questionário',
             'CA2: tentar o mesmo e-mail de novo → "Este e-mail já está cadastrado"'],
            "SELECT nome, email, data_nascimento, perfil\nFROM usuario ORDER BY id DESC LIMIT 1;"),
    'US6': (['Entrar como administrador → Questionário → botão "Pesos"',
             'CA1: mudar um peso e "Salvar pesos" → "Pesos atualizados"',
             'CA2: digitar −3 ou 11 → "Use pesos inteiros de 0 a 10", nada gravado',
             'CA3: abrir "Para quem é o perfume?" e salvar → aviso de alternativa sem afinidade'],
            "SELECT a.texto, f.nome, ap.peso\nFROM alternativa_peso ap\nJOIN alternativa a ON a.id = ap.alternativa_id\n"
            "JOIN familia_olfativa f ON f.id = ap.familia_id\nWHERE a.pergunta_id = 3;"),
    'US7': (['Sem login, abrir Perfumes → um perfume (CA3: convite para criar conta)',
             'Logado, abrir a mesma ficha (CA1: pirâmide, acordes e "Adicionar à sacola")',
             'CA2: abrir /perfumes/99999 → "Perfume não encontrado." (404)'],
            "SELECT p.nome, pn.nivel, n.nome AS nota\nFROM perfume p JOIN perfume_nota pn ON pn.perfume_id = p.id\n"
            "JOIN nota_olfativa n ON n.id = pn.nota_id\nWHERE p.id = 1;"),
    'US8': (['Consultor → "Quero um perfume fresco para o trabalho, no calor."',
             'US8 CA1 e US9 CA1: resposta + cartões dos perfumes',
             'US9 CA3: com uma conta sem questionário, abrir o consultor → vai ao questionário',
             'US8 CA2 e CA3 e US9 CA2: mostrar os testes automáticos (pág. 25)'],
            "SELECT papel, LEFT(conteudo_json, 60) FROM mensagem\nORDER BY id DESC LIMIT 2;\n"
            "SELECT posicao, perfume_id, justificativa\nFROM recomendacao ORDER BY id DESC LIMIT 2;"),
    'US10': (['CA1: "Adicionar à sacola" no cartão da recomendação',
              'CA2: na ficha do mesmo perfume, adicionar de novo → não duplica',
              'CA3: "Remover" na sacola → "Perfume removido da sacola."'],
             "SELECT u.nome, p.nome AS perfume, s.adicionado_em\nFROM sacola_item s JOIN usuario u ON u.id = s.usuario_id\n"
             "JOIN perfume p ON p.id = s.perfume_id;"),
}


def caixa_demo(chave):
    passos, sql = DEMO[chave]
    return (f'<div class="card demo"><span class="mono rot">AO VIVO, NESTA ORDEM</span>'
            + ''.join(f'<p class="passo-demo"><span class="mono">{i + 1}</span>{e(p)}</p>' for i, p in enumerate(passos))
            + f'<span class="mono rot">BANCO PREENCHIDO E RECUPERADO</span><pre>{e(sql)}</pre></div>')


def secao(numero, titulo, sub, minutos):
    add(f'''<div class="capa secao"><div class="chips"><span class="chip">[ {numero} ]</span><span class="chip">{minutos} MIN</span></div>
  <h1>{titulo}</h1><p class="sub">{sub}</p></div>''', escuro=True)


US_POR_COD = {u['cod']: u for u in US2}

# ---------------------------------------------------------------- abertura
add(f'''<div class="capa">
  <div class="chips"><span class="chip">EXPERIÊNCIA CRIATIVA · PUCPR</span><span class="chip">{SPRINT}</span><span class="chip">RESULTADOS PARA A BANCA</span></div>
  <h1>Modular <span class="grad">Perfumes</span></h1>
  <p class="sub">Consultor olfativo com inteligência artificial: do questionário à sacola</p>
  <div class="equipe"><div><span class="mono">EQUIPE</span><p>Enzo Koeche Castagna · Angelo · André Lagos</p></div>
  <div><span class="mono">ORIENTADORES</span><p>Profa. Cristina Verçosa P. B. de Souza · Prof. Giulio Domenico Bordin · Profa. Rosilene Fernandes</p></div></div>
</div>''', escuro=True)

add(topo('ROTEIRO', 'Dez minutos, no roteiro da banca') + '''
<div class="grade2">
  <div class="card passo"><span class="num mono">[ 1 ] · 2 MIN</span><h3>Canvas PBB atualizado</h3>
    <p>Quais personas, features e PBIs entraram na 2ª Sprint, e os ajustes feitos desde a 1ª.</p><span class="tempo mono">PÁG. 3–6</span></div>
  <div class="card passo"><span class="num mono">[ 2 ] · 8 MIN</span><h3>Product Increment ao vivo</h3>
    <p>Cada história com os critérios de aceite funcionando no site, o banco preenchido e recuperado, e a interface (validação, perfil logado, login obrigatório, logout).</p><span class="tempo mono">PÁG. 7–18</span></div>
</div>
<p class="nota-rodape">A demonstração é ao vivo. Cada história tem uma página com os passos da demonstração e a consulta ao banco, e outra com os prints do mesmo fluxo, caso algo falhe na hora. O apêndice (pág. 20 em diante) explica como funciona por dentro, para as perguntas da banca.</p>''', 'ROTEIRO')

# ---------------------------------------------------------------- [1] Canvas PBB
secao(1, 'Canvas PBB atualizado <span class="grad">para a Sprint 2</span>', 'Personas, features e PBIs escolhidos, e os ajustes finais.', 2)

add(topo('[1] CANVAS PBB', 'Canvas PBB da 2ª Sprint', 'Em vermelho, os PBIs implementados nesta sprint. Com borda verde, os entregues na 1ª.')
    + f'<div class="figura"><img src="file://{REPO / "entregas/pbb/Modular_Perfumes_Canvas_PBB_Sprint2.png"}" style="max-height:790px;max-width:100%;border-radius:12px;border:1px solid #e6e8ec"></div>',
    '[1] CANVAS PBB')

escolhas = [('Administrador', 'Questionário de Perfil', [(6, 'Manter as alternativas e os pesos')],
             'Os pesos definem como as respostas viram o perfil olfativo.'),
            ('Cliente', 'Consultor Olfativo por IA', [(7, 'Consultar a ficha do perfume'), (8, 'Conversar com o agente consultor'),
                                                      (9, 'Receber as recomendações personalizadas')],
             'É o valor principal do produto: a conversa que recomenda.'),
            ('Cliente', 'Sacola e Compra nas Lojas', [(10, 'Adicionar e remover perfumes da sacola')],
             'Guarda o que o cliente gostou; a compra nas lojas vem na Sprint 3.')]
add(topo('[1] CANVAS PBB', 'Persona → feature → PBIs escolhidos') + '<div class="grade3">' + ''.join(
    f'<div class="card escolha"><span class="mono rot">PERSONA</span><h3>{e(p)}</h3><span class="mono rot">FEATURE</span>'
    f'<p class="feat">{e(f)}</p><span class="mono rot">PBIs DA SPRINT 2</span>'
    + ''.join(f'<p class="item espera"><b class="mono">US{n}</b> {e(t)}</p>' for n, t in pbis)
    + f'<p class="obs">{e(por)}</p></div>' for p, f, pbis, por in escolhas) + '</div>'
    + '''<div class="card ajustes"><span class="mono rot">AJUSTES FINAIS DESDE A 1ª SPRINT</span>
    <p><b>US1, cadastro:</b> data de nascimento com máscara (não pode ser no futuro), confirmação de senha, campos obrigatórios marcados e dicas de preenchimento.</p>
    <p><b>US9 CA3:</b> sem questionário, o consultor agora leva ao questionário. <b>US6 CA2:</b> a mensagem do critério aparece também no navegador.</p></div>''',
    '[1] CANVAS PBB')

meia = len(PBIS) // 2
add(topo('[1] CANVAS PBB', 'Product Backlog: 10 de 28 PBIs entregues') + '<div class="grade2 backlog">'
    + ''.join('<table class="dados pbis"><thead><tr><th>#</th><th>PBI</th><th>Persona</th><th>Sprint</th><th>Estado</th></tr></thead><tbody>'
              + ''.join(linha_pbi(*p) for p in parte) + '</tbody></table>' for parte in (PBIS[:meia], PBIS[meia:]))
    + '</div><p class="nota-rodape">A ordem vem do valor: primeiro a base (acesso, questionário e catálogo), depois o consultor e a sacola, e por fim os papéis de lojista e administrador.</p>',
    '[1] CANVAS PBB')

# ---------------------------------------------------------------- [2] Product Increment
secao(2, 'Product Increment <span class="grad">ao vivo</span>', 'Cada história com os critérios de aceite, a tela e o banco.', 8)

US1 = {'cod': 'US1', 'pbi': 1, 'dono': 'ajuste da 1ª Sprint', 'nome': 'Realizar o cadastro do cliente', 'persona': 'Cliente',
       'posso': 'realizar o cadastro, informando nome, data de nascimento, e-mail e senha',
       'para': 'ter acesso grátis com login ao consultor olfativo',
       'cas': [('fluxo principal', ('estou na página de cadastro', 'informo os dados válidos e aciono "Criar conta"',
                                    'grava a conta com a senha criptografada e me leva ao questionário')),
               ('exceção', ('estou na página de cadastro', 'informo um e-mail que já tem conta',
                            'não cria a conta e exibe "Este e-mail já está cadastrado"')),
               ('exceção', ('estou na página de cadastro', 'deixo campo vazio, senhas diferentes ou data no futuro',
                            'não envia o formulário e mostra a mensagem no campo a corrigir'))]}

add(topo('[2] AJUSTE DA 1ª SPRINT · US1', 'Cadastro: validação completa') + f'''
<div class="grade3 prints cadastro">
  <div class="print"><span class="mono rot erro">CA3 · DATA NO FUTURO E SENHAS DIFERENTES: NÃO ENVIA</span>{img("us1_ca3")}</div>
  <div class="print"><span class="mono rot erro">CA2 · E-MAIL JÁ CADASTRADO (SERVIDOR)</span>{img("us1_ca2")}</div>
  <div class="coluna-prints">
    {caixa_demo("US1")}
    <span class="mono rot">BANCO · usuario (depois do CA1)</span>{tabela(EV["us1_banco"], ["nome", "data_nascimento", "perfil", "senha_hash"], ["nome", "nascimento", "perfil", "senha_hash (início)"])}
    <p class="obs">Máscara dd/mm/aaaa, RegEx no e-mail, <b>*</b> nos obrigatórios e uma dica embaixo de cada campo. Depois do CA2, o e-mail continua com {EV["us1_ca2_total"]} conta.</p>
  </div>
</div>''', '[2] PRODUCT INCREMENT')

pesos_ca2 = EV['pesos_depois_ca2'][0]
paginas_us = [
    ('US6', 'Manter as alternativas e os pesos', f'''
<div class="lado">
  <div class="print"><span class="mono rot">TELA DE PESOS · UMA LINHA POR ALTERNATIVA, UMA COLUNA POR FAMÍLIA</span>{img("us6_tela")}</div>
  <div class="banco coluna us6">
    <div class="print"><span class="mono rot ok">CA1 · PESOS ATUALIZADOS</span>{img("us6_ca1")}</div>
    <div class="print"><span class="mono rot erro">CA2 · PESO −3: NADA É GRAVADO</span>{img("us6_ca2")}</div>
    <div class="print"><span class="mono rot aviso">CA3 · ALTERNATIVA TODA EM ZERO: GRAVA E AVISA</span>{img("us6_ca3")}</div>
    <p class="obs">Banco depois do CA2: {pesos_ca2["pesos"]} pesos na pergunta, {pesos_ca2["negativos"]} negativos.</p>
  </div>
</div>'''),
    ('US7', 'Consultar a ficha do perfume', f'''
<div class="grade2 us7">
  <div class="print"><span class="mono rot ok">CA1 · FICHA COMPLETA, COM "ADICIONAR À SACOLA"</span>{img("us7_ca1")}</div>
  <div class="print"><span class="mono rot ok">CA3 · VISITANTE SEM LOGIN: CONVITE PARA CRIAR CONTA</span>{img("us7_ca3")}</div>
</div>
<div class="grade2 us7b">
  <div class="print"><span class="mono rot erro">CA2 · PERFUME OCULTO: 404</span>{img("us7_ca2")}</div>
  <p class="obs"><b>Pirâmide olfativa:</b> notas de <b>saída</b> (o primeiro cheiro), de <b>corpo</b> (o meio) e de <b>fundo</b> (o que fica na pele). <b>Acordes</b> são a impressão geral, com a intensidade que vem da API.</p>
</div>'''),
]


def pagina_historia(cod_us, extra=None):
    cards = cartao_us(US_POR_COD[cod_us]) + (cartao_us(US_POR_COD[extra]) if extra else '')
    classe = 'pag-historia-dupla' if extra else 'pag-historia'
    add(topo(f'[2] {cod_us}{" · " + extra if extra else ""} · HISTÓRIA', US_POR_COD[cod_us]['nome'] if not extra else 'Conversar com o agente e receber recomendações')
        + f'<div class="{classe}">{cards}{caixa_demo(cod_us)}</div>', '[2] PRODUCT INCREMENT')


for cod, nome, corpo_html in paginas_us:
    pagina_historia(cod)
    add(topo(f'[2] {cod} · NO SITE', nome) + corpo_html, '[2] PRODUCT INCREMENT')

aviso_ia = '' if IA_REAL else (
    '<p class="aviso-demo"><b>Sobre este print:</b> o consultor rodou com o <b>modelo simulado</b> dos testes automáticos, porque o computador '
    'que gerou os prints não tem a chave da API da Anthropic. As ferramentas rodaram de verdade no banco; só o texto da resposta é fixo. '
    'Ao vivo, com a <span class="mono">ANTHROPIC_API_KEY</span> no <span class="mono">.env</span>, quem responde é o Claude.</p>')
pagina_historia('US8', 'US9')
add(topo('[2] US8 · US9 · NO SITE', 'Conversa e recomendações personalizadas') + f'''
<div class="lado">
  <div class="print"><span class="mono rot ok">US8 CA1 · RESPOSTA NA TELA · US9 CA1 · CARTÕES REGISTRADOS PELA FERRAMENTA</span>{img("us8_us9_conversa")}</div>
  <div class="banco coluna">
    <span class="mono rot">BANCO · mensagem (histórico da conversa)</span>
    {tabela(EV["mensagens"], ["id", "papel", "texto"])}
    <span class="mono rot">BANCO · recomendacao</span>
    {tabela(EV["recomendacoes"], ["posicao", "perfume", "justificativa"])}
    <p class="obs"><b>US8 CA2:</b> sem chave ou com a API fora do ar, aparece "O consultor está indisponível agora" e o histórico fica. <b>US8 CA3:</b> na 31ª mensagem do dia, a IA nem é chamada. <b>US9 CA2:</b> a ferramenta recusa perfume inexistente ou oculto.</p>
    {aviso_ia}
  </div>
</div>''', '[2] PRODUCT INCREMENT')

pagina_historia('US10')
add(topo('[2] US10 · NO SITE', 'Adicionar e remover perfumes da sacola') + f'''
<div class="grade2 sacola">
  <div class="coluna-prints">
    <div class="print"><span class="mono rot ok">CA1 · ENTROU NA SACOLA (PELO CARTÃO DA RECOMENDAÇÃO)</span>{img("us10_ca1")}</div>
    <div class="print"><span class="mono rot aviso">CA2 · O MESMO PERFUME DE NOVO: NÃO DUPLICA</span>{img("us10_ca2")}</div>
  </div>
  <div class="coluna-prints">
    <div class="print"><span class="mono rot ok">CA3 · REMOVIDO DA SACOLA</span>{img("us10_ca3")}</div>
    <span class="mono rot">BANCO · sacola_item (depois do CA3)</span>{tabela(EV["sacola"], ["perfume", "adicionado_em"])}
    <p class="obs">Depois do CA2, a sacola continuou com {EV["us10_ca2_itens"]} item. A chave primária é <b>cliente + perfume</b>, então o próprio banco impede a duplicata.</p>
  </div>
</div>''', '[2] PRODUCT INCREMENT')

itens_interface = [
    ('Identidade visual em todas as páginas, com CSS / framework CSS', 'Bootstrap 5 + estilo.css próprio: mesmas cores, fontes e componentes', 'todas'),
    ('Páginas responsivas', 'Menu vira botão no celular; colunas empilham (390 px)', 'pág. 18'),
    ('Validação: RegEx / JavaScript, obrigatórios, máscara, data não futura, dicas, só envia válido', 'Cadastro (US1) e tela de pesos (US6)', 'pág. 8, 10'),
    ('Perfil / identidade do usuário logado em todas as páginas autenticadas', 'Nome + selo "Cliente" ou "Administrador" no menu', 'todas'),
    ('Confirmação de senha no cadastro', 'Campo "Confirmar senha", conferido no navegador e no servidor', 'pág. 8'),
    ('Exige autenticação ao acessar uma URL sem login', 'Vai para o login com "Entre na sua conta para continuar."', 'pág. 18'),
    ('Finaliza a sessão (logout)', 'Botão "Sair" → "Você saiu da sua conta."', 'pág. 18'),
    ('Não permite campo único duplicado, com mensagem', 'E-mail: "Este e-mail já está cadastrado"; sacola sem duplicata (US10 CA2)', 'pág. 8, 16'),
    ('Implementa todos os PBIs da Sprint 2, Front + Back', 'US6 a US10 com rotas, telas, banco e testes', 'pág. 9–16'),
]
add(topo('[2] INTERFACE E INTEGRAÇÃO', 'O checklist da banca, item por item')
    + '<table class="dados checklist"><thead><tr><th>Exigência</th><th>Como atendemos</th><th>Onde ver</th></tr></thead><tbody>'
    + ''.join(f'<tr><td><span class="ok-mark">✓</span> {e(a)}</td><td>{e(b)}</td><td class="mono">{e(c)}</td></tr>' for a, b, c in itens_interface)
    + '</tbody></table>', '[2] PRODUCT INCREMENT')

add(topo('[2] INTERFACE E INTEGRAÇÃO', 'Celular, login obrigatório e logout') + f'''
<div class="interface">
  <div class="print cel"><span class="mono rot">390 PX · FICHA</span>{img("mobile_ficha")}</div>
  <div class="print cel"><span class="mono rot">390 PX · CONSULTOR</span>{img("mobile_consultor")}</div>
  <div class="print cel"><span class="mono rot">390 PX · SACOLA</span>{img("mobile_sacola")}</div>
  <div class="coluna-prints">
    <div class="print"><span class="mono rot erro">SEM LOGIN, /sacola/ → LOGIN</span>{img("auth_exigida")}</div>
    <div class="print"><span class="mono rot ok">LOGOUT</span>{img("logout")}</div>
  </div>
</div>''', '[2] PRODUCT INCREMENT')

add('''<div class="capa fim">
  <div class="chips"><span class="chip">2ª SPRINT ENTREGUE</span><span class="chip">10 DE 28 PBIs</span></div>
  <h1>Obrigado!</h1>
  <p class="sub">Próxima sprint: as <span class="grad">lojas parceiras</span> entram, e finalizar a sacola leva o cliente à loja de cada perfume.</p>
  <div class="equipe"><div><span class="mono">GITHUB</span><p>github.com/EnzoKoeche/modular-perfumes</p></div>
  <div><span class="mono">TRELLO</span><p>trello.com/b/PN46fipf</p></div></div>
</div>''', escuro=True)

# ---------------------------------------------------------------- apêndice (perguntas da banca)
add(topo('APÊNDICE', 'Roteiro de fala (10 minutos)', 'Preencham a coluna "Quem". Treinem a demonstração ao vivo pelo menos uma vez com o cronômetro.')
    + '<table class="dados roteiro"><thead><tr><th>Bloco</th><th>Páginas</th><th>Tempo</th><th>O que fazer</th><th>Quem</th></tr></thead><tbody>'
    + ''.join(f'<tr><td><b>{e(b)}</b></td><td class="mono">{e(p)}</td><td class="mono">{e(t)}</td><td>{e(d)}</td><td class="quem"></td></tr>' for b, p, t, d in [
        ('[1] Canvas PBB', '3–6', '2 min', 'Mostrar o Canvas da Sprint 2: persona → feature → PBIs em vermelho. Citar os ajustes finais (cadastro, US9, US6).'),
        ('[2] Cadastro (ajuste)', '8', '1 min', 'Ao vivo: data no futuro e senhas diferentes, depois criar a conta, depois e-mail duplicado. Mostrar o usuario no banco.'),
        ('[2] US6 · pesos', '9–10', '1,5 min', 'Ao vivo como administrador: salvar, digitar −3, salvar a pergunta "Para quem é". Mostrar alternativa_peso.'),
        ('[2] US7 · ficha', '11–12', '1 min', 'Ficha sem login e com login; /perfumes/99999 para o 404.'),
        ('[2] US8 e US9 · consultor', '13–14', '2 min', 'Mandar a mensagem, mostrar os cartões e as tabelas mensagem e recomendacao.'),
        ('[2] US10 · sacola', '15–16', '1 min', 'Adicionar pelo cartão, adicionar de novo, remover. Mostrar sacola_item.'),
        ('[2] Interface', '17–18', '0,5 min', 'Celular (F12 → modo dispositivo), abrir /sacola/ sem login, logout.'),
    ])
    + '</tbody></table><p class="nota-rodape"><b>Antes de entrar na sala:</b> banco e site no ar (<span class="mono">docker compose up -d db</span> e <span class="mono">flask --app app run --port 5050</span>), <span class="mono">ANTHROPIC_API_KEY</span> no <span class="mono">.env</span>, uma aba logada como administrador, outra como cliente com o questionário respondido, e um terminal com o MySQL aberto para as consultas.</p>',
    'APÊNDICE')

perfil = EV['perfil'][:5]
add(topo('APÊNDICE · COMO FUNCIONA', 'Do questionário ao perfil: a soma dos pesos (US3 + US6)') + f'''
<div class="lado">
  <div class="card didatico">
    <span class="mono rot">A IDEIA</span>
    <p>Cada alternativa do questionário vale pontos para uma ou mais <b>famílias olfativas</b>. Quem define esses pontos é o administrador, na tela de pesos da <b>US6</b>. Ao concluir o questionário, o sistema <b>soma os pontos por família</b>; as famílias com mais pontos são as que mais combinam com o cliente, e é isso que o consultor de IA lê depois.</p>
    <pre>INSERT INTO perfil_familia (perfil_id, familia_id, afinidade)
SELECT %s, ap.familia_id, SUM(ap.peso)
FROM resposta_item ri
JOIN alternativa_peso ap ON ap.alternativa_id = ri.alternativa_id
WHERE ri.resposta_id = %s GROUP BY ap.familia_id;</pre></div>
  <div class="banco coluna">
    <div class="print"><span class="mono rot ok">PERFIL DA CLIENTE DE DEMONSTRAÇÃO</span>{img("us3_perfil")}</div>
    <span class="mono rot">BANCO · perfil_familia</span>{tabela(perfil, ["familia", "afinidade"])}
  </div>
</div>''', 'APÊNDICE')

add(topo('APÊNDICE · COMO FUNCIONA', 'O agente de IA: o modelo conversa, o sistema confere') + '''
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
  </div>
</div>''', 'APÊNDICE')

add(topo('APÊNDICE · ARTEFATO 6', 'Modelo relacional: 21 tabelas (17 da 1ª Sprint + 4 da 2ª)')
    + f'<div class="figura"><img src="file://{REPO / "entregas/der/Modular_Perfumes_DER_Logico_Sprint2.png"}" style="max-height:800px;max-width:100%;border-radius:12px;border:1px solid #e6e8ec;background:#fff"></div>',
    'APÊNDICE')

add(topo('APÊNDICE · ARTEFATO 8', 'Diagramas de atividades') + f'''
<div class="grade2 atividades">
  <div class="print"><img src="file://{REPO / "entregas/atividades/Modular_Perfumes_Atividades_Cliente.png"}"></div>
  <div class="print"><img src="file://{REPO / "entregas/atividades/Modular_Perfumes_Atividades_Admin_Pesos.png"}"></div>
</div>''', 'APÊNDICE')

linhas = ''.join(f'<tr><td><span class="selo">{u}</span></td>' + ''.join(f'<td class="mono teste">{e(x)}</td>' for x in cas) + '</tr>'
                 for u, *cas in TESTES_POR_CA)
add(topo('APÊNDICE · QUALIDADE', f'{TESTES} testes automáticos: cada critério de aceite tem o seu') + f'''
<table class="dados testes"><thead><tr><th></th><th>CA1</th><th>CA2</th><th>CA3</th></tr></thead><tbody>{linhas}</tbody></table>
<div class="grade3 qualidade">
  <div class="card"><span class="mono rot">COMO RODAM</span><p>Com <span class="mono">pytest</span>, num banco MySQL de teste recriado a cada rodada pelos scripts oficiais.</p></div>
  <div class="card"><span class="mono rot">E A IA?</span><p>Nos testes, o Claude é trocado por um dublê; as ferramentas rodam de verdade no banco, sem gastar a API.</p></div>
  <div class="card"><span class="mono rot">SEGURANÇA</span><p>Senha com hash PBKDF2, bloqueio após 5 tentativas, CSRF e perfil conferido no servidor.</p></div>
</div>''', 'APÊNDICE')

autores = ''.join(f'<div class="card"><span class="mono rot">{e(nome.upper())}</span><p class="grande">{n}</p><p class="obs">commits</p></div>'
                  for n, nome in COMMITS)
add(topo('APÊNDICE · PROCESSO', 'Scrum no Trello, código no GitHub') + f'''
<div class="colunas-trello">
  <div class="col"><span class="mono">PRODUCT BACKLOG</span><p>os 28 PBIs</p></div><div class="seta">→</div>
  <div class="col"><span class="mono">SPRINT BACKLOG</span><p>PBIs da sprint, com responsável e prazo</p></div><div class="seta">→</div>
  <div class="col"><span class="mono">EM DESENVOLVIMENTO</span><p>comentário "comecei"</p></div><div class="seta">→</div>
  <div class="col"><span class="mono">EM TESTE</span><p>testes passando</p></div><div class="seta">→</div>
  <div class="col ok"><span class="mono">CONCLUÍDO</span><p>critérios marcados + link do commit</p></div>
</div>
<div class="lado processo">
  <div class="card"><span class="mono rot">REGRAS DO TIME</span>
    <p class="item">Commits pequenos, com a US na mensagem ("US6: tela de pesos...").</p>
    <p class="item">Antes do push, todos os testes verdes.</p>
    <p class="item">Documentos das entregas (DER, SQL, PDF, especificação) gerados por código, em <span class="mono">entregas/*/fonte</span>.</p></div>
  <div class="grade2 numeros">{autores}</div>
</div>''', 'APÊNDICE')

prox = {s: [p for p in PBIS if p[3] == s] for s in (3, 4, 5)}
objetivos = {3: 'Lojas parceiras: cadastro, aprovação e ofertas; a sacola passa a abrir a loja de cada perfume.',
             4: 'Contas e cadastros completos; avaliação das recomendações e diretrizes do agente.',
             5: 'Curadoria do catálogo, sincronização agendada e indicadores para o administrador.'}
add(topo('APÊNDICE · PRÓXIMOS PASSOS', 'O que vem nas próximas sprints') + '<div class="grade3">' + ''.join(
    f'<div class="card"><span class="mono rot">SPRINT {s}</span><p class="obj">{e(objetivos[s])}</p>'
    + ''.join(f'<p class="pbi-item"><span class="mono">{n:02d}</span> {e(nome)}</p>' for n, nome, _, _ in prox[s]) + '</div>'
    for s in (3, 4, 5)) + '</div><p class="nota-rodape">Também na fila: a resposta do consultor aparecer aos poucos, enquanto é gerada (streaming, RF-21).</p>',
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

.capa.secao h1 { font-size: 110px; } .capa.secao .sub { margin-bottom: 0; }
.demo { padding: 22px 26px; } .demo pre { font-size: 15px; }
.passo-demo { font-size: 20px; margin: 8px 0; line-height: 1.35; display: flex; gap: 12px; }
.passo-demo .mono { color: #7c3aed; font-weight: 700; min-width: 20px; }
.pag-historia { display: grid; grid-template-columns: 1.15fr 1fr; gap: 28px; align-items: start; }
.pag-historia-dupla { display: grid; grid-template-columns: 1fr 1fr 0.9fr; gap: 22px; align-items: start; }
.pag-historia-dupla .us .historia { font-size: 18px; } .pag-historia-dupla .ca p { font-size: 17px; } .pag-historia-dupla .us h3 { font-size: 23px; }
.pag-historia-dupla .passo-demo { font-size: 18px; }
.escolha h3 { margin-bottom: 4px; } .escolha .item { font-size: 21px; }
.ajustes { margin-top: 24px; padding: 18px 28px; } .ajustes p { font-size: 20px; margin: 6px 0; color: #344054; }
.cadastro { grid-template-columns: 0.75fr 0.75fr 1.2fr !important; align-items: start; }
.cadastro .print img { height: 760px !important; object-fit: cover; object-position: top; }
.cadastro .demo .passo-demo { font-size: 18px; }
table.checklist { font-size: 21px; } table.checklist td { padding: 13px 14px; }
.ok-mark { color: #12b76a; font-weight: 800; margin-right: 6px; }
.interface { display: grid; grid-template-columns: 0.55fr 0.55fr 0.55fr 1.35fr; gap: 20px; align-items: start; }
.interface .cel img { max-height: 760px; object-fit: cover; object-position: top; }
.interface .coluna-prints .print img { max-height: 330px; object-fit: cover; object-position: top; }
.atividades { align-items: start; } .atividades .print img { max-height: 820px; object-fit: contain; }
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
