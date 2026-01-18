import requests # pyright: ignore[reportMissingModuleSource]
import json
from django.conf import settings # pyright: ignore[reportMissingModuleSource]
from datetime import datetime, timedelta
import pandas as pd # pyright: ignore[reportMissingModuleSource]
from typing import List, Dict, Optional

class NewsAPIClient:
    """Клиент для NewsAPI (пример внешнего API)"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or getattr(settings, 'NEWS_API_KEY', '')
        self.base_url = 'https://newsapi.org/v2'
    
    def search_articles(self, query: str, language='ru', page_size=10):
        """Поиск статей по запросу"""
        if not self.api_key:
            return {'error': 'API key not configured'}
        
        endpoint = f'{self.base_url}/everything'
        params = {
            'q': query,
            'language': language,
            'pageSize': page_size,
            'apiKey': self.api_key,
            'sortBy': 'relevance'
        }
        
        try:
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'ok':
                return self._format_articles(data['articles'], query)
            return {'error': data.get('message', 'Unknown error')}
            
        except requests.RequestException as e:
            return {'error': str(e)}
    
    def _format_articles(self, articles: List[Dict], query: str) -> List[Dict]:
        """Форматирование статей для нашей системы"""
        formatted = []
        for article in articles:
            formatted.append({
                'title': article.get('title', ''),
                'url': article.get('url', ''),
                'description': article.get('description', '')[:200],
                'source': article.get('source', {}).get('name', ''),
                'published_at': article.get('publishedAt', ''),
                'content_type': 'article',
                'tags': self._extract_tags(article, query),
                'external_id': article.get('url', '')[:100]
            })
        return formatted
    
    def _extract_tags(self, article: Dict, query: str) -> List[str]:
        """Извлечение тегов из статьи"""
        tags = [query.lower()]
        
        # Добавляем источник как тег
        source = article.get('source', {}).get('name', '').lower()
        if source:
            tags.append(source)
        
        # Можно добавить логику для извлечения ключевых слов
        # из заголовка или описания
        
        return list(set(tags))[:5]

class YouTubeAPIClient:
    """Клиент для YouTube API (упрощенная версия)"""
    
    def search_videos(self, query: str, max_results=10):
        """Поиск видео (симуляция, так как нужен API ключ)"""
        # В реальности здесь будет работа с YouTube API
        # Для примера возвращаем mock-данные
        
        mock_videos = [
            {
                'title': f'Видео про {query} - часть 1',
                'url': f'https://youtube.com/watch?v=test1_{query}',
                'description': f'Обучение {query} для начинающих',
                'content_type': 'video',
                'tags': [query, 'обучение', 'видео'],
                'duration': '10:30',
                'views': '1500'
            },
            {
                'title': f'Как освоить {query} быстро',
                'url': f'https://youtube.com/watch?v=test2_{query}',
                'description': f'Секреты быстрого изучения {query}',
                'content_type': 'video',
                'tags': [query, 'быстро', 'уроки'],
                'duration': '15:45',
                'views': '2500'
            }
        ]
        
        return mock_videos[:max_results]

class ContentAnalyzer:
    """Анализатор контента с использованием pandas"""
    
    def __init__(self):
        self.df = None
    
    def load_data(self, queryset):
        """Загрузка данных из queryset в DataFrame"""
        data = list(queryset.values(
            'id', 'title', 'content_type', 'status',
            'created_at', 'category__name'
        ))
        self.df = pd.DataFrame(data)
        
        if not self.df.empty:
            self.df['created_at'] = pd.to_datetime(self.df['created_at'])
            self.df['month'] = self.df['created_at'].dt.to_period('M')
        
        return self.df
    
    def get_monthly_stats(self):
        """Статистика по месяцам"""
        if self.df is None or self.df.empty:
            return {}
        
        monthly = self.df.groupby('month').agg({
            'id': 'count',
            'content_type': lambda x: x.value_counts().to_dict()
        }).reset_index()
        
        monthly['month'] = monthly['month'].astype(str)
        return monthly.to_dict('records')
    
    def get_content_type_distribution(self):
        """Распределение по типам контента"""
        if self.df is None or self.df.empty:
            return {}
        
        distribution = self.df['content_type'].value_counts().to_dict()
        return distribution
    
    def get_recommendations_based_on_history(self, user_content):
        """Рекомендации на основе истории пользователя"""
        if self.df is None or self.df.empty:
            return []
        
        # Простая рекомендательная логика
        user_types = user_content.values_list('content_type', flat=True)
        if not user_types:
            return []
        
        # Рекомендуем популярный контент того же типа
        popular_content = self.df[
            self.df['content_type'].isin(user_types)
        ].sort_values('created_at', ascending=False)
        
        recommendations = popular_content.head(5)['id'].tolist()
        return recommendations