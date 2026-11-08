# Gerar a apresentação da 2ª Sprint (projeto completo, US1 a US10)

Com o banco no ar (`docker compose up -d db`) e o Playwright no `.venv` (`pip install playwright && python -m playwright install chromium`):

```bash
cd entregas/apresentacao/fonte_sprint2
python servidor_demo.py &                   # site em http://127.0.0.1:5050
python capturar.py                          # prints em img/ e consultas em evidencias.json
python montar.py ../Modular_Perfumes_Apresentacao_Sprint2.pdf
```

- `capturar.py` cria um administrador temporário (apagado no fim) e a cliente fictícia "Marina Demo", importa o
  catálogo do provedor do `.env` e percorre cada critério de aceite. Para importar marcas reais com
  `CATALOGO_PROVEDOR=fragella`, passe as marcas: `python capturar.py Dior Chanel`.
- Sem `ANTHROPIC_API_KEY` no `.env`, o `servidor_demo.py` usa um **modelo simulado** (o mesmo tipo de dublê dos
  testes): as ferramentas do agente rodam de verdade no banco, só o texto da resposta é fixo. O PDF avisa isso no
  slide do consultor. Com a chave, quem responde é o Claude.
