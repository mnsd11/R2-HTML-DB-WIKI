# Описание

Тут должна быть ваша база данных: ```FNLParm.bak```, а так же не удаляйте и ничего не изменяйте в файле: ```restore.sql```, это необходимо для Docker!

### Нужный .env конфиг-файл для Docker
```
DB_DRIVER={ODBC Driver 17 for SQL Server}
DB_SERVER=localhost
DB_NAME=FNLParm
DB_USER=sa
DB_PASSWORD=SqlServer2025!
PORT=5000
GITHUB_URL=https://raw.githubusercontent.com/Aksel911/R2-HTML-DB/main/static/
```