import plotly.graph_objects as go # pyright: ignore[reportMissingImports]
import plotly.express as px # pyright: ignore[reportMissingImports]
from plotly.subplots import make_subplots # pyright: ignore[reportMissingImports]
import pandas as pd # pyright: ignore[reportMissingModuleSource]
from django.db.models import Count # pyright: ignore[reportMissingModuleSource]
from .models import ContentItem, Category
import json

class ContentVisualizer:
    """Создание визуализаций для контента"""
    
    @staticmethod
    def create_content_type_chart():
        """Круговая диаграмма распределения по типам контента"""
        data = ContentItem.objects.values('content_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        df = pd.DataFrame(list(data))
        
        if df.empty:
            # Создаем пустой график
            fig = go.Figure()
            fig.add_annotation(
                text="Нет данных для отображения",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
        
        # Преобразуем тип контента в читаемый формат
        type_names = {
            'article': 'Статьи',
            'video': 'Видео',
            'book': 'Книги',
            'podcast': 'Подкасты',
            'course': 'Курсы'
        }
        
        df['content_type'] = df['content_type'].map(
            lambda x: type_names.get(x, x.capitalize())
        )
        
        fig = px.pie(
            df, 
            values='count', 
            names='content_type',
            title='Распределение по типам контента',
            hole=0.3,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Количество: %{value}<br>Процент: %{percent}'
        )
        
        fig.update_layout(
            margin=dict(t=50, b=20, l=20, r=20),
            showlegend=False
        )
        
        return fig
    
    @staticmethod
    def create_monthly_timeline():
        """График добавления контента по месяцам"""
        from django.db.models.functions import TruncMonth # pyright: ignore[reportMissingModuleSource]
        
        data = ContentItem.objects.annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')
        
        df = pd.DataFrame(list(data))
        
        if df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="Нет данных для отображения",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
        
        df['month'] = pd.to_datetime(df['month'])
        df['month_str'] = df['month'].dt.strftime('%b %Y')
        
        fig = px.bar(
            df,
            x='month_str',
            y='count',
            title='Динамика добавления контента',
            labels={'month_str': 'Месяц', 'count': 'Количество'},
            color='count',
            color_continuous_scale='Blues'
        )
        
        fig.update_layout(
            xaxis_title="Месяц",
            yaxis_title="Количество добавлений",
            margin=dict(t=50, b=50, l=50, r=20),
            coloraxis_showscale=False
        )
        
        fig.update_traces(
            hovertemplate='<b>%{x}</b><br>Добавлено: %{y}'
        )
        
        return fig
    
    @staticmethod
    def create_tag_cloud_data():
        """Данные для облака тегов"""
        from taggit.models import Tag # pyright: ignore[reportMissingImports]
        from django.db.models import Count # pyright: ignore[reportMissingModuleSource]
        
        tags = Tag.objects.annotate(
            num_times=Count('taggit_taggeditem_items')
        ).order_by('-num_times')[:30]
        
        data = []
        for tag in tags:
            data.append({
                'text': tag.name,
                'value': tag.num_times,
                'size': min(50, 10 + tag.num_times * 2)
            })
        
        return data
    
    @staticmethod
    def create_category_comparison():
        """Сравнение категорий"""
        data = Category.objects.annotate(
            content_count=Count('contentitem'),
            avg_tags=Count('contentitem__tags') / Count('contentitem')
        ).order_by('-content_count')
        
        df = pd.DataFrame(list(data.values('name', 'content_count', 'avg_tags')))
        
        if df.empty:
            return None
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Количество контента по категориям', 'Среднее количество тегов'),
            specs=[[{'type': 'bar'}, {'type': 'bar'}]]
        )
        
        # Первый график - количество контента
        fig.add_trace(
            go.Bar(
                x=df['name'],
                y=df['content_count'],
                name='Количество',
                marker_color='lightblue',
                hovertemplate='<b>%{x}</b><br>Контента: %{y}'
            ),
            row=1, col=1
        )
        
        # Второй график - среднее количество тегов
        fig.add_trace(
            go.Bar(
                x=df['name'],
                y=df['avg_tags'].round(1),
                name='Ср. тегов',
                marker_color='lightcoral',
                hovertemplate='<b>%{x}</b><br>Среднее тегов: %{y}'
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            title_text='Сравнение категорий',
            showlegend=False,
            margin=dict(t=100, b=50, l=50, r=50)
        )
        
        fig.update_xaxes(tickangle=45)
        
        return fig
    
    @staticmethod
    def get_all_charts():
        """Получить все графики в виде JSON"""
        charts = {
            'content_type_pie': ContentVisualizer.create_content_type_chart().to_json(),
            'monthly_timeline': ContentVisualizer.create_monthly_timeline().to_json(),
            'tag_cloud': ContentVisualizer.create_tag_cloud_data(),
        }
        
        category_comparison = ContentVisualizer.create_category_comparison()
        if category_comparison:
            charts['category_comparison'] = category_comparison.to_json()
        
        return charts