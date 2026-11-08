"""Sobe o site na porta 5050 para a captura dos prints.

Com ANTHROPIC_API_KEY no .env, o consultor usa o modelo de verdade.
Sem a chave, o MODELO é simulado (o mesmo tipo de dublê dos testes automáticos): as ferramentas do agente
rodam de verdade no banco (perfil, busca e registro das recomendações); só o texto da resposta é fixo.
O PDF avisa quando o print do consultor saiu do modo simulado.
"""
import json
import os
import pathlib
import sys
from types import SimpleNamespace

REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
os.chdir(REPO)

from dotenv import load_dotenv  # noqa: E402

load_dotenv(REPO / '.env')
SIMULADO = not os.getenv('ANTHROPIC_API_KEY')
if SIMULADO:
    os.environ['ANTHROPIC_API_KEY'] = 'simulada'   # só para a tela liberar o campo; a chave não é usada

from app import consultor, create_app  # noqa: E402

JUSTIFICATIVAS = {
    'Brisa de Bergamota': 'Abre com bergamota e limão, os cítricos que você marcou, e é leve o bastante para o trabalho.',
    'Maré Alta': 'Lembra brisa do mar e ar livre, como você pediu, e funciona bem no calor.',
}


class RunnerSimulado:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __iter__(self):
        f = {t.name: t for t in self.kwargs['tools']}
        f['obter_perfil_olfativo'].call({})
        achados = json.loads(f['buscar_perfumes'].call({'acordes': 'citrus,marine', 'limite': 4}))
        nomes = []
        for p in achados[:2]:
            f['registrar_recomendacao'].call({
                'perfume_id': p['id'],
                'justificativa': JUSTIFICATIVAS.get(p['nome'], 'Combina com as famílias frescas do seu perfil.')})
            nomes.append(p['nome'])
        texto = ('Pelo seu perfil, você está começando no mundo dos perfumes e gosta de cheiros frescos, '
                 'que lembram frutas cítricas e brisa do mar. Para o trabalho, no calor, o melhor é algo leve, '
                 'que não incomode quem está perto.\n\n'
                 f'Separei {" e ".join(nomes)}. O primeiro abre com cítricos: as "notas de saída" são o primeiro '
                 'cheiro que você sente ao borrifar. O segundo lembra mar e ar livre. Os dois são unissex e ficam '
                 'bem durante o dia.')
        yield SimpleNamespace(stop_reason='end_turn', content=[SimpleNamespace(type='text', text=texto)], usage=None)


if SIMULADO:
    consultor.cliente_anthropic = lambda: SimpleNamespace(
        beta=SimpleNamespace(messages=SimpleNamespace(tool_runner=lambda **kw: RunnerSimulado(**kw))))

if __name__ == '__main__':
    print('consultor:', 'MODELO SIMULADO' if SIMULADO else 'modelo real', flush=True)
    create_app().run(port=5050)
