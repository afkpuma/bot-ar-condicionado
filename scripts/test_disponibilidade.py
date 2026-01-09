from datetime import datetime
from calendar_utils import horario_disponivel

calendar_id = "yamyokai@gmail.com"

data_teste = datetime(2026, 1, 10, 14, 0)

livre = horario_disponivel(calendar_id, data_teste, "limpeza")

print("Horário disponível?", livre)
