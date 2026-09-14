"""US3 — Responder o questionário de perfil olfativo."""
from flask import Blueprint, flash, redirect, render_template, request, url_for

from . import db
from .auth import perfil_obrigatorio, questionario_concluido, usuario_logado

bp = Blueprint('questionario', __name__, url_prefix='/questionario')

# A pergunta de ordem 1 define o nível de conhecimento (alternativa de ordem 1, 2 ou 3).
NIVEIS = {1: 'INICIANTE', 2: 'INTERMEDIARIO', 3: 'AVANCADO'}


def questionario_ativo():
    return db.consultar_um('SELECT id, titulo FROM questionario WHERE ativo = 1 ORDER BY id DESC LIMIT 1')


def perguntas_com_alternativas(questionario_id):
    perguntas = db.consultar(
        'SELECT id, enunciado, tipo, ordem, obrigatoria FROM pergunta '
        'WHERE questionario_id = %s AND ativa = 1 ORDER BY ordem, id', (questionario_id,))
    for p in perguntas:
        p['alternativas'] = db.consultar(
            'SELECT id, texto FROM alternativa WHERE pergunta_id = %s AND ativa = 1 ORDER BY ordem, id', (p['id'],))
    return perguntas


def resposta_em_andamento(usuario_id, questionario_id):
    r = db.consultar_um(
        'SELECT id FROM resposta_questionario WHERE usuario_id = %s AND questionario_id = %s '
        'AND concluida_em IS NULL ORDER BY id DESC LIMIT 1', (usuario_id, questionario_id))
    if r:
        return r['id']
    novo = db.executar('INSERT INTO resposta_questionario (usuario_id, questionario_id) VALUES (%s, %s)',
                       (usuario_id, questionario_id))
    db.confirmar()
    return novo


def respostas_salvas(resposta_id):
    salvas = {}
    for item in db.consultar('SELECT pergunta_id, alternativa_id FROM resposta_item WHERE resposta_id = %s',
                             (resposta_id,)):
        salvas.setdefault(item['pergunta_id'], set()).add(item['alternativa_id'])
    return salvas


def gravar_respostas(resposta_id, perguntas, formulario):
    """Grava o que veio no formulário, pergunta a pergunta (RF-09)."""
    for p in perguntas:
        validas = {a['id'] for a in p['alternativas']}
        escolhidas = {int(v) for v in formulario.getlist(f'pergunta_{p["id"]}') if v.isdigit()} & validas
        if p['tipo'] == 'UNICA' and len(escolhidas) > 1:
            escolhidas = {min(escolhidas)}
        db.executar('DELETE FROM resposta_item WHERE resposta_id = %s AND pergunta_id = %s', (resposta_id, p['id']))
        for alt in escolhidas:
            db.executar('INSERT INTO resposta_item (resposta_id, pergunta_id, alternativa_id) VALUES (%s, %s, %s)',
                        (resposta_id, p['id'], alt))
    db.confirmar()


def gerar_perfil(usuario_id, resposta_id):
    """Gera o perfil olfativo: nível pela pergunta de ordem 1 e afinidade pela soma dos pesos (RF-11)."""
    nivel_alt = db.consultar_um(
        'SELECT a.ordem FROM resposta_item ri '
        'JOIN pergunta p ON p.id = ri.pergunta_id AND p.ordem = 1 '
        'JOIN alternativa a ON a.id = ri.alternativa_id '
        'WHERE ri.resposta_id = %s LIMIT 1', (resposta_id,))
    nivel = NIVEIS.get(nivel_alt['ordem'] if nivel_alt else 1, 'INICIANTE')
    db.executar('DELETE FROM perfil_olfativo WHERE usuario_id = %s', (usuario_id,))
    perfil_id = db.executar(
        'INSERT INTO perfil_olfativo (usuario_id, resposta_id, nivel_conhecimento) VALUES (%s, %s, %s)',
        (usuario_id, resposta_id, nivel))
    db.executar(
        'INSERT INTO perfil_familia (perfil_id, familia_id, afinidade) '
        'SELECT %s, ap.familia_id, SUM(ap.peso) FROM resposta_item ri '
        'JOIN alternativa_peso ap ON ap.alternativa_id = ri.alternativa_id '
        'WHERE ri.resposta_id = %s GROUP BY ap.familia_id', (perfil_id, resposta_id))
    db.executar('UPDATE resposta_questionario SET concluida_em = NOW() WHERE id = %s', (resposta_id,))
    db.confirmar()


@bp.route('/', methods=['GET', 'POST'])
@perfil_obrigatorio('CLIENTE')
def responder():
    usuario = usuario_logado()
    questionario = questionario_ativo()
    if not questionario:
        return render_template('erro.html', codigo=503,
                               mensagem='O questionário ainda não está disponível. Volte mais tarde.'), 503
    if request.method == 'GET' and questionario_concluido(usuario['id']) and not request.args.get('refazer'):
        return redirect(url_for('cliente.inicio'))

    perguntas = perguntas_com_alternativas(questionario['id'])
    resposta_id = resposta_em_andamento(usuario['id'], questionario['id'])
    pendentes = set()

    if request.method == 'POST':
        gravar_respostas(resposta_id, perguntas, request.form)
        if request.form.get('acao') == 'salvar':
            flash('Respostas salvas. Quando voltar, você continua de onde parou.', 'info')
            return redirect(url_for('cliente.inicio'))
        salvas = respostas_salvas(resposta_id)
        pendentes = {p['id'] for p in perguntas if p['obrigatoria'] and not salvas.get(p['id'])}
        if not pendentes:                                               # US3 CA1
            gerar_perfil(usuario['id'], resposta_id)
            flash('Perfil olfativo gerado! O consultor de IA está liberado para você.', 'success')
            return redirect(url_for('cliente.inicio'))
        flash('Responda as perguntas destacadas para concluir.', 'danger')   # US3 CA2

    salvas = respostas_salvas(resposta_id)
    # US3 CA3: retoma a partir da primeira pergunta sem resposta
    primeira_sem_resposta = next((p['id'] for p in perguntas if not salvas.get(p['id'])), None)
    return render_template('cliente/questionario.html', questionario=questionario, perguntas=perguntas,
                           salvas=salvas, pendentes=pendentes, primeira_sem_resposta=primeira_sem_resposta), \
        (400 if pendentes else 200)
