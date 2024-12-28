FROM python:3.10-slim

WORKDIR /app

# Установка системных зависимостей и ODBC драйвера
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        gnupg2 \
        apt-transport-https && \
    # Добавление репозитория Microsoft
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    # Удаление старых пакетов ODBC
    apt-get update && \
    apt-get remove -y unixodbc unixodbc-dev odbcinst odbcinst1debian2 libodbc1 && \
    apt-get autoremove -y && \
    # Установка новых пакетов ODBC
    ACCEPT_EULA=Y apt-get install -y --no-install-recommends \
        msodbcsql17 \
        mssql-tools \
        unixodbc-dev && \
    # Создание символических ссылок для инструментов SQL
    ln -fsv /opt/mssql-tools/bin/* /usr/bin/ && \
    # Установка build-essential
    apt-get install -y --no-install-recommends build-essential && \
    # Очистка
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Копирование и установка зависимостей Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование файлов приложения
COPY . .

ENV FLASK_APP=app.py \
    FLASK_RUN_HOST=0.0.0.0 \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]