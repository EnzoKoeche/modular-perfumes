"""Vitrine de perfumes e consultor de IA (a API da Anthropic é simulada; nenhuma chamada real)."""
import json
from types import SimpleNamespace

from app import consultor
from test_sprint1 import RESPOSTAS_COMPLETAS, cadastrar


def importar_exemplo(admin):
    admin.post('/admin/catalogo', data={'marca': 'Casa Demo'})
    admin.post('/admin/catalogo', data={'marca': 'Atelier Exemplo'})


def cliente_com_perfil(app):
    c = app.test_client()
    cadastrar(c)
    c.post('/questionario/', data={**RESPOSTAS_COMPLETAS, 'acao': 'concluir'})
    return c


# ---------------------------------------------------------------- vitrine

def test_vitrine_publica_com_destaques_decadas_e_tabela(admin, app):
    importar_exemplo(admin)
    visitante = app.test_client()
    html = visitante.get('/perfumes/').get_data(as_text=True)
    assert 'Melhores de 2022' in html and 'Caramelo Salgado' in html          # ano mais recente com avaliação
    assert 'ANOS 2010' in html and 'ANOS 2020' in html                       # clássicos por década
    assert 'Todos os perfumes' in html and 'Noite de Âmbar' in html
    assert 'Mais bem avaliados' in visitante.get('/').get_data(as_text=True)


def test_vitrine_filtra_por_nome_e_genero(admin, app):
    importar_exemplo(admin)
    html = app.test_client().get('/perfumes/?q=cedro&genero=MASCULINO').get_data(as_text=True)
    tabela = html.split('id="todos"')[1]
    assert 'Cedro Urbano' in tabela and 'Brisa de Bergamota' not in tabela


def test_ficha_mostra_piramide_e_acordes(admin, app, banco):
    importar_exemplo(admin)
    pid = banco("SELECT id FROM perfume WHERE api_id = 'exemplo-002'")[0]['id']
    html = app.test_client().get(f'/perfumes/{pid}').get_data(as_text=True)
    assert 'Noite de Âmbar' in html and 'Notas de saída' in html and 'Cinnamon' in html and 'amber · dominant' in html
    assert app.test_client().get('/perfumes/99999').status_code == 404


# ---------------------------------------------------------------- ferramentas do agente

def test_ferramentas_leem_perfil_e_catalogo(admin, app, banco):
    importar_exemplo(admin)
    cliente_com_perfil(app)
    uid = banco("SELECT id FROM usuario WHERE email = 'cliente@teste.com'")[0]['id']
    with app.app_context():
        conversa_id = consultor.conversa_atual(uid)
        ferramentas = {f.name: f for f in consultor.criar_ferramentas(uid, conversa_id)}
        perfil = json.loads(ferramentas['obter_perfil_olfativo'].call({}))
        assert perfil['nivel_conhecimento'] == 'INICIANTE'
        assert perfil['afinidade_por_familia'][0]['familia'] == 'Fresco/Cítrico'
        assert any('investir' in r['enunciado'] for r in perfil['respostas_do_questionario'])
        achados = json.loads(ferramentas['buscar_perfumes'].call({'acordes': 'citrus,marine', 'limite': 5}))
        assert {p['nome'] for p in achados} == {'Brisa de Bergamota', 'Maré Alta'}
        erro = json.loads(ferramentas['registrar_recomendacao'].call({'perfume_id': 99999, 'justificativa': 'x'}))
        assert 'erro' in erro


# ---------------------------------------------------------------- rota do consultor

class RunnerFalso:
    """Imita o tool runner: usa a ferramenta de recomendação e devolve uma resposta final."""

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __iter__(self):
        ferramentas = {f.name: f for f in self.kwargs['tools']}
        achados = json.loads(ferramentas['buscar_perfumes'].call({'acordes': 'citrus'}))
        ferramentas['registrar_recomendacao'].call({'perfume_id': achados[0]['id'],
                                                     'justificativa': 'Cítrico e leve, como você pediu.'})
        yield SimpleNamespace(stop_reason='end_turn', content=[SimpleNamespace(type='text', text='Separei um cítrico.')],
                              usage=SimpleNamespace(input_tokens=1200, output_tokens=80, cache_read_input_tokens=900))


def cliente_falso(chamadas):
    def tool_runner(**kwargs):
        chamadas.append(kwargs)
        return RunnerFalso(**kwargs)
    return SimpleNamespace(beta=SimpleNamespace(messages=SimpleNamespace(tool_runner=tool_runner)))


def test_consultor_responde_registra_recomendacao_e_tokens(admin, app, banco, monkeypatch):
    importar_exemplo(admin)
    c = cliente_com_perfil(app)
    chamadas = []
    monkeypatch.setattr(consultor, 'cliente_anthropic', lambda: cliente_falso(chamadas))
    resp = c.post('/consultor/mensagem', json={'texto': 'Quero algo fresco para o trabalho'})
    dados = resp.get_json()
    assert resp.status_code == 200 and dados['texto'] == 'Separei um cítrico.'
    assert dados['recomendacoes'][0]['nome'] == 'Brisa de Bergamota'
    kwargs = chamadas[0]
    # o modelo vem da configuração (IA_MODELO no .env), então o teste não depende de qual é
    assert kwargs['model'] == app.config['IA_MODELO'] and kwargs['fallbacks'] == 'default'
    assert kwargs['messages'][-1] == {'role': 'user', 'content': 'Quero algo fresco para o trabalho'}
    assert kwargs['system'][0]['cache_control'] == {'type': 'ephemeral'}
    ia = banco("SELECT tokens_entrada, tokens_saida, tokens_cache FROM mensagem WHERE papel = 'ASSISTENTE'")[0]
    assert ia == {'tokens_entrada': 1200, 'tokens_saida': 80, 'tokens_cache': 900}
    assert 'Separei um cítrico.' in c.get('/consultor/').get_data(as_text=True)


def test_consultor_sem_chave_responde_indisponivel(admin, app, monkeypatch):
    c = cliente_com_perfil(app)
    monkeypatch.delenv('ANTHROPIC_API_KEY', raising=False)
    resp = c.post('/consultor/mensagem', json={'texto': 'oi'})
    assert resp.status_code == 503 and 'indisponível' in resp.get_json()['erro']


def test_consultor_bloqueado_sem_questionario(client):
    cadastrar(client)
    assert client.get('/consultor/').status_code == 403
    assert client.post('/consultor/mensagem', json={'texto': 'oi'}).status_code == 403
