"""US6 — manter os pesos das alternativas por família olfativa (um teste por critério de aceite)."""


def pesos_da_pergunta(banco, pergunta_id=2):
    return banco('SELECT ap.alternativa_id, ap.familia_id, ap.peso FROM alternativa_peso ap '
                 'JOIN alternativa a ON a.id = ap.alternativa_id WHERE a.pergunta_id = %s '
                 'ORDER BY ap.alternativa_id, ap.familia_id', (pergunta_id,))


def formulario(banco, pergunta_id=2, valor='0'):
    """Todos os campos peso_<alternativa>_<familia> da pergunta, com o mesmo valor."""
    alternativas = banco('SELECT id FROM alternativa WHERE pergunta_id = %s AND ativa = 1', (pergunta_id,))
    familias = banco('SELECT id FROM familia_olfativa')
    return {f'peso_{a["id"]}_{f["id"]}': valor for a in alternativas for f in familias}


def test_ca1_grava_pesos_e_exibe_mensagem(admin, banco):
    assert 'Salvar pesos' in admin.get('/admin/perguntas/2/pesos').get_data(as_text=True)
    dados = formulario(banco, valor='1')
    alt = banco('SELECT MIN(id) AS id FROM alternativa WHERE pergunta_id = 2')[0]['id']
    dados[f'peso_{alt}_1'] = '10'
    html = admin.post('/admin/perguntas/2/pesos', data=dados, follow_redirects=True).get_data(as_text=True)
    assert 'Pesos atualizados' in html
    gravados = pesos_da_pergunta(banco)
    assert len(gravados) == len(dados)
    assert {(p['alternativa_id'], p['familia_id']): int(p['peso']) for p in gravados}[(alt, 1)] == 10


def test_ca2_peso_invalido_nao_grava_nada(admin, banco):
    antes = pesos_da_pergunta(banco)
    campo = next(iter(formulario(banco)))
    for invalido in ('-1', '11', 'abc', '2.5'):
        dados = formulario(banco, valor='5')
        dados[campo] = invalido
        resp = admin.post('/admin/perguntas/2/pesos', data=dados)
        assert resp.status_code == 400 and 'Use pesos inteiros de 0 a 10' in resp.get_data(as_text=True)
    assert pesos_da_pergunta(banco) == antes


def test_ca3_alternativa_so_com_zeros_grava_e_avisa(admin, banco):
    dados = formulario(banco, valor='2')
    alt = banco('SELECT id, texto FROM alternativa WHERE pergunta_id = 2 ORDER BY ordem, id LIMIT 1')[0]
    for campo in dados:
        if campo.startswith(f'peso_{alt["id"]}_'):
            dados[campo] = '0'
    html = admin.post('/admin/perguntas/2/pesos', data=dados, follow_redirects=True).get_data(as_text=True)
    assert 'Pesos atualizados' in html and 'não soma afinidade com nenhuma família' in html
    assert banco('SELECT 1 FROM alternativa_peso WHERE alternativa_id = %s', (alt['id'],)) == ()
    assert len(pesos_da_pergunta(banco)) > 0


def test_lista_de_perguntas_tem_botao_pesos(admin):
    assert '/admin/perguntas/2/pesos' in admin.get('/admin/perguntas').get_data(as_text=True)


def test_ca2_tambem_e_validado_no_navegador(admin):
    html = admin.get('/admin/perguntas/2/pesos').get_data(as_text=True)
    assert 'novalidate' in html and 'id="erro-pesos"' in html and "'Use pesos inteiros de 0 a 10'" in html
