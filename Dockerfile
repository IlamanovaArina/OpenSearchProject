# Dockerfile
FROM python:3.11-slim

# Задаём рабочую директорию
WORKDIR /app

# Копируем только зависимостей сначала (кэширование)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY src/ ./src

# Устанавливаем PYTHONPATH, чтобы можно было импортировать myapp
ENV PYTHONPATH=/app/src

# Не запускаем от root
RUN useradd --create-home appuser && chown -R appuser /app
USER appuser

# ENTRYPOINT/команда запуска:
ENTRYPOINT ["python", "-m", "main"]
# Можно переопределить запуск через CMD, e.g. CMD ["--once"]
