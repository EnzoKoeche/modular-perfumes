"""Testes contra um MySQL de verdade (o do docker-compose), num banco separado: modular_perfumes_teste.

Rodar:  docker compose up -d db  &&  pytest
"""
import os
import pathlib

import pymysql
import pytest
from werkzeug.security import generate_password_hash

from app import create_app

RAIZ = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = RAIZ / 'entregas' / 'sql' / 'modular_perfumes_sprint1.sql'
BANCO_TESTE = 'modular_perfumes_teste'
CONEXAO = dict(host=os.getenv('MYSQL_HOST', '127.0.0.1'), port=int(os.getenv('MYSQL_PORT', '3307')),
               user='root', password=os.getenv('MYSQL_ROOT_PASSWORD', 'root_dev'), charset='utf8mb4')


def recriar_banco():
    sql = SCRIPT.read_text(encoding='utf-8')
    sql = sql.replace('CREATE DATABASE IF NOT EXISTS modular_perfumes', f'CREATE DATABASE IF NOT EXISTS {BANCO_TESTE}')
    sql = sql.replace('USE modular_perfumes;', f'USE {BANCO_TESTE};')
    con = pymysql.connect(client_flag=pymysql.constants.CLIENT.MULTI_STATEMENTS, autocommit=True, **CONEXAO)
    try:
        with con.cursor() as cur:
            cur.execute(sql)
            while cur.nextset():
                pass
    finally:
        con.close()


@pytest.fixture
def app():
    recriar_banco()
    return create_app({
        'TESTING': True, 'WTF_CSRF_ENABLED': False, 'SECRET_KEY': 'teste',
        'MYSQL_HOST': CONEXAO['host'], 'MYSQL_PORT': CONEXAO['port'],
        'MYSQL_USER': CONEXAO['user'], 'MYSQL_PASSWORD': CONEXAO['password'], 'MYSQL_DATABASE': BANCO_TESTE,
        'CATALOGO_PROVEDOR': 'exemplo', 'FRAGELLA_API_KEY': '',
    })


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def banco():
    """Consulta direta ao banco de teste, para conferir o que a aplicação gravou."""
    def consultar(sql, params=()):
        con = pymysql.connect(database=BANCO_TESTE, cursorclass=pymysql.cursors.DictCursor, **CONEXAO)
        try:
            with con.cursor() as cur:
                cur.execute(sql, params)
                resultado = cur.fetchall()
            con.commit()
            return resultado
        finally:
            con.close()
    return consultar


@pytest.fixture
def admin(client, banco):
    banco("INSERT INTO usuario (nome, email, senha_hash, perfil) VALUES ('Admin', 'admin@teste.com', %s, 'ADMIN')",
          (generate_password_hash('senha-admin', method='pbkdf2:sha256'),))
    client.post('/login', data={'email': 'admin@teste.com', 'senha': 'senha-admin'})
    return client
