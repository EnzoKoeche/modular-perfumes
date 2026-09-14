"""US5 — Importação do catálogo por uma API externa.

Provedores com a mesma interface `buscar_por_marca(marca, limite)`, que devolvem perfumes
no formato da Fragella API (https://api.fragella.com/api/v1):
- FragellaProvider: API real, exige FRAGELLA_API_KEY (plano grátis = 20 requisições/mês).
- ExemploProvider: perfumes fictícios de app/catalogo_exemplo.json, para desenvolver sem gastar cota.
"""
import json
import os

import requests
from flask import current_app

from . import db


class ErroCatalogo(Exception):
    """Falha da API de catálogo, com mensagem pronta para o log."""


class FragellaProvider:
    URL_BASE = 'https://api.fragella.com/api/v1'

    def __init__(self, chave):
        self.chave = chave

    def buscar_por_marca(self, marca, limite):
        if not self.chave:
            raise ErroCatalogo('Chave de acesso da API não configurada (FRAGELLA_API_KEY).')
        try:
            resp = requests.get(f'{self.URL_BASE}/brands/{requests.utils.quote(marca)}',
                                params={'limit': limite}, headers={'x-api-key': self.chave}, timeout=20)
        except requests.RequestException as erro:
            raise ErroCatalogo(f'API de catálogo indisponível: {erro.__class__.__name__}.') from erro
        if resp.status_code in (401, 403):
            raise ErroCatalogo('A API de catálogo recusou a chave de acesso.')
        if resp.status_code == 404:
            return []
        if resp.status_code >= 400:
            raise ErroCatalogo(f'A API de catálogo respondeu com erro {resp.status_code}.')
        dados = resp.json()
        return dados if isinstance(dados, list) else dados.get('data', [])


class ExemploProvider:
    ARQUIVO = os.path.join(os.path.dirname(__file__), 'catalogo_exemplo.json')

    def buscar_por_marca(self, marca, limite):
        with open(self.ARQUIVO, encoding='utf-8') as f:
            todos = json.load(f)
        return [p for p in todos if p.get('Brand', '').lower() == marca.lower()][:limite]


def provedor():
    if current_app.config['CATALOGO_PROVEDOR'] == 'fragella':
        return FragellaProvider(current_app.config['FRAGELLA_API_KEY'])
    return ExemploProvider()


# ---------------------------------------------------------------- conversão do formato da API

def _genero(valor):
    v = (valor or '').lower()
    if 'unisex' in v or 'unissex' in v:
        return 'UNISSEX'
    if 'women' in v or 'female' in v or 'fem' in v:
        return 'FEMININO'
    if 'men' in v or 'male' in v or 'masc' in v:
        return 'MASCULINO'
    return None


def _ano(valor):
    v = str(valor or '').strip()
    return int(v) if v.isdigit() and 1800 <= int(v) <= 2100 else None


def _url_imagem(valor):
    """Algumas URLs da Fragella têm '#' ou espaço no nome do arquivo (ex.: chanel-#5.jpg)."""
    url = str(valor or '').strip()
    return url.replace(' ', '%20').replace('#', '%23')[:500] or None


def _nota(valor):
    try:
        nota = float(str(valor).replace(',', '.'))
    except (TypeError, ValueError):
        return None
    return round(nota, 2) if 0 <= nota <= 10 else None


def _nomes(lista):
    """Notas podem vir como texto ou como objeto com nome e imageUrl."""
    nomes = []
    for item in lista or []:
        nome = item.get('name') or item.get('Name') if isinstance(item, dict) else item
        if nome and str(nome).strip():
            nomes.append(str(nome).strip()[:80])
    return nomes


def _id_por_nome(tabela, nome):
    linha = db.consultar_um(f'SELECT id FROM {tabela} WHERE nome = %s', (nome,))
    return linha['id'] if linha else db.executar(f'INSERT INTO {tabela} (nome) VALUES (%s)', (nome,))


def gravar_perfume(dado):
    """Insere ou atualiza um perfume pelo `_id` da API (RN-07). Devolve 'incluido' ou 'atualizado'."""
    api_id = str(dado.get('_id') or '').strip()
    nome = (dado.get('Name') or '').strip()
    marca_nome = (dado.get('Brand') or '').strip()
    if not api_id or not nome or not marca_nome:
        raise ErroCatalogo('A API devolveu um perfume sem identificador, nome ou marca.')

    marca = db.consultar_um('SELECT id, pais FROM marca WHERE nome = %s', (marca_nome,))
    if marca:
        marca_id = marca['id']
        if not marca['pais'] and dado.get('Country'):
            db.executar('UPDATE marca SET pais = %s WHERE id = %s', (dado['Country'][:60], marca_id))
    else:
        marca_id = db.executar('INSERT INTO marca (nome, pais) VALUES (%s, %s)',
                               (marca_nome[:80], (dado.get('Country') or '')[:60] or None))

    campos = {
        'marca_id': marca_id,
        'nome': nome[:150],
        'genero': _genero(dado.get('Gender')),
        'ano': _ano(dado.get('Year')),
        'imagem_url': _url_imagem(dado.get('Image URL')),
        'fixacao': (dado.get('Longevity') or None),
        'projecao': (dado.get('Sillage') or None),
        'concentracao': (dado.get('OilType') or None),
        'avaliacao': _nota(dado.get('rating')),
        'popularidade': (str(dado.get('Popularity') or '')[:30] or None),
    }
    existente = db.consultar_um('SELECT id, campos_revisados FROM perfume WHERE api_id = %s', (api_id,))
    if existente:                                       # US5 CA3: atualiza sem duplicar
        revisados = set(json.loads(existente['campos_revisados'] or '[]'))
        mudar = {k: v for k, v in campos.items() if k not in revisados}
        atribuicoes = [f'{k} = %s' for k in mudar] + ['atualizado_em = NOW()']
        db.executar('UPDATE perfume SET ' + ', '.join(atribuicoes) + ' WHERE id = %s',
                    (*mudar.values(), existente['id']))
        perfume_id, resultado = existente['id'], 'atualizado'
    else:
        perfume_id = db.executar(
            'INSERT INTO perfume (api_id, ' + ', '.join(campos) + ') VALUES (%s, ' +
            ', '.join(['%s'] * len(campos)) + ')', (api_id, *campos.values()))
        resultado = 'incluido'

    db.executar('DELETE FROM perfume_nota WHERE perfume_id = %s', (perfume_id,))
    notas = dado.get('Notes') or {}
    for nivel, chave in (('SAIDA', 'Top'), ('CORPO', 'Middle'), ('FUNDO', 'Base')):
        for nome_nota in dict.fromkeys(_nomes(notas.get(chave))):
            db.executar('INSERT INTO perfume_nota (perfume_id, nota_id, nivel) VALUES (%s, %s, %s)',
                        (perfume_id, _id_por_nome('nota_olfativa', nome_nota), nivel))

    db.executar('DELETE FROM perfume_acorde WHERE perfume_id = %s', (perfume_id,))
    intensidades = dado.get('Main Accords Percentage') or {}
    for nome_acorde in dict.fromkeys(a[:60] for a in _nomes(dado.get('Main Accords'))):
        intensidade = intensidades.get(nome_acorde)
        db.executar('INSERT INTO perfume_acorde (perfume_id, acorde_id, intensidade) VALUES (%s, %s, %s)',
                    (perfume_id, _id_por_nome('acorde', nome_acorde),
                     str(intensidade)[:20] if intensidade is not None else None))
    return resultado


def importar(marca, limite=10):
    """Registra a importação no log e grava os perfumes; se algo falhar, o catálogo fica como estava."""
    log_id = db.executar("INSERT INTO importacao_catalogo (origem, status) VALUES ('MANUAL', 'EM_ANDAMENTO')")
    db.confirmar()
    try:
        perfumes = provedor().buscar_por_marca(marca, limite)
        contagem = {'incluido': 0, 'atualizado': 0}
        for dado in perfumes:
            contagem[gravar_perfume(dado)] += 1
        db.executar("UPDATE importacao_catalogo SET status = 'CONCLUIDA', qtd_incluidos = %s, "
                    "qtd_atualizados = %s, finalizada_em = NOW() WHERE id = %s",
                    (contagem['incluido'], contagem['atualizado'], log_id))
        db.confirmar()                                  # US5 CA1
        return True, contagem
    except Exception as erro:                           # US5 CA2
        db.desfazer()
        mensagem = str(erro) if isinstance(erro, ErroCatalogo) else f'Erro inesperado: {erro.__class__.__name__}.'
        db.executar("UPDATE importacao_catalogo SET status = 'FALHOU', mensagem_erro = %s, "
                    "finalizada_em = NOW() WHERE id = %s", (mensagem, log_id))
        db.confirmar()
        return False, mensagem
