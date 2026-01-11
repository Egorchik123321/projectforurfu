ContentHub — Интеллектуальный агрегатор персонального контента
ContentHub — это умная система для сбора, анализа и рекомендации образовательного контента. Сервис автоматически парсит статьи, видео и книги, определяет тематику с помощью NLP-анализа и предлагает персонализированные рекомендации на основе ваших интересов. Идеален для разработчиков, исследователей и всех, кто постоянно потребляет профессиональный контент.

Ссылка на рабочий проект: https://ваш-логин.pythonanywhere.com

Технологии
Python 3.11

Django 5.0

Django REST Framework 3.15

PostgreSQL 15

SpaCy 3.7 (NLP-обработка)

Celery 5.3 + Redis 7.0 (фоновые задачи)

Bootstrap 5 (интерфейс)

Chart.js (визуализация аналитики)

Скриншоты
Отсутствуют, будут добавлены после начала работ. Дедлайн проекта 20.01.2026.

Как запустить проект локально
1. Клонируйте репозиторий:
bash
git clone https://github.com/ваш-юзернейм/contenthub.git
cd contenthub
2. Создайте и активируйте виртуальное окружение:
bash
# Для Linux/Mac:
python -m venv venv
source venv/bin/activate

# Для Windows:
python -m venv venv
venv\Scripts\activate
3. Установите зависимости:
bash
pip install -r requirements.txt
4. Настройте базу данных и переменные окружения:
bash
# Создайте файл .env в корне проекта:
echo "SECRET_KEY=ваш-секретный-ключ-сгенерируйте-через-django-shell
DEBUG=True
DB_NAME=contenthub
DB_USER=ваш-пользователь
DB_PASSWORD=ваш-пароль
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/0
SPACY_MODEL=ru_core_news_sm" > .env
5. Создайте базу данных PostgreSQL:
bash
sudo -u postgres psql -c "CREATE DATABASE contenthub;"
sudo -u postgres psql -c "CREATE USER ваш_пользователь WITH PASSWORD 'ваш_пароль';"
sudo -u postgres psql -c "ALTER ROLE ваш_пользователь SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE ваш_пользователь SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE ваш_пользователь SET timezone TO 'UTC';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE contenthub TO ваш_пользователь;"
6. Загрузите NLP-модели:
bash
python -m spacy download ru_core_news_sm
python -m spacy download en_core_web_sm
7. Выполните миграции:
bash
python manage.py migrate
8. Создайте суперпользователя:
bash
python manage.py createsuperuser
9. Запустите Redis (для фоновых задач):
bash
# Для Ubuntu/Debian:
sudo systemctl start redis

# Для Mac:
brew services start redis

# Для Windows - установите Redis из Microsoft Archive
10. Запустите Celery worker (в отдельном терминале):
bash
celery -A config worker -l info
11. Запустите сервер разработки:
bash
python manage.py runserver