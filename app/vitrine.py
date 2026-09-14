"""Vitrine pública de perfumes: destaques do ano, clássicos por década, lista com filtros e ficha."""
from flask import Blueprint, render_template, request

from . import db
from .consultor import ficha

bp = Blueprint('vitrine', __name__, url_prefix='/perfumes')

POR_PAGINA = 20
COLUNAS = ('p.id, p.nome, p.ano, p.genero, p.imagem_url, p.avaliacao, p.concentracao, m.nome AS marca, '
           "(SELECT GROUP_CONCAT(a.nome ORDER BY a.nome SEPARATOR ', ') FROM perfume_acorde pa "
           ' JOIN acorde a ON a.id = pa.acorde_id WHERE pa.perfume_id = p.id) AS acordes')
ORDENACOES = {
    'avaliacao': 'p.avaliacao IS NULL, p.avaliacao DESC, p.nome',
    'recentes': 'p.ano IS NULL, p.ano DESC, p.nome',
    'nome': 'p.nome',
}


@bp.route('/')
def lista():
    ano_destaque = db.consultar_um('SELECT MAX(ano) AS ano FROM perfume WHERE visivel = 1 AND avaliacao IS NOT NULL')['ano']
    destaques = db.consultar(
        f'SELECT {COLUNAS} FROM perfume p JOIN marca m ON m.id = p.marca_id '
        'WHERE p.visivel = 1 AND p.ano = %s AND p.avaliacao IS NOT NULL ORDER BY p.avaliacao DESC LIMIT 8',
        (ano_destaque,)) if ano_destaque else []

    decadas = {}
    for linha in db.consultar(
            f'SELECT {COLUNAS}, FLOOR(p.ano / 10) * 10 AS decada FROM perfume p JOIN marca m ON m.id = p.marca_id '
            'WHERE p.visivel = 1 AND p.ano IS NOT NULL AND p.avaliacao IS NOT NULL '
            'ORDER BY decada DESC, p.avaliacao DESC'):
        grupo = decadas.setdefault(int(linha['decada']), [])
        if len(grupo) < 4:
            grupo.append(linha)

    busca = request.args.get('q', '').strip()
    genero = request.args.get('genero', '')
    ordem = request.args.get('ordem', 'avaliacao')
    pagina = max(1, request.args.get('pagina', 1, type=int))
    condicoes, params = ['p.visivel = 1'], []
    if busca:
        condicoes.append('(p.nome LIKE %s OR m.nome LIKE %s)')
        params += [f'%{busca}%', f'%{busca}%']
    if genero in ('MASCULINO', 'FEMININO', 'UNISSEX'):
        condicoes.append('p.genero = %s')
        params.append(genero)
    onde = ' AND '.join(condicoes)
    total = db.consultar_um(f'SELECT COUNT(*) AS n FROM perfume p JOIN marca m ON m.id = p.marca_id WHERE {onde}',
                            params)['n']
    perfumes = db.consultar(
        f'SELECT {COLUNAS} FROM perfume p JOIN marca m ON m.id = p.marca_id WHERE {onde} '
        f'ORDER BY {ORDENACOES.get(ordem, ORDENACOES["avaliacao"])} LIMIT %s OFFSET %s',
        (*params, POR_PAGINA, (pagina - 1) * POR_PAGINA))
    return render_template('vitrine/lista.html', destaques=destaques, ano_destaque=ano_destaque, decadas=decadas,
                           perfumes=perfumes, total=total, pagina=pagina, paginas=max(1, -(-total // POR_PAGINA)),
                           busca=busca, genero=genero, ordem=ordem)


@bp.route('/<int:perfume_id>')
def detalhe(perfume_id):
    p = ficha(perfume_id)
    if not p:
        return render_template('erro.html', codigo=404, mensagem='Perfume não encontrado.'), 404
    return render_template('vitrine/ficha.html', p=p)
