from django.db.models import Count, Q # pyright: ignore[reportMissingModuleSource]
from taggit.models import Tag # pyright: ignore[reportMissingImports]
import numpy as np # pyright: ignore[reportMissingImports]
from collections import defaultdict
from datetime import datetime, timedelta
import math

class AdvancedRecommendationEngine:
    """Продвинутый движок рекомендаций"""
    
    def __init__(self):
        self.user_profiles = {}
        self.content_vectors = {}
    
    def build_user_profile(self, user):
        """Создание профиля пользователя на основе его контента"""
        user_content = user.contentitem_set.all()
        
        # Собираем статистику по тегам
        tag_weights = defaultdict(float)
        type_weights = defaultdict(float)
        category_weights = defaultdict(float)
        
        for item in user_content:
            # Вес зависит от статуса и давности
            time_weight = self._calculate_time_weight(item.created_at)
            status_weight = self._get_status_weight(item.status)
            
            total_weight = time_weight * status_weight
            
            # Теги
            for tag in item.tags.all():
                tag_weights[tag.name] += total_weight
            
            # Типы контента
            type_weights[item.content_type] += total_weight
            
            # Категории
            if item.category:
                category_weights[item.category.slug] += total_weight
        
        # Нормализуем веса
        tag_total = sum(tag_weights.values()) or 1
        type_total = sum(type_weights.values()) or 1
        category_total = sum(category_weights.values()) or 1
        
        profile = {
            'tags': {k: v/tag_total for k, v in tag_weights.items()},
            'content_types': {k: v/type_total for k, v in type_weights.items()},
            'categories': {k: v/category_total for k, v in category_weights.items()},
            'total_items': user_content.count()
        }
        
        self.user_profiles[user.id] = profile
        return profile
    
    def build_content_vector(self, content_item):
        """Создание вектора для контента"""
        vector = {
            'tags': set(tag.name for tag in content_item.tags.all()),
            'content_type': content_item.content_type,
            'category': content_item.category.slug if content_item.category else None,
            'popularity': self._calculate_popularity(content_item),
            'recency': self._calculate_recency(content_item.created_at)
        }
        
        self.content_vectors[content_item.id] = vector
        return vector
    
    def calculate_similarity(self, user_profile, content_vector):
        """Расчет схожести между пользователем и контентом"""
        score = 0.0
        
        # Совпадение по тегам
        user_tags = set(user_profile['tags'].keys())
        content_tags = content_vector['tags']
        
        common_tags = user_tags.intersection(content_tags)
        if common_tags:
            tag_score = sum(user_profile['tags'].get(tag, 0) for tag in common_tags)
            score += tag_score * 0.4
        
        # Совпадение по типу контента
        content_type = content_vector['content_type']
        type_weight = user_profile['content_types'].get(content_type, 0)
        score += type_weight * 0.3
        
        # Совпадение по категории
        category = content_vector['category']
        if category:
            category_weight = user_profile['categories'].get(category, 0)
            score += category_weight * 0.2
        
        # Популярность и свежесть
        score += content_vector['popularity'] * 0.05
        score += content_vector['recency'] * 0.05
        
        return min(score, 1.0)
    
    def get_recommendations(self, user, limit=10):
        """Получение рекомендаций для пользователя"""
        user_profile = self.build_user_profile(user)
        
        # Исключаем контент пользователя
        user_content_ids = set(user.contentitem_set.values_list('id', flat=True))
        
        # Берем свежий и релевантный контент
        candidates = ContentItem.objects.exclude( # pyright: ignore[reportUndefinedVariable]
            id__in=user_content_ids
        ).select_related('category').prefetch_related('tags')[:100]
        
        recommendations = []
        for candidate in candidates:
            content_vector = self.build_content_vector(candidate)
            similarity = self.calculate_similarity(user_profile, content_vector)
            
            if similarity > 0.1:  # Минимальный порог
                recommendations.append({
                    'content_item': candidate,
                    'score': similarity,
                    'reason': self._generate_reason(user_profile, content_vector, similarity)
                })
        
        # Сортируем по релевантности
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return recommendations[:limit]
    
    def _calculate_time_weight(self, created_at):
        """Вес в зависимости от времени создания"""
        days_ago = (datetime.now(created_at.tzinfo) - created_at).days
        return math.exp(-days_ago / 30)  # Экспоненциальное затухание
    
    def _get_status_weight(self, status):
        """Вес в зависимости от статуса"""
        weights = {
            'completed': 1.0,
            'in_progress': 0.8,
            'new': 0.6,
            'postponed': 0.3
        }
        return weights.get(status, 0.5)
    
    def _calculate_popularity(self, content_item):
        """Расчет популярности контента"""
        # Простая метрика популярности
        similar_count = ContentItem.objects.filter( # pyright: ignore[reportUndefinedVariable]
            tags__in=content_item.tags.all()
        ).count()
        
        return min(similar_count / 10, 1.0)
    
    def _calculate_recency(self, created_at):
        """Свежесть контента"""
        days_ago = (datetime.now(created_at.tzinfo) - created_at).days
        return max(0, 1 - (days_ago / 90))  # Контент старше 90 дней теряет актуальность
    
    def _generate_reason(self, user_profile, content_vector, similarity):
        """Генерация объяснения рекомендации"""
        reasons = []
        
        # Теги
        common_tags = set(user_profile['tags'].keys()).intersection(content_vector['tags'])
        if common_tags:
            top_tags = sorted(common_tags, 
                            key=lambda x: user_profile['tags'].get(x, 0), 
                            reverse=True)[:2]
            reasons.append(f"Совпадают теги: {', '.join(top_tags)}")
        
        # Тип контента
        content_type = content_vector['content_type']
        if user_profile['content_types'].get(content_type, 0) > 0.1:
            type_names = {
                'article': 'статьи',
                'video': 'видео',
                'book': 'книги',
                'podcast': 'подкасты',
                'course': 'курсы'
            }
            reasons.append(f"Вы часто сохраняете {type_names.get(content_type, 'такой контент')}")
        
        # Категория
        category = content_vector['category']
        if category and user_profile['categories'].get(category, 0) > 0.1:
            reasons.append(f"Входит в ваши любимые категории")
        
        # Свежесть
        if content_vector['recency'] > 0.8:
            reasons.append("Свежий контент")
        
        return " • ".join(reasons[:2]) if reasons else "Рекомендовано на основе вашей активности"