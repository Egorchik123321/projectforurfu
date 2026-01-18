from django.core.management.base import BaseCommand # pyright: ignore[reportMissingModuleSource]
from django.contrib.auth.models import User # pyright: ignore[reportMissingModuleSource]
from content.models import Category, ContentItem
from taggit.models import Tag # pyright: ignore[reportMissingImports]
import random

class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми данными'

    def handle(self, *args, **kwargs):
        # Создаем пользователя если нет
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com'}
        )
        if created:
            user.set_password('testpass123')
            user.save()
        
        # Создаем категории
        categories = [
            ('programming', 'Программирование'),
            ('science', 'Наука'),
            ('business', 'Бизнес'),
            ('design', 'Дизайн'),
            ('psychology', 'Психология'),
        ]
        
        for slug, name in categories:
            Category.objects.get_or_create(slug=slug, defaults={'name': name})
        
        # Создаем тестовый контент
        content_items = [
            {
                'title': 'Как изучать Django эффективно',
                'url': 'https://example.com/django-guide',
                'content_type': 'article',
                'category': 'programming',
                'tags': ['django', 'python', 'web-development'],
            },
            {
                'title': 'Введение в машинное обучение',
                'url': 'https://example.com/ml-intro',
                'content_type': 'video',
                'category': 'science',
                'tags': ['ai', 'machine-learning', 'data-science'],
            },
            # Добавьте еще 10-15 записей по аналогии
        ]
        
        for item_data in content_items:
            category = Category.objects.get(slug=item_data['category'])
            content_item, created = ContentItem.objects.get_or_create(
                title=item_data['title'],
                defaults={
                    'user': user,
                    'url': item_data['url'],
                    'content_type': item_data['content_type'],
                    'category': category,
                    'status': random.choice(['new', 'in_progress', 'completed']),
                }
            )
            if created:
                content_item.tags.add(*item_data['tags'])
        
        self.stdout.write(self.style.SUCCESS('Тестовые данные успешно созданы!'))