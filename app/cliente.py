"""Páginas iniciais do cliente (perfil olfativo) e do lojista."""
from flask import Blueprint, redirect, render_template, url_for

from . import db
from .auth import perfil_obrigatorio, questionario_concluido, usuario_logado

bp = Blueprint('cliente', __name__)


@bp.route('/inicio')
@perfil_obrigatorio('CLIENTE')
def inicio():
    usuario = usuario_logado()
    if not questionario_concluido(usuario['id']):       # RN-04: sem questionário, sem consultor
        return redirect(url_for('questionario.responder'))
    perfil = db.consultar_um(
        'SELECT id, nivel_conhecimento, gerado_em FROM perfil_olfativo WHERE usuario_id = %s', (usuario['id'],))
    familias = db.consultar(
        'SELECT f.nome, f.descricao, pf.afinidade FROM perfil_familia pf '
        'JOIN familia_olfativa f ON f.id = pf.familia_id '
        'WHERE pf.perfil_id = %s ORDER BY pf.afinidade DESC', (perfil['id'],))
    maior = max((f['afinidade'] for f in familias), default=0) or 1
    return render_template('cliente/inicio.html', perfil=perfil, familias=familias, maior=maior)


@bp.route('/lojista')
@perfil_obrigatorio('LOJISTA')
def lojista():
    return render_template('cliente/lojista.html')
