"""US10 — adicionar e remover perfumes da sacola (um teste por critério de aceite)."""
from test_sprint1 import cadastrar
from test_sprint2 import cliente_com_perfil, importar_exemplo


def perfume_id(banco, api_id='exemplo-002'):
    return banco('SELECT id FROM perfume WHERE api_id = %s', (api_id,))[0]['id']


def test_ca1_adiciona_e_lista_na_sacola(admin, app, banco):
    importar_exemplo(admin)
    c = cliente_com_perfil(app)
    pid = perfume_id(banco)
    html = c.post(f'/sacola/adicionar/{pid}', follow_redirects=True).get_data(as_text=True)
    assert 'Noite de Âmbar entrou na sacola.' in html and 'Minha sacola' in html
    assert len(banco('SELECT 1 FROM sacola_item WHERE perfume_id = %s', (pid,))) == 1


def test_ca2_mesmo_perfume_nao_duplica(admin, app, banco):
    importar_exemplo(admin)
    c = cliente_com_perfil(app)
    pid = perfume_id(banco)
    c.post(f'/sacola/adicionar/{pid}')
    html = c.post(f'/sacola/adicionar/{pid}', follow_redirects=True).get_data(as_text=True)
    assert 'Este perfume já está na sua sacola.' in html
    assert len(banco('SELECT 1 FROM sacola_item WHERE perfume_id = %s', (pid,))) == 1


def test_ca3_remove_da_sacola(admin, app, banco):
    importar_exemplo(admin)
    c = cliente_com_perfil(app)
    pid = perfume_id(banco)
    c.post(f'/sacola/adicionar/{pid}')
    html = c.post(f'/sacola/remover/{pid}', follow_redirects=True).get_data(as_text=True)
    assert 'Perfume removido da sacola.' in html and 'Sua sacola está vazia' in html
    assert banco('SELECT 1 FROM sacola_item') == ()


def test_oculto_nao_entra_e_fica_indisponivel_na_sacola(admin, app, banco):
    importar_exemplo(admin)
    c = cliente_com_perfil(app)
    pid, oculto = perfume_id(banco), perfume_id(banco, 'exemplo-003')
    banco('UPDATE perfume SET visivel = 0 WHERE id = %s', (oculto,))
    assert c.post(f'/sacola/adicionar/{oculto}').status_code == 404               # RN-08
    c.post(f'/sacola/adicionar/{pid}')
    banco('UPDATE perfume SET visivel = 0 WHERE id = %s', (pid,))
    assert 'Indisponível' in c.get('/sacola/').get_data(as_text=True)


def test_sacola_bloqueada_sem_questionario(client):
    cadastrar(client)
    assert '/questionario' in client.get('/sacola/').headers['Location']             # RN-04


def test_botao_da_sacola_na_ficha_e_no_cartao_de_recomendacao(admin, app, banco):
    importar_exemplo(admin)
    c = cliente_com_perfil(app)
    pid = perfume_id(banco)
    assert f'/sacola/adicionar/{pid}' in c.get(f'/perfumes/{pid}').get_data(as_text=True)          # US7 CA1
    assert '/sacola/adicionar/' not in app.test_client().get(f'/perfumes/{pid}').get_data(as_text=True)  # US7 CA3
    uid = banco("SELECT id FROM usuario WHERE email = 'cliente@teste.com'")[0]['id']
    banco('INSERT INTO conversa (usuario_id) VALUES (%s)', (uid,))
    cid = banco('SELECT MAX(id) AS id FROM conversa')[0]['id']
    banco("INSERT INTO recomendacao (conversa_id, perfume_id, posicao, justificativa) VALUES (%s, %s, 1, 'teste')",
          (cid, pid))
    assert f'/sacola/adicionar/{pid}' in c.get('/consultor/').get_data(as_text=True)               # US9 CA1
