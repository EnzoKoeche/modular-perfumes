"""Um teste por critério de aceite das user stories da 1ª Sprint."""
import re

import requests

RESPOSTAS_COMPLETAS = {  # alternativas da carga inicial (perguntas 1 a 10 são obrigatórias; a 11 não)
    'pergunta_1': '1', 'pergunta_2': ['4', '7'], 'pergunta_3': ['9', '13'], 'pergunta_4': '15', 'pergunta_5': '19',
    'pergunta_6': '22', 'pergunta_7': '26', 'pergunta_8': '28', 'pergunta_9': '31', 'pergunta_10': '35',
}


def cadastrar(client, email='cliente@teste.com', senha='senha-segura'):
    return client.post('/cadastro', data={'nome': 'Cliente', 'email': email, 'senha': senha, 'aceite': 'on'})


# ---------------------------------------------------------------- US1 — cadastro do cliente

def test_us1_ca1_cadastro_grava_cliente_com_hash_e_leva_ao_questionario(client, banco):
    resp = cadastrar(client)
    assert resp.status_code == 302 and resp.headers['Location'].endswith('/questionario/')
    u = banco("SELECT perfil, senha_hash FROM usuario WHERE email = 'cliente@teste.com'")[0]
    assert u['perfil'] == 'CLIENTE' and u['senha_hash'] != 'senha-segura' and len(u['senha_hash']) > 40


def test_us1_ca2_email_ja_cadastrado(client, banco):
    cadastrar(client)
    client.post('/sair')
    resp = cadastrar(client)
    assert resp.status_code == 400 and 'Este e-mail já está cadastrado' in resp.get_data(as_text=True)
    assert banco("SELECT COUNT(*) AS n FROM usuario")[0]['n'] == 1


def test_us1_ca3_campo_obrigatorio_ou_senha_curta(client, banco):
    resp = client.post('/cadastro', data={'nome': '', 'email': 'x@teste.com', 'senha': '123', 'aceite': 'on'})
    html = resp.get_data(as_text=True)
    assert resp.status_code == 400 and 'is-invalid' in html and 'pelo menos 8 caracteres' in html
    assert banco("SELECT COUNT(*) AS n FROM usuario")[0]['n'] == 0


# ---------------------------------------------------------------- US2 — login

def test_us2_ca1_login_com_questionario_concluido_vai_para_o_perfil(client):
    cadastrar(client)
    client.post('/questionario/', data={**RESPOSTAS_COMPLETAS, 'acao': 'concluir'})
    client.post('/sair')
    resp = client.post('/login', data={'email': 'cliente@teste.com', 'senha': 'senha-segura'})
    assert resp.status_code == 302 and resp.headers['Location'].endswith('/inicio')


def test_us2_ca2_senha_errada_mensagem_generica(client):
    cadastrar(client)
    client.post('/sair')
    resp = client.post('/login', data={'email': 'cliente@teste.com', 'senha': 'errada123'})
    resp_email = client.post('/login', data={'email': 'naoexiste@teste.com', 'senha': 'senha-segura'})
    for r in (resp, resp_email):
        assert r.status_code == 401 and 'E-mail ou senha inválidos' in r.get_data(as_text=True)


def test_us2_ca3_sem_questionario_vai_para_o_questionario(client):
    cadastrar(client)
    client.post('/sair')
    resp = client.post('/login', data={'email': 'cliente@teste.com', 'senha': 'senha-segura'})
    assert resp.headers['Location'].endswith('/questionario/')
    assert client.get('/inicio').headers['Location'].endswith('/questionario/')   # consultor bloqueado


def test_rnf05_bloqueio_apos_cinco_tentativas(client):
    cadastrar(client)
    client.post('/sair')
    for _ in range(5):
        client.post('/login', data={'email': 'cliente@teste.com', 'senha': 'errada123'})
    resp = client.post('/login', data={'email': 'cliente@teste.com', 'senha': 'senha-segura'})
    assert 'Muitas tentativas' in resp.get_data(as_text=True)


# ---------------------------------------------------------------- US3 — questionário de perfil

def test_us3_ca1_concluir_gera_perfil_e_libera_consultor(client, banco):
    cadastrar(client)
    resp = client.post('/questionario/', data={**RESPOSTAS_COMPLETAS, 'acao': 'concluir'})
    assert resp.status_code == 302 and resp.headers['Location'].endswith('/inicio')
    perfil = banco("SELECT id, nivel_conhecimento FROM perfil_olfativo")[0]
    assert perfil['nivel_conhecimento'] == 'INICIANTE'
    afinidades = {r['nome']: float(r['afinidade']) for r in banco(
        'SELECT f.nome, pf.afinidade FROM perfil_familia pf JOIN familia_olfativa f ON f.id = pf.familia_id')}
    assert afinidades['Fresco/Cítrico'] == 12.0 and afinidades['Aquático'] == 10.0
    assert 'Seu perfil olfativo' in client.get('/inicio').get_data(as_text=True)


def test_us3_ca2_pergunta_obrigatoria_sem_resposta_nao_conclui(client, banco):
    cadastrar(client)
    parcial = {k: v for k, v in RESPOSTAS_COMPLETAS.items() if k != 'pergunta_3'}
    resp = client.post('/questionario/', data={**parcial, 'acao': 'concluir'})
    assert resp.status_code == 400 and 'pergunta-pendente' in resp.get_data(as_text=True)
    assert banco("SELECT COUNT(*) AS n FROM perfil_olfativo")[0]['n'] == 0
    assert banco("SELECT concluida_em FROM resposta_questionario")[0]['concluida_em'] is None


def test_us3_ca3_retoma_da_primeira_pergunta_sem_resposta(client, banco):
    cadastrar(client)
    client.post('/questionario/', data={'pergunta_1': '2', 'pergunta_2': '5', 'acao': 'salvar'})
    client.post('/sair')
    client.post('/login', data={'email': 'cliente@teste.com', 'senha': 'senha-segura'})
    html = client.get('/questionario/').get_data(as_text=True)
    trecho = html.split('id="pergunta-3"')[0].rsplit('<fieldset', 1)[1]
    assert 'pergunta-continuar' in trecho                       # destaca a pergunta 3
    assert re.search(r'id="alt-2" value="2"\s+checked', html)                  # resposta salva volta marcada
    assert banco("SELECT COUNT(*) AS n FROM resposta_item")[0]['n'] == 2


# ---------------------------------------------------------------- US4 — perguntas do questionário

def test_us4_ca1_cadastra_pergunta_ativa_com_alternativas(admin, banco):
    resp = admin.post('/admin/perguntas/nova', data={
        'enunciado': 'Você usa perfume todos os dias?', 'tipo': 'UNICA', 'ordem': '6', 'obrigatoria': 'on',
        'alternativas': 'Sim\nNão\nÀs vezes'})
    assert resp.status_code == 302
    p = banco("SELECT id, ativa, ordem FROM pergunta WHERE enunciado = 'Você usa perfume todos os dias?'")[0]
    assert p['ativa'] == 1 and p['ordem'] == 6
    assert banco("SELECT COUNT(*) AS n FROM alternativa WHERE pergunta_id = %s", (p['id'],))[0]['n'] == 3
    assert 'Você usa perfume todos os dias?' in admin.get('/admin/perguntas').get_data(as_text=True)


def test_us4_ca2_sem_enunciado_ou_com_menos_de_duas_alternativas(admin, banco):
    for dados in ({'enunciado': '', 'alternativas': 'A\nB'}, {'enunciado': 'Pergunta', 'alternativas': 'Só uma'}):
        resp = admin.post('/admin/perguntas/nova', data={**dados, 'tipo': 'UNICA'})
        assert resp.status_code == 400
        assert 'Informe o enunciado e pelo menos duas alternativas' in resp.get_data(as_text=True)
    assert banco("SELECT COUNT(*) AS n FROM pergunta")[0]['n'] == 11


def test_us4_ca3_excluir_pergunta_respondida_desativa(client, app, banco):
    cadastrar(client)
    client.post('/questionario/', data={'pergunta_1': '1', 'acao': 'salvar'})
    admin = app.test_client()
    from werkzeug.security import generate_password_hash
    banco("INSERT INTO usuario (nome, email, senha_hash, perfil) VALUES ('Admin', 'admin@teste.com', %s, 'ADMIN')",
          (generate_password_hash('senha-admin', method='pbkdf2:sha256'),))
    admin.post('/login', data={'email': 'admin@teste.com', 'senha': 'senha-admin'})
    admin.post('/admin/perguntas/1/excluir')
    admin.post('/admin/perguntas/2/excluir')
    assert banco("SELECT ativa FROM pergunta WHERE id = 1")[0]['ativa'] == 0          # respondida: desativada
    assert banco("SELECT COUNT(*) AS n FROM pergunta WHERE id = 2")[0]['n'] == 0      # sem respostas: excluída
    assert banco("SELECT COUNT(*) AS n FROM resposta_item WHERE pergunta_id = 1")[0]['n'] == 1
    assert 'Quanto você entende de perfumes?' not in client.get('/questionario/').get_data(as_text=True)


def test_us4_alterar_mantem_alternativas_e_pesos(admin, banco):
    resp = admin.post('/admin/perguntas/5/editar', data={
        'enunciado': 'Em que clima você usaria?', 'tipo': 'UNICA', 'ordem': '5', 'obrigatoria': 'on',
        'alternativas': 'Calor\nFrio\nUso o ano todo\nMeia-estação'})
    assert resp.status_code == 302
    assert banco("SELECT enunciado FROM pergunta WHERE id = 5")[0]['enunciado'] == 'Em que clima você usaria?'
    assert banco("SELECT COUNT(*) AS n FROM alternativa_peso WHERE alternativa_id = 19")[0]['n'] == 2
    assert banco("SELECT COUNT(*) AS n FROM alternativa WHERE pergunta_id = 5")[0]['n'] == 4


def test_cliente_nao_acessa_area_admin(client):
    cadastrar(client)
    assert client.get('/admin/perguntas').status_code == 403


# ---------------------------------------------------------------- US5 — importação do catálogo

def test_us5_ca1_importa_perfumes_com_notas_acordes_e_log(admin, banco):
    resp = admin.post('/admin/catalogo', data={'marca': 'Casa Demo', 'limite': '10'})
    assert resp.status_code == 302
    assert banco("SELECT COUNT(*) AS n FROM perfume")[0]['n'] == 3
    assert banco("SELECT COUNT(*) AS n FROM perfume_nota")[0]['n'] > 0
    assert banco("SELECT intensidade FROM perfume_acorde pa JOIN acorde a ON a.id = pa.acorde_id "
                 "WHERE a.nome = 'citrus'")[0]['intensidade'] == 'Dominant'
    log = banco("SELECT status, qtd_incluidos FROM importacao_catalogo")[0]
    assert log == {'status': 'CONCLUIDA', 'qtd_incluidos': 3}
    assert 'Brisa de Bergamota' in admin.get('/admin/catalogo').get_data(as_text=True)


def test_us5_ca2_api_fora_do_ar_ou_chave_recusada_mantem_catalogo(admin, app, banco, monkeypatch):
    admin.post('/admin/catalogo', data={'marca': 'Casa Demo'})
    app.config.update(CATALOGO_PROVEDOR='fragella', FRAGELLA_API_KEY='')
    admin.post('/admin/catalogo', data={'marca': 'Casa Demo'})                  # sem chave

    class Resposta401:
        status_code = 401
    app.config['FRAGELLA_API_KEY'] = 'chave-invalida'
    monkeypatch.setattr(requests, 'get', lambda *a, **k: Resposta401())
    admin.post('/admin/catalogo', data={'marca': 'Casa Demo'})                  # chave recusada

    def fora_do_ar(*a, **k):
        raise requests.ConnectionError('sem rede')
    monkeypatch.setattr(requests, 'get', fora_do_ar)
    admin.post('/admin/catalogo', data={'marca': 'Casa Demo'})                  # API fora do ar

    logs = banco("SELECT status, mensagem_erro FROM importacao_catalogo ORDER BY id")
    assert [l['status'] for l in logs] == ['CONCLUIDA', 'FALHOU', 'FALHOU', 'FALHOU']
    assert 'não configurada' in logs[1]['mensagem_erro']
    assert 'recusou a chave' in logs[2]['mensagem_erro']
    assert 'indisponível' in logs[3]['mensagem_erro']
    assert banco("SELECT COUNT(*) AS n FROM perfume")[0]['n'] == 3


def test_us5_ca3_reimportar_atualiza_sem_duplicar(admin, banco):
    admin.post('/admin/catalogo', data={'marca': 'Casa Demo'})
    admin.post('/admin/catalogo', data={'marca': 'Casa Demo'})
    assert banco("SELECT COUNT(*) AS n FROM perfume")[0]['n'] == 3
    ultimo = banco("SELECT qtd_incluidos, qtd_atualizados FROM importacao_catalogo ORDER BY id DESC LIMIT 1")[0]
    assert ultimo == {'qtd_incluidos': 0, 'qtd_atualizados': 3}


def test_acentos_gravados_corretamente(client, banco):
    """O script SQL declara utf8mb4; acentos não podem virar "Ã©" no banco."""
    assert banco("SELECT nome FROM familia_olfativa WHERE id = 2")[0]['nome'] == 'Fresco/Cítrico'
    assert 'você' in banco("SELECT enunciado FROM pergunta WHERE id = 1")[0]['enunciado']
