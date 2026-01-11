Техническое задание на разработку ContentHub
1. Общие сведения
1.1 Наименование проекта
ContentHub — Веб-сервис интеллектуальной агрегации образовательного контента для IT-специалистов с NLP-анализом и рекомендательной системой

1.2 Цель проекта
Создать платформу для автоматического сбора, анализа и рекомендации профессионального контента (статьи, видео, книги) с использованием машинного обучения для классификации и персонализации.

1.3 Критерии успеха
Автоматическая обработка 95% передаваемых ссылок

Точность категоризации контента ≥ 85%

Время генерации рекомендаций < 500 мс

Поддержка 1000+ активных пользователей

2. Требования к системе
2.1 Функциональные требования
2.1.1 Пользовательские роли
Анонимный пользователь:

Просмотр публичных коллекций

Регистрация и вход

Зарегистрированный пользователь:

Управление личным контентом (CRUD)

Автоматический парсинг ссылок

NLP-анализ добавленного контента

Персонализированные рекомендации

Создание публичных/приватных коллекций

Подписка на других пользователей

Экспорт данных

Администратор:

Модерация пользовательского контента

Управление системными настройками

Просмотр аналитики платформы

Управление NLP-моделями

2.1.2 Интеллектуальная обработка контента
Автоматический парсинг:

Извлечение Open Graph метаданных

Определение типа контента (статья/видео/книга)

Получение превью-изображений

Обработка ошибок и таймаутов

NLP-анализ:

Извлечение ключевых сущностей (технологии, языки, фреймворки)

Автоматическая тегизация

Определение языковой принадлежности

Классификация по темам (Backend/Frontend/Data Science/DevOps)

Рекомендательная система:

Контентная фильтрация (по тегам и категориям)

Коллаборативная фильтрация (по действиям похожих пользователей)

Гибридный алгоритм с весовыми коэффициентами

Механизм разнообразия рекомендаций

2.1.3 Аналитика и отчетность
Визуализация интересов пользователя

Статистика по потреблению контента

Отслеживание прогресса обучения

Экспорт данных в CSV/JSON

2.2 Нефункциональные требования
Производительность: Время отклика API < 200 мс, рендеринг страниц < 1 с

Масштабируемость: Поддержка до 10,000 пользователей

Надежность: Доступность 99.5%, резервное копирование ежедневно

Безопасность: HTTPS, защита от XSS/CSRF, валидация входных данных

Юзабилити: Mobile-first дизайн, progressive enhancement
3. Архитектура системы
3.1 Технологический стек
text
Backend:
  • Django 5.0 + Django REST Framework 3.15
  • Python 3.11
  • PostgreSQL 15 с расширениями:
    - pg_trgm для триграммного поиска
    - pgvector для векторных операций (опционально)
  • Redis 7.0 для кэширования и очередей
  • Celery 5.3 для фоновых задач

AI/ML компоненты:
  • SpaCy 3.7 для NLP анализа
  • scikit-learn 1.3 для кластеризации
  • NLTK/TextBlob для текстовой обработки
  • SentenceTransformers для векторных представлений

Фронтенд:
  • Django Templates + HTMX для динамики
  • Bootstrap 5 для стилей
  • Chart.js для визуализации
  • Alpine.js для интерактивных компонентов

Инфраструктура:
  • Docker + Docker Compose
  • Nginx как reverse proxy
  • Gunicorn/Uvicorn как ASGI сервер
  • GitHub Actions для CI/CD
3.2 Модели данных
3.2.1 Пользователь (CustomUser)
python
class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, verbose_name="Email")
    username = models.CharField(max_length=150, unique=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True, verbose_name="О себе")
    job_title = models.CharField(max_length=100, blank=True, verbose_name="Должность")
    company = models.CharField(max_length=100, blank=True, verbose_name="Компания")
    
    # Настройки пользователя
    language_preference = models.CharField(
        max_length=2, 
        choices=[('ru', 'Русский'), ('en', 'English')],
        default='ru'
    )
    receive_recommendations = models.BooleanField(default=True)
    is_content_public = models.BooleanField(default=False)
    
    # Статистика
    content_count = models.IntegerField(default=0)
    last_active = models.DateTimeField(auto_now=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['last_active']),
        ]
3.2.2 Контент (ContentItem)
python
class ContentItem(models.Model):
    CONTENT_TYPES = [
        ('article', '📝 Статья'),
        ('video', '🎥 Видео'),
        ('book', '📚 Книга'),
        ('course', '🎓 Курс'),
        ('podcast', '🎧 Подкаст'),
        ('tutorial', '🛠️ Руководство'),
        ('research', '🔬 Исследование'),
        ('other', '📦 Другое'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('in_progress', 'В процессе'),
        ('completed', 'Завершено'),
        ('postponed', 'Отложено'),
        ('archived', 'В архиве'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE,
        related_name='content_items',
        verbose_name="Владелец"
    )
    
    # Основные данные
    url = models.URLField(max_length=2000, verbose_name="URL")
    title = models.CharField(max_length=500, verbose_name="Заголовок")
    description = models.TextField(blank=True, verbose_name="Описание")
    content_type = models.CharField(
        max_length=20, 
        choices=CONTENT_TYPES,
        default='article',
        verbose_name="Тип контента"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name="Статус"
    )
    
    # Автоматически извлеченные данные
    domain = models.CharField(max_length=255, blank=True, verbose_name="Домен")
    preview_image = models.URLField(max_length=2000, blank=True, verbose_name="Превью")
    estimated_read_time = models.IntegerField(null=True, blank=True, verbose_name="Время чтения (мин)")
    
    # NLP анализ
    extracted_text = models.TextField(blank=True, verbose_name="Извлеченный текст")
    language = models.CharField(max_length=10, blank=True, verbose_name="Язык")
    entities = models.JSONField(default=dict, verbose_name="Извлеченные сущности")
    sentiment_score = models.FloatField(null=True, blank=True, verbose_name="Тональность")
    complexity_score = models.FloatField(null=True, blank=True, verbose_name="Сложность")
    
    # Системные поля
    is_public = models.BooleanField(default=False, verbose_name="Публичный доступ")
    is_parsed = models.BooleanField(default=False, verbose_name="Обработан")
    parsing_attempts = models.IntegerField(default=0, verbose_name="Попыток парсинга")
    
    # Временные метки
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="Добавлено")
    started_at = models.DateTimeField(null=True, blank=True, verbose_name="Начало чтения")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Завершено")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")
    
    class Meta:
        verbose_name = "Контент"
        verbose_name_plural = "Контент"
        ordering = ['-added_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['content_type']),
            models.Index(fields=['added_at']),
            models.Index(fields=['domain']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'url'],
                name='unique_user_url'
            )
        ]
3.2.3 Тег (Tag) - ManyToMany через промежуточную модель
python
class Tag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, verbose_name="Название")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Slug")
    description = models.TextField(blank=True, verbose_name="Описание")
    
    # Автоматические теги vs пользовательские
    is_auto_generated = models.BooleanField(default=False, verbose_name="Автогенерируемый")
    category = models.CharField(
        max_length=50,
        choices=[
            ('technology', 'Технология'),
            ('language', 'Язык программирования'),
            ('framework', 'Фреймворк'),
            ('topic', 'Тема'),
            ('skill', 'Навык'),
            ('other', 'Другое'),
        ],
        default='topic',
        verbose_name="Категория тега"
    )
    
    # Статистика использования
    usage_count = models.IntegerField(default=0, verbose_name="Частота использования")
    last_used = models.DateTimeField(auto_now=True, verbose_name="Последнее использование")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ['-usage_count', 'name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['category']),
        ]


class ContentItemTag(models.Model):
    """Промежуточная модель для связи контента и тегов с дополнительными данными"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content_item = models.ForeignKey(
        ContentItem, 
        on_delete=models.CASCADE,
        related_name='tag_relations'
    )
    tag = models.ForeignKey(
        Tag, 
        on_delete=models.CASCADE,
        related_name='content_relations'
    )
    
    # Вес тега для этого контента (от NLP анализа)
    relevance_score = models.FloatField(
        default=1.0,
        verbose_name="Релевантность"
    )
    source = models.CharField(
        max_length=20,
        choices=[
            ('auto', 'Автоматически'),
            ('manual', 'Вручную'),
            ('both', 'Авто + ручное'),
        ],
        default='auto',
        verbose_name="Источник"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Связь контент-тег"
        verbose_name_plural = "Связи контент-тег"
        unique_together = [['content_item', 'tag']]
        indexes = [
            models.Index(fields=['content_item', 'relevance_score']),
        ]
3.2.4 Категория пользователя (UserCategory)
python
class UserCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='categories',
        verbose_name="Пользователь"
    )
    name = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    
    # Иерархическая структура
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name="Родительская категория"
    )
    
    # Визуальные настройки
    color = models.CharField(
        max_length=7,
        default='#3B82F6',
        verbose_name="Цвет (HEX)"
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Иконка"
    )
    order = models.IntegerField(default=0, verbose_name="Порядок")
    
    # Статистика
    content_count = models.IntegerField(default=0, verbose_name="Кол-во материалов")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Категория пользователя"
        verbose_name_plural = "Категории пользователей"
        ordering = ['order', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'name'],
                name='unique_user_category_name'
            )
        ]
3.2.5 Действие пользователя (UserAction)
python
class UserAction(models.Model):
    ACTION_TYPES = [
        ('view', 'Просмотр'),
        ('save', 'Сохранение'),
        ('start_reading', 'Начало чтения'),
        ('complete', 'Завершение'),
        ('rate', 'Оценка'),
        ('comment', 'Комментарий'),
        ('share', 'Поделиться'),
        ('tag', 'Добавление тега'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='actions',
        verbose_name="Пользователь"
    )
    content_item = models.ForeignKey(
        ContentItem,
        on_delete=models.CASCADE,
        related_name='actions',
        verbose_name="Контент"
    )
    
    action_type = models.CharField(
        max_length=50,
        choices=ACTION_TYPES,
        verbose_name="Тип действия"
    )
    
    # Дополнительные данные в зависимости от типа
    metadata = models.JSONField(
        default=dict,
        verbose_name="Метаданные действия"
    )
    """
    Пример metadata:
    - Для 'rate': {'rating': 4.5, 'max_rating': 5}
    - Для 'view': {'duration_seconds': 120, 'scroll_depth': 0.75}
    - Для 'comment': {'comment_id': 'uuid', 'text': '...'}
    """
    
    # Временные метки
    performed_at = models.DateTimeField(auto_now_add=True, verbose_name="Время действия")
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Истекает"
    )  # Для временных действий
    
    class Meta:
        verbose_name = "Действие пользователя"
        verbose_name_plural = "Действия пользователей"
        ordering = ['-performed_at']
        indexes = [
            models.Index(fields=['user', 'action_type']),
            models.Index(fields=['content_item', 'action_type']),
            models.Index(fields=['performed_at']),
        ]
3.2.6 Рекомендация (Recommendation)
python
class Recommendation(models.Model):
    SOURCE_TYPES = [
        ('content_based', 'На основе контента'),
        ('collaborative', 'Коллаборативная'),
        ('hybrid', 'Гибридная'),
        ('trending', 'Популярное'),
        ('serendipity', 'Неожиданное'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='recommendations',
        verbose_name="Пользователь"
    )
    content_item = models.ForeignKey(
        ContentItem,
        on_delete=models.CASCADE,
        related_name='recommendations',
        verbose_name="Рекомендуемый контент"
    )
    
    # Алгоритмические данные
    source_type = models.CharField(
        max_length=50,
        choices=SOURCE_TYPES,
        verbose_name="Тип рекомендации"
    )
    score = models.FloatField(
        verbose_name="Скор рекомендации",
        help_text="От 0.0 до 1.0"
    )
    reason = models.JSONField(
        default=dict,
        verbose_name="Причина рекомендации"
    )
    """
    Пример reason:
    {
        'matched_tags': ['python', 'django'],
        'similar_users_count': 15,
        'category_match': 'backend',
        'explanation': 'На основе вашего интереса к Python'
    }
    """
    
    # Статус рекомендации
    is_viewed = models.BooleanField(default=False, verbose_name="Просмотрено")
    is_accepted = models.BooleanField(null=True, blank=True, verbose_name="Принято")
    
    # Временные метки
    generated_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    expires_at = models.DateTimeField(
        verbose_name="Истекает",
        help_text="Рекомендация актуальна 7 дней"
    )
    
    class Meta:
        verbose_name = "Рекомендация"
        verbose_name_plural = "Рекомендации"
        ordering = ['-score', '-generated_at']
        indexes = [
            models.Index(fields=['user', 'is_viewed']),
            models.Index(fields=['user', 'score']),
            models.Index(fields=['expires_at']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'content_item'],
                condition=models.Q(expires_at__gt=models.F('generated_at')),
                name='unique_active_recommendation'
            )
        ]
        4. Логика работы системы
4.1 Основные бизнес-процессы
4.1.1 Добавление нового контента
text
1. Пользователь вводит URL
   ↓
2. Валидация URL (формат, доступность, не дубликат)
   ↓
3. Создание асинхронной задачи Celery на парсинг
   ↓
4. Парсинг (синхронный или асинхронный):
   ├── 4.1. Извлечение Open Graph метаданных
   ├── 4.2. Заголовок из <title> или h1
   ├── 4.3. Описание из meta description или первых абзацев
   ├── 4.4. Превью-изображение
   ├── 4.5. Определение типа контента по домену/структуре
   ↓
5. NLP обработка (если включено):
   ├── 5.1. Извлечение текста (удаление HTML, JS, CSS)
   ├── 5.2. Определение языка
   ├── 5.3. Извлечение сущностей (NER)
   ├── 5.4. Автоматическая тегизация
   ├── 5.5. Определение тональности и сложности
   ↓
6. Сохранение в базу со статусом "new"
   ↓
7. Предпросмотр пользователю с возможностью редактирования
   ↓
8. Подтверждение и окончательное сохранение
4.1.2 Генерация рекомендаций
text
1. Триггер генерации:
   ├── Добавление нового контента
   ├── Действие пользователя (просмотр/завершение)
   ├── По расписанию (ежедневно)
   ↓
2. Сбор данных для пользователя:
   ├── История действий (последние 90 дней)
   ├── Текущие теги и категории
   ├── Похожие пользователи (коллаборативная фильтрация)
   ↓
3. Алгоритм рекомендаций:
   ├── Этап 1: Контентная фильтрация (70% веса)
   │   ├── Поиск по совпадающим тегам
   │   ├── Контент из любимых категорий
   │   ├── Контент похожей сложности
   │
   ├── Этап 2: Коллаборативная фильтрация (20% веса)
   │   ├── Находка k ближайших пользователей
   │   ├── Анализ их предпочтений
   │   ├── Контент, который им понравился
   │
   ├── Этап 3: Разнообразие (10% веса)
   │   ├── Новые темы для пользователя
   │   ├── Контент из смежных областей
   │   ├── "Неожиданные" рекомендации
   ↓
4. Ранжирование и фильтрация:
   ├── Исключение уже просмотренного
   ├── Учет языковых предпочтений
   ├── Фильтр по качеству (is_parsed=True)
   ↓
5. Сохранение рекомендаций в базу
   ↓
6. Отображение на главной/в разделе рекомендаций
4.1.3 NLP обработка текста
python
class ContentAnalyzer:
    """Основной класс для NLP анализа контента"""
    
    def __init__(self, language='ru'):
        self.language = language
        self.nlp = spacy.load(f"{language}_core_news_sm")
        self.stop_words = set(stopwords.words(language))
        
    def analyze(self, text: str, url: str = None) -> Dict:
        """Полный анализ текста"""
        doc = self.nlp(text[:100000])  # Ограничение длины
        
        return {
            'language': self.detect_language(text),
            'entities': self.extract_entities(doc),
            'keywords': self.extract_keywords(text),
            'tags': self.generate_tags(doc, url),
            'sentiment': self.analyze_sentiment(text),
            'complexity': self.estimate_complexity(text),
            'read_time_minutes': self.estimate_read_time(text),
            'summary': self.generate_summary(text),
        }
    
    def extract_entities(self, doc) -> List[Dict]:
        """Извлечение именованных сущностей"""
        entities = []
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PRODUCT', 'TECH', 'LANG']:
                entities.append({
                    'text': ent.text,
                    'label': ent.label_,
                    'start': ent.start_char,
                    'end': ent.end_char,
                })
        return entities
    
    def generate_tags(self, doc, url=None) -> List[Dict]:
        """Генерация тегов на основе контента"""
        tags = []
        
        # 1. Из сущностей
        tags.extend([e['text'].lower() for e in self.extract_entities(doc)])
        
        # 2. Из ключевых слов (TF-IDF)
        tags.extend(self.extract_keywords(doc.text))
        
        # 3. Из домена (если есть)
        if url:
            domain = urlparse(url).netloc
            if 'github' in domain:
                tags.append('github')
            elif 'medium' in domain:
                tags.append('medium')
            # и т.д.
        
        # 4. Дедупликация и ранжирование
        tag_counts = Counter(tags)
        return [
            {'tag': tag, 'score': count/len(tags)}
            for tag, count in tag_counts.most_common(10)
        ]
4.2 API Endpoints
4.2.1 Аутентификация
http
POST   /api/v1/auth/register/
POST   /api/v1/auth/login/
POST   /api/v1/auth/logout/
POST   /api/v1/auth/refresh/
GET    /api/v1/auth/profile/
PUT    /api/v1/auth/profile/
4.2.2 Контент
http
GET    /api/v1/content/                    # Список с фильтрами
POST   /api/v1/content/                    # Добавление
GET    /api/v1/content/{id}/               # Детали
PUT    /api/v1/content/{id}/               # Обновление
DELETE /api/v1/content/{id}/               # Удаление
POST   /api/v1/content/{id}/parse/         # Принудительный парсинг
POST   /api/v1/content/{id}/analyze/       # NLP анализ
POST   /api/v1/content/batch/              # Пакетное добавление
GET    /api/v1/content/stats/              # Статистика
4.2.3 Рекомендации
http
GET    /api/v1/recommendations/            # Актуальные рекомендации
POST   /api/v1/recommendations/generate/   # Принудительная генерация
PUT    /api/v1/recommendations/{id}/       # Отметка как просмотренное
GET    /api/v1/recommendations/history/    # История рекомендаций
4.2.4 Аналитика
http
GET    /api/v1/analytics/interests/        # График интересов
GET    /api/v1/analytics/timeline/         # Таймлайн активности
GET    /api/v1/analytics/productivity/     # Продуктивность
GET    /api/v1/analytics/export/           # Экспорт данных
4.3 Алгоритмы и формулы
4.3.1 Расчет релевантности тега
text
relevance_score(tag, content) = 
  0.4 * tfidf(tag, content) +
  0.3 * entity_weight(tag) +
  0.2 * domain_relevance(tag, url) +
  0.1 * popularity(tag)
4.3.2 Сходство пользователей (для коллаборативной фильтрации)
text
similarity(user_a, user_b) = 
  cosine_similarity(
    vectorize(user_a.actions),
    vectorize(user_b.actions)
  )
  
vectorize(actions) = [
  count_tags_used * tag_weights,
  categories_preferences,
  content_types_distribution,
  ...
]
4.3.3 Оценка сложности текста
text
complexity_score(text) = 
  0.3 * avg_sentence_length +
  0.3 * avg_word_length +
  0.2 * unique_words_ratio +
  0.1 * technical_terms_count +
  0.1 * passive_voice_ratio
5. Этапы разработки
Этап 1: Базовый каркас (Неделя 1-2)
Настройка Django проекта и окружения

Модели CustomUser, ContentItem, Tag

Базовая аутентификация (Django Allauth)

CRUD операции для контента

Простой парсинг метаданных

Этап 2: Интеллектуальная обработка (Неделя 3-4)
Интеграция SpaCy для NLP

Автоматическая тегизация

Определение языка и сущностей

Система рекомендаций (базовая)

Интерфейс пользователя

Этап 3: Расширенные функции (Неделя 5)
Категории пользователя (иерархические)

Подписки и социальные функции

Аналитика и визуализация

Экспорт данных

Оптимизация производительности

Этап 4: Тестирование и деплой (Неделя 6)
Написание тестов (unit, integration)

Настройка CI/CD (GitHub Actions)

Оптимизация запросов и индексов

Production настройки

Документация

6. Критерии приемки
6.1 Функциональные критерии
Все модели реализованы согласно спецификации

CRUD операции работают корректно для всех сущностей

Парсинг извлекает метаданные для 95% ссылок

NLP анализ определяет теги с точностью ≥ 85%

Рекомендации генерируются за < 500 мс

Интерфейс адаптирован под мобильные устройства

6.2 Технические критерии
Время отклика API < 200 мс (p95)

80% покрытие тестами критического функционала

Код соответствует PEP8 и проходит линтеры

Наличие документации API (OpenAPI/Swagger)

Рабочий деплой на сервере (Docker)

Миграции базы данных обратно совместимы