"""Entrada do site na Vercel (e em qualquer servidor WSGI): expõe o objeto `app` do Flask."""
from app import create_app

app = create_app()
