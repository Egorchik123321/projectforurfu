from django.shortcuts import render, get_object_or_404, redirect # pyright: ignore[reportMissingModuleSource]
from django.contrib.auth.decorators import login_required # pyright: ignore[reportMissingModuleSource]
from django.contrib import messages # pyright: ignore[reportMissingModuleSource]
from django.db.models import Count, Q # pyright: ignore[reportMissingModuleSource]
from .models import ContentItem, Category, Recommendation
from .forms import ContentItemForm # pyright: ignore[reportMissingImports]
from taggit.models import Tag # pyright: ignore[reportMissingImports]
import pandas as pd # pyright: ignore[reportMissingModuleSource]
from django.core.paginator import Paginator # pyright: ignore[reportMissingModuleSource]

def home(request):
    """Главная страница"""
    # Статистика
    total_content = ContentItem.objects.count()
    total_categories = Category.objects.count()
    
    # Последние добавления
    latest_content = ContentItem.objects.select_related('category', 'user').order_by('-created_at')[:6]
    
    # Популярные теги
    popular_tags = Tag.objects.annotate(num_times=Count('taggit_taggeditem_items')).order_by('-num_times')[:10]
    
    context = {
        'total_content': total_content,
        'total_categories': total_categories,
        'latest_content': latest_content,
        'popular_tags': popular_tags,
    }
    return render(request, 'content/home.html', context)

def content_list(request):
    """Список всего контента"""
    content_items = ContentItem.objects.select_related('category', 'user').order_by('-created_at')
    
    # Фильтрация по категории
    category_slug = request.GET.get('category')
    if category_slug:
        content_items = content_items.filter(category__slug=category_slug)
    
    # Фильтрация по тегу
    tag_slug = request.GET.get('tag')
    if tag_slug:
        content_items = content_items.filter(tags__slug=tag_slug)
    
    # Фильтрация по типу
    content_type = request.GET.get('type')
    if content_type:
        content_items = content_items.filter(content_type=content_type)
    
    # Поиск
    search_query = request.GET.get('q')
    if search_query:
        content_items = content_items.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(tags__name__icontains=search_query)
        ).distinct()
    
    # Пагинация
    paginator = Paginator(content_items, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Все категории для фильтра
    categories = Category.objects.all()
    
    # Типы контента
    content_types = ContentItem.CONTENT_TYPES
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'content_types': content_types,
        'selected_category': category_slug,
        'selected_type': content_type,
        'selected_tag': tag_slug,
        'search_query': search_query or '',
    }
    return render(request, 'content/content_list.html', context)

def content_detail(request, pk):
    """Детальная страница контента"""
    content_item = get_object_or_404(
        ContentItem.objects.select_related('category', 'user'),
        pk=pk
    )
    
    # Похожий контент по тегам
    similar_content = ContentItem.objects.filter(
        tags__in=content_item.tags.all()
    ).exclude(pk=pk).distinct()[:4]
    
    # Простая рекомендательная система
    recommendations = []
    if request.user.is_authenticated:
        # Находим контент с похожими тегами
        user_tags = Tag.objects.filter(
            taggit_taggeditem_items__content_object__user=request.user
        ).distinct()
        
        if user_tags:
            recommended = ContentItem.objects.filter(
                tags__in=user_tags
            ).exclude(
                Q(pk=pk) | Q(user=request.user)
            ).distinct()[:3]
            
            for rec in recommended:
                common_tags = set(rec.tags.names()) & set(content_item.tags.names())
                if common_tags:
                    recommendations.append({
                        'item': rec,
                        'reason': f"Общие теги: {', '.join(list(common_tags)[:3])}"
                    })
    
    context = {
        'content_item': content_item,
        'similar_content': similar_content,
        'recommendations': recommendations,
    }
    return render(request, 'content/content_detail.html', context)

@login_required
def add_content(request):
    """Добавление нового контента"""
    if request.method == 'POST':
        form = ContentItemForm(request.POST)
        if form.is_valid():
            content_item = form.save(commit=False)
            content_item.user = request.user
            content_item.save()
            form.save_m2m()  # Для тегов
            
            messages.success(request, 'Контент успешно добавлен!')
            return redirect('content_detail', pk=content_item.pk)
    else:
        form = ContentItemForm()
    
    return render(request, 'content/content_form.html', {'form': form})

@login_required
def edit_content(request, pk):
    """Редактирование контента"""
    content_item = get_object_or_404(ContentItem, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = ContentItemForm(request.POST, instance=content_item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Контент успешно обновлен!')
            return redirect('content_detail', pk=content_item.pk)
    else:
        form = ContentItemForm(instance=content_item)
    
    return render(request, 'content/content_form.html', {'form': form})

@login_required
def delete_content(request, pk):
    """Удаление контента"""
    content_item = get_object_or_404(ContentItem, pk=pk, user=request.user)
    
    if request.method == 'POST':
        content_item.delete()
        messages.success(request, 'Контент успешно удален!')
        return redirect('content_list')
    
    return render(request, 'content/content_confirm_delete.html', {'content_item': content_item})

def category_detail(request, slug):
    """Детальная страница категории"""
    category = get_object_or_404(Category, slug=slug)
    content_items = ContentItem.objects.filter(category=category).order_by('-created_at')
    
    # Статистика по категории
    stats = content_items.aggregate(
        total=Count('id'),
        articles=Count('id', filter=Q(content_type='article')),
        videos=Count('id', filter=Q(content_type='video')),
        books=Count('id', filter=Q(content_type='book')),
    )
    
    # Популярные теги в категории
    popular_tags = Tag.objects.filter(
        taggit_taggeditem_items__content_object__category=category
    ).annotate(num_times=Count('taggit_taggeditem_items')).order_by('-num_times')[:10]
    
    context = {
        'category': category,
        'content_items': content_items[:12],
        'stats': stats,
        'popular_tags': popular_tags,
    }
    return render(request, 'content/category_detail.html', context)

def tag_detail(request, slug):
    """Детальная страница тега"""
    tag = get_object_or_404(Tag, slug=slug)
    content_items = ContentItem.objects.filter(tags=tag).order_by('-created_at')
    
    context = {
        'tag': tag,
        'content_items': content_items,
    }
    return render(request, 'content/tag_detail.html', context)

def statistics(request):
    """Страница со статистикой"""
    # Используем pandas для анализа данных
    import pandas as pd # pyright: ignore[reportMissingModuleSource]
    from django.db import connection # pyright: ignore[reportMissingModuleSource]
    
    # Получаем данные через pandas для анализа
    query = """
    SELECT 
        c.content_type,
        COUNT(*) as count,
        AVG(LENGTH(ci.description)) as avg_desc_length
    FROM content_contentitem ci
    JOIN content_category c ON ci.category_id = c.id
    GROUP BY c.content_type
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        stats_data = pd.DataFrame(cursor.fetchall(), columns=columns)
    
    # Общая статистика
    total_content = ContentItem.objects.count()
    total_users = ContentItem.objects.values('user').distinct().count()
    avg_tags_per_item = ContentItem.objects.annotate(
        tag_count=Count('tags')
    ).aggregate(avg=Avg('tag_count'))['avg'] or 0 # pyright: ignore[reportUndefinedVariable]
    
    context = {
        'total_content': total_content,
        'total_users': total_users,
        'avg_tags_per_item': round(avg_tags_per_item, 1),
        'stats_data': stats_data.to_dict('records'),
    }
    return render(request, 'content/statistics.html', context)