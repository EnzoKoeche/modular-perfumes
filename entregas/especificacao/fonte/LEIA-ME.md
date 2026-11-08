# Especificação da 2ª Sprint

`especificacao_sprint2.py` gera `../Modular_Perfumes_Especificacao_do_Projeto_Sprint2.docx` a partir da versão entregue na
1ª Sprint (que não é alterada), com o Canvas PBB da Sprint 2, a US1 ajustada, as US6 a US10, o DER com as 21 tabelas,
o Artefato 7 (não se aplica) e o Artefato 8 (Diagramas de Atividades).

```bash
pip install python-docx pillow
python especificacao_sprint2.py
```

Depois abra no Word e responda "Sim" para atualizar os campos (numeração das figuras, sumário e índice de ilustrações);
o PDF de mesmo nome foi exportado pelo Word já com os campos atualizados.

As imagens vêm dos geradores: `entregas/pbb/fonte/pbb.py ... sprint2`, `entregas/der/fonte/render_der.py ... sprint2`
e `entregas/atividades/fonte/atividades.py` (os dois últimos precisam do Graphviz, comando `dot`).
