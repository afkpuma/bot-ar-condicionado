"""
Testes unitários para os handlers estáticos do bot.
"""
from services.state_handlers import handle_servico, handle_data

def test_handle_servico():
    assert handle_servico("11987654321", "limpeza") == "limpeza"
    assert handle_servico("11987654321", "quero uma manutenção") == "manutencao"
    assert handle_servico("11987654321", "instalar ar") == "instalacao"
    assert handle_servico("11987654321", "qualquer coisa") is None

def test_handle_data_valida():
    assert handle_data("15/01/2026") == "2026-01-15"
    assert handle_data("15-01-2026") == "2026-01-15"
    assert handle_data("15.01.2026") == "2026-01-15"

def test_handle_data_invalida():
    assert handle_data("data errada") is None
    assert handle_data("32/01/2026") is None
