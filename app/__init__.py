"""Modular Perfumes — aplicação Flask da 1ª Sprint.

Rodar:  flask --app app run --port 5050 --debug
"""
import os

import click
from dotenv import load_dotenv
from flask import Flask, render_template
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash

from . import db

csrf = CSRFProtect()


def create_app(config=None):
    load_dotenv()
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.getenv('SECRET_KEY', 'dev-troque-no-env'),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        MYSQL_HOST=os.getenv('MYSQL_HOST', '127.0.0.1'),
        MYSQL_PORT=int(os.getenv('MYSQL_PORT', '3307')),
        MYSQL_USER=os.getenv('MYSQL_USER', 'modular'),
        MYSQL_PASSWORD=os.getenv('MYSQL_PASSWORD', 'modular_dev'),
        MYSQL_DATABASE=os.getenv('MYSQL_DATABASE', 'modular_perfumes'),
        CATALOGO_PROVEDOR=os.getenv('CATALOGO_PROVEDOR', 'exemplo'),
        FRAGELLA_API_KEY=os.getenv('FRAGELLA_API_KEY', ''),
    )
    if config:
        app.config.update(config)

    csrf.init_app(app)
    db.init_app(app)

    from .auth import METODO_HASH, bp as auth_bp, usuario_logado
    from .questionario import bp as questionario_bp
    from .cliente import bp as cliente_bp
    from .admin import bp as admin_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(questionario_bp)
    app.register_blueprint(cliente_bp)
    app.register_blueprint(admin_bp)

    @app.context_processor
    def injeta_usuario():
        return {'usuario': usuario_logado()}

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.cli.command('criar-admin')
    @click.argument('email')
    @click.argument('nome')
    @click.password_option()
    def criar_admin(email, nome, password):
        """Cria (ou promove) um usuário ADMIN."""
        if len(password) < 8:
            raise click.ClickException('A senha precisa ter pelo menos 8 caracteres.')
        existente = db.consultar_um('SELECT id FROM usuario WHERE email = %s', (email,))
        if existente:
            db.executar("UPDATE usuario SET perfil = 'ADMIN', senha_hash = %s WHERE id = %s",
                        (generate_password_hash(password, method=METODO_HASH), existente['id']))
        else:
            db.executar("INSERT INTO usuario (nome, email, senha_hash, perfil) VALUES (%s, %s, %s, 'ADMIN')",
                        (nome, email, generate_password_hash(password, method=METODO_HASH)))
        db.confirmar()
        click.echo(f'Administrador pronto: {email}')

    return app
