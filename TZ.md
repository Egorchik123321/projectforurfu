1. Общие сведения
1.1 Наименование проекта
ContentHub — Веб-сервис для агрегации и организации персонального контента с рекомендательной системой

1.2 Цель проекта
Создать простую и функциональную платформу для сохранения, организации и поиска образовательного контента (статьи, видео, книги) с базовой системой рекомендаций на основе тегов.

1.3 Критерии успеха
Рабочий веб-интерфейс с адаптивным дизайном
Функциональная система добавления и фильтрации контента
Работающая рекомендательная система
Успешный деплой на PythonAnywhere
Наполненная база данных для демонстрации

2. Требования к системе
2.1 Функциональные требования
2.1.1 Пользовательские роли
Анонимный пользователь:

Просмотр публичного контента
Использование поиска и фильтров
Зарегистрированный пользователь:
Добавление нового контента (вручную и через парсинг URL)
Управление своим контентом (CRUD операции)
Получение персонализированных рекомендаций
Использование системы тегов для организации

Администратор:

Полный доступ к админ-панели Django
Управление категориями и контентом
Просмотр статистики

2.1.2 Основные функции
Управление контентом:

Добавление статей, видео, книг, подкастов, курсов
Автоматический парсинг метаданных по URL
Ручное тегирование
Фильтрация по типу, категориям, тегам

Система рекомендаций:

Рекомендации на основе общих тегов
Простой алгоритм коллаборативной фильтрации
Объяснение рекомендаций

Аналитика:

Базовая статистика по контенту
Визуализация распределения типов контента
Динамика добавления контента

2.2 Нефункциональные требования
Производительность: Время загрузки страниц < 2 сек
Надежность: Базовые обработки ошибок
Безопасность: Защита от CSRF, безопасное хранение настроек
Юзабилити: Адаптивный дизайн на Bootstrap 5

3. Архитектура системы
3.1 Технологический стек
text
Backend:
  • Django 4.2
  • Django REST Framework 3.14
  • SQLite 3 / PostgreSQL (готово к миграции)
  • Django Taggit для управления тегами

Frontend:
  • Django Templates
  • Bootstrap 5.1
  • Plotly.js для визуализации
  • JavaScript (ES6+)

Data Science компоненты:
  • Pandas для анализа данных
  • Plotly для создания графиков
  • Requests для работы с внешними API

Инфраструктура:
  • PythonAnywhere для хостинга
  • Git для контроля версий


3.2 Модели данных

3.2.1 Категория (Category)
python
class Category(models.Model):
    """Модель для категорий контента"""
    name = models.CharField('Название', max_length=100, unique=True)
    slug = models.SlugField('URL', max_length=100, unique=True)
    description = models.TextField('Описание', blank=True)

3.2.2 Контент (ContentItem)
python
class ContentItem(models.Model):
    """Основная модель для хранения контента"""
    CONTENT_TYPES = [
        ('article', 'Статья'),
        ('video', 'Видео'),
        ('book', 'Книга'),
        ('podcast', 'Подкаст'),
        ('course', 'Курс'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('in_progress', 'Читаю/Смотрю'),
        ('completed', 'Завершено'),
        ('postponed', 'Отложено'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField('Заголовок', max_length=200)
    url = models.URLField('Ссылка', max_length=500, blank=True)
    description = models.TextField('Описание', blank=True)
    content_type = models.CharField('Тип контента', max_length=20, choices=CONTENT_TYPES)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='new')
    
    # Теги через django-taggit
    tags = TaggableManager()
    
    # Временные метки
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    completed_at = models.DateTimeField('Дата завершения', null=True, blank=True)

3.2.3 Рекомендация (Recommendation)
python
class Recommendation(models.Model):
    """Модель для хранения рекомендаций"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    content_item = models.ForeignKey(ContentItem, on_delete=models.CASCADE, verbose_name='Контент')
    score = models.FloatField('Оценка релевантности', default=0.0)
    reason = models.CharField('Причина рекомендации', max_length=200)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

3.3 Структура проекта
text
projectforurfu/
├── content/                    # Основное приложение
│   ├── migrations/            # Миграции базы данных
│   ├── management/commands/   # Кастомные команды Django
│   ├── models.py              # Модели данных
│   ├── views.py               # Контроллеры (views)
│   ├── forms.py               # Формы Django
│   ├── serializers.py         # Сериализаторы API
│   ├── urls.py                # Маршруты приложения
│   ├── admin.py               # Админ-панель
│   ├── services.py            # Внешние сервисы и API
│   ├── recommendation_engine.py # Движок рекомендаций
│   └── visualizations.py      # Визуализация данных
├── project/                   # Настройки проекта
│   ├── settings.py           # Основные настройки
│   ├── urls.py               # Главные маршруты
│   └── wsgi.py               # WSGI конфигурация
├── templates/                # HTML шаблоны
│   ├── base.html             # Базовый шаблон
│   └── content/              # Шаблоны приложения
│       ├── home.html         # Главная страница
│       ├── content_list.html # Список контента
│       ├── content_detail.html # Детали контента
│       └── statistics.html   # Статистика
├── static/                   # Статические файлы
├── .env                      # Переменные окружения
├── requirements.txt          # Зависимости
├── manage.py                 # Django CLI
├── README.md                 # Документация
└── TZ.md                     # Техническое задание

4. Логика работы системы

4.1 Основные бизнес-процессы

4.1.1 Добавление нового контенту
text
1. Пользователь вводит URL или заполняет форму вручную
   ↓
2. Если указан URL:
   ├── 2.1. Отправка запроса к странице
   ├── 2.2. Парсинг HTML с помощью BeautifulSoup
   ├── 2.3. Извлечение:
   │   ├── Заголовок (тег <title>)
   │   ├── Описание (meta description)
   │   ├── Ключевые слова (meta keywords)
   │   └── Автоматическое определение типа контента
   ↓
3. Сохранение контента в базу данных
   ↓
4. Добавление тегов (автоматически из ключевых слов или вручную)
   ↓
5. Обновление системы рекомендаций для пользователя

4.1.2 Генерация рекомендаций
text
1. Сбор данных о пользователе:
   ├── Теги из сохраненного контента
   ├── Предпочтительные типы контента
   ├── Активность (последние добавления)
   ↓
2. Поиск похожего контента:
   ├── По общим тегам с другими пользователями
   ├── В тех же категориях
   ├── Такого же типа
   ↓
3. Расчет релевантности:
   ├── Вес совпадающих тегов
   ├── Свежесть контента
   ├── Популярность среди других пользователей
   ↓
4. Формирование списка рекомендаций
   ↓
5. Отображение на главной странице

4.2 API Endpoints

4.2.1 Веб-интерфейс
text
GET    /                      # Главная страница
GET    /content/              # Список всего контента
GET    /content/<id>/         # Детали контента
GET    /content/add/          # Форма добавления
POST   /content/add/          # Добавление контента
GET    /category/<slug>/      # Контент по категории
GET    /tag/<slug>/           # Контент по тегу
GET    /statistics/           # Статистика

4.2.2 REST API
text
GET    /api/                  # Корень API
GET    /api/contents/         # Список контента
POST   /api/contents/         # Добавление контента
GET    /api/contents/<id>/    # Детали контента
GET    /api/categories/       # Список категорий
GET    /api/recommendations/for_me/ # Персональные рекомендации
POST   /api/parse/            # Парсинг URL
GET    /api/visualizations/   # Данные для графиков
GET    /api/analytics/        # Аналитика

4.3 Алгоритмы

4.3.1 Расчет рекомендаций
python
def calculate_recommendation_score(user, content_item):
    """Расчет релевантности контента для пользователя"""
    
    # 1. Совпадение тегов (40% веса)
    user_tags = get_user_tags(user)
    content_tags = content_item.tags.all()
    common_tags = set(user_tags) & set(content_tags)
    tag_score = len(common_tags) / max(len(user_tags), 1) * 0.4
    
    # 2. Предпочтения по типу (30% веса)
    user_preferred_types = get_user_content_types(user)
    type_score = 0.3 if content_item.content_type in user_preferred_types else 0
    
    # 3. Свежесть контента (20% веса)
    days_old = (timezone.now() - content_item.created_at).days
    recency_score = max(0, 1 - days_old / 90) * 0.2
    
    # 4. Популярность (10% веса)
    similar_content_count = ContentItem.objects.filter(
        tags__in=content_item.tags.all()
    ).count()
    popularity_score = min(similar_content_count / 10, 1) * 0.1
    
    return tag_score + type_score + recency_score + popularity_score

4.3.2 Анализ данных
python
def analyze_content_data():
    """Анализ данных контента с помощью pandas"""
    
    # Загрузка данных в DataFrame
    data = ContentItem.objects.all().values()
    df = pd.DataFrame(data)
    
    # Анализ распределения
    analysis = {
        'total_items': len(df),
        'by_type': df['content_type'].value_counts().to_dict(),
        'by_status': df['status'].value_counts().to_dict(),
        'monthly_growth': df.groupby(
            pd.Grouper(key='created_at', freq='M')
        ).size().to_dict(),
        'avg_tags_per_item': calculate_avg_tags(df)
    }
    
    return analysis


5. Этапы разработки

Этап 1: Базовый каркас (День 1-2)
Настройка Django проекта
Создание базовых моделей (Category, ContentItem)
Настройка админ-панели
Базовая миграция базы данных

Этап 2: Веб-интерфейс (День 3-4)
Создание шаблонов с Bootstrap
Реализация views для отображения контента
Добавление системы фильтрации и поиска
Формы для добавления/редактирования контента

Этап 3: Расширенный функционал (День 5-6)
Интеграция django-taggit для тегов
Реализация системы рекомендаций
Создание REST API с Django REST Framework
Интеграция внешних API (парсинг URL)

Этап 4: Аналитика и визуализация (День 7-8)
Реализация анализа данных с pandas
Создание графиков с Plotly
Страница статистики
Оптимизация производительности

Этап 5: Деплой и тестирование (День 9-10)
Настройка для продакшена
Деплой на PythonAnywhere
Создание тестовых данных
Написание документации


6. Критерии приемки

6.1 Функциональные критерии

Все модели реализованы и работают
CRUD операции для контента функционируют
Система рекомендаций выдает релевантные результаты
Парсинг URL извлекает основные метаданные
Фильтрация и поиск работают корректно
API возвращает данные в правильном формате

6.2 Технические критерии
Проект запускается по инструкции из README.md
Код соответствует PEP8 стандартам
Настройки безопасности применены (DEBUG=False в продакшене)
Статические файлы загружаются корректно
База данных содержит тестовые данные (10-15 записей)

6.3 Интерфейсные критерии
Адаптивный дизайн на Bootstrap 5
Удобная навигация между страницами
Интуитивно понятные формы
Корректное отображение на мобильных устройствах

7. Документация

7.1 Файлы документации
README.md - Основная документация проекта
TZ.md - Техническое задание
requirements.txt - Список зависимостей
.env.example - Пример файла окружения


7.2 Инструкция по запуску
bash
# 1. Клонирование репозитория
git clone <repository-url>
cd projectforurfu

# 2. Создание виртуального окружения
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# или
.venv\Scripts\activate     # Windows

# 3. Установка зависимостей
pip install -r requirements.txt

# 4. Настройка окружения
cp .env.example .env
# Отредактировать .env файл

# 5. Настройка базы данных
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_data

# 6. Запуск сервера
python manage.py runserver

7.3 Демо-доступ
Сайт: http://Egor06.pythonanywhere.com/

Админка: http://Egor06.pythonanywhere.com/admin/

API: http://Egor06.pythonanywhere.com/api/