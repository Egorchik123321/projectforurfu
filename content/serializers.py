from rest_framework import serializers # pyright: ignore[reportMissingImports]
from taggit.serializers import TagListSerializerField, TaggitSerializer # pyright: ignore[reportMissingImports]
from .models import Category, ContentItem, Recommendation
from django.contrib.auth.models import User # pyright: ignore[reportMissingModuleSource]

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class CategorySerializer(serializers.ModelSerializer):
    content_count = serializers.IntegerField(source='contentitem_set.count', read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'content_count']

class ContentItemSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()
    user = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )
    
    # Статистика
    view_count = serializers.SerializerMethodField()
    similar_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ContentItem
        fields = [
            'id', 'title', 'url', 'description', 'content_type',
            'category', 'category_id', 'status', 'tags', 'user',
            'created_at', 'updated_at', 'completed_at',
            'view_count', 'similar_count'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']
    
    def get_view_count(self, obj):
        # Можно добавить систему просмотров
        return 0
    
    def get_similar_count(self, obj):
        from taggit.models import Tag # pyright: ignore[reportMissingImports]
        similar = ContentItem.objects.filter(
            tags__in=obj.tags.all()
        ).exclude(id=obj.id).distinct().count()
        return similar
    
    def create(self, validated_data):
        # Автоматически назначаем текущего пользователя
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class RecommendationSerializer(serializers.ModelSerializer):
    content_item = ContentItemSerializer(read_only=True)
    content_item_id = serializers.PrimaryKeyRelatedField(
        queryset=ContentItem.objects.all(),
        source='content_item',
        write_only=True
    )
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Recommendation
        fields = ['id', 'user', 'content_item', 'content_item_id', 'score', 'reason', 'created_at']
        read_only_fields = ['user', 'created_at']