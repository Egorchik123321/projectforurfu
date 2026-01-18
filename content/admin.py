from django.contrib import admin # pyright: ignore[reportMissingModuleSource]
from .models import Category, ContentItem, Recommendation
from taggit.models import Tag # pyright: ignore[reportMissingImports]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(ContentItem)
class ContentItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'content_type', 'status', 'created_at')
    list_filter = ('content_type', 'status', 'created_at', 'category')
    search_fields = ('title', 'description', 'url')
    filter_horizontal = ()
    raw_id_fields = ('user',)
    date_hierarchy = 'created_at'
    list_per_page = 20

@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('user', 'content_item', 'score', 'reason', 'created_at')
    list_filter = ('created_at', 'score')
    search_fields = ('user__username', 'content_item__title', 'reason')
    list_per_page = 20

# Регистрируем Tag из taggit для управления в админке
admin.site.register(Tag)