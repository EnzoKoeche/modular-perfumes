# Gerar a apresentação da 1ª Sprint

Com o banco (`docker compose up -d db`) e o site (`flask --app app run --port 5050`) no ar, e o Playwright instalado no `.venv` (`pip install playwright && python -m playwright install chromium`):

```bash
cd entregas/apresentacao/fonte
python capturar.py "SENHA_DO_ADMIN"        # percorre as user stories e tira os prints (pasta img/)
python montar.py ../Modular_Perfumes_Apresentacao_Sprint1.pdf
```

`capturar.py` cria a cliente fictícia "Marina Demo", faz os fluxos de cada critério de aceite e guarda as consultas ao banco em `evidencias.json`; o que ele cria no admin (pergunta de teste) é desfeito no fim.
