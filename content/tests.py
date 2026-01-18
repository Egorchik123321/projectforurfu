
"""
Тесты для приложения content
"""
from django.test import TestCase, Client # pyright: ignore[reportMissingModuleSource]
from django.urls import reverse # pyright: ignore[reportMissingModuleSource]
from django.contrib.auth.models import User # pyright: ignore[reportMissingModuleSource]
from django.utils import timezone # pyright: ignore[reportMissingModuleSource]
from rest_framework.test import APITestCase, APIClient # pyright: ignore[reportMissingImports]
from rest_framework import status # pyright: ignore[reportMissingImports]
from .models import Category, ContentItem
from .forms import ContentItemForm
import json

class CategoryModelTest(TestCase):
    """Тесты модели Category"""
    
    def setUp(self):
        self.category = Category.objects.create(
            name='Программирование',
            slug='programming',
            description='Категория для программирования'
        )
    
    def test_category_creation(self):
        """Тест создания категории"""
        self.assertEqual(self.category.name, 'Программирование')
        self.assertEqual(self.category.slug, 'programming')
        self.assertTrue(isinstance(self.category, Category))
    
    def test_category_str(self):
        """Тест строкового представления"""
        self.assertEqual(str(self.category), 'Программирование')
    
    def test_category_unique_slug(self):
        """Тест уникальности slug"""
        with self.assertRaises(Exception):
            Category.objects.create(
                name='Другое программирование',
                slug='programming'  # Дубликат
            )

class ContentItemModelTest(TestCase):
    """Тесты модели ContentItem"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Тестовая категория',
            slug='test-category'
        )
        
        self.content = ContentItem.objects.create(
            user=self.user,
            title='Тестовая статья',
            url='https://example.com/test',
            description='Тестовое описание',
            content_type='article',
            category=self.category,
            status='new'
        )
        self.content.tags.add('test', 'django', 'python')
    
    def test_content_creation(self):
        """Тест создания контента"""
        self.assertEqual(self.content.title, 'Тестовая статья')
        self.assertEqual(self.content.content_type, 'article')
        self.assertEqual(self.content.status, 'new')
        self.assertEqual(self.content.user.username, 'testuser')
    
    def test_content_str(self):
        """Тест строкового представления"""
        self.assertEqual(str(self.content), 'Тестовая статья')
    
    def test_content_tags(self):
        """Тест тегов контента"""
        tags = list(self.content.tags.names())
        self.assertIn('test', tags)
        self.assertIn('django', tags)
        self.assertIn('python', tags)
        self.assertEqual(len(tags), 3)
    
    def test_content_completed_status(self):
        """Тест обновления статуса на завершенный"""
        self.content.status = 'completed'
        self.content.save()
        
        self.assertIsNotNone(self.content.completed_at)
        self.assertEqual(self.content.status, 'completed')

class ContentItemFormTest(TestCase):
    """Тесты формы ContentItemForm"""
    
    def setUp(self):
        self.category = Category.objects.create(
            name='Форма тест',
            slug='form-test'
        )
        self.user = User.objects.create_user(
            username='formuser',
            password='formpass123'
        )
    
    def test_valid_form(self):
        """Тест валидной формы"""
        form_data = {
            'title': 'Тест через форму',
            'url': 'https://example.com/form-test',
            'description': 'Тестирование формы',
            'content_type': 'article',
            'category': self.category.id,
            'status': 'new',
            'tags': 'form,test,django'
        }
        
        form = ContentItemForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_invalid_form_empty_title(self):
        """Тест невалидной формы (пустой заголовок)"""
        form_data = {
            'title': '',
            'url': 'https://example.com/test',
            'content_type': 'article'
        }
        
        form = ContentItemForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
    
    def test_form_save(self):
        """Тест сохранения через форму"""
        form_data = {
            'title': 'Сохранение через форму',
            'url': 'https://example.com/save',
            'description': 'Тест сохранения',
            'content_type': 'video',
            'category': self.category.id,
            'status': 'in_progress',
            'tags': 'video,test'
        }
        
        form = ContentItemForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Сохраняем с пользователем
        content = form.save(commit=False)
        content.user = self.user
        content.save()
        form.save_m2m()  # Для тегов
        
        self.assertEqual(content.title, 'Сохранение через форму')
        self.assertEqual(content.content_type, 'video')
        self.assertIn('video', list(content.tags.names()))

class ViewTests(TestCase):
    """Тесты представлений"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='viewuser',
            password='viewpass123',
            email='view@example.com'
        )
        
        self.category = Category.objects.create(
            name='Тест просмотров',
            slug='view-test'
        )
        
        self.content = ContentItem.objects.create(
            user=self.user,
            title='Тест для просмотра',
            url='https://example.com/view',
            description='Тест описания',
            content_type='article',
            category=self.category
        )
    
    def test_home_view(self):
        """Тест главной страницы"""
        response = self.client.get(reverse('home'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'content/home.html')
        self.assertContains(response, 'ContentHub')
    
    def test_content_list_view(self):
        """Тест списка контента"""
        response = self.client.get(reverse('content_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'content/content_list.html')
        self.assertContains(response, 'Тест для просмотра')
    
    def test_content_detail_view(self):
        """Тест детальной страницы контента"""
        response = self.client.get(
            reverse('content_detail', args=[self.content.pk])
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'content/content_detail.html')
        self.assertContains(response, self.content.title)
    
    def test_category_detail_view(self):
        """Тест страницы категории"""
        response = self.client.get(
            reverse('category_detail', args=[self.category.slug])
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'content/category_detail.html')
        self.assertContains(response, self.category.name)
    
    def test_add_content_view_requires_login(self):
        """Тест что добавление контента требует авторизации"""
        response = self.client.get(reverse('add_content'))
        
        # Должен перенаправить на страницу входа
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            f'/admin/login/?next={reverse("add_content")}'
        )
    
    def test_add_content_view_with_login(self):
        """Тест добавления контента с авторизацией"""
        self.client.login(username='viewuser', password='viewpass123')
        response = self.client.get(reverse('add_content'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'content/content_form.html')

class APITests(APITestCase):
    """Тесты API"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='apiuser',
            password='apipass123'
        )
        
        self.category = Category.objects.create(
            name='API Тест',
            slug='api-test'
        )
        
        self.content = ContentItem.objects.create(
            user=self.user,
            title='API Тестовая статья',
            url='https://api.example.com/test',
            description='Тест API',
            content_type='article',
            category=self.category
        )
        self.content.tags.add('api', 'test')
    
    def test_api_categories_list(self):
        """Тест API списка категорий"""
        response = self.client.get('/api/categories/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'API Тест')
    
    def test_api_contents_list(self):
        """Тест API списка контента"""
        response = self.client.get('/api/contents/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 4)  # count, next, previous, results
        self.assertEqual(response.data['count'], 1)
    
    def test_api_content_detail(self):
        """Тест API деталей контента"""
        response = self.client.get(f'/api/contents/{self.content.pk}/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'API Тестовая статья')
        self.assertEqual(response.data['content_type'], 'article')
    
    def test_api_create_content_unauthorized(self):
        """Тест создания контента без авторизации"""
        data = {
            'title': 'Новый контент',
            'url': 'https://example.com/new',
            'content_type': 'article'
        }
        
        response = self.client.post('/api/contents/', data, format='json')
        
        # Должен вернуть 401 или 403
        self.assertIn(response.status_code, [401, 403])
    
    def test_api_create_content_authorized(self):
        """Тест создания контента с авторизацией"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'title': 'Авторизованный контент',
            'url': 'https://example.com/auth',
            'description': 'Создан через API',
            'content_type': 'video',
            'category_id': self.category.id,
            'tags': ['video', 'api', 'test']
        }
        
        response = self.client.post('/api/contents/', data, format='json')
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['title'], 'Авторизованный контент')
        self.assertEqual(response.data['content_type'], 'video')
    
    def test_api_search_content(self):
        """Тест поиска через API"""
        # Создаем еще контент для поиска
        ContentItem.objects.create(
            user=self.user,
            title='Поисковый тест Django',
            url='https://example.com/search',
            content_type='article',
            category=self.category
        ).tags.add('django', 'search')
        
        response = self.client.get('/api/contents/?search=django')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertIn('django', response.data['results'][0]['title'].lower())
    
    def test_api_filter_by_type(self):
        """Тест фильтрации по типу"""
        # Добавляем видео
        ContentItem.objects.create(
            user=self.user,
            title='API Видео тест',
            url='https://example.com/video',
            content_type='video',
            category=self.category
        )
        
        response = self.client.get('/api/contents/?content_type=video')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['content_type'], 'video')
    
    def test_api_similar_content(self):
        """Тест похожего контента"""
        # Создаем похожий контент
        similar = ContentItem.objects.create(
            user=self.user,
            title='Похожий контент',
            url='https://example.com/similar',
            content_type='article',
            category=self.category
        )
        similar.tags.add('api', 'test', 'extra')
        
        response = self.client.get(f'/api/contents/{self.content.pk}/similar/')
        
        self.assertEqual(response.status_code, 200)
        # Должен найти похожий контент по тегам
        self.assertEqual(len(response.data), 1)
    
    def test_api_statistics(self):
        """Тест статистики"""
        response = self.client.get('/api/contents/stats/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('total', response.data)
        self.assertIn('by_type', response.data)
        self.assertIn('article', response.data['by_type'])

class RecommendationEngineTest(TestCase):
    """Тесты движка рекомендаций"""
    
    def setUp(self):
        from .recommendation_engine import AdvancedRecommendationEngine
        
        self.user1 = User.objects.create_user('user1', 'user1@example.com', 'pass123')
        self.user2 = User.objects.create_user('user2', 'user2@example.com', 'pass123')
        
        self.category = Category.objects.create(
            name='Рекомендации',
            slug='recommendations'
        )
        
        # Контент для user1
        self.user1_content = ContentItem.objects.create(
            user=self.user1,
            title='User1 Контент 1',
            url='https://example.com/u1-1',
            content_type='article',
            category=self.category,
            status='completed'
        )
        self.user1_content.tags.add('python', 'django', 'web')
        
        self.user1_content2 = ContentItem.objects.create(
            user=self.user1,
            title='User1 Контент 2',
            url='https://example.com/u1-2',
            content_type='video',
            category=self.category,
            status='in_progress'
        )
        self.user1_content2.tags.add('python', 'machine-learning')
        
        # Контент для user2 (будет рекомендован)
        self.recommended_content = ContentItem.objects.create(
            user=self.user2,
            title='Рекомендуемый контент',
            url='https://example.com/rec',
            content_type='article',
            category=self.category,
            status='new'
        )
        self.recommended_content.tags.add('python', 'django', 'advanced')
        
        self.engine = AdvancedRecommendationEngine()
    
    def test_build_user_profile(self):
        """Тест построения профиля пользователя"""
        profile = self.engine.build_user_profile(self.user1)
        
        self.assertIn('tags', profile)
        self.assertIn('python', profile['tags'])
        self.assertIn('content_types', profile)
        self.assertIn('article', profile['content_types'])
        self.assertIn('video', profile['content_types'])
        self.assertIn('total_items', profile)
        self.assertEqual(profile['total_items'], 2)
    
    def test_get_recommendations(self):
        """Тест получения рекомендаций"""
        recommendations = self.engine.get_recommendations(self.user1, limit=5)
        
        self.assertTrue(len(recommendations) > 0)
        
        # Проверяем структуру рекомендации
        rec = recommendations[0]
        self.assertIn('content_item', rec)
        self.assertIn('score', rec)
        self.assertIn('reason', rec)
        self.assertIsInstance(rec['score'], float)
        self.assertIsInstance(rec['reason'], str)
        
        # Убедимся что не рекомендуем собственный контент
        user_content_titles = [c.title for c in ContentItem.objects.filter(user=self.user1)]
        for rec in recommendations:
            self.assertNotIn(rec['content_item'].title, user_content_titles)

class ManagementCommandTest(TestCase):
    """Тесты кастомных команд управления"""
    
    def test_seed_data_command(self):
        """Тест команды заполнения данными"""
        from django.core.management import call_command # pyright: ignore[reportMissingModuleSource]
        from io import StringIO
        
        out = StringIO()
        
        # Запускаем команду
        call_command('seed_data', stdout=out)
        
        # Проверяем вывод
        output = out.getvalue()
        self.assertIn('Начинаю заполнение базы данных', output)
        self.assertIn('Создан пользователь testuser', output)
        self.assertIn('База данных успешно заполнена', output)
        
        # Проверяем что данные созданы
        self.assertTrue(User.objects.filter(username='testuser').exists())
        self.assertTrue(Category.objects.filter(slug='programming').exists())
        self.assertTrue(ContentItem.objects.count() > 0)

class IntegrationTests(TestCase):
    """Интеграционные тесты"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='integration',
            password='integration123'
        )
        self.client.login(username='integration', password='integration123')
        
        self.category = Category.objects.create(
            name='Интеграция',
            slug='integration'
        )
    
    def test_full_content_workflow(self):
        """Полный тест workflow работы с контентом"""
        # 1. Добавляем контент
        add_url = reverse('add_content')
        response = self.client.post(add_url, {
            'title': 'Интеграционный тест',
            'url': 'https://integration.example.com',
            'description': 'Тестирование полного workflow',
            'content_type': 'article',
            'category': self.category.id,
            'status': 'new',
            'tags': 'integration,test,workflow'
        })
        
        # Должен перенаправить на детальную страницу
        self.assertEqual(response.status_code, 302)
        
        # 2. Получаем созданный контент
        content = ContentItem.objects.get(title='Интеграционный тест')
        
        # 3. Проверяем детальную страницу
        detail_url = reverse('content_detail', args=[content.pk])
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Интеграционный тест')
        
        # 4. Редактируем контент
        edit_url = reverse('edit_content', args=[content.pk])
        response = self.client.post(edit_url, {
            'title': 'Обновленный интеграционный тест',
            'url': 'https://updated.integration.example.com',
            'description': 'Обновленное описание',
            'content_type': 'article',
            'category': self.category.id,
            'status': 'in_progress',
            'tags': 'integration,updated,test'
        })
        
        self.assertEqual(response.status_code, 302)
        
        # 5. Проверяем обновление
        content.refresh_from_db()
        self.assertEqual(content.title, 'Обновленный интеграционный тест')
        self.assertEqual(content.status, 'in_progress')
        
        # 6. Удаляем контент
        delete_url = reverse('delete_content', args=[content.pk])
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 302)
        
        # 7. Проверяем что удалился
        with self.assertRaises(ContentItem.DoesNotExist):
            ContentItem.objects.get(pk=content.pk)

class ErrorHandlingTests(TestCase):
    """Тесты обработки ошибок"""
    
    def test_404_page(self):
        """Тест страницы 404"""
        response = self.client.get('/non-existent-page/')
        self.assertEqual(response.status_code, 404)
    
    def test_invalid_content_id(self):
        """Тест неверного ID контента"""
        response = self.client.get(reverse('content_detail', args=[99999]))
        self.assertEqual(response.status_code, 404)
    
    def test_invalid_category_slug(self):
        """Тест неверного slug категории"""
        response = self.client.get(reverse('category_detail', args=['non-existent-slug']))
        self.assertEqual(response.status_code, 404)

# Запуск тестов через coverage
# coverage run manage.py test content
# coverage report
# coverage html

if __name__ == '__main__':
    # Запуск тестов напрямую (для отладки)
    import django # pyright: ignore[reportMissingModuleSource]
    django.setup()
    from django.test.utils import get_runner # pyright: ignore[reportMissingModuleSource]
    from django.conf import settings # pyright: ignore[reportMissingModuleSource]
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(['content'])
    
    if failures:
        print(f"\n❌ Тесты не прошли: {failures} ошибок")
        exit(1)
    else:
        print("\n✅ Все тесты прошли успешно!")