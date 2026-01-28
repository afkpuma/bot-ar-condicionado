"""
Testes automatizados para a interface Streamlit.
Usa a classe AppTest para simular interações do usuário sem navegador.
"""
from streamlit.testing.v1 import AppTest
import sys
import os

# Adiciona raiz ao path para imports funcionarem
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Timeout aumentado para o AppTest devido ao carregamento dos services
DEFAULT_TIMEOUT = 30


def test_app_loads_correctly():
    """Smoke test: Verifica se o app inicia sem erros e carrega o título."""
    at = AppTest.from_file("frontend/app.py", default_timeout=DEFAULT_TIMEOUT)
    at.run()
    assert not at.exception
    
    # O título está em um st.markdown com HTML customizado
    # Verificamos se existe pelo menos um elemento markdown na página
    assert len(at.markdown) > 0, "Nenhum elemento markdown encontrado no app."


def test_form_structure():
    """Verifica se o formulário e o botão existem."""
    at = AppTest.from_file("frontend/app.py", default_timeout=DEFAULT_TIMEOUT)
    at.run()
    
    # Verifica se existe pelo menos um botão (o submit)
    # Nota: Em versões recentes do AppTest, form_submit_button pode aparecer em .button
    assert len(at.button) > 0 or len(at.form) > 0


def test_initial_session_state():
    """Verifica se o app roda do início ao fim sem crashar."""
    at = AppTest.from_file("frontend/app.py", default_timeout=DEFAULT_TIMEOUT)
    at.run()
    assert not at.exception
