# Dockerfile

# 1. Imagem Base: Python 3.11 versão "slim" (mais leve, baseada em Debian)
FROM python:3.11-slim

# 2. Configurações de Ambiente para Python
# PYTHONDONTWRITEBYTECODE: Evita criar pastas __pycache__ desnecessárias
# PYTHONUNBUFFERED: Garante que os logs apareçam instantaneamente no console (essencial para debug)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 3. Define o diretório de trabalho dentro do container
WORKDIR /app

# 4. Instalar dependências do sistema operacional
# (Opcional, mas útil se precisarmos de compiladores ou ferramentas de rede como curl/ping para debug)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 5. Copiar apenas o arquivo de requisitos primeiro (Estratégia de Cache)
# Se você mudar o código mas não os requisitos, o Docker não reinstala tudo de novo.
COPY requirements.txt .

# 6. Instalar as dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 7. Copiar o restante do código do projeto para dentro do container
COPY . .

# 8. Expor a porta que o FastAPI usa (apenas para documentação, o docker-compose que libera de verdade)
EXPOSE 8000

# 9. Comando para iniciar a aplicação
# --host 0.0.0.0 é crucial em containers para aceitar conexões externas
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]