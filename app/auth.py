"""US1 (cadastro do cliente) e US2 (login na plataforma), mais o controle de acesso por perfil."""
import re
from datetime import datetime, timedelta
from functools import wraps

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from . import db

bp = Blueprint('auth', __name__)

EMAIL_VALIDO = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
MAX_TENTATIVAS = 5          # RNF-05
METODO_HASH = 'pbkdf2:sha256'   # RNF-01: hash com salt; funciona em qualquer instalação do Python
BLOQUEIO = timedelta(minutes=15)


# ---------------------------------------------------------------- sessão e permissões

def usuario_logado():
    if 'usuario' not in g:
        uid = session.get('usuario_id')
        g.usuario = db.consultar_um(
            'SELECT id, nome, email, perfil FROM usuario WHERE id = %s AND ativo = 1', (uid,)) if uid else None
    return g.usuario


def login_obrigatorio(view):
    @wraps(view)
    def envolvida(*args, **kwargs):
        if not usuario_logado():
            flash('Entre na sua conta para continuar.', 'warning')
            return redirect(url_for('auth.login', proximo=request.path))
        return view(*args, **kwargs)
    return envolvida


def perfil_obrigatorio(*perfis):
    """Checa o perfil no servidor (RNF-03): esconder o botão na tela não basta."""
    def decorador(view):
        @wraps(view)
        @login_obrigatorio
        def envolvida(*args, **kwargs):
            if usuario_logado()['perfil'] not in perfis:
                return render_template('erro.html', codigo=403,
                                       mensagem='Você não tem permissão para acessar esta página.'), 403
            return view(*args, **kwargs)
        return envolvida
    return decorador


def questionario_concluido(usuario_id):
    return db.consultar_um(
        'SELECT 1 FROM perfil_olfativo WHERE usuario_id = %s', (usuario_id,)) is not None


def pagina_inicial(usuario):
    if usuario['perfil'] == 'ADMIN':
        return url_for('admin.inicio')
    if usuario['perfil'] == 'LOJISTA':
        return url_for('cliente.lojista')
    if not questionario_concluido(usuario['id']):       # US2 CA3 / RN-04
        return url_for('questionario.responder')
    return url_for('cliente.inicio')


def _entrar(usuario_id):
    session.clear()
    session['usuario_id'] = usuario_id
    g.pop('usuario', None)


# ---------------------------------------------------------------- US1: cadastro

@bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if usuario_logado():
        return redirect(pagina_inicial(usuario_logado()))
    dados, erros = {'nome': '', 'email': ''}, {}
    if request.method == 'POST':
        dados = {'nome': request.form.get('nome', '').strip(),
                 'email': request.form.get('email', '').strip().lower()}
        senha = request.form.get('senha', '')
        if not dados['nome']:
            erros['nome'] = 'Informe o seu nome.'
        if not EMAIL_VALIDO.match(dados['email']):
            erros['email'] = 'Informe um e-mail válido.'
        if len(senha) < 8:
            erros['senha'] = 'A senha precisa ter pelo menos 8 caracteres.'
        if not request.form.get('aceite'):
            erros['aceite'] = 'É preciso aceitar os termos de uso e a política de privacidade.'
        if not erros and db.consultar_um('SELECT 1 FROM usuario WHERE email = %s', (dados['email'],)):
            erros['email'] = 'Este e-mail já está cadastrado'           # US1 CA2
        if not erros:                                                  # US1 CA1
            novo_id = db.executar(
                "INSERT INTO usuario (nome, email, senha_hash, perfil, aceite_termos_em) "
                "VALUES (%s, %s, %s, 'CLIENTE', NOW())",
                (dados['nome'], dados['email'], generate_password_hash(senha, method=METODO_HASH)))
            db.confirmar()
            _entrar(novo_id)
            flash('Conta criada! Agora responda o questionário de perfil olfativo.', 'success')
            return redirect(url_for('questionario.responder'))
    return render_template('auth/cadastro.html', dados=dados, erros=erros), (400 if erros else 200)


# ---------------------------------------------------------------- US2: login e logout

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if usuario_logado():
        return redirect(pagina_inicial(usuario_logado()))
    email, erro = '', None
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')
        u = db.consultar_um(
            'SELECT id, senha_hash, ativo, tentativas_login, bloqueado_ate FROM usuario WHERE email = %s', (email,))
        agora = datetime.now()
        if u and u['bloqueado_ate'] and u['bloqueado_ate'] > agora:
            erro = 'Muitas tentativas seguidas. Tente novamente em alguns minutos.'
        elif u and u['ativo'] and check_password_hash(u['senha_hash'], senha):
            db.executar('UPDATE usuario SET tentativas_login = 0, bloqueado_ate = NULL WHERE id = %s', (u['id'],))
            db.confirmar()
            _entrar(u['id'])                                            # US2 CA1
            return redirect(pagina_inicial(usuario_logado()))
        else:
            if u:
                tentativas = u['tentativas_login'] + 1
                if tentativas >= MAX_TENTATIVAS:
                    db.executar('UPDATE usuario SET tentativas_login = 0, bloqueado_ate = %s WHERE id = %s',
                                (agora + BLOQUEIO, u['id']))
                else:
                    db.executar('UPDATE usuario SET tentativas_login = %s WHERE id = %s', (tentativas, u['id']))
                db.confirmar()
            erro = 'E-mail ou senha inválidos'                          # US2 CA2
    return render_template('auth/login.html', email=email, erro=erro), (401 if erro else 200)


@bp.route('/sair', methods=['POST'])
def sair():
    session.clear()
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('index'))
