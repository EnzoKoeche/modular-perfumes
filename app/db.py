"""Conexão com o MySQL usando SQL puro (PyMySQL).

Uma conexão por requisição, guardada em `flask.g`. Leituras e escritas usam
os helpers abaixo; quem grava chama `confirmar()` no fim da operação.
"""
import os
import tempfile

import pymysql
from flask import current_app, g

_arquivo_ca = None


def _ssl(cfg):
    """Banco na nuvem (ex.: Aiven) exige TLS: MYSQL_SSL_CA traz o certificado da CA em texto (PEM)."""
    global _arquivo_ca
    pem = cfg.get('MYSQL_SSL_CA', '').replace('\\n', '\n').strip()
    if not pem:
        return None
    if _arquivo_ca is None or not os.path.exists(_arquivo_ca):
        with tempfile.NamedTemporaryFile('w', suffix='.pem', delete=False) as f:
            f.write(pem + '\n')
            _arquivo_ca = f.name
    return {'ca': _arquivo_ca}


def conexao():
    if 'conexao' not in g:
        cfg = current_app.config
        g.conexao = pymysql.connect(
            host=cfg['MYSQL_HOST'], port=cfg['MYSQL_PORT'],
            user=cfg['MYSQL_USER'], password=cfg['MYSQL_PASSWORD'],
            database=cfg['MYSQL_DATABASE'], charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor, autocommit=False,
            ssl=_ssl(cfg),
        )
    return g.conexao


def consultar(sql, params=()):
    with conexao().cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()


def consultar_um(sql, params=()):
    with conexao().cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchone()


def executar(sql, params=()):
    """Executa INSERT/UPDATE/DELETE e devolve o id gerado (quando houver)."""
    with conexao().cursor() as cur:
        cur.execute(sql, params)
        return cur.lastrowid


def confirmar():
    conexao().commit()


def desfazer():
    conexao().rollback()


def _fechar(_erro=None):
    con = g.pop('conexao', None)
    if con is not None:
        con.close()


def init_app(app):
    app.teardown_appcontext(_fechar)
