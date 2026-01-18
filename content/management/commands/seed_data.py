from django.core.management.base import BaseCommand # pyright: ignore[reportMissingModuleSource]
from django.contrib.auth.models import User # pyright: ignore[reportMissingModuleSource]
from content.models import Category, ContentItem
import random

class Command(BaseCommand):
    help = "Заполняет базу данных тестовыми данными"

    def handle(self, *args, **kwargs):
        self.stdout.write("Начинаю заполнение базы данных...")
        
        # 1. Создаем тестового пользователя
        user, created = User.objects.get_or_create(
            username="testuser",
            defaults={"email": "test@example.com"}
        )
        if created:
            user.set_password("testpass123")
            user.save()
            self.stdout.write(self.style.SUCCESS("✓ Создан пользователь testuser"))
        
        # 2. Создаем категории
        categories_data = [
            {"name": "Программирование", "slug": "programming"},
            {"name": "Наука", "slug": "science"},
            {"name": "Бизнес", "slug": "business"},
            {"name": "Дизайн", "slug": "design"},
            {"name": "Психология", "slug": "psychology"},
        ]
        
        for cat_data in categories_data:
            cat, created = Category.objects.get_or_create(
                slug=cat_data["slug"],
                defaults={"name": cat_data["name"]}
            )
            if created:
                self.stdout.write(f"✓ Создана категория: {cat.name}")
        
        # 3. Создаем тестовый контент
        content_items = [
            {
                "title": "Как изучать Django эффективно",
                "url": "https://docs.djangoproject.com/",
                "description": "Официальная документация Django - лучший источник для изучения",
                "content_type": "article",
                "category_slug": "programming",
                "tags": ["django", "python", "web", "backend", "framework"],
            },
            {
                "title": "Введение в машинное обучение на Python",
                "url": "https://scikit-learn.org/",
                "description": "Библиотека scikit-learn для машинного обучения",
                "content_type": "article",
                "category_slug": "programming",
                "tags": ["machine-learning", "python", "ai", "data-science", "algorithms"],
            },
            {
                "title": "Основы веб-дизайна 2024",
                "url": "https://www.youtube.com/watch?v=example1",
                "description": "Современные тренды в дизайне интерфейсов",
                "content_type": "video",
                "category_slug": "design",
                "tags": ["design", "ui", "ux", "web-design", "frontend"],
            },
            {
                "title": "Как начать свой бизнес с нуля",
                "url": "",
                "description": "Практическое руководство для начинающих предпринимателей",
                "content_type": "book",
                "category_slug": "business",
                "tags": ["business", "startup", "entrepreneurship", "marketing", "finance"],
            },
            {
                "title": "Нейробиология принятия решений",
                "url": "https://example.com/neuro",
                "description": "Как мозг принимает решения: научный подход",
                "content_type": "article",
                "category_slug": "science",
                "tags": ["neuroscience", "psychology", "science", "brain", "decision-making"],
            },
            {
                "title": "Полный курс по React",
                "url": "https://reactjs.org/docs/getting-started.html",
                "description": "Официальная документация React с примерами",
                "content_type": "course",
                "category_slug": "programming",
                "tags": ["react", "javascript", "frontend", "web", "hooks"],
            },
            {
                "title": "Искусство публичных выступлений",
                "url": "https://www.youtube.com/watch?v=example2",
                "description": "Как уверенно выступать перед аудиторией",
                "content_type": "video",
                "category_slug": "psychology",
                "tags": ["public-speaking", "communication", "confidence", "presentation"],
            },
        ]
        
        # Добавляем еще контента
        for i in range(8, 16):
            content_items.append({
                "title": f"Интересная статья #{i} по программированию",
                "url": f"https://example.com/article{i}",
                "description": f"Подробное описание и примеры кода для статьи #{i}",
                "content_type": random.choice(["article", "video", "book"]),
                "category_slug": random.choice(["programming", "science", "business"]),
                "tags": [f"tag{i}", "learning", "education", "tutorial"],
            })
        
        created_count = 0
        for item_data in content_items:
            try:
                category = Category.objects.get(slug=item_data["category_slug"])
                
                # Проверяем, существует ли уже такой контент
                if not ContentItem.objects.filter(title=item_data["title"]).exists():
                    content_item = ContentItem.objects.create(
                        user=user,
                        title=item_data["title"],
                        url=item_data["url"],
                        description=item_data["description"],
                        content_type=item_data["content_type"],
                        category=category,
                        status=random.choice(["new", "in_progress", "completed", "postponed"]),
                    )
                    
                    # Добавляем теги
                    for tag in item_data["tags"]:
                        content_item.tags.add(tag)
                    
                    created_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"✗ Ошибка при создании {item_data['title']}: {e}"))
        
        self.stdout.write(self.style.SUCCESS(f"✓ Создано {created_count} записей контента"))
        self.stdout.write(self.style.SUCCESS("✓ База данных успешно заполнена!"))