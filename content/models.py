from django.db import models # pyright: ignore[reportMissingModuleSource]
from django.contrib.auth.models import User # pyright: ignore[reportMissingModuleSource]
from taggit.managers import TaggableManager # pyright: ignore[reportMissingImports]
from django.utils import timezone # pyright: ignore[reportMissingModuleSource]

class Category(models.Model):
    """Категория контента"""
    name = models.CharField('Название', max_length=100, unique=True)
    slug = models.SlugField('URL', max_length=100, unique=True)
    description = models.TextField('Описание', blank=True)
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class ContentItem(models.Model):
    """Элемент контента (статья, видео, книга)"""
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
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    title = models.CharField('Заголовок', max_length=200)
    url = models.URLField('Ссылка', max_length=500, blank=True)
    description = models.TextField('Описание', blank=True)
    content_type = models.CharField('Тип контента', max_length=20, choices=CONTENT_TYPES, default='article')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Категория')
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    completed_at = models.DateTimeField('Дата завершения', null=True, blank=True)
    
    # Теги через django-taggit
    tags = TaggableManager()
    
    class Meta:
        verbose_name = 'Элемент контента'
        verbose_name_plural = 'Элементы контента'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status != 'completed':
            self.completed_at = None
        super().save(*args, **kwargs)

class Recommendation(models.Model):
    """Рекомендация контента"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    content_item = models.ForeignKey(ContentItem, on_delete=models.CASCADE, verbose_name='Контент')
    score = models.FloatField('Оценка релевантности', default=0.0)
    reason = models.CharField('Причина рекомендации', max_length=200)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Рекомендация'
        verbose_name_plural = 'Рекомендации'
        ordering = ['-score']
    
    def __str__(self):
        return f"{self.user.username} → {self.content_item.title}"