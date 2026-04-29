FROM python:3.10-slim

# Definir diretório de trabalho
WORKDIR /app

# Definir variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar os arquivos do projeto
COPY . .

# Expor a porta que a aplicação vai rodar
EXPOSE 8000

# Comando para rodar a aplicação
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
