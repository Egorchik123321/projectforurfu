from rest_framework import viewsets, generics, permissions, status # pyright: ignore[reportMissingImports]
from rest_framework.decorators import action # pyright: ignore[reportMissingImports]
from rest_framework.response import Response # pyright: ignore[reportMissingImports]
from rest_framework.parsers import MultiPartParser, FormParser # pyright: ignore[reportMissingImports]
from django_filters.rest_framework import DjangoFilterBackend # pyright: ignore[reportMissingModuleSource]
from rest_framework.filters import SearchFilter, OrderingFilter # pyright: ignore[reportMissingImports]
from django.db.models import Count, Q # pyright: ignore[reportMissingModuleSource]
from .models import Category, ContentItem, Recommendation
from .serializers import (
    CategorySerializer, ContentItemSerializer,
    RecommendationSerializer, UserSerializer
)
from django.contrib.auth.models import User # pyright: ignore[reportMissingModuleSource]
import requests # pyright: ignore[reportMissingModuleSource]
from bs4 import BeautifulSoup # pyright: ignore[reportMissingImports]
import re

class IsOwnerOrReadOnly(permissions.BasePermission):
    """Разрешение на редактирование только владельцам контента"""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user

class CategoryViewSet(viewsets.ModelViewSet):
    """API для категорий"""
    queryset = Category.objects.annotate(
        content_count=Count('contentitem')
    ).order_by('name')
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    
    @action(detail=True, methods=['get'])
    def contents(self, request, slug=None):
        """Получить весь контент в категории"""
        category = self.get_object()
        contents = ContentItem.objects.filter(category=category).order_by('-created_at')
        page = self.paginate_queryset(contents)
        if page is not None:
            serializer = ContentItemSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = ContentItemSerializer(contents, many=True, context={'request': request})
        return Response(serializer.data)

class ContentItemViewSet(viewsets.ModelViewSet):
    """API для контента"""
    queryset = ContentItem.objects.select_related('user', 'category').order_by('-created_at')
    serializer_class = ContentItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['content_type', 'status', 'category']
    search_fields = ['title', 'description', 'tags__name']
    ordering_fields = ['created_at', 'updated_at', 'title']
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def mine(self, request):
        """Получить только мой контент"""
        contents = ContentItem.objects.filter(user=request.user).order_by('-created_at')
        page = self.paginate_queryset(contents)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(contents, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def similar(self, request, pk=None):
        """Похожий контент по тегам"""
        content_item = self.get_object()
        similar = ContentItem.objects.filter(
            tags__in=content_item.tags.all()
        ).exclude(id=content_item.id).distinct()[:10]
        serializer = self.get_serializer(similar, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Статистика по контенту"""
        stats = {
            'total': ContentItem.objects.count(),
            'by_type': dict(ContentItem.objects.values('content_type').annotate(
                count=Count('id')
            ).values_list('content_type', 'count')),
            'by_status': dict(ContentItem.objects.values('status').annotate(
                count=Count('id')
            ).values_list('status', 'count')),
        }
        return Response(stats)

class RecommendationViewSet(viewsets.ModelViewSet):
    """API для рекомендаций"""
    queryset = Recommendation.objects.select_related('user', 'content_item').order_by('-score')
    serializer_class = RecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def for_me(self, request):
        """Рекомендации для текущего пользователя"""
        engine = AdvancedRecommendationEngine() # pyright: ignore[reportUndefinedVariable]
        recommendations = engine.get_recommendations(request.user, limit=10)
        
        serialized = []
        for rec in recommendations:
            serialized.append({
                'content_item': ContentItemSerializer(
                    rec['content_item'], 
                    context={'request': request}
                ).data,
                'score': rec['score'],
                'reason': rec['reason'],
                'engine': 'advanced'
            })
        
        return Response(serialized)
    
    @action(detail=False, methods=['get'])
    def advanced(self, request):
        """Продвинутые рекомендации с разными алгоритмами"""
        from .recommendation_engine import AdvancedRecommendationEngine
        
        engine = AdvancedRecommendationEngine()
        recommendations = engine.get_recommendations(request.user, limit=15)
        
        # Группируем по причинам
        grouped = {}
        for rec in recommendations:
            reason = rec['reason']
            if reason not in grouped:
                grouped[reason] = []
            grouped[reason].append({
                'item': ContentItemSerializer(
                    rec['content_item'],
                    context={'request': request}
                ).data,
                'score': rec['score']
            })
        
        return Response({
            'total': len(recommendations),
            'grouped_by_reason': grouped,
            'top_score': recommendations[0]['score'] if recommendations else 0,
            'average_score': np.mean([r['score'] for r in recommendations]) if recommendations else 0 # pyright: ignore[reportUndefinedVariable]
        })

class UserViewSet(viewsets.ReadOnlyModelView):
    """API для пользователей"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    @action(detail=True, methods=['get'])
    def contents(self, request, pk=None):
        """Контент пользователя"""
        user = self.get_object()
        contents = ContentItem.objects.filter(user=user).order_by('-created_at')
        page = self.paginate_queryset(contents)
        if page is not None:
            serializer = ContentItemSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = ContentItemSerializer(contents, many=True, context={'request': request})
        return Response(serializer.data)

class ParseContentView(generics.CreateAPIView):
    """API для парсинга контента по URL"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ContentItemSerializer
    
    def post(self, request, *args, **kwargs):
        url = request.data.get('url', '').strip()
        
        if not url:
            return Response(
                {'error': 'URL обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Парсим мета-данные страницы
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Извлекаем заголовок
            title = soup.title.string if soup.title else ''
            
            # Ищем мета-описание
            description = ''
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                description = meta_desc['content']
            else:
                # Берем первый параграф
                first_p = soup.find('p')
                if first_p:
                    description = first_p.get_text()[:200]
            
            # Определяем тип контента по домену
            content_type = 'article'
            if 'youtube.com' in url or 'vimeo.com' in url:
                content_type = 'video'
            elif 'github.com' in url or 'stackoverflow.com' in url:
                content_type = 'article'
            
            # Извлекаем ключевые слова
            keywords = []
            meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
            if meta_keywords and meta_keywords.get('content'):
                keywords = [k.strip() for k in meta_keywords['content'].split(',')[:5]]
            
            # Автоматически подбираем категорию
            category = None
            if any(word in url.lower() for word in ['python', 'django', 'programming', 'code']):
                category = Category.objects.filter(slug='programming').first()
            elif any(word in url.lower() for word in ['design', 'ui', 'ux', 'figma']):
                category = Category.objects.filter(slug='design').first()
            
            # Создаем контент
            content_data = {
                'title': title[:200],
                'url': url,
                'description': description[:500],
                'content_type': content_type,
                'category_id': category.id if category else None,
                'tags': keywords,
                'status': 'new'
            }
            
            serializer = self.get_serializer(data=content_data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except requests.RequestException as e:
            return Response(
                {'error': f'Ошибка при загрузке URL: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Ошибка при парсинге: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
class ExternalSearchView(generics.GenericAPIView):
    """Поиск контента во внешних источниках"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        query = request.query_params.get('q', '')
        
        if not query:
            return Response(
                {'error': 'Поисковый запрос обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Пример использования NewsAPI
        news_client = NewsAPIClient() # pyright: ignore[reportUndefinedVariable]
        articles = news_client.search_articles(query, page_size=5)
        
        # Пример использования YouTube API
        youtube_client = YouTubeAPIClient() # pyright: ignore[reportUndefinedVariable]
        videos = youtube_client.search_videos(query, max_results=3)
        
        results = {
            'query': query,
            'articles': articles if not isinstance(articles, dict) or 'error' not in articles else [],
            'videos': videos,
            'total_results': (0 if isinstance(articles, dict) and 'error' in articles else len(articles)) + len(videos)
        }
        
        return Response(results)

class AnalyticsView(generics.GenericAPIView):
    """Аналитика контента с использованием pandas"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        analyzer = ContentAnalyzer() # pyright: ignore[reportUndefinedVariable]
        analyzer.load_data(ContentItem.objects.all())
        
        stats = {
            'monthly_stats': analyzer.get_monthly_stats(),
            'content_type_distribution': analyzer.get_content_type_distribution(),
            'total_items': ContentItem.objects.count(),
            'unique_users': ContentItem.objects.values('user').distinct().count(),
        }
        
        # Если пользователь авторизован, добавляем персонализированные рекомендации
        if request.user.is_authenticated:
            user_content = ContentItem.objects.filter(user=request.user)
            stats['personal_recommendations'] = analyzer.get_recommendations_based_on_history(user_content)
        
        return Response(stats)
    
class VisualizationView(generics.GenericAPIView):
    """API для визуализаций"""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get(self, request):
        from .visualizations import ContentVisualizer # pyright: ignore[reportMissingImports]
        
        chart_type = request.query_params.get('type', 'all')
        
        if chart_type == 'content_type':
            fig = ContentVisualizer.create_content_type_chart()
            return Response({'chart': fig.to_json()})
        
        elif chart_type == 'timeline':
            fig = ContentVisualizer.create_monthly_timeline()
            return Response({'chart': fig.to_json()})
        
        elif chart_type == 'tag_cloud':
            data = ContentVisualizer.create_tag_cloud_data()
            return Response({'data': data})
        
        elif chart_type == 'categories':
            fig = ContentVisualizer.create_category_comparison()
            if fig:
                return Response({'chart': fig.to_json()})
            return Response({'error': 'No data'}, status=404)
        
        else:  # all
            charts = ContentVisualizer.get_all_charts()
            return Response(charts)