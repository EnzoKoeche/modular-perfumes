"""Área do administrador: US4 (manter perguntas do questionário) e US5 (importar o catálogo)."""
from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for

from . import catalogo, db
from .auth import perfil_obrigatorio
from .questionario import questionario_ativo

bp = Blueprint('admin', __name__, url_prefix='/admin')

MSG_PERGUNTA_INVALIDA = 'Informe o enunciado e pelo menos duas alternativas'


@bp.route('/')
@perfil_obrigatorio('ADMIN')
def inicio():
    resumo = db.consultar_um(
        'SELECT (SELECT COUNT(*) FROM usuario WHERE perfil = %s) AS clientes, '
        '(SELECT COUNT(*) FROM perfil_olfativo) AS perfis, '
        '(SELECT COUNT(*) FROM pergunta WHERE ativa = 1) AS perguntas, '
        '(SELECT COUNT(*) FROM perfume) AS perfumes', ('CLIENTE',))
    return render_template('admin/inicio.html', resumo=resumo)


# ---------------------------------------------------------------- US4: perguntas do questionário

def _ler_formulario():
    alternativas = []
    for linha in request.form.get('alternativas', '').splitlines():
        texto = linha.strip()[:150]
        if texto and texto not in alternativas:
            alternativas.append(texto)
    ordem = request.form.get('ordem', '').strip()
    return {
        'enunciado': request.form.get('enunciado', '').strip()[:255],
        'tipo': 'MULTIPLA' if request.form.get('tipo') == 'MULTIPLA' else 'UNICA',
        'ordem': int(ordem) if ordem.isdigit() else None,
        'obrigatoria': 1 if request.form.get('obrigatoria') else 0,
        'alternativas': alternativas,
    }


def _valido(dados):
    return bool(dados['enunciado']) and len(dados['alternativas']) >= 2      # US4 CA2 / RN-06


@bp.route('/perguntas')
@perfil_obrigatorio('ADMIN')
def perguntas():
    questionario = questionario_ativo()
    lista = db.consultar(
        'SELECT p.id, p.enunciado, p.tipo, p.ordem, p.obrigatoria, p.ativa, '
        '(SELECT COUNT(*) FROM alternativa a WHERE a.pergunta_id = p.id AND a.ativa = 1) AS qtd_alternativas, '
        '(SELECT COUNT(*) FROM resposta_item ri WHERE ri.pergunta_id = p.id) AS qtd_respostas '
        'FROM pergunta p WHERE p.questionario_id = %s ORDER BY p.ativa DESC, p.ordem, p.id',
        (questionario['id'],)) if questionario else []
    return render_template('admin/perguntas.html', questionario=questionario, perguntas=lista)


@bp.route('/perguntas/nova', methods=['GET', 'POST'])
@perfil_obrigatorio('ADMIN')
def nova_pergunta():
    questionario = questionario_ativo()
    proxima = db.consultar_um('SELECT COALESCE(MAX(ordem), 0) + 1 AS n FROM pergunta WHERE questionario_id = %s',
                              (questionario['id'],))['n']
    dados = {'enunciado': '', 'tipo': 'UNICA', 'ordem': proxima, 'obrigatoria': 1, 'alternativas': []}
    if request.method == 'POST':
        dados = _ler_formulario()
        dados['ordem'] = dados['ordem'] or proxima
        if not _valido(dados):
            flash(MSG_PERGUNTA_INVALIDA, 'danger')
            return render_template('admin/pergunta_form.html', dados=dados, pergunta=None), 400
        pergunta_id = db.executar(
            'INSERT INTO pergunta (questionario_id, enunciado, tipo, ordem, obrigatoria, ativa) '
            'VALUES (%s, %s, %s, %s, %s, 1)',
            (questionario['id'], dados['enunciado'], dados['tipo'], dados['ordem'], dados['obrigatoria']))
        for i, texto in enumerate(dados['alternativas'], 1):
            db.executar('INSERT INTO alternativa (pergunta_id, texto, ordem) VALUES (%s, %s, %s)',
                        (pergunta_id, texto, i))
        db.confirmar()                                                       # US4 CA1
        flash('Pergunta cadastrada.', 'success')
        return redirect(url_for('admin.perguntas'))
    return render_template('admin/pergunta_form.html', dados=dados, pergunta=None)


@bp.route('/perguntas/<int:pergunta_id>/editar', methods=['GET', 'POST'])
@perfil_obrigatorio('ADMIN')
def editar_pergunta(pergunta_id):
    pergunta = db.consultar_um('SELECT * FROM pergunta WHERE id = %s', (pergunta_id,))
    if not pergunta:
        return render_template('erro.html', codigo=404, mensagem='Pergunta não encontrada.'), 404
    atuais = db.consultar('SELECT id, texto, ativa FROM alternativa WHERE pergunta_id = %s ORDER BY ordem, id',
                          (pergunta_id,))
    dados = {**pergunta, 'alternativas': [a['texto'] for a in atuais if a['ativa']]}
    if request.method == 'POST':
        dados = _ler_formulario()
        dados['ordem'] = dados['ordem'] or pergunta['ordem']
        if not _valido(dados):
            flash(MSG_PERGUNTA_INVALIDA, 'danger')
            return render_template('admin/pergunta_form.html', dados=dados, pergunta=pergunta), 400
        db.executar('UPDATE pergunta SET enunciado = %s, tipo = %s, ordem = %s, obrigatoria = %s WHERE id = %s',
                    (dados['enunciado'], dados['tipo'], dados['ordem'], dados['obrigatoria'], pergunta_id))
        por_texto = {a['texto']: a for a in atuais}
        for i, texto in enumerate(dados['alternativas'], 1):
            if texto in por_texto:          # mantém o id (e os pesos) da alternativa que continua
                db.executar('UPDATE alternativa SET ordem = %s, ativa = 1 WHERE id = %s', (i, por_texto[texto]['id']))
            else:
                db.executar('INSERT INTO alternativa (pergunta_id, texto, ordem) VALUES (%s, %s, %s)',
                            (pergunta_id, texto, i))
        for texto, alt in por_texto.items():
            if texto not in dados['alternativas']:
                usada = db.consultar_um('SELECT 1 FROM resposta_item WHERE alternativa_id = %s LIMIT 1', (alt['id'],))
                if usada:
                    db.executar('UPDATE alternativa SET ativa = 0 WHERE id = %s', (alt['id'],))
                else:
                    db.executar('DELETE FROM alternativa WHERE id = %s', (alt['id'],))
        db.confirmar()
        flash('Pergunta alterada. Os próximos clientes já veem a versão nova.', 'success')
        return redirect(url_for('admin.perguntas'))
    return render_template('admin/pergunta_form.html', dados=dados, pergunta=pergunta)


@bp.route('/perguntas/<int:pergunta_id>/excluir', methods=['POST'])
@perfil_obrigatorio('ADMIN')
def excluir_pergunta(pergunta_id):
    respondida = db.consultar_um('SELECT 1 FROM resposta_item WHERE pergunta_id = %s LIMIT 1', (pergunta_id,))
    if respondida:                                                           # US4 CA3 / RN-05
        db.executar('UPDATE pergunta SET ativa = 0 WHERE id = %s', (pergunta_id,))
        flash('A pergunta já tinha respostas: foi desativada e não aparece mais para novos clientes.', 'warning')
    else:
        db.executar('DELETE FROM alternativa WHERE pergunta_id = %s', (pergunta_id,))
        db.executar('DELETE FROM pergunta WHERE id = %s', (pergunta_id,))
        flash('Pergunta excluída.', 'success')
    db.confirmar()
    return redirect(url_for('admin.perguntas'))


@bp.route('/perguntas/<int:pergunta_id>/reativar', methods=['POST'])
@perfil_obrigatorio('ADMIN')
def reativar_pergunta(pergunta_id):
    db.executar('UPDATE pergunta SET ativa = 1 WHERE id = %s', (pergunta_id,))
    db.confirmar()
    flash('Pergunta reativada.', 'success')
    return redirect(url_for('admin.perguntas'))


# ---------------------------------------------------------------- US5: importação do catálogo

@bp.route('/catalogo', methods=['GET', 'POST'])
@perfil_obrigatorio('ADMIN')
def catalogo_view():
    if request.method == 'POST':
        marca = request.form.get('marca', '').strip()
        limite = request.form.get('limite', '10')
        limite = max(1, min(50, int(limite))) if limite.isdigit() else 10
        if not marca:
            flash('Informe a marca a importar.', 'danger')
        else:
            ok, resultado = catalogo.importar(marca, limite)
            if ok:
                flash(f'Importação concluída: {resultado["incluido"]} perfume(s) incluído(s) e '
                      f'{resultado["atualizado"]} atualizado(s).', 'success')
            else:
                flash(f'A importação falhou e o catálogo atual foi mantido. Motivo: {resultado}', 'danger')
        return redirect(url_for('admin.catalogo_view'))

    logs = db.consultar('SELECT * FROM importacao_catalogo ORDER BY id DESC LIMIT 10')
    perfumes = db.consultar(
        'SELECT p.id, p.api_id, p.nome, p.genero, p.ano, p.imagem_url, p.fixacao, p.projecao, m.nome AS marca, '
        "(SELECT GROUP_CONCAT(n.nome ORDER BY pn.nivel, n.nome SEPARATOR ', ') FROM perfume_nota pn "
        ' JOIN nota_olfativa n ON n.id = pn.nota_id WHERE pn.perfume_id = p.id) AS notas, '
        "(SELECT GROUP_CONCAT(a.nome SEPARATOR ', ') FROM perfume_acorde pa "
        ' JOIN acorde a ON a.id = pa.acorde_id WHERE pa.perfume_id = p.id) AS acordes '
        'FROM perfume p JOIN marca m ON m.id = p.marca_id ORDER BY p.atualizado_em DESC, p.nome LIMIT 100')
    provedor = current_app.config['CATALOGO_PROVEDOR']
    return render_template('admin/catalogo.html', logs=logs, perfumes=perfumes, provedor=provedor,
                           chave_configurada=bool(current_app.config['FRAGELLA_API_KEY']))
