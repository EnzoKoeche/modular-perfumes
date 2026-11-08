"""Gera a Especificação da 2ª Sprint a partir da versão entregue na 1ª Sprint.

uso (precisa de python-docx):  python especificacao_sprint2.py
Entrada: ../Modular_Perfumes_Especificacao_do_Projeto.docx (Sprint 1, não é alterada)
Saída:   ../Modular_Perfumes_Especificacao_do_Projeto_Sprint2.docx

O que muda: Artefato 4 (Canvas PBB da Sprint 2), Artefato 5 (US1 ajustada + US6 a US10), Artefato 6 (DER com as
21 tabelas), Artefato 7 (justificativa) e Artefato 8 (Diagramas de Atividades). Ao abrir no Word, responda "Sim"
para atualizar os campos (numeração das figuras e índice de ilustrações).
"""
import copy
import pathlib

import docx
from docx.oxml.ns import qn
from docx.shared import Cm, Emu

PASTA = pathlib.Path(__file__).parent
ENTREGAS = PASTA.parents[1]
ENTRADA = PASTA.parent / 'Modular_Perfumes_Especificacao_do_Projeto.docx'
SAIDA = PASTA.parent / 'Modular_Perfumes_Especificacao_do_Projeto_Sprint2.docx'
PBB = ENTREGAS / 'pbb' / 'Modular_Perfumes_Canvas_PBB_Sprint2.png'
DER = ENTREGAS / 'der' / 'Modular_Perfumes_DER_Logico_Sprint2.png'
ATIV_CLIENTE = ENTREGAS / 'atividades' / 'Modular_Perfumes_Atividades_Cliente.png'
ATIV_ADMIN = ENTREGAS / 'atividades' / 'Modular_Perfumes_Atividades_Admin_Pesos.png'

# (número, PBI, persona, posso, para, [(dado, quando, então) x 3]) — mesma fonte: docs/05-backlog-e-user-stories.md
US = [
    (6, 'Manter as alternativas e os pesos', 'Administrador',
     'definir o peso de cada alternativa do questionário para cada família olfativa.',
     'ter um perfil olfativo calculado com regras que eu mesmo ajusto.',
     [('estou na gestão do questionário e abro "Pesos" de uma pergunta',
       'informo um peso inteiro de 0 a 10 para cada família em cada alternativa e aciono "Salvar pesos"',
       'o sistema grava os pesos e exibe "Pesos atualizados".'),
      ('estou editando os pesos', 'informo um peso negativo, maior que 10 ou que não é número e aciono "Salvar pesos"',
       'o sistema não grava nada e exibe "Use pesos inteiros de 0 a 10".'),
      ('deixo todos os pesos de uma alternativa em 0', 'aciono "Salvar pesos"',
       'o sistema grava e avisa que essa alternativa não soma afinidade com nenhuma família.')]),
    (7, 'Consultar a ficha do perfume', 'Cliente', 'consultar a ficha completa de um perfume.',
     'conhecer a pirâmide olfativa e os acordes antes de decidir.',
     [('o perfume está visível no catálogo', 'abro a ficha pela vitrine ou por uma recomendação',
       'o sistema exibe foto, nome, marca, gênero, ano, notas de saída, corpo e fundo e os acordes, com o botão "Adicionar à sacola".'),
      ('o perfume não existe ou está oculto', 'acesso o endereço da ficha',
       'o sistema exibe "Perfume não encontrado." com o código 404.'),
      ('não estou logado', 'abro a ficha',
       'o sistema exibe a ficha e troca o botão da sacola por "Criar conta e descobrir se combina com você".')]),
    (8, 'Conversar com o agente consultor', 'Cliente', 'conversar com o agente consultor de IA.',
     'tirar dúvidas sobre perfumes em linguagem natural, levando em conta o meu perfil.',
     [('concluí o questionário de perfil', 'envio uma mensagem ao consultor',
       'o sistema mostra a resposta do agente e guarda a conversa no histórico.'),
      ('a chave da IA não está configurada ou o serviço está fora do ar', 'envio uma mensagem',
       'o sistema avisa que o consultor está indisponível, sem perder o histórico.'),
      ('já enviei 30 mensagens hoje (RN-15)', 'envio mais uma',
       'o sistema não chama a IA e exibe a mensagem de limite diário.')]),
    (9, 'Receber as recomendações personalizadas', 'Cliente',
     'receber recomendações de perfumes do catálogo com a justificativa de cada uma.',
     'saber quais perfumes combinam com o meu perfil e por quê.',
     [('o agente recomenda um perfume na conversa', 'a resposta chega',
       'o sistema registra a recomendação com posição e justificativa e exibe o cartão com foto, "ver ficha" e "Adicionar à sacola".'),
      ('o agente tenta recomendar um perfume que não existe ou está oculto', 'a ferramenta de registro é chamada',
       'o sistema recusa o registro e o cartão não aparece.'),
      ('ainda não concluí o questionário', 'abro o consultor', 'o sistema me leva ao questionário (RN-04).')]),
    (10, 'Adicionar e remover perfumes da sacola', 'Cliente', 'adicionar, listar e remover perfumes da minha sacola.',
     'juntar os perfumes que quero comprar nas lojas parceiras.',
     [('concluí o questionário e o perfume está visível', 'aciono "Adicionar à sacola"',
       'o perfume entra na sacola, que lista nome, marca e foto, com a mensagem "<perfume> entrou na sacola."'),
      ('o perfume já está na sacola', 'aciono "Adicionar à sacola" de novo',
       'o sistema não duplica e exibe "Este perfume já está na sua sacola."'),
      ('tenho um perfume na sacola', 'aciono "Remover"',
       'o perfume sai da sacola e o sistema exibe "Perfume removido da sacola."')]),
]


def trocar_texto(p_el, texto):
    """Põe o texto no primeiro w:t do parágrafo e apaga os demais (mantém a formatação do primeiro trecho)."""
    ts = list(p_el.iter(qn('w:t')))
    ts[0].text = texto
    ts[0].set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    for t in ts[1:]:
        t.text = ''


def trocar_legenda(p_el, texto):
    """Legenda 'Figura <n> – ...': mantém 'Figura ' e o campo de numeração, troca o resto."""
    ts = list(p_el.iter(qn('w:t')))
    ts[-1].text = texto
    ts[-1].set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')


def preencher_us(tbl, n, pbi, persona, posso, para, cas):
    linhas = tbl.findall(qn('w:tr'))
    trocar_texto(linhas[0].findall(qn('w:tc'))[0].findall(qn('w:p'))[0], f'HISTÓRIA DO USUÁRIO {n} – PBI: {pbi}')
    ps = linhas[1].findall(qn('w:tc'))[0].findall(qn('w:p'))
    for p, t in zip(ps, (f'COMO: {persona}', f'POSSO: {posso}', f'PARA: {para}')):
        trocar_texto(p, t)
    for linha, (dado, quando, entao) in zip(linhas[2:], cas):
        ps = linha.findall(qn('w:tc'))[1].findall(qn('w:p'))
        for p, t in zip(ps, (f'DADO QUE: {dado}', f'QUANDO: {quando}', f'ENTÃO: {entao}')):
            trocar_texto(p, t)


def trocar_imagem(doc, p_el, caminho, largura_max=None):
    from PIL import Image
    rid = next(p_el.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}blip')).get(qn('r:embed'))
    doc.part.related_parts[rid]._blob = caminho.read_bytes()
    w, h = Image.open(caminho).size
    for ext in list(p_el.iter(qn('wp:extent'))) + list(p_el.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}ext')):
        if ext.get('cx') is None:
            continue
        cx = int(ext.get('cx'))
        if largura_max:
            cx = min(cx, int(largura_max))
        ext.set('cx', str(cx))
        ext.set('cy', str(int(cx * h / w)))


doc = docx.Document(str(ENTRADA))
corpo = doc.element.body
els = list(corpo.iterchildren())


def achar(prefixo, tag='p'):
    for el in corpo.iterchildren():
        if el.tag == qn(f'w:{tag}') and ''.join(t.text or '' for t in el.iter(qn('w:t'))).strip().startswith(prefixo):
            return el
    raise LookupError(prefixo)


def achar_contem(trecho):
    """A última ocorrência: a primeira costuma ser a linha do índice de ilustrações."""
    achados = [el for el in corpo.iterchildren(qn('w:p')) if trecho in ''.join(t.text or '' for t in el.iter(qn('w:t')))]
    if not achados:
        raise LookupError(trecho)
    return achados[-1]


# ---------------------------------------------------------------- capa: identificar a versão
trocar_texto(achar('ESPECIFICAÇÃO DO PROJETO'), 'ESPECIFICAÇÃO DO PROJETO — 2ª SPRINT')
corpo.remove(achar('ANGELO'))   # saiu do grupo antes da 2ª Sprint

# ---------------------------------------------------------------- Artefato 4: Canvas PBB da Sprint 2
# o quadro do Artefato 3 enche a página; os parágrafos vazios antes da quebra geravam uma página em branco
quebra4 = achar('ARTEFATO 4').getprevious()
anterior = quebra4.getprevious()
while anterior is not None and anterior.tag == qn('w:p') and not ''.join(t.text or '' for t in anterior.iter(qn('w:t'))).strip() \
        and not list(anterior.iter(qn('w:drawing'))):
    vazio, anterior = anterior, anterior.getprevious()
    corpo.remove(vazio)
# e a própria quebra caía sozinha numa página: troca por "quebra de página antes" no título do Artefato 4
titulo4 = achar('ARTEFATO 4')
corpo.remove(quebra4)
ppr = titulo4.find(qn('w:pPr'))
from docx.oxml import OxmlElement
ppr.insert(0, OxmlElement('w:pageBreakBefore'))
while True:   # sobra de parágrafo vazio entre a legenda do Artefato 3 e o título do Artefato 4
    antes = titulo4.getprevious()
    while antes.tag in (qn('w:bookmarkStart'), qn('w:bookmarkEnd')):   # o marcador do sumário não conta
        antes = antes.getprevious()
    if antes.tag == qn('w:p') and not ''.join(t.text or '' for t in antes.iter(qn('w:t'))).strip() \
            and not list(antes.iter(qn('w:drawing'))) and not list(antes.iter(qn('w:pict'))):
        corpo.remove(antes)
    else:
        break
leg_pbb = achar_contem('– Canvas PBB do Modular')
img_pbb = leg_pbb.getprevious()
trocar_imagem(doc, img_pbb, PBB)
trocar_legenda(leg_pbb, ' – Canvas PBB do Modular Perfumes. Os PBIs destacados em vermelho compõem a Sprint 2; '
                        'os de borda verde foram entregues na Sprint 1. Fonte: os autores, com base em AGUIAR, F. 2018.')

# ---------------------------------------------------------------- Artefato 5: US1 ajustada + US6 a US10
tabelas = [t for t in corpo.iterchildren(qn('w:tbl'))]
us1 = next(t for t in tabelas if 'HISTÓRIA DO USUÁRIO 1' in ''.join(x.text or '' for x in t.iter(qn('w:t'))))
linhas = us1.findall(qn('w:tr'))
for p in linhas[1].findall(qn('w:tc'))[0].findall(qn('w:p')):
    if ''.join(x.text or '' for x in p.iter(qn('w:t'))).startswith('POSSO'):
        trocar_texto(p, 'POSSO: realizar o cadastro na plataforma, informando nome, data de nascimento, e-mail e senha.')
ca1 = linhas[2].findall(qn('w:tc'))[1].findall(qn('w:p'))
trocar_texto(ca1[1], 'QUANDO: informo nome, data de nascimento, e-mail válido, senha com no mínimo 8 caracteres e a '
                     'confirmação da senha e aciono "Criar conta"')
ca3 = linhas[4].findall(qn('w:tc'))[1].findall(qn('w:p'))
trocar_texto(ca3[1], 'QUANDO: deixo um campo obrigatório vazio, informo senha com menos de 8 caracteres, senhas que não '
                     'conferem ou data de nascimento no futuro e aciono "Criar conta"')
trocar_texto(ca3[2], 'ENTÃO: o sistema não envia o formulário e indica o campo que precisa ser corrigido, com a mensagem do problema.')

us5 = next(t for t in tabelas if 'HISTÓRIA DO USUÁRIO 5' in ''.join(x.text or '' for x in t.iter(qn('w:t'))))
espaco = us5.getprevious()          # parágrafo vazio entre as tabelas
ancora = us5
for n, pbi, persona, posso, para, cas in US:
    novo_espaco, nova = copy.deepcopy(espaco), copy.deepcopy(us5)
    preencher_us(nova, n, pbi, persona, posso, para, cas)
    ancora.addnext(novo_espaco)
    novo_espaco.addnext(nova)
    ancora = nova
trocar_legenda(achar_contem('– Relação de User Stories'),
               ' – Relação de User Stories e Critérios de Aceite: US1 a US5 (1ª Sprint, com o ajuste da US1) e US6 a '
               'US10 (2ª Sprint). Fonte: os autores, com base em AGUIAR, F. 2018.')
trello = achar('LINK DO TRELLO')
ts = list(trello.iter(qn('w:t')))
ts[-1].text = ' — quadro com as listas Product Backlog, Sprint 1 Backlog, Sprint 2 Backlog, Em Desenvolvimento, Em Teste e Concluído.'
TRELLO_URL = 'https://trello.com/b/PN46fipf'   # o mesmo link público da apresentação
for link in trello.iter(qn('w:hyperlink')):
    doc.part.rels[link.get(qn('r:id'))]._target = TRELLO_URL
    trocar_texto(link, TRELLO_URL)

# ---------------------------------------------------------------- Artefato 6: DER com as 21 tabelas
leg_der = achar_contem('– Diagrama de Entidade e Relacionamento')
tbl_der = leg_der.getprevious()
trocar_imagem(doc, tbl_der, DER)
trocar_legenda(leg_der, ' – Diagrama de Entidade e Relacionamento (lógico) do Modular Perfumes: as 17 tabelas da 1ª Sprint '
                        '(usuario com data_nascimento) e as 4 da 2ª (conversa, mensagem, recomendacao e sacola_item). Fonte: os autores.')

# ---------------------------------------------------------------- Artefatos 7 e 8, antes das referências
titulo6 = achar('ARTEFATO 6')
quebra = titulo6.getprevious()      # parágrafo com a quebra de página
ref = achar('REFERÊNCIA BIBLIOGRÁFICAS')
antes_ref = ref.getprevious()       # quebra de página das referências


def paragrafo(texto, estilo='Normal'):
    p = doc.add_paragraph(texto, style=estilo)
    el = p._p
    corpo.remove(el)
    return el, p


def figura(caminho, largura_cm, legenda):
    _, p = paragrafo('')
    p.alignment = 1
    p.add_run().add_picture(str(caminho), width=Cm(largura_cm))
    leg = copy.deepcopy(leg_der)
    trocar_legenda(leg, legenda)
    return [p._p, leg]


novos = []
for titulo, textos, figs in [
    ('ARTEFATO 7: Diagrama de Classes',
     ['Não se aplica a esta entrega. O código do Modular Perfumes é organizado em módulos e funções Python (Flask), '
      'com SQL escrito à mão, sem classes de domínio. Conforme o template, o Diagrama de Classes é exigido para '
      'produtos orientados a objetos, o que não é o caso deste projeto.'], []),
    ('ARTEFATO 8: Diagrama de Atividades',
     ['Os diagramas a seguir mostram o fluxo das funcionalidades da 2ª Sprint, na notação UML. Cada decisão (losango) '
      'corresponde a um critério de aceite das user stories do Artefato 5, indicado entre parênteses. A cor das ações '
      'indica quem as executa: a persona, o sistema (Flask + MySQL) ou o agente de IA.'],
     [(ATIV_CLIENTE, 13.5, ' – Diagrama de Atividades 8.1: Cliente, do cadastro à sacola (US1, US3 e US7 a US10). Fonte: os autores.'),
      (ATIV_ADMIN, 15.5, ' – Diagrama de Atividades 8.2: Administrador mantém os pesos das alternativas (US6). Fonte: os autores.')]),
]:
    novos.append(copy.deepcopy(quebra))
    cab = copy.deepcopy(titulo6)
    trocar_texto(cab, titulo)
    novos.append(cab)
    for t in textos:
        novos.append(paragrafo(t)[0])
    for i, (caminho, largura, legenda) in enumerate(figs):
        if i:
            novos.append(copy.deepcopy(quebra))
        novos += figura(caminho, largura, legenda)
for el in novos:
    antes_ref.addprevious(el)

doc.save(str(SAIDA))
print('ok ->', SAIDA)
