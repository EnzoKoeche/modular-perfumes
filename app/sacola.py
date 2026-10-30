"""US10 (adicionar e remover perfumes da sacola). Finalizar a sacola abrindo as lojas é a US15."""
from flask import Blueprint, flash, redirect, render_template, url_for

from . import db
from .auth import perfil_obrigatorio, questionario_concluido, usuario_logado

bp = Blueprint('sacola', __name__, url_prefix='/sacola')

MSG_JA_NA_SACOLA = 'Este perfume já está na sua sacola.'
MSG_REMOVIDO = 'Perfume removido da sacola.'


def _cliente_liberado():
    """RN-04: sem questionário concluído, sem sacola."""
    return questionario_concluido(usuario_logado()['id'])


@bp.route('/')
@perfil_obrigatorio('CLIENTE')
def ver():
    if not _cliente_liberado():
        return redirect(url_for('questionario.responder'))
    itens = db.consultar(
        'SELECT p.id, p.nome, p.ano, p.imagem_url, p.visivel, m.nome AS marca, s.adicionado_em '
        'FROM sacola_item s JOIN perfume p ON p.id = s.perfume_id JOIN marca m ON m.id = p.marca_id '
        'WHERE s.usuario_id = %s ORDER BY s.adicionado_em DESC, p.nome', (usuario_logado()['id'],))
    return render_template('cliente/sacola.html', itens=itens)


@bp.route('/adicionar/<int:perfume_id>', methods=['POST'])
@perfil_obrigatorio('CLIENTE')
def adicionar(perfume_id):
    if not _cliente_liberado():
        return redirect(url_for('questionario.responder'))
    uid = usuario_logado()['id']
    perfume = db.consultar_um('SELECT id, nome FROM perfume WHERE id = %s AND visivel = 1', (perfume_id,))
    if not perfume:                                     # RN-08: perfume oculto não entra na sacola
        return render_template('erro.html', codigo=404, mensagem='Perfume não encontrado.'), 404
    if db.consultar_um('SELECT 1 FROM sacola_item WHERE usuario_id = %s AND perfume_id = %s', (uid, perfume_id)):
        flash(MSG_JA_NA_SACOLA, 'warning')              # US10 CA2
    else:
        db.executar('INSERT INTO sacola_item (usuario_id, perfume_id) VALUES (%s, %s)', (uid, perfume_id))
        db.confirmar()
        flash(f'{perfume["nome"]} entrou na sacola.', 'success')
    return redirect(url_for('sacola.ver'))


@bp.route('/remover/<int:perfume_id>', methods=['POST'])
@perfil_obrigatorio('CLIENTE')
def remover(perfume_id):
    db.executar('DELETE FROM sacola_item WHERE usuario_id = %s AND perfume_id = %s',
                (usuario_logado()['id'], perfume_id))
    db.confirmar()
    flash(MSG_REMOVIDO, 'success')                      # US10 CA3
    return redirect(url_for('sacola.ver'))
